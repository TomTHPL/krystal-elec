import tkinter as tk
from datetime import datetime, timedelta

import customtkinter as ctk


class HomePage(ctk.CTkFrame):
    def __init__(self, parent, client_repository, quote_repository, appointment_repository, on_navigate=None):
        super().__init__(parent, fg_color="transparent")
        self.client_repository = client_repository
        self.quote_repository = quote_repository
        self.appointment_repository = appointment_repository
        self.on_navigate = on_navigate
        self._fin_months_data = []

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        self._build_header()
        self._build_kpis()
        self._build_finance()
        self._build_content()
        self.refresh_dashboard()

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------

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
        self.kpis_frame.grid(row=1, column=0, padx=30, pady=(0, 10), sticky="ew")
        for column in range(5):
            self.kpis_frame.grid_columnconfigure(column, weight=1)

        self.kpi_cards = {}
        kpi_configs = [
            ("clients",   "Clients",             "◈", "#0d9488"),
            ("drafts",    "Devis brouillon",      "≡", "#d97706"),
            ("sent",      "En attente réponse",   "↑", "#7c3aed"),
            ("follow_up", "A relancer",           "⚡", "#dc2626"),
            ("today",     "RDV aujourd'hui",      "⊙", "#2563eb"),
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

            ctk.CTkLabel(card, text=icon, font=ctk.CTkFont(size=16), text_color=accent).grid(
                row=0, column=0, padx=14, pady=(12, 0), sticky="w"
            )

            value_label = ctk.CTkLabel(
                card, text="0", font=ctk.CTkFont(size=30, weight="bold"), text_color="#1e293b"
            )
            value_label.grid(row=1, column=0, padx=14, pady=(2, 0), sticky="w")

            ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=11), text_color="#64748b").grid(
                row=2, column=0, padx=14, pady=(2, 12), sticky="w"
            )

            self.kpi_cards[key] = value_label

    def _build_finance(self):
        finance_card = ctk.CTkFrame(
            self,
            corner_radius=12,
            fg_color="#f8fafc",
            border_width=1,
            border_color="#dbe4ef",
        )
        finance_card.grid(row=2, column=0, padx=30, pady=(0, 10), sticky="ew")
        finance_card.grid_columnconfigure(0, weight=1)
        finance_card.grid_columnconfigure(1, weight=1)
        finance_card.grid_columnconfigure(2, weight=1)
        finance_card.grid_columnconfigure(3, weight=2)

        ctk.CTkLabel(
            finance_card,
            text="≋  Tableau de bord financier",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#0f172a",
        ).grid(row=0, column=0, columnspan=4, padx=16, pady=(12, 6), sticky="w")

        ctk.CTkFrame(finance_card, height=1, fg_color="#e2eaf3").grid(
            row=1, column=0, columnspan=4, padx=16, sticky="ew"
        )

        # Bloc — CA ce mois
        b0 = ctk.CTkFrame(finance_card, fg_color="transparent")
        b0.grid(row=2, column=0, padx=(16, 8), pady=14, sticky="w")

        ctk.CTkLabel(b0, text="CA accepté — ce mois", font=ctk.CTkFont(size=10), text_color="#94a3b8").pack(anchor="w")
        self._fin_curr_val = ctk.CTkLabel(b0, text="—", font=ctk.CTkFont(size=20, weight="bold"), text_color="#0f172a")
        self._fin_curr_val.pack(anchor="w")
        self._fin_curr_month = ctk.CTkLabel(b0, text="", font=ctk.CTkFont(size=10), text_color="#64748b")
        self._fin_curr_month.pack(anchor="w")

        # Séparateur vertical simulé par un Frame fin
        ctk.CTkFrame(finance_card, width=1, fg_color="#e2eaf3").grid(row=2, column=0, padx=(0, 0), pady=6, sticky="nse")

        # Bloc — vs mois précédent
        b1 = ctk.CTkFrame(finance_card, fg_color="transparent")
        b1.grid(row=2, column=1, padx=8, pady=14, sticky="w")

        ctk.CTkLabel(b1, text="vs mois précédent", font=ctk.CTkFont(size=10), text_color="#94a3b8").pack(anchor="w")
        self._fin_delta_val = ctk.CTkLabel(b1, text="—", font=ctk.CTkFont(size=20, weight="bold"), text_color="#64748b")
        self._fin_delta_val.pack(anchor="w")
        self._fin_delta_sub = ctk.CTkLabel(b1, text="", font=ctk.CTkFont(size=10), text_color="#64748b")
        self._fin_delta_sub.pack(anchor="w")

        # Bloc — CA prévisionnel
        b2 = ctk.CTkFrame(finance_card, fg_color="transparent")
        b2.grid(row=2, column=2, padx=8, pady=14, sticky="w")

        ctk.CTkLabel(b2, text="CA prévisionnel", font=ctk.CTkFont(size=10), text_color="#94a3b8").pack(anchor="w")
        self._fin_forecast_val = ctk.CTkLabel(b2, text="—", font=ctk.CTkFont(size=20, weight="bold"), text_color="#7c3aed")
        self._fin_forecast_val.pack(anchor="w")
        self._fin_forecast_sub = ctk.CTkLabel(b2, text="", font=ctk.CTkFont(size=10), text_color="#64748b")
        self._fin_forecast_sub.pack(anchor="w")

        # Bloc — bar chart 6 mois
        b3 = ctk.CTkFrame(finance_card, fg_color="transparent")
        b3.grid(row=2, column=3, padx=(8, 16), pady=14, sticky="ew")
        b3.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(b3, text="6 derniers mois (CA accepté)", font=ctk.CTkFont(size=10), text_color="#94a3b8").grid(
            row=0, column=0, sticky="w"
        )

        self._fin_canvas = tk.Canvas(b3, height=80, bg="#f8fafc", highlightthickness=0)
        self._fin_canvas.grid(row=1, column=0, sticky="ew")
        self._fin_canvas.bind("<Configure>", lambda _e: self._redraw_chart())

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
        card = ctk.CTkFrame(parent, corner_radius=12, fg_color="#f8fafc", border_width=1, border_color="#dbe4ef")
        card.grid(row=row, column=0, sticky="nsew")
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(
            card, text=title, font=ctk.CTkFont(size=14, weight="bold"), text_color="#0f172a"
        ).grid(row=0, column=0, padx=16, pady=(14, 10), sticky="w")

        ctk.CTkFrame(card, height=1, fg_color="#e2eaf3").grid(row=1, column=0, padx=16, sticky="ew")

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

    # ------------------------------------------------------------------
    # Rafraîchissement
    # ------------------------------------------------------------------

    def refresh_dashboard(self):
        clients = self.client_repository.get_all_clients()
        quotes = self.quote_repository.get_all_quotes()
        appointments = self.appointment_repository.get_all_appointments()

        today = datetime.now().date()
        draft_quotes = [q for q in quotes if (q.get("statut") or "").strip().lower() == "brouillon"]
        sent_quotes = [q for q in quotes if (q.get("statut") or "").strip().lower() == "envoye"]
        follow_up_quotes = [
            q for q in quotes
            if (q.get("statut") or "").strip().lower() in ("brouillon", "envoye")
            and self._is_quote_older_than_days(q, 4)
        ]
        appointments_today = [a for a in appointments if a.get("date_rdv") == today.isoformat()]
        upcoming_appointments = [
            a for a in appointments if a.get("date_rdv") and a.get("date_rdv") >= today.isoformat()
        ][:3]

        self.kpi_cards["clients"].configure(text=str(len(clients)))
        self.kpi_cards["drafts"].configure(text=str(len(draft_quotes)))
        self.kpi_cards["sent"].configure(text=str(len(sent_quotes)))
        self.kpi_cards["follow_up"].configure(text=str(len(follow_up_quotes)))
        self.kpi_cards["today"].configure(text=str(len(appointments_today)))

        self._render_finance(quotes)
        self._render_today_list(upcoming_appointments)
        self._render_follow_up_list(follow_up_quotes[:5])
        self._render_activity(quotes[:3], appointments[-3:])

    # ------------------------------------------------------------------
    # Tableau de bord financier
    # ------------------------------------------------------------------

    def _render_finance(self, quotes):
        today = datetime.now()

        # CA mensuel des devis acceptés
        monthly_ca: dict[str, float] = {}
        for q in quotes:
            if (q.get("statut") or "").strip().lower() != "accepte":
                continue
            ym = (q.get("created_at") or "")[:7]
            if len(ym) == 7:
                monthly_ca[ym] = monthly_ca.get(ym, 0) + float(q.get("total") or 0)

        curr_ym = today.strftime("%Y-%m")
        prev_dt = (today.replace(day=1) - timedelta(days=1))
        prev_ym = prev_dt.strftime("%Y-%m")

        curr_total = monthly_ca.get(curr_ym, 0.0)
        prev_total = monthly_ca.get(prev_ym, 0.0)

        # Bloc ce mois
        self._fin_curr_val.configure(text=self._format_currency(curr_total))
        self._fin_curr_month.configure(text=today.strftime("%B %Y").capitalize())

        # Bloc delta
        if curr_total == 0 and prev_total == 0:
            self._fin_delta_val.configure(text="—", text_color="#94a3b8")
            self._fin_delta_sub.configure(text="Aucune donnée", text_color="#94a3b8")
        elif prev_total == 0:
            self._fin_delta_val.configure(text=f"↑ {self._format_currency(curr_total)}", text_color="#16a34a")
            self._fin_delta_sub.configure(text="Premier mois enregistré", text_color="#16a34a")
        else:
            delta = curr_total - prev_total
            delta_pct = (delta / prev_total) * 100
            arrow = "↑" if delta >= 0 else "↓"
            color = "#16a34a" if delta >= 0 else "#dc2626"
            self._fin_delta_val.configure(
                text=f"{arrow} {self._format_currency(abs(delta))}",
                text_color=color,
            )
            self._fin_delta_sub.configure(
                text=f"{arrow} {abs(delta_pct):.1f}% vs {prev_dt.strftime('%B').capitalize()}",
                text_color=color,
            )

        # Bloc prévisionnel
        forecast_quotes = [q for q in quotes if (q.get("statut") or "").strip().lower() == "envoye"]
        forecast_total = sum(float(q.get("total") or 0) for q in forecast_quotes)
        n = len(forecast_quotes)
        self._fin_forecast_val.configure(text=self._format_currency(forecast_total))
        self._fin_forecast_sub.configure(
            text=f"{n} devis envoyé{'s' if n > 1 else ''}" if n > 0 else "Aucun devis envoyé"
        )

        # Données bar chart
        months = self._get_last_n_months(6)
        self._fin_months_data = [(m, monthly_ca.get(m, 0.0)) for m in months]
        self._redraw_chart()

    def _get_last_n_months(self, n: int) -> list[str]:
        today = datetime.now()
        year, month = today.year, today.month
        months = []
        for _ in range(n):
            months.insert(0, f"{year}-{month:02d}")
            month -= 1
            if month == 0:
                month = 12
                year -= 1
        return months

    def _redraw_chart(self):
        canvas = self._fin_canvas
        canvas.delete("all")

        if not self._fin_months_data:
            return

        canvas.update_idletasks()
        w = canvas.winfo_width()
        h = canvas.winfo_height()
        if w <= 1 or h <= 1:
            return

        values = [v for _, v in self._fin_months_data]
        max_val = max(values) if any(v > 0 for v in values) else 1.0

        n = len(self._fin_months_data)
        pad_x = 4
        label_h = 18
        val_label_h = 14
        bar_top_pad = val_label_h + 2
        bar_area_h = h - label_h - bar_top_pad
        total_w = w - pad_x * 2
        gap = 5
        bar_w = max(4, (total_w - gap * (n - 1)) // n)
        current_month = datetime.now().strftime("%Y-%m")

        for i, (month, value) in enumerate(self._fin_months_data):
            x0 = pad_x + i * (bar_w + gap)
            x1 = x0 + bar_w
            cx = (x0 + x1) // 2

            is_current = (month == current_month)
            bar_fill = "#2563eb" if is_current else "#bfdbfe"
            text_color = "#1e3a8a" if is_current else "#64748b"

            bar_h = int((value / max_val) * bar_area_h) if value > 0 else 2
            y0 = bar_top_pad + (bar_area_h - bar_h)
            y1 = bar_top_pad + bar_area_h

            canvas.create_rectangle(x0, y0, x1, y1, fill=bar_fill, outline="")

            # Étiquette de valeur au-dessus de la barre
            if value > 0:
                canvas.create_text(
                    cx, y0 - 4,
                    text=self._format_k(value),
                    font=("Segoe UI", 7),
                    fill="#334155",
                    anchor="s",
                )

            # Libellé du mois en bas
            try:
                month_label = datetime.strptime(month, "%Y-%m").strftime("%b")
            except Exception:
                month_label = month[-2:]
            canvas.create_text(
                cx, h - label_h // 2,
                text=month_label,
                font=("Segoe UI", 8),
                fill=text_color,
            )

    def _format_k(self, value: float) -> str:
        if value >= 10_000:
            return f"{value / 1000:.0f}k"
        if value >= 1_000:
            return f"{value / 1000:.1f}k"
        return str(int(value))

    # ------------------------------------------------------------------
    # Sections de contenu
    # ------------------------------------------------------------------

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

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _navigate(self, page_name):
        if callable(self.on_navigate):
            self.on_navigate(page_name)

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
            return f"{float(value):,.2f} EUR".replace(",", " ")
        except Exception:
            return "0,00 EUR"
