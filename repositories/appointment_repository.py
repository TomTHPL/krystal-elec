from database import get_connection, notify_data_changed


class AppointmentRepository:
    """Gere les operations CRUD des rendez-vous."""

    def get_all_appointments(self):
        with get_connection() as connection:
            rows = connection.execute(
                """
                SELECT
                    a.id,
                    a.client_id,
                    c.nom AS client_nom,
                    a.date_rdv,
                    a.heure_rdv,
                    a.adresse,
                    a.note
                FROM appointments a
                JOIN clients c ON c.id = a.client_id
                ORDER BY a.date_rdv ASC, a.heure_rdv ASC, a.id ASC
                """
            ).fetchall()

        return [dict(row) for row in rows]

    def create_appointment(self, client_id, date_rdv, heure_rdv, adresse, note):
        with get_connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO appointments (client_id, date_rdv, heure_rdv, adresse, note)
                VALUES (?, ?, ?, ?, ?)
                """,
                (client_id, date_rdv, heure_rdv, adresse, note),
            )

        notify_data_changed("appointment_created")
        return cursor.lastrowid

    def get_appointment_by_id(self, appointment_id):
        with get_connection() as connection:
            row = connection.execute(
                """
                SELECT
                    a.id,
                    a.client_id,
                    c.nom AS client_nom,
                    a.date_rdv,
                    a.heure_rdv,
                    a.adresse,
                    a.note
                FROM appointments a
                JOIN clients c ON c.id = a.client_id
                WHERE a.id = ?
                """,
                (appointment_id,),
            ).fetchone()

        return dict(row) if row else None

    def update_appointment(self, appointment_id, client_id, date_rdv, heure_rdv, adresse, note):
        with get_connection() as connection:
            connection.execute(
                """
                UPDATE appointments
                SET client_id = ?, date_rdv = ?, heure_rdv = ?, adresse = ?, note = ?
                WHERE id = ?
                """,
                (client_id, date_rdv, heure_rdv, adresse, note, appointment_id),
            )
        notify_data_changed("appointment_updated")

    def delete_appointment(self, appointment_id):
        with get_connection() as connection:
            connection.execute("DELETE FROM appointments WHERE id = ?", (appointment_id,))
        notify_data_changed("appointment_deleted")
