import sqlite3

from app_paths import get_app_paths
from services.data_protection_service import get_data_protection_service


APP_PATHS = get_app_paths()
DB_DIR = APP_PATHS.data_dir
DB_PATH = APP_PATHS.db_path
_ALLOWED_TABLE_NAMES = {"quotes"}


def get_connection():
    """Retourne une connexion SQLite."""
    DB_DIR.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_database():
    """Cree les tables si elles n'existent pas encore."""
    get_data_protection_service().initialize()

    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT NOT NULL,
                telephone TEXT,
                email TEXT,
                adresse TEXT,
                notes TEXT
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS quotes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero TEXT NOT NULL UNIQUE,
                client_id INTEGER NOT NULL,
                statut TEXT NOT NULL DEFAULT 'Brouillon',
                total REAL NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (client_id) REFERENCES clients (id)
            )
            """
        )
        _ensure_column(connection, "quotes", "delai", "TEXT NOT NULL DEFAULT '2 jours'")
        _ensure_column(connection, "quotes", "materiel_charge", "TEXT NOT NULL DEFAULT 'client'")
        _ensure_column(connection, "quotes", "acompte_percent", "INTEGER NOT NULL DEFAULT 30")
        _ensure_column(connection, "quotes", "validite", "TEXT NOT NULL DEFAULT '30 jours'")
        _ensure_column(connection, "quotes", "conditions_exceptionnelles", "TEXT NOT NULL DEFAULT ''")
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS quote_lines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                quote_id INTEGER NOT NULL,
                description TEXT NOT NULL,
                quantite REAL NOT NULL,
                prix_unitaire REAL NOT NULL,
                total_ligne REAL NOT NULL,
                FOREIGN KEY (quote_id) REFERENCES quotes (id) ON DELETE CASCADE
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS quote_catalog_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT NOT NULL UNIQUE,
                prix_unitaire REAL NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS appointments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id INTEGER NOT NULL,
                date_rdv TEXT NOT NULL,
                heure_rdv TEXT NOT NULL,
                adresse TEXT NOT NULL,
                note TEXT,
                FOREIGN KEY (client_id) REFERENCES clients (id)
            )
            """
        )


def _ensure_column(connection, table_name, column_name, column_definition):
    if table_name not in _ALLOWED_TABLE_NAMES:
        raise ValueError(f"Table non autorisee pour migration: {table_name}")

    columns = connection.execute(f"PRAGMA table_info({table_name})").fetchall()
    column_names = {column["name"] for column in columns}
    if column_name in column_names:
        return

    connection.execute(
        f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_definition}"
    )


def notify_data_changed(reason: str):
    get_data_protection_service().on_data_changed(reason)
