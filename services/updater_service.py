from __future__ import annotations

import json
import os
import subprocess
import threading
from pathlib import Path
from urllib import request
from urllib.error import URLError


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


def _get_downloads_dir() -> Path:
    downloads = Path.home() / "Downloads"
    if not downloads.exists():
        downloads = Path.home() / "Téléchargements"
    if not downloads.exists():
        downloads = Path.home()
    return downloads


def download_installer(download_url: str, on_progress=None, on_done=None) -> None:
    """Télécharge l'installateur dans le dossier Téléchargements."""
    def _run():
        try:
            dest = _get_downloads_dir() / "KrystalElec_Setup.exe"
            with request.urlopen(download_url, timeout=120) as response:
                total = int(response.headers.get("Content-Length", 0))
                downloaded = 0
                chunk_size = 65536
                with open(dest, "wb") as f:
                    while True:
                        chunk = response.read(chunk_size)
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded += len(chunk)
                        if on_progress and total:
                            on_progress(downloaded / total)

            if on_done:
                on_done(dest)

        except Exception:
            if on_progress:
                on_progress(-1)

    threading.Thread(target=_run, daemon=True).start()


def open_installer_location(path: Path) -> None:
    """Ouvre l'explorateur avec le fichier sélectionné."""
    subprocess.Popen(["explorer", "/select,", str(path)])
