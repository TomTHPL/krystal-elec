from __future__ import annotations

import subprocess
import sys
import tempfile
import threading
from pathlib import Path
from urllib import request
from urllib.error import URLError
import json


def _fetch_latest_release(repo: str) -> dict | None:
    url = f"https://api.github.com/repos/{repo}/releases/latest"
    req = request.Request(url, headers={"Accept": "application/vnd.github+json", "User-Agent": "KrystalElec"})
    try:
        with request.urlopen(req, timeout=5) as response:
            return json.loads(response.read())
    except (URLError, Exception):
        return None


def _version_tuple(version_str: str) -> tuple[int, ...]:
    try:
        return tuple(int(x) for x in version_str.lstrip("v").split("."))
    except ValueError:
        return (0,)


def check_for_update(current_version: str, repo: str) -> tuple[bool, str, str]:
    """Retourne (update_disponible, derniere_version, url_download)."""
    data = _fetch_latest_release(repo)
    if not data:
        return False, current_version, ""

    latest_tag = data.get("tag_name", "")
    if not latest_tag:
        return False, current_version, ""

    assets = data.get("assets", [])
    download_url = ""
    for asset in assets:
        if asset.get("name", "").endswith(".exe"):
            download_url = asset.get("browser_download_url", "")
            break

    if _version_tuple(latest_tag) > _version_tuple(current_version):
        return True, latest_tag, download_url

    return False, latest_tag, ""


def download_and_launch_installer(download_url: str, on_progress=None) -> None:
    """Télécharge l'installateur dans un dossier temporaire et le lance."""
    def _run():
        try:
            with request.urlopen(download_url, timeout=60) as response:
                total = int(response.headers.get("Content-Length", 0))
                downloaded = 0
                chunk_size = 65536
                suffix = ".exe"
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                    tmp_path = Path(tmp.name)
                    while True:
                        chunk = response.read(chunk_size)
                        if not chunk:
                            break
                        tmp.write(chunk)
                        downloaded += len(chunk)
                        if on_progress and total:
                            on_progress(downloaded / total)

            subprocess.Popen([str(tmp_path)], shell=True)
            sys.exit(0)
        except Exception as e:
            if on_progress:
                on_progress(-1)

    thread = threading.Thread(target=_run, daemon=True)
    thread.start()
