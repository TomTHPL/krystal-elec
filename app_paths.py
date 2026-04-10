from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path


@dataclass(frozen=True)
class AppPaths:
    project_root: Path
    bundle_root: Path
    app_data_root: Path
    data_dir: Path
    db_path: Path
    backups_dir: Path
    exports_dir: Path
    logs_dir: Path


@lru_cache(maxsize=1)
def get_app_paths() -> AppPaths:
    if getattr(sys, "frozen", False):
        project_root = Path(sys.executable).resolve().parent
        bundle_root = Path(getattr(sys, "_MEIPASS", project_root))
    else:
        project_root = Path(__file__).resolve().parent
        bundle_root = project_root

    custom_root = os.getenv("CRYSTALELEC_DATA_DIR")
    candidates: list[Path] = []
    if custom_root:
        candidates.append(Path(custom_root).expanduser())
    else:
        local_appdata = os.getenv("LOCALAPPDATA")
        if local_appdata:
            candidates.append(Path(local_appdata) / "CrystalElec")
        candidates.append(Path.home() / ".crystalelec")

    # Last-resort fallback for restricted environments (sandbox, locked profile folders).
    candidates.append(project_root / ".localdata")

    app_data_root: Path | None = None
    for candidate in candidates:
        try:
            candidate.mkdir(parents=True, exist_ok=True)
            app_data_root = candidate
            break
        except OSError:
            continue

    if app_data_root is None:
        raise RuntimeError("Impossible de creer un dossier de donnees utilisateur.")

    data_dir = app_data_root / "data"
    db_path = data_dir / "elecflow.db"
    backups_dir = app_data_root / "backups"
    exports_dir = app_data_root / "exports"
    logs_dir = app_data_root / "logs"

    return AppPaths(
        project_root=project_root,
        bundle_root=bundle_root,
        app_data_root=app_data_root,
        data_dir=data_dir,
        db_path=db_path,
        backups_dir=backups_dir,
        exports_dir=exports_dir,
        logs_dir=logs_dir,
    )
