from __future__ import annotations

import json
from pathlib import Path

from app_paths import get_app_paths


_SETTINGS_PATH = get_app_paths().app_data_root / "settings.json"


def _load() -> dict:
    try:
        if _SETTINGS_PATH.exists():
            return json.loads(_SETTINGS_PATH.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {}


def _save(data: dict) -> None:
    _SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
    _SETTINGS_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def get_exports_dir() -> Path:
    data = _load()
    custom = data.get("exports_dir")
    if custom:
        path = Path(custom)
        if path.exists() or _try_create(path):
            return path
    return get_app_paths().exports_dir


def set_exports_dir(path: Path | str) -> None:
    data = _load()
    data["exports_dir"] = str(path)
    _save(data)


def _try_create(path: Path) -> bool:
    try:
        path.mkdir(parents=True, exist_ok=True)
        return True
    except Exception:
        return False
