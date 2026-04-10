from datetime import datetime, timedelta

import customtkinter as ctk


class HomePage(ctk.CTkFrame):
    def __init__(self, parent, client_repository, quote_repository, appointment_repository, on_navigate=None):
        super().__init__(parent, fg_color="transparent")
        self.client_repository = client_repository
        self.quote_repository = quote_repository
        self.appointment_repository = appointment_repository
        self.on_navigate = on_navigate

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        self._build_header()
        self._build_kpis()
        self._build_content()
        self.refresh_dashboard()

    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, padx=30, pady=(26, 8), sticky="ew")
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header,
            text="Accueil",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#0f172a",
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            header,
            text="Tableau de bord — vue d'ensemble de votre activite",
            font=ctk.CTkFont(size=12),
            text_color="#64748b",
        ).grid(row=1, column=0, pady=(3, 0), sticky="w")

    def _build_kpis(self):
        self.kpis_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.kpis_frame.grid(row=1, column=0, padx=30, pady=(0, 12), sticky="ew")
        for column in range(4):
            self.kpis_frame.grid_columnconfigure(column, weight=1)

        self.kpi_cards = {}
        kpi_configs = [
            ("clients",   "Clients",          "◈", "#0d9488"),
            ("drafts",    "Devis brouillon",   "≡", "#d97706"),
            ("follow_up", "A relancer",        "⚡", "#dc2626"),
            ("today",     "RDV aujourd'hui",   "⊙", "#2563eb"),
        ]
        for index, (key, title, icon, accent) in enumerate(kpi_configs):
            card = ctk.CTkFrame(
                self.kpis_frame,
                corner_radius=12,
                fg_color="#f8fafc",
                border_width=2,
                border_color=accent,
            )
            card.grid(row=0, column=index, padx=(0 if index == 0 else 8, 0), sticky="ew")

            ctk.CTkLabel(
                card,
                text=icon,
                font=ctk.CTkFont(size=16),
                text_color=accent,
            ).grid(row=0, column=0, padx=14, pady=(12, 0), sticky="w")

            value_label = ctk.CTkLabel(
                card,
                text="0",
                font=ctk.CTkFont(size=30, weight="bold"),
                text_color="#1e293b",
            )
            value_label.grid(row=1, column=0, padx=14, pady=(2, 0), sticky="w")

            ctk.CTkLabel(
                card,
                text=title,
                font=ctk.CTkFont(size=11),
                text_color="#64748b",
            ).grid(row=2, column=0, padx=14, pady=(2, 12), sticky="w")

            self.kpi_cards[key] = value_label

    def _build_content(self):
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.grid(row=3, column=0, padx=30, pady=(0, 20), sticky="nsew")
        content.grid_columnconfigure(0, weight=3)
        content.grid_columnconfigure(1, weight=2)
        content.grid_rowconfigure(0, weight=1)

        left_col = ctk.CTkFrame(content, fg_color="transparent")
        left_col.grid(row=0, column=0, padx=(0, 8), sticky="nsew")
        left_col.grid_columnconfigure(0, weight=1)
        left_col.grid_rowconfigure(1, weight=1)

        right_col = ctk.CTkFrame(content, fg_color="transparent")
        right_col.grid(row=0, column=1, padx=(8, 0), sticky="nsew")
        right_col.grid_columnconfigure(0, weight=1)
        right_col.grid_rowconfigure(1, weight=1)

        self.today_card, self.today_body = self._create_section(left_col, 0, "Aujourd'hui")
        self.follow_card, self.follow_body = self._create_section(left_col, 1, "Devis a traiter")
        self.follow_card.grid_configure(pady=(8, 0))

        self.actions_card, self.actions_body = self._create_section(right_col, 0, "Actions rapides")
        self.activity_card, self.activity_body = self._create_section(right_col, 1, "Activite recente")
        self.activity_card.grid_configure(pady=(8, 0))

        self._build_actions()

    def _create_section(self, parent, row, title):
        card = ctk.CTkFrame(
            parent,
            corner_radius=12,
            fg_color="#f8fafc",
            border_width=1,
            border_color="#dbe4ef",
        )
        card.grid(row=row, column=0, sticky="nsew")
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#0f172a",
        ).grid(row=0, column=0, padx=16, pady=(14, 10), sticky="w")

        ctk.CTkFrame(card, height=1, fg_color="#e2eaf3").grid(
            row=1, column=0, padx=16, sticky="ew"
        )

        body = ctk.CTkFrame(card, fg_color="transparent")
        body.grid(row=2, column=0, padx=16, pady=(10, 14), sticky="nsew")
        body.grid_columnconfigure(0, weight=1)
        return card, body

    def _build_actions(self):
        buttons = [
            ("+ Nouveau client",       "Clients",      "#0f766e", "#115e59"),
            ("+ Nouveau devis",        "Devis",        "#2563eb", "#1d4ed8"),
            ("+ Nouveau rendez-vous",  "Rendez-vous",  "#4f46e5", "#4338ca"),
        ]
        for row, (label, target_page, fg_color, hover_color) in enumerate(buttons):
            ctk.CTkButton(
                self.actions_body,
                text=label,
                height=40,
                corner_radius=10,
                font=ctk.CTkFont(size=13, weight="bold"),
                fg_color=fg_color,
                hover_color=hover_color,
                command=lambda page=target_page: self._navigate(page),
            ).grid(row=row, column=0, pady=(0, 8 if row < len(buttons) - 1 else 0), sticky="ew")

    def _navigate(self, page_name):
        if callable(self.on_navigate):
            self.on_navigate(page_name)

    def refresh_dashboard(self):
        clients = self.client_repository.get_all_clients()
        quotes = self.quote_repository.get_all_quotes()
        appointments = self.appointment_repository.get_all_appointments()

        today = datetime.now().date()
        draft_quotes = [quote for quote in quotes if (quote.get("statut") or "").strip().lower() == "brouillon"]
        follow_up_quotes = [
            quote for quote in quotes
            if (quote.get("statut") or "").strip().lower() in ("brouillon", "envoye")
            and self._is_quote_older_than_days(quote, 4)
        ]
        appointments_today = [item for item in appointments if item.get("date_rdv") == today.isoformat()]
        upcoming_appointments = [
            item for item in appointments if item.get("date_rdv") and item.get("date_rdv") >= today.isoformat()
        ][:3]

        self.kpi_cards["clients"].configure(text=str(len(clients)))
        self.kpi_cards["drafts"].configure(text=str(len(draft_quotes)))
        self.kpi_cards["follow_up"].configure(text=str(len(follow_up_quotes)))
        self.kpi_cards["today"].configure(text=str(len(appointments_today)))

        self._render_today_list(upcoming_appointments)
        self._render_follow_up_list(follow_up_quotes[:5])
        self._render_activity(quotes[:3], appointments[-3:])

    def _render_today_list(self, appointments):
        self._clear_body(self.today_body)
        if not appointments:
            self._empty_state(self.today_body, "Aucun rendez-vous a venir.")
            return

        for row, item in enumerate(appointments):
            when = f"{self._format_short_date(item['date_rdv'])}  {item['heure_rdv']}"
            row_frame = ctk.CTkFrame(self.today_body, fg_color="#eef6ff", corner_radius=8)
            row_frame.grid(row=row, column=0, pady=(0, 6), sticky="ew")
            row_frame.grid_columnconfigure(1, weight=1)
            ctk.CTkLabel(row_frame, text="⊙", font=ctk.CTkFont(size=12), text_color="#2563eb", width=24).grid(
                row=0, column=0, padx=(10, 6), pady=8, sticky="w"
            )
            ctk.CTkLabel(
                row_frame,
                text=f"{when}  —  {item['client_nom']}",
                text_color="#1e3a8a",
                font=ctk.CTkFont(size=12),
                anchor="w",
                justify="left",
            ).grid(row=0, column=1, padx=(0, 10), pady=8, sticky="w")

    def _render_follow_up_list(self, quotes):
        self._clear_body(self.follow_body)
        if not quotes:
            self._empty_state(self.follow_body, "Aucun devis en attente de relance.")
            return

        for row, quote in enumerate(quotes):
            row_frame = ctk.CTkFrame(self.follow_body, fg_color="#fff7ed", corner_radius=8)
            row_frame.grid(row=row, column=0, pady=(0, 6), sticky="ew")
            row_frame.grid_columnconfigure(1, weight=1)
            ctk.CTkLabel(row_frame, text="≡", font=ctk.CTkFont(size=12), text_color="#d97706", width=24).grid(
                row=0, column=0, padx=(10, 6), pady=8, sticky="w"
            )
            ctk.CTkLabel(
                row_frame,
                text=f"{quote['numero']}  —  {quote['client_nom']}  ({self._format_currency(quote['total'])})",
                text_color="#92400e",
                font=ctk.CTkFont(size=12),
                anchor="w",
                justify="left",
            ).grid(row=0, column=1, padx=(0, 10), pady=8, sticky="w")

    def _render_activity(self, recent_quotes, recent_appointments):
        self._clear_body(self.activity_body)
        row = 0

        if recent_quotes:
            ctk.CTkLabel(
                self.activity_body,
                text="Derniers devis",
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color="#94a3b8",
            ).grid(row=row, column=0, pady=(0, 4), sticky="w")
            row += 1
            for quote in recent_quotes:
                ctk.CTkLabel(
                    self.activity_body,
                    text=f"  ≡  {quote['numero']}  —  {quote['client_nom']}",
                    text_color="#334155",
                    font=ctk.CTkFont(size=12),
                ).grid(row=row, column=0, pady=(0, 4), sticky="w")
                row += 1

        if recent_appointments:
            if row > 0:
                ctk.CTkFrame(self.activity_body, height=1, fg_color="#e2eaf3").grid(
                    row=row, column=0, pady=(4, 8), sticky="ew"
                )
                row += 1
            ctk.CTkLabel(
                self.activity_body,
                text="Derniers rendez-vous",
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color="#94a3b8",
            ).grid(row=row, column=0, pady=(0, 4), sticky="w")
            row += 1
            for appointment in reversed(recent_appointments):
                ctk.CTkLabel(
                    self.activity_body,
                    text=f"  ⊙  {self._format_short_date(appointment['date_rdv'])}  —  {appointment['client_nom']}",
                    text_color="#334155",
                    font=ctk.CTkFont(size=12),
                ).grid(row=row, column=0, pady=(0, 4), sticky="w")
                row += 1

        if row == 0:
            self._empty_state(self.activity_body, "Aucune activite recente.")

    def _clear_body(self, body):
        for widget in body.winfo_children():
            widget.destroy()

    def _empty_state(self, body, text):
        ctk.CTkLabel(
            body,
            text=f"  {text}",
            text_color="#94a3b8",
            font=ctk.CTkFont(size=12),
            anchor="w",
            justify="left",
        ).grid(row=0, column=0, sticky="w")

    def _is_quote_older_than_days(self, quote, days):
        created_at = quote.get("created_at")
        if not created_at:
            return False
        try:
            created = datetime.fromisoformat(created_at.replace(" ", "T"))
        except Exception:
            return False
        return created.date() <= (datetime.now().date() - timedelta(days=days))

    def _format_short_date(self, value):
        try:
            return datetime.strptime(value, "%Y-%m-%d").strftime("%d/%m/%Y")
        except Exception:
            return value or ""

    def _format_currency(self, value):
        try:
            return f"{float(value):.2f} EUR"
        except Exception:
            return "0.00 EUR"
