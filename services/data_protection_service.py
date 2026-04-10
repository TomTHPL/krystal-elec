from __future__ import annotations

import os
import shutil
import threading
from datetime import datetime
from pathlib import Path
from queue import Empty, Queue
from typing import Any
from urllib import parse, request

from app_paths import AppPaths, get_app_paths


class DataProtectionService:
    def __init__(self, paths: AppPaths | None = None) -> None:
        self.paths = paths or get_app_paths()
        self._lock = threading.Lock()
        self._upload_queue: Queue[dict[str, Any]] = Queue()
        self._upload_worker: threading.Thread | None = None
        self._upload_scheduled = False
        self._last_backup_at: datetime | None = None
        self._initialized = False

    def initialize(self) -> None:
        with self._lock:
            if self._initialized:
                return

            self.paths.app_data_root.mkdir(parents=True, exist_ok=True)
            self.paths.data_dir.mkdir(parents=True, exist_ok=True)
            self.paths.backups_dir.mkdir(parents=True, exist_ok=True)
            self.paths.exports_dir.mkdir(parents=True, exist_ok=True)
            self.paths.logs_dir.mkdir(parents=True, exist_ok=True)
            self._initialized = True

        if self.paths.db_path.exists():
            self.create_backup("startup", force=True)
            self.schedule_cloud_upload("startup")

    def on_data_changed(self, reason: str) -> None:
        self.create_backup(reason, force=False)
        self.schedule_cloud_upload(reason)

    def create_backup(self, reason: str, force: bool) -> Path | None:
        with self._lock:
            if not self.paths.db_path.exists():
                return None

            now = datetime.now()
            min_interval_minutes = max(1, self._get_int_env("CRYSTALELEC_BACKUP_INTERVAL_MINUTES", 5))
            if not force and self._last_backup_at is not None:
                elapsed = (now - self._last_backup_at).total_seconds()
                if elapsed < min_interval_minutes * 60:
                    return None

            safe_reason = self._sanitize_filename(reason)
            filename = f"elecflow_{now.strftime('%Y%m%d_%H%M%S')}_{safe_reason}.db"
            destination = self.paths.backups_dir / filename
            shutil.copy2(self.paths.db_path, destination)
            self._last_backup_at = now
            self._prune_old_backups()
            return destination

    def schedule_cloud_upload(self, reason: str) -> None:
        if not self._is_cloud_enabled():
            return

        with self._lock:
            if self._upload_scheduled:
                return
            self._upload_scheduled = True
            self._upload_queue.put({"reason": reason, "scheduled_at": datetime.now()})
            if self._upload_worker is None or not self._upload_worker.is_alive():
                self._upload_worker = threading.Thread(
                    target=self._run_upload_worker,
                    name="data-cloud-sync",
                    daemon=True,
                )
                self._upload_worker.start()

    def _run_upload_worker(self) -> None:
        while True:
            try:
                job = self._upload_queue.get(timeout=1)
            except Empty:
                return

            try:
                self._upload_current_database(job)
            except Exception as error:  # pragma: no cover - depends on external IO
                self._append_log(f"Cloud sync failed: {error}")
            finally:
                with self._lock:
                    self._upload_scheduled = False

    def _upload_current_database(self, job: dict[str, Any]) -> None:
        if not self.paths.db_path.exists():
            return

        payload = self.paths.db_path.read_bytes()
        if not payload:
            return

        if self._is_supabase_enabled():
            self._upload_to_supabase(payload, job)
            return

        webhook_url = os.getenv("CRYSTALELEC_BACKUP_WEBHOOK_URL")
        if webhook_url:
            self._upload_to_webhook(webhook_url, payload, job)

    def _upload_to_supabase(self, payload: bytes, job: dict[str, Any]) -> None:
        supabase_url = os.getenv("SUPABASE_URL", "").rstrip("/")
        supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY")
        bucket = os.getenv("SUPABASE_BACKUP_BUCKET", "crystalelec-backups")
        machine_name = self._sanitize_filename(os.getenv("COMPUTERNAME", "desktop"))
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        reason = self._sanitize_filename(str(job.get("reason", "sync")))

        latest_object = f"{machine_name}/latest/elecflow.db"
        history_object = f"{machine_name}/history/elecflow_{timestamp}_{reason}.db"

        self._supabase_upload_object(supabase_url, supabase_key, bucket, latest_object, payload)
        self._supabase_upload_object(supabase_url, supabase_key, bucket, history_object, payload)

    def _supabase_upload_object(
        self,
        supabase_url: str,
        supabase_key: str | None,
        bucket: str,
        object_path: str,
        payload: bytes,
    ) -> None:
        if not supabase_url or not supabase_key:
            return

        bucket_escaped = parse.quote(bucket, safe="")
        object_escaped = parse.quote(object_path, safe="/")
        url = f"{supabase_url}/storage/v1/object/{bucket_escaped}/{object_escaped}"
        headers = {
            "authorization": f"Bearer {supabase_key}",
            "apikey": supabase_key,
            "x-upsert": "true",
            "content-type": "application/octet-stream",
        }
        req = request.Request(url=url, data=payload, method="POST", headers=headers)
        with request.urlopen(req, timeout=20):  # pragma: no cover - external IO
            pass

    def _upload_to_webhook(self, webhook_url: str, payload: bytes, job: dict[str, Any]) -> None:
        reason = self._sanitize_filename(str(job.get("reason", "sync")))
        headers = {
            "content-type": "application/octet-stream",
            "x-crystalelec-reason": reason,
            "x-crystalelec-filename": "elecflow.db",
        }
        req = request.Request(url=webhook_url, data=payload, method="POST", headers=headers)
        with request.urlopen(req, timeout=20):  # pragma: no cover - external IO
            pass

    def _prune_old_backups(self) -> None:
        keep = max(5, self._get_int_env("CRYSTALELEC_BACKUP_KEEP", 50))
        backup_files = sorted(
            self.paths.backups_dir.glob("elecflow_*.db"),
            key=lambda item: item.stat().st_mtime,
            reverse=True,
        )
        for old_file in backup_files[keep:]:
            old_file.unlink(missing_ok=True)

    def _append_log(self, message: str) -> None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_file = self.paths.logs_dir / "data_protection.log"
        log_file.parent.mkdir(parents=True, exist_ok=True)
        with log_file.open("a", encoding="utf-8") as handle:
            handle.write(f"[{timestamp}] {message}\n")

    def _is_cloud_enabled(self) -> bool:
        return self._is_supabase_enabled() or bool(os.getenv("CRYSTALELEC_BACKUP_WEBHOOK_URL"))

    def _is_supabase_enabled(self) -> bool:
        return bool(os.getenv("SUPABASE_URL")) and bool(
            os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY")
        )

    def _get_int_env(self, key: str, default: int) -> int:
        raw_value = os.getenv(key)
        if raw_value is None:
            return default
        try:
            return int(raw_value)
        except ValueError:
            return default

    def _sanitize_filename(self, value: str) -> str:
        cleaned = "".join(character for character in value if character.isalnum() or character in ("-", "_"))
        return cleaned or "sync"


_SERVICE = DataProtectionService()


def get_data_protection_service() -> DataProtectionService:
    return _SERVICE
