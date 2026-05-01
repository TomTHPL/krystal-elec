from __future__ import annotations

import json
import shutil
import zipfile
from datetime import datetime
from pathlib import Path

BACKUP_MAGIC = "CrystalElecBackup"
BACKUP_SCHEMA_VERSION = 1
BACKUP_EXTENSION = ".cebak"


def create_backup(destination_dir: Path) -> Path:
    from app_paths import get_app_paths
    from version import __version__

    paths = get_app_paths()
    if not paths.db_path.exists():
        raise FileNotFoundError("Base de données introuvable.")

    destination_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = destination_dir / f"CrystalElec_sauvegarde_{timestamp}{BACKUP_EXTENSION}"

    manifest = {
        "magic": BACKUP_MAGIC,
        "schema_version": BACKUP_SCHEMA_VERSION,
        "app_version": __version__,
        "created_at": datetime.now().isoformat(),
    }

    with zipfile.ZipFile(backup_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("manifest.json", json.dumps(manifest, indent=2))
        zf.write(paths.db_path, "database.db")

    return backup_path


def validate_backup(backup_path: Path) -> dict:
    """Valide un fichier de sauvegarde. Retourne le manifest si valide, lève ValueError sinon."""
    if not backup_path.exists():
        raise ValueError("Fichier introuvable.")

    if backup_path.suffix != BACKUP_EXTENSION:
        raise ValueError(
            f"Format non reconnu. Sélectionnez un fichier '{BACKUP_EXTENSION}'."
        )

    try:
        with zipfile.ZipFile(backup_path, "r") as zf:
            if "manifest.json" not in zf.namelist() or "database.db" not in zf.namelist():
                raise ValueError("Fichier corrompu ou incompatible.")
            manifest = json.loads(zf.read("manifest.json"))
    except zipfile.BadZipFile:
        raise ValueError("Le fichier sélectionné n'est pas une sauvegarde valide.")

    if manifest.get("magic") != BACKUP_MAGIC:
        raise ValueError("Ce fichier n'est pas une sauvegarde CrystalElec valide.")

    return manifest


def restore_backup(backup_path: Path) -> None:
    """Restaure une sauvegarde. Lève ValueError si le fichier est invalide."""
    from app_paths import get_app_paths

    manifest = validate_backup(backup_path)  # noqa: F841 — raises if invalid
    paths = get_app_paths()

    if paths.db_path.exists():
        safety = paths.backups_dir / f"pre_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        paths.backups_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(paths.db_path, safety)

    paths.data_dir.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(backup_path, "r") as zf:
        db_data = zf.read("database.db")

    paths.db_path.write_bytes(db_data)
