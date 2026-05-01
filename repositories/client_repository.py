from database import get_connection, notify_data_changed


class ClientRepository:
    """Gere les operations CRUD des clients."""

    def get_all_clients(self):
        with get_connection() as connection:
            rows = connection.execute(
                "SELECT * FROM clients ORDER BY nom ASC"
            ).fetchall()
        return [dict(row) for row in rows]

    def get_client_by_id(self, client_id):
        with get_connection() as connection:
            row = connection.execute(
                "SELECT * FROM clients WHERE id = ?",
                (client_id,),
            ).fetchone()

        return dict(row) if row else None

    def add_client(self, nom, telephone, email, adresse, notes):
        with get_connection() as connection:
            next_id = self._get_next_available_id(connection)
            connection.execute(
                """
                INSERT INTO clients (id, nom, telephone, email, adresse, notes)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (next_id, nom, telephone, email, adresse, notes),
            )
        notify_data_changed("client_added")

    def update_client(self, client_id, nom, telephone, email, adresse, notes):
        with get_connection() as connection:
            connection.execute(
                """
                UPDATE clients
                SET nom = ?, telephone = ?, email = ?, adresse = ?, notes = ?
                WHERE id = ?
                """,
                (nom, telephone, email, adresse, notes, client_id),
            )
        notify_data_changed("client_updated")

    def get_quotes_count_for_client(self, client_id):
        with get_connection() as connection:
            row = connection.execute(
                "SELECT COUNT(*) AS count FROM quotes WHERE client_id = ?",
                (client_id,),
            ).fetchone()
        return row["count"] if row else 0

    def delete_client(self, client_id):
        with get_connection() as connection:
            connection.execute("DELETE FROM clients WHERE id = ?", (client_id,))
        notify_data_changed("client_deleted")

    def delete_client_with_quotes(self, client_id):
        with get_connection() as connection:
            connection.execute("DELETE FROM quotes WHERE client_id = ?", (client_id,))
            connection.execute("DELETE FROM clients WHERE id = ?", (client_id,))
        notify_data_changed("client_deleted_with_quotes")

    def _get_next_available_id(self, connection):
        rows = connection.execute(
            "SELECT id FROM clients ORDER BY id ASC"
        ).fetchall()

        next_id = 1
        for row in rows:
            current_id = row["id"]
            if current_id != next_id:
                break
            next_id += 1

        return next_id
