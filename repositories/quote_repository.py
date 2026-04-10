from datetime import datetime

from database import get_connection, notify_data_changed


class QuoteRepository:
    """Gere les operations CRUD des devis."""

    QUOTE_SELECT_FIELDS = """
        q.id,
        q.numero,
        q.client_id,
        c.nom AS client_nom,
        q.statut,
        q.total,
        q.created_at,
        q.delai,
        q.materiel_charge,
        q.acompte_percent,
        q.validite,
        q.conditions_exceptionnelles
    """

    LEGACY_QUOTE_SELECT_FIELDS = """
        q.id,
        q.numero,
        q.client_id,
        c.nom AS client_nom,
        q.statut,
        q.total,
        q.created_at,
        '2 jours' AS delai,
        'client' AS materiel_charge,
        30 AS acompte_percent,
        '30 jours' AS validite,
        '' AS conditions_exceptionnelles
    """

    def get_all_quotes(self):
        with get_connection() as connection:
            rows = self._execute_quote_select(
                connection,
                """
                FROM quotes q
                JOIN clients c ON c.id = q.client_id
                ORDER BY q.id DESC
                """,
            ).fetchall()

        return [dict(row) for row in rows]

    def get_quote_by_id(self, quote_id):
        with get_connection() as connection:
            quote_row = self._execute_quote_select(
                connection,
                """
                FROM quotes q
                JOIN clients c ON c.id = q.client_id
                WHERE q.id = ?
                """,
                (quote_id,),
            ).fetchone()

            if quote_row is None:
                return None

            line_rows = connection.execute(
                """
                SELECT id, description, quantite, prix_unitaire, total_ligne
                FROM quote_lines
                WHERE quote_id = ?
                ORDER BY id ASC
                """,
                (quote_id,),
            ).fetchall()

        quote = dict(quote_row)
        quote["lignes"] = [dict(row) for row in line_rows]
        return quote

    def get_next_quote_number(self):
        with get_connection() as connection:
            current_year = datetime.now().year
            next_sequence = self._get_next_year_sequence(connection, current_year)

        return self._format_quote_number(current_year, next_sequence)

    def create_quote(self, client_id, statut, lignes, conditions):
        total = sum(line["total_ligne"] for line in lignes)

        with get_connection() as connection:
            quote_id = self._get_next_available_id(connection)
            current_year = datetime.now().year
            next_sequence = self._get_next_year_sequence(connection, current_year)
            numero = self._format_quote_number(current_year, next_sequence)
            created_at = datetime.now().astimezone().isoformat(sep=" ", timespec="seconds")
            connection.execute(
                """
                INSERT INTO quotes (
                    id,
                    numero,
                    client_id,
                    statut,
                    total,
                    created_at,
                    delai,
                    materiel_charge,
                    acompte_percent,
                    validite,
                    conditions_exceptionnelles
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    quote_id,
                    numero,
                    client_id,
                    statut,
                    total,
                    created_at,
                    conditions["delai"],
                    conditions["materiel_charge"],
                    conditions["acompte_percent"],
                    conditions["validite"],
                    conditions["conditions_exceptionnelles"],
                ),
            )

            for line in lignes:
                connection.execute(
                    """
                    INSERT INTO quote_lines (
                        quote_id,
                        description,
                        quantite,
                        prix_unitaire,
                        total_ligne
                    )
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        quote_id,
                        line["description"],
                        line["quantite"],
                        line["prix_unitaire"],
                        line["total_ligne"],
                    ),
                )

        notify_data_changed("quote_created")
        return quote_id

    def update_quote(self, quote_id, client_id, statut, lignes, conditions):
        total = sum(line["total_ligne"] for line in lignes)

        with get_connection() as connection:
            connection.execute(
                """
                UPDATE quotes
                SET
                    client_id = ?,
                    statut = ?,
                    total = ?,
                    delai = ?,
                    materiel_charge = ?,
                    acompte_percent = ?,
                    validite = ?,
                    conditions_exceptionnelles = ?
                WHERE id = ?
                """,
                (
                    client_id,
                    statut,
                    total,
                    conditions["delai"],
                    conditions["materiel_charge"],
                    conditions["acompte_percent"],
                    conditions["validite"],
                    conditions["conditions_exceptionnelles"],
                    quote_id,
                ),
            )
            connection.execute(
                "DELETE FROM quote_lines WHERE quote_id = ?",
                (quote_id,),
            )

            for line in lignes:
                connection.execute(
                    """
                    INSERT INTO quote_lines (
                        quote_id,
                        description,
                        quantite,
                        prix_unitaire,
                        total_ligne
                    )
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        quote_id,
                        line["description"],
                        line["quantite"],
                        line["prix_unitaire"],
                        line["total_ligne"],
                    ),
                )

        notify_data_changed("quote_updated")

    def delete_quote(self, quote_id):
        with get_connection() as connection:
            connection.execute("DELETE FROM quote_lines WHERE quote_id = ?", (quote_id,))
            connection.execute("DELETE FROM quotes WHERE id = ?", (quote_id,))
        notify_data_changed("quote_deleted")

    def _get_next_available_id(self, connection):
        rows = connection.execute(
            "SELECT id FROM quotes ORDER BY id ASC"
        ).fetchall()

        next_id = 1
        for row in rows:
            current_id = row["id"]
            if current_id != next_id:
                break
            next_id += 1

        return next_id

    def _get_next_year_sequence(self, connection, year):
        prefix = f"{year}-"
        rows = connection.execute(
            """
            SELECT numero
            FROM quotes
            WHERE numero LIKE ?
            ORDER BY id ASC
            """,
            (f"{prefix}%",),
        ).fetchall()

        max_sequence = 0
        for row in rows:
            numero = row["numero"]
            if not numero.startswith(prefix):
                continue

            sequence_text = numero[len(prefix):]
            if not sequence_text.isdigit():
                continue

            max_sequence = max(max_sequence, int(sequence_text))

        return max_sequence + 1

    def _format_quote_number(self, year, sequence):
        return f"{year}-{sequence:03d}"

    def _execute_quote_select(self, connection, suffix_sql, params=()):
        try:
            return connection.execute(
                f"SELECT {self.QUOTE_SELECT_FIELDS} {suffix_sql}",
                params,
            )
        except Exception as error:
            if "no such column" not in str(error).lower():
                raise

            return connection.execute(
                f"SELECT {self.LEGACY_QUOTE_SELECT_FIELDS} {suffix_sql}",
                params,
            )
