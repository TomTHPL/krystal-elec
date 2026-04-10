from sqlite3 import IntegrityError

from database import get_connection, notify_data_changed


class CatalogItemRepository:
    """Gere le catalogue produits/services utilise par les devis."""

    def get_all_items(self):
        with get_connection() as connection:
            rows = connection.execute(
                """
                SELECT id, nom, prix_unitaire
                FROM quote_catalog_items
                ORDER BY nom ASC
                """
            ).fetchall()

        return [dict(row) for row in rows]

    def get_item_by_id(self, item_id):
        with get_connection() as connection:
            row = connection.execute(
                """
                SELECT id, nom, prix_unitaire
                FROM quote_catalog_items
                WHERE id = ?
                """,
                (item_id,),
            ).fetchone()

        return dict(row) if row else None

    def add_item(self, nom, prix_unitaire):
        with get_connection() as connection:
            next_id = self._get_next_available_id(connection)
            try:
                connection.execute(
                    """
                    INSERT INTO quote_catalog_items (id, nom, prix_unitaire)
                    VALUES (?, ?, ?)
                    """,
                    (next_id, nom, prix_unitaire),
                )
            except IntegrityError as error:
                raise ValueError("Un article avec ce nom existe deja.") from error
        notify_data_changed("catalog_item_added")

    def update_item(self, item_id, nom, prix_unitaire):
        with get_connection() as connection:
            try:
                connection.execute(
                    """
                    UPDATE quote_catalog_items
                    SET nom = ?, prix_unitaire = ?
                    WHERE id = ?
                    """,
                    (nom, prix_unitaire, item_id),
                )
            except IntegrityError as error:
                raise ValueError("Un article avec ce nom existe deja.") from error
        notify_data_changed("catalog_item_updated")

    def delete_item(self, item_id):
        with get_connection() as connection:
            connection.execute(
                "DELETE FROM quote_catalog_items WHERE id = ?",
                (item_id,),
            )
        notify_data_changed("catalog_item_deleted")

    def _get_next_available_id(self, connection):
        rows = connection.execute(
            "SELECT id FROM quote_catalog_items ORDER BY id ASC"
        ).fetchall()

        next_id = 1
        for row in rows:
            current_id = row["id"]
            if current_id != next_id:
                break
            next_id += 1

        return next_id
