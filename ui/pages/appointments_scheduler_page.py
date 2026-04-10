import calendar
from datetime import datetime
import tkinter as tk

import customtkinter as ctk
from tkinter import messagebox, ttk


class AppointmentsSchedulerPage(ctk.CTkFrame):
    def __init__(self, parent, client_repository, appointment_repository):
        super().__init__(parent, fg_color="transparent")

        self.client_repository = client_repository
        self.appointment_repository = appointment_repository
        self.client_map = {}
        self.client_choices_all = []
        self.selected_client_name = None
        self.client_suggestions = []
        self.client_popup = None
        self.client_listbox = None
        self.selected_appointment_id = None
        self.appointments_cache = []

        now = datetime.now()
        self.current_year = now.year
        self.current_month = now.month
        self.selected_day = now.day
        self.selected_hour = now.strftime("%H")
        self.selected_minute = "00"

        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(1, weight=1)

        self._build_header()
        self._build_calendar_panel()
        self._build_form_panel()

    # ─────────────────────────────────────────────────────────────────────────
    # Layout
    # ─────────────────────────────────────────────────────────────────────────

    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, columnspan=2, padx=30, pady=(26, 10), sticky="ew")
        header.grid_columnconfigure(0, weight=1)

        # Title + subtitle
        title_block = ctk.CTkFrame(header, fg_color="transparent")
        title_block.grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            title_block,
            text="Rendez-vous",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#0f172a",
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            title_block,
            text="Planifiez et gerez vos rendez-vous clients",
            font=ctk.CTkFont(size=12),
            text_color="#64748b",
        ).grid(row=1, column=0, pady=(3, 0), sticky="w")

        # KPI badges
        kpi_block = ctk.CTkFrame(header, fg_color="transparent")
        kpi_block.grid(row=0, column=1, sticky="e")

        upcoming_badge = ctk.CTkFrame(
            kpi_block,
            corner_radius=12,
            fg_color="#eff6ff",
            border_width=1,
            border_color="#bfdbfe",
        )
        upcoming_badge.grid(row=0, column=0, padx=(0, 10))

        self.kpi_label = ctk.CTkLabel(
            upcoming_badge,
            text="0",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#1d4ed8",
        )
        self.kpi_label.grid(row=0, column=0, padx=16, pady=(10, 2))
        ctk.CTkLabel(
            upcoming_badge,
            text="a venir",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color="#60a5fa",
        ).grid(row=1, column=0, padx=16, pady=(0, 10))

        day_badge = ctk.CTkFrame(
            kpi_block,
            corner_radius=12,
            fg_color="#f0fdf4",
            border_width=1,
            border_color="#bbf7d0",
        )
        day_badge.grid(row=0, column=1)

        self.day_kpi_label = ctk.CTkLabel(
            day_badge,
            text="0",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#15803d",
        )
        self.day_kpi_label.grid(row=0, column=0, padx=16, pady=(10, 2))
        ctk.CTkLabel(
            day_badge,
            text="ce jour",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color="#4ade80",
        ).grid(row=1, column=0, padx=16, pady=(0, 10))

    def _build_calendar_panel(self):
        self.calendar_card = ctk.CTkFrame(
            self,
            corner_radius=16,
            fg_color="#ffffff",
            border_width=1,
            border_color="#e2e8f0",
        )
        self.calendar_card.grid(row=1, column=0, padx=(30, 12), pady=(0, 24), sticky="nsew")
        self.calendar_card.grid_columnconfigure(0, weight=1)
        self.calendar_card.grid_rowconfigure(2, weight=1)

        # Navigation bar
        nav = ctk.CTkFrame(self.calendar_card, fg_color="transparent")
        nav.grid(row=0, column=0, padx=18, pady=(18, 8), sticky="ew")
        nav.grid_columnconfigure(2, weight=1)
        nav.grid_columnconfigure(3, weight=1)

        _btn_cfg = dict(height=32, corner_radius=8, fg_color="#f1f5f9", text_color="#374151", hover_color="#e2e8f0")

        ctk.CTkButton(nav, text="«", width=32, font=ctk.CTkFont(size=13, weight="bold"),
                      command=self._previous_year, **_btn_cfg).grid(row=0, column=0, padx=(0, 4))
        ctk.CTkButton(nav, text="‹", width=32, font=ctk.CTkFont(size=16, weight="bold"),
                      command=self._previous_month, **_btn_cfg).grid(row=0, column=1, padx=(0, 8))

        nav_style = ttk.Style()
        nav_style.configure(
            "Nav.TCombobox",
            fieldbackground="#ffffff",
            background="#f1f5f9",
            foreground="#1e293b",
            selectbackground="#dbeafe",
            selectforeground="#1e3a8a",
            padding=(8, 4),
        )
        nav_style.map(
            "Nav.TCombobox",
            fieldbackground=[("readonly", "#ffffff")],
            foreground=[("readonly", "#1e293b")],
            selectbackground=[("readonly", "#dbeafe")],
            selectforeground=[("readonly", "#1e3a8a")],
        )

        self.month_option = ttk.Combobox(
            nav,
            values=self._month_names(),
            state="readonly",
            height=5,
            style="Nav.TCombobox",
            font=("Segoe UI", 11, "bold"),
            exportselection=False,
        )
        self.month_option.grid(row=0, column=2, padx=(0, 6), ipady=4, sticky="ew")
        self.month_option.bind("<<ComboboxSelected>>", lambda _e: (
            self._change_month(self.month_option.get()),
            self.month_option.selection_clear(),
        ))

        self.year_option = ttk.Combobox(
            nav,
            values=[str(y) for y in range(2026, datetime.now().year + 10)],
            state="readonly",
            height=5,
            style="Nav.TCombobox",
            font=("Segoe UI", 11, "bold"),
            exportselection=False,
        )
        self.year_option.grid(row=0, column=3, padx=(0, 8), ipady=4, sticky="ew")
        self.year_option.bind("<<ComboboxSelected>>", lambda _e: (
            self._change_year(self.year_option.get()),
            self.year_option.selection_clear(),
        ))

        ctk.CTkButton(nav, text="›", width=32, font=ctk.CTkFont(size=16, weight="bold"),
                      command=self._next_month, **_btn_cfg).grid(row=0, column=4, padx=(0, 4))
        ctk.CTkButton(nav, text="»", width=32, font=ctk.CTkFont(size=13, weight="bold"),
                      command=self._next_year, **_btn_cfg).grid(row=0, column=5, padx=(0, 10))

        ctk.CTkButton(
            nav, text="Aujourd'hui", width=94, height=32, corner_radius=8,
            font=ctk.CTkFont(size=12, weight="bold"), fg_color="#0f766e", hover_color="#115e59",
            command=self._go_to_today,
        ).grid(row=0, column=6)

        # Calendar grid (day cells rendered by _render_calendar)
        self.calendar_grid = ctk.CTkFrame(self.calendar_card, fg_color="transparent")
        self.calendar_grid.grid(row=1, column=0, padx=18, pady=(0, 10), sticky="ew")
        for i in range(7):
            self.calendar_grid.grid_columnconfigure(i, weight=1)

        # Planning list
        planning_shell = ctk.CTkFrame(self.calendar_card, fg_color="transparent")
        planning_shell.grid(row=2, column=0, padx=18, pady=(0, 18), sticky="nsew")
        planning_shell.grid_columnconfigure(0, weight=1)
        planning_shell.grid_rowconfigure(1, weight=1)

        planning_header = ctk.CTkFrame(planning_shell, fg_color="transparent")
        planning_header.grid(row=0, column=0, pady=(0, 8), sticky="ew")
        planning_header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            planning_header,
            text="Planning",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#0f172a",
        ).grid(row=0, column=0, sticky="w")

        self.appointments_scroll = ctk.CTkScrollableFrame(
            planning_shell,
            corner_radius=12,
            fg_color="#f8fafc",
            border_width=1,
            border_color="#e2e8f0",
            scrollbar_button_color="#cbd5e1",
            scrollbar_button_hover_color="#94a3b8",
        )
        self.appointments_scroll.grid(row=1, column=0, sticky="nsew")
        self.appointments_scroll.grid_columnconfigure(0, weight=1)

        self.month_option.set(self._month_names()[self.current_month - 1])
        self.year_option.set(str(self.current_year))
        self._render_calendar()

    def _build_form_panel(self):
        self.form_card = ctk.CTkFrame(
            self,
            corner_radius=16,
            fg_color="#ffffff",
            border_width=1,
            border_color="#e2e8f0",
        )
        self.form_card.grid(row=1, column=1, padx=(12, 30), pady=(0, 24), sticky="nsew")
        self.form_card.grid_columnconfigure(0, weight=1)
        self.form_card.grid_rowconfigure(1, weight=1)

        self._configure_combobox_style()

        # Fixed header (not scrollable)
        form_header = ctk.CTkFrame(self.form_card, fg_color="transparent")
        form_header.grid(row=0, column=0, sticky="ew")
        form_header.grid_columnconfigure(0, weight=1)

        self.form_title = ctk.CTkLabel(
            form_header,
            text="Nouveau rendez-vous",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#0f172a",
        )
        self.form_title.grid(row=0, column=0, padx=22, pady=(20, 16), sticky="w")

        ctk.CTkFrame(form_header, height=1, fg_color="#e2e8f0").grid(row=1, column=0, sticky="ew")

        # Scrollable fields
        scroll = ctk.CTkScrollableFrame(
            self.form_card,
            fg_color="transparent",
            corner_radius=0,
            scrollbar_button_color="#cbd5e1",
            scrollbar_button_hover_color="#94a3b8",
        )
        scroll.grid(row=1, column=0, sticky="nsew")
        scroll.grid_columnconfigure(0, weight=1)
        scroll.grid_columnconfigure(1, weight=1)
        scroll.bind("<MouseWheel>", self._on_form_scroll, add="+")
        scroll.bind("<Button-4>",   self._on_form_scroll, add="+")
        scroll.bind("<Button-5>",   self._on_form_scroll, add="+")

        # ── Client ──────────────────────────────────────────────────────────
        self._field_label(scroll, 0, "Client")
        self.client_option = ttk.Combobox(
            scroll, values=["Aucun client"], state="normal", height=5,
            style="Appointments.TCombobox",
        )
        self.client_option.grid(row=1, column=0, columnspan=2, padx=20, pady=(0, 4), sticky="ew")
        self.client_option.bind("<KeyRelease>",      self._on_client_search)
        self.client_option.bind("<<ComboboxSelected>>", self._on_client_selected)
        self.client_option.bind("<Return>",          self._on_client_selected)
        self.client_option.bind("<FocusOut>",
            lambda _e: self.after(120, self._hide_client_popup), add="+")

        # ── Date ────────────────────────────────────────────────────────────
        self._field_label(scroll, 2, "Date selectionnee")
        self.date_value_label = ctk.CTkLabel(
            scroll,
            text="",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#2563eb",
        )
        self.date_value_label.grid(row=3, column=0, columnspan=2, padx=20, pady=(0, 4), sticky="w")

        # ── Heure ───────────────────────────────────────────────────────────
        self._field_label(scroll, 4, "Heure")

        time_row = ctk.CTkFrame(scroll, fg_color="transparent")
        time_row.grid(row=5, column=0, columnspan=2, padx=20, pady=(0, 4), sticky="ew")
        time_row.grid_columnconfigure(0, weight=1)
        time_row.grid_columnconfigure(2, weight=1)

        self.hour_entry = ctk.CTkEntry(
            time_row, placeholder_text="HH", height=42,
            font=ctk.CTkFont(size=18, weight="bold"), justify="center",
        )
        self.hour_entry.grid(row=0, column=0, sticky="ew")
        self.hour_entry.bind("<KeyRelease>", self._on_hour_input)

        ctk.CTkLabel(
            time_row, text=":", font=ctk.CTkFont(size=22, weight="bold"), text_color="#cbd5e1",
        ).grid(row=0, column=1, padx=10)

        self.minute_entry = ctk.CTkEntry(
            time_row, placeholder_text="MM", height=42,
            font=ctk.CTkFont(size=18, weight="bold"), justify="center",
        )
        self.minute_entry.grid(row=0, column=2, sticky="ew")
        self.minute_entry.bind("<KeyRelease>", self._on_minute_input)

        # ── Adresse ─────────────────────────────────────────────────────────
        self._field_label(scroll, 6, "Adresse")
        self.address_entry = ctk.CTkEntry(
            scroll, placeholder_text="Adresse du rendez-vous", height=38,
        )
        self.address_entry.grid(row=7, column=0, columnspan=2, padx=20, pady=(0, 4), sticky="ew")

        # ── Note ────────────────────────────────────────────────────────────
        self._field_label(scroll, 8, "Note")
        self.note_text = ctk.CTkTextbox(
            scroll, height=96,
            fg_color="#f8fafc", border_width=1, border_color="#e2e8f0",
            text_color="#111827",
        )
        self.note_text.grid(row=9, column=0, columnspan=2, padx=20, pady=(0, 10), sticky="ew")

        # ── Séparateur ──────────────────────────────────────────────────────
        ctk.CTkFrame(scroll, height=1, fg_color="#e2e8f0").grid(
            row=10, column=0, columnspan=2, padx=20, pady=(6, 14), sticky="ew"
        )

        # ── Boutons ─────────────────────────────────────────────────────────
        btn = ctk.CTkFrame(scroll, fg_color="transparent")
        btn.grid(row=11, column=0, columnspan=2, padx=20, pady=(0, 24), sticky="ew")
        btn.grid_columnconfigure((0, 1), weight=1)

        self.create_button = ctk.CTkButton(
            btn, text="Creer le rendez-vous",
            height=44, corner_radius=10, font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#0f766e", hover_color="#115e59",
            command=self.create_appointment,
        )
        self.create_button.grid(row=0, column=0, columnspan=2, pady=(0, 8), sticky="ew")

        self.update_button = ctk.CTkButton(
            btn, text="Enregistrer",
            height=38, corner_radius=10, font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#2563eb", hover_color="#1d4ed8",
            command=self.update_appointment,
        )
        self.update_button.grid(row=1, column=0, padx=(0, 5), sticky="ew")

        self.reset_button = ctk.CTkButton(
            btn, text="Nouveau",
            height=38, corner_radius=10, font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#64748b", hover_color="#475569",
            command=self.reset_form,
        )
        self.reset_button.grid(row=1, column=1, padx=(5, 0), sticky="ew")

        self.delete_button = ctk.CTkButton(
            btn, text="Supprimer",
            height=34, corner_radius=10, font=ctk.CTkFont(size=12),
            fg_color="#fef2f2", hover_color="#fee2e2", text_color="#dc2626",
            command=self.delete_appointment,
        )
        self.delete_button.grid(row=2, column=0, columnspan=2, pady=(8, 0), sticky="ew")

        self.refresh_client_choices()
        self._set_time_inputs(self.selected_hour, self.selected_minute)
        self._update_selected_date_label()
        self.refresh_appointments()
        self._sync_form_mode()

    def _field_label(self, parent, row, text):
        ctk.CTkLabel(
            parent,
            text=text,
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#94a3b8",
        ).grid(row=row, column=0, columnspan=2, padx=20, pady=(16, 4), sticky="w")

    # ─────────────────────────────────────────────────────────────────────────
    # Calendar rendering
    # ─────────────────────────────────────────────────────────────────────────

    def _render_calendar(self):
        for widget in self.calendar_grid.winfo_children():
            widget.destroy()

        today = datetime.now()
        today_day = (
            today.day
            if today.year == self.current_year and today.month == self.current_month
            else -1
        )

        month_prefix = f"{self.current_year:04d}-{self.current_month:02d}-"
        days_with_appt = {
            int(a["date_rdv"][8:10])
            for a in self.appointments_cache
            if a["date_rdv"].startswith(month_prefix)
        }

        day_names = ["Lu", "Ma", "Me", "Je", "Ve", "Sa", "Di"]
        for col, name in enumerate(day_names):
            ctk.CTkLabel(
                self.calendar_grid,
                text=name,
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color="#94a3b8",
                width=38,
            ).grid(row=0, column=col, padx=2, pady=(8, 6))

        for row_i, week in enumerate(
            calendar.monthcalendar(self.current_year, self.current_month), start=1
        ):
            for col_i, day in enumerate(week):
                if day == 0:
                    ctk.CTkLabel(self.calendar_grid, text="", width=38, height=38).grid(
                        row=row_i, column=col_i, padx=2, pady=2
                    )
                    continue

                is_selected = day == self.selected_day
                is_today    = day == today_day
                has_appt    = day in days_with_appt

                if is_selected:
                    fg, hover, txt, border = "#2563eb", "#1d4ed8", "#ffffff", "#2563eb"
                    weight = "bold"
                elif is_today:
                    fg, hover, txt, border = "#eff6ff", "#dbeafe", "#1d4ed8", "#93c5fd"
                    weight = "bold"
                elif has_appt:
                    fg, hover, txt, border = "#f0fdf4", "#dcfce7", "#15803d", "#86efac"
                    weight = "normal"
                else:
                    fg, hover, txt, border = "#f8fafc", "#f1f5f9", "#374151", "#e2e8f0"
                    weight = "normal"

                ctk.CTkButton(
                    self.calendar_grid,
                    text=str(day),
                    width=38, height=38,
                    corner_radius=8,
                    fg_color=fg, hover_color=hover,
                    text_color=txt,
                    border_width=1, border_color=border,
                    font=ctk.CTkFont(size=12, weight=weight),
                    command=lambda d=day: self._select_day(d),
                ).grid(row=row_i, column=col_i, padx=2, pady=2)

    # ─────────────────────────────────────────────────────────────────────────
    # Appointment list rendering
    # ─────────────────────────────────────────────────────────────────────────

    def refresh_appointments(self):
        self.appointments_cache = self.appointment_repository.get_all_appointments()
        for widget in self.appointments_scroll.winfo_children():
            widget.destroy()

        self._update_kpis()

        if not self.appointments_cache:
            ctk.CTkLabel(
                self.appointments_scroll,
                text="Aucun rendez-vous pour le moment.",
                text_color="#94a3b8",
                font=ctk.CTkFont(size=13),
            ).grid(row=0, column=0, padx=16, pady=20, sticky="w")
            return

        today_str    = datetime.now().strftime("%Y-%m-%d")
        selected_str = self._selected_date_string()
        current_date = None
        row_i        = 0

        for appt in self.appointments_cache:
            # ── Date header ────────────────────────────────────────────────
            if appt["date_rdv"] != current_date:
                current_date      = appt["date_rdv"]
                is_selected_date  = current_date == selected_str
                is_today_date     = current_date == today_str

                if is_selected_date:
                    date_color = "#2563eb"
                elif is_today_date:
                    date_color = "#059669"
                else:
                    date_color = "#94a3b8"

                date_row = ctk.CTkFrame(self.appointments_scroll, fg_color="transparent")
                date_row.grid(
                    row=row_i, column=0,
                    padx=12, pady=(14 if row_i > 0 else 8, 4),
                    sticky="ew",
                )
                date_row.grid_columnconfigure(1, weight=1)

                ctk.CTkFrame(date_row, width=3, corner_radius=2, fg_color=date_color).grid(
                    row=0, column=0, padx=(0, 8), sticky="ns"
                )
                ctk.CTkLabel(
                    date_row,
                    text=self._format_display_date(current_date),
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color=date_color,
                ).grid(row=0, column=1, sticky="w")

                row_i += 1

            # ── Appointment card ───────────────────────────────────────────
            is_active = appt["id"] == self.selected_appointment_id

            card = ctk.CTkFrame(
                self.appointments_scroll,
                corner_radius=10,
                fg_color="#eff6ff" if is_active else "#ffffff",
                border_width=1,
                border_color="#93c5fd" if is_active else "#f1f5f9",
            )
            card.grid(row=row_i, column=0, padx=12, pady=(0, 6), sticky="ew")
            card.grid_columnconfigure(1, weight=1)

            # Time badge
            badge = ctk.CTkFrame(
                card, corner_radius=8,
                fg_color="#1d4ed8" if is_active else "#2563eb",
            )
            badge.grid(row=0, column=0, padx=(12, 10), pady=12, sticky="ns")
            badge_lbl = ctk.CTkLabel(
                badge,
                text=appt["heure_rdv"],
                text_color="#ffffff",
                font=ctk.CTkFont(size=13, weight="bold"),
            )
            badge_lbl.pack(padx=10, pady=9)

            # Text content
            content = ctk.CTkFrame(card, fg_color="transparent")
            content.grid(row=0, column=1, padx=(0, 12), pady=10, sticky="ew")
            content.grid_columnconfigure(0, weight=1)

            name_lbl = ctk.CTkLabel(
                content,
                text=appt["client_nom"],
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color="#0f172a",
                anchor="w",
            )
            name_lbl.grid(row=0, column=0, sticky="w")

            addr_lbl = ctk.CTkLabel(
                content,
                text=appt["adresse"] or "",
                text_color="#64748b",
                font=ctk.CTkFont(size=11),
                wraplength=320, justify="left", anchor="w",
            )
            addr_lbl.grid(row=1, column=0, pady=(2, 0), sticky="w")

            note_text = (appt.get("note") or "").strip()
            if note_text:
                note_lbl = ctk.CTkLabel(
                    content,
                    text=note_text,
                    text_color="#94a3b8",
                    font=ctk.CTkFont(size=11),
                    wraplength=320, justify="left", anchor="w",
                )
                note_lbl.grid(row=2, column=0, pady=(2, 0), sticky="w")
            else:
                note_lbl = None

            # Bind click on every sub-widget
            callback = lambda _e, aid=appt["id"]: self._load_appointment(aid)
            for w in (card, badge, badge_lbl, content, name_lbl, addr_lbl):
                w.bind("<Button-1>", callback)
            if note_lbl:
                note_lbl.bind("<Button-1>", callback)

            row_i += 1

    # ─────────────────────────────────────────────────────────────────────────
    # CRUD actions
    # ─────────────────────────────────────────────────────────────────────────

    def create_appointment(self):
        payload = self._validate_form()
        if payload is None:
            return
        self.appointment_repository.create_appointment(**payload)
        self.refresh_appointments()
        self.reset_form()
        messagebox.showinfo("Rendez-vous cree", "Le rendez-vous a bien ete enregistre.")
        self._sync_form_mode()

    def update_appointment(self):
        if self.selected_appointment_id is None:
            messagebox.showwarning("Selection requise", "Cliquez d'abord sur un rendez-vous a modifier.")
            return
        payload = self._validate_form()
        if payload is None:
            return
        self.appointment_repository.update_appointment(
            appointment_id=self.selected_appointment_id, **payload)
        self.refresh_appointments()
        self.reset_form()
        messagebox.showinfo("Rendez-vous modifie", "Le rendez-vous a bien ete mis a jour.")
        self._sync_form_mode()

    def delete_appointment(self):
        if self.selected_appointment_id is None:
            messagebox.showwarning("Selection requise", "Cliquez d'abord sur un rendez-vous a supprimer.")
            return
        if not messagebox.askyesno("Confirmation", "Voulez-vous vraiment supprimer ce rendez-vous ?"):
            return
        self.appointment_repository.delete_appointment(self.selected_appointment_id)
        self.refresh_appointments()
        self.reset_form()
        messagebox.showinfo("Rendez-vous supprime", "Le rendez-vous a bien ete supprime.")
        self._sync_form_mode()

    def reset_form(self):
        now = datetime.now()
        self.selected_appointment_id = None
        self.form_title.configure(text="Nouveau rendez-vous")
        self.current_year   = now.year
        self.current_month  = now.month
        self.selected_day   = now.day
        self.selected_hour  = now.strftime("%H")
        self.selected_minute = "00"
        self._set_time_inputs(self.selected_hour, self.selected_minute)
        self.address_entry.delete(0, "end")
        self.note_text.delete("1.0", "end")
        self.refresh_client_choices()
        self.month_option.set(self._month_names()[self.current_month - 1])
        self.year_option.set(str(self.current_year))
        self._render_calendar()
        self._update_selected_date_label()
        self.refresh_appointments()
        self._hide_client_popup()
        self._sync_form_mode()

    # ─────────────────────────────────────────────────────────────────────────
    # Internal helpers
    # ─────────────────────────────────────────────────────────────────────────

    def _validate_form(self):
        if not self.client_map:
            messagebox.showwarning("Client requis", "Ajoutez d'abord un client dans le module Clients.")
            return None

        self._on_client_selected()
        client_name = self.client_option.get().strip()
        client_id   = self.client_map.get(client_name)
        adresse     = self.address_entry.get().strip()
        note        = self.note_text.get("1.0", "end").strip()

        if client_id is None:
            messagebox.showwarning("Client requis", "Selectionnez un client valide.")
            return None
        if not adresse:
            messagebox.showwarning("Champ requis", "L'adresse du rendez-vous est obligatoire.")
            return None
        if not self._validate_time_inputs():
            return None

        return {
            "client_id": client_id,
            "date_rdv":  self._selected_date_string(),
            "heure_rdv": f"{self.selected_hour}:{self.selected_minute}",
            "adresse":   adresse,
            "note":      note,
        }

    def _load_appointment(self, appointment_id):
        appt = self.appointment_repository.get_appointment_by_id(appointment_id)
        if appt is None:
            return

        self.selected_appointment_id = appt["id"]
        self.form_title.configure(text="Modifier le rendez-vous")
        self.refresh_client_choices()

        for name, cid in self.client_map.items():
            if cid == appt["client_id"]:
                self.client_option.set(name)
                self.selected_client_name = name
                break

        dt = datetime.strptime(appt["date_rdv"], "%Y-%m-%d")
        self.current_year  = dt.year
        self.current_month = dt.month
        self.selected_day  = dt.day
        self.selected_hour, self.selected_minute = appt["heure_rdv"].split(":")

        self.month_option.set(self._month_names()[self.current_month - 1])
        self.year_option.set(str(self.current_year))
        self._set_time_inputs(self.selected_hour, self.selected_minute)
        self.address_entry.delete(0, "end")
        self.address_entry.insert(0, appt["adresse"] or "")
        self.note_text.delete("1.0", "end")
        self.note_text.insert("1.0", appt["note"] or "")
        self._render_calendar()
        self._update_selected_date_label()
        self.refresh_appointments()
        self._hide_client_popup()
        self._sync_form_mode()

    def _select_day(self, day):
        self.selected_day = day
        self._render_calendar()
        self._update_selected_date_label()
        self.refresh_appointments()

    def _change_month(self, value):
        self.current_month = self._month_names().index(value) + 1
        self._ensure_valid_selected_day()
        self._render_calendar()
        self._update_selected_date_label()
        self.refresh_appointments()

    def _change_year(self, value):
        self.current_year = int(value)
        self._ensure_valid_selected_day()
        self._render_calendar()
        self._update_selected_date_label()
        self.refresh_appointments()

    def _previous_month(self):
        if self.current_month == 1:
            self.current_month = 12
            self.current_year -= 1
        else:
            self.current_month -= 1
        self._ensure_valid_selected_day()
        self.month_option.set(self._month_names()[self.current_month - 1])
        self.year_option.set(str(self.current_year))
        self._render_calendar()
        self._update_selected_date_label()
        self.refresh_appointments()

    def _previous_year(self):
        self.current_year -= 1
        self.year_option.set(str(self.current_year))
        self._ensure_valid_selected_day()
        self._render_calendar()
        self._update_selected_date_label()
        self.refresh_appointments()

    def _next_month(self):
        if self.current_month == 12:
            self.current_month = 1
            self.current_year += 1
        else:
            self.current_month += 1
        self._ensure_valid_selected_day()
        self.month_option.set(self._month_names()[self.current_month - 1])
        self.year_option.set(str(self.current_year))
        self._render_calendar()
        self._update_selected_date_label()
        self.refresh_appointments()

    def _next_year(self):
        self.current_year += 1
        self.year_option.set(str(self.current_year))
        self._ensure_valid_selected_day()
        self._render_calendar()
        self._update_selected_date_label()
        self.refresh_appointments()

    def _go_to_today(self):
        now = datetime.now()
        self.current_year  = now.year
        self.current_month = now.month
        self.selected_day  = now.day
        self.month_option.set(self._month_names()[self.current_month - 1])
        self.year_option.set(str(self.current_year))
        self._render_calendar()
        self._update_selected_date_label()
        self.refresh_appointments()

    def _ensure_valid_selected_day(self):
        self.selected_day = min(
            self.selected_day,
            calendar.monthrange(self.current_year, self.current_month)[1],
        )

    def _on_hour_input(self, _event=None):
        self._sanitize_time_entry(self.hour_entry, max_digits=2)

    def _on_minute_input(self, _event=None):
        self._sanitize_time_entry(self.minute_entry, max_digits=2)

    def _sanitize_time_entry(self, entry, max_digits):
        text     = entry.get()
        filtered = "".join(c for c in text if c.isdigit())[:max_digits]
        if filtered != text:
            pos = entry.index(tk.INSERT)
            entry.delete(0, tk.END)
            entry.insert(0, filtered)
            entry.icursor(max(0, min(pos - (len(text) - len(filtered)), len(filtered))))

    def _set_time_inputs(self, hour_text, minute_text):
        self.hour_entry.delete(0, tk.END)
        self.hour_entry.insert(0, hour_text)
        self.minute_entry.delete(0, tk.END)
        self.minute_entry.insert(0, minute_text)

    def _validate_time_inputs(self):
        h = self.hour_entry.get().strip()
        m = self.minute_entry.get().strip()
        if not h or not m:
            messagebox.showwarning("Heure invalide", "Renseignez l'heure et les minutes.")
            return False
        if not h.isdigit() or not m.isdigit():
            messagebox.showwarning("Heure invalide", "Seuls des numeros sont autorises pour l'heure.")
            return False
        if not (0 <= int(h) <= 23):
            messagebox.showwarning("Heure invalide", "L'heure doit etre comprise entre 00 et 23.")
            return False
        if not (0 <= int(m) <= 59):
            messagebox.showwarning("Heure invalide", "Les minutes doivent etre comprises entre 00 et 59.")
            return False
        self.selected_hour   = f"{int(h):02d}"
        self.selected_minute = f"{int(m):02d}"
        self._set_time_inputs(self.selected_hour, self.selected_minute)
        return True

    def _update_selected_date_label(self):
        self.date_value_label.configure(
            text=self._format_display_date(self._selected_date_string())
        )

    def _selected_date_string(self):
        return f"{self.current_year:04d}-{self.current_month:02d}-{self.selected_day:02d}"

    def _update_kpis(self):
        today        = datetime.now().strftime("%Y-%m-%d")
        upcoming     = sum(1 for a in self.appointments_cache if a["date_rdv"] >= today)
        day_count    = sum(1 for a in self.appointments_cache
                          if a["date_rdv"] == self._selected_date_string())
        self.kpi_label.configure(text=str(upcoming))
        self.day_kpi_label.configure(text=str(day_count))

    def _sync_form_mode(self):
        editing = self.selected_appointment_id is not None
        self.update_button.configure(state="normal" if editing else "disabled")
        self.delete_button.configure(state="normal" if editing else "disabled")
        self.create_button.configure(state="disabled" if editing else "normal")

    def _on_form_scroll(self, _event):
        self._close_open_dropdowns()

    def _close_open_dropdowns(self):
        w = getattr(self, "client_option", None)
        if w is None:
            return
        try:
            w.event_generate("<Escape>")
        except Exception:
            pass
        self._hide_client_popup()

    # ── Combobox / popup helpers ─────────────────────────────────────────────

    def refresh_client_choices(self):
        clients = self.client_repository.get_all_clients()
        if not clients:
            self.client_map = {}
            self.client_choices_all = ["Aucun client"]
            self.client_option.configure(values=self.client_choices_all)
            self.client_option.set("Aucun client")
            self.selected_client_name = "Aucun client"
            return

        self.client_map = {
            f'{c["nom"]} (ID {c["id"]})': c["id"] for c in clients
        }
        self.client_choices_all = list(self.client_map.keys())
        self.client_option.configure(values=self.client_choices_all)
        current = self.client_option.get()
        if current not in self.client_map:
            current = self.client_choices_all[0]
            self.client_option.set(current)
        self.selected_client_name = current

    def _configure_combobox_style(self):
        style = ttk.Style()
        style.configure(
            "Appointments.TCombobox",
            fieldbackground="#ffffff",
            background="#ffffff",
            foreground="#111827",
            padding=6,
        )

    def _on_client_search(self, event):
        self._filter_combobox_values(self.client_option, self.client_choices_all)
        if event.keysym == "Escape":
            self._hide_client_popup()
            return
        if event.keysym == "Return":
            if self.client_suggestions:
                self.client_option.set(self.client_suggestions[0])
            self._on_client_selected()
            return
        if event.keysym in {"Up", "Down", "Tab"}:
            return
        self._show_client_popup()

    def _on_client_selected(self, _event=None):
        selected = self._enforce_combobox_selection(
            self.client_option, self.client_choices_all, self.selected_client_name)
        if selected:
            self.selected_client_name = selected
        self.client_option.configure(values=self.client_choices_all)
        self._hide_client_popup()

    def _filter_combobox_values(self, combobox, all_values):
        if not all_values:
            return
        text = combobox.get()
        try:
            pos = combobox.index(tk.INSERT)
        except tk.TclError:
            pos = len(text)
        query   = self._normalize_search_text(text)
        filtered = all_values if not query else [
            v for v in all_values if query in self._normalize_search_text(v)
        ]
        if tuple(combobox.cget("values")) != tuple(filtered):
            combobox.configure(values=filtered)
        if combobox.get() != text:
            combobox.delete(0, tk.END)
            combobox.insert(0, text)
            combobox.icursor(max(0, min(pos, len(text))))

    def _normalize_search_text(self, value):
        return (value or "").strip().lower()

    def _enforce_combobox_selection(self, combobox, all_values, fallback):
        if not all_values:
            combobox.set("")
            return ""
        current = combobox.get().strip()
        if current in all_values:
            return current
        chosen = fallback if fallback in all_values else all_values[0]
        combobox.set(chosen)
        return chosen

    def _show_client_popup(self):
        self.client_suggestions = list(self.client_option.cget("values"))
        if not self.client_suggestions:
            self._hide_client_popup()
            return
        popup, listbox = self._ensure_client_popup()
        self._fill_popup_listbox(listbox, self.client_suggestions)
        self._place_popup_for_combobox(popup, self.client_option)

    def _hide_client_popup(self):
        if self.client_popup is not None and self.client_popup.winfo_exists():
            self.client_popup.withdraw()

    def _ensure_client_popup(self):
        if (
            self.client_popup is not None
            and self.client_popup.winfo_exists()
            and self.client_listbox is not None
            and self.client_listbox.winfo_exists()
        ):
            return self.client_popup, self.client_listbox

        self.client_popup = tk.Toplevel(self)
        self.client_popup.withdraw()
        self.client_popup.overrideredirect(True)
        self.client_popup.configure(background="#cbd5e1")

        self.client_listbox = tk.Listbox(
            self.client_popup,
            relief="flat", borderwidth=0,
            exportselection=False, activestyle="none",
            font=("Segoe UI", 10),
        )
        self.client_listbox.pack(fill="both", expand=True, padx=1, pady=1)
        self.client_listbox.bind("<ButtonRelease-1>", self._on_client_popup_item_click)
        self.client_listbox.bind("<Return>",          self._on_client_popup_item_click)
        return self.client_popup, self.client_listbox

    def _fill_popup_listbox(self, listbox, values):
        listbox.delete(0, tk.END)
        for v in values:
            listbox.insert(tk.END, v)
        if values:
            listbox.selection_set(0)
            listbox.activate(0)

    def _place_popup_for_combobox(self, popup, combobox):
        combobox.update_idletasks()
        w = max(combobox.winfo_width(), 220)
        rows = min(max(len(combobox.cget("values")), 1), 8)
        h = max(rows * 22 + 4, 28)
        x = combobox.winfo_rootx()
        y = combobox.winfo_rooty() + combobox.winfo_height()
        popup.geometry(f"{w}x{h}+{x}+{y}")
        popup.deiconify()
        popup.lift()

    def _on_client_popup_item_click(self, _event=None):
        if self.client_listbox is None or not self.client_listbox.winfo_exists():
            return
        sel = self.client_listbox.curselection()
        if not sel:
            return
        self.client_option.set(self.client_listbox.get(sel[0]))
        self._on_client_selected()

    # ── Date/time formatting ─────────────────────────────────────────────────

    def _month_names(self):
        return [
            "Janvier", "Fevrier", "Mars", "Avril", "Mai", "Juin",
            "Juillet", "Aout", "Septembre", "Octobre", "Novembre", "Decembre",
        ]

    def _format_display_date(self, value):
        dt = datetime.strptime(value, "%Y-%m-%d")
        day_names   = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
        month_names = [
            "janvier", "fevrier", "mars", "avril", "mai", "juin",
            "juillet", "aout", "septembre", "octobre", "novembre", "decembre",
        ]
        return f"{day_names[dt.weekday()]} {dt.day:02d} {month_names[dt.month - 1]} {dt.year}"

    # ── Unused legacy helpers (kept for safety) ──────────────────────────────

    def _create_entry_field(self, parent, row, label_text, placeholder):
        ctk.CTkLabel(parent, text=label_text, text_color="#374151").grid(
            row=row, column=0, columnspan=2, padx=20, pady=(8, 6), sticky="w"
        )
        entry = ctk.CTkEntry(parent, placeholder_text=placeholder, height=38)
        entry.grid(row=row + 1, column=0, columnspan=2, padx=20, pady=(0, 4), sticky="ew")
        return entry

    def _create_scrollable_combobox(self, parent, row, label_text, values):
        if label_text:
            ctk.CTkLabel(parent, text=label_text, text_color="#374151").grid(
                row=row, column=0, columnspan=2, padx=20, pady=(8, 6), sticky="w"
            )
        combobox = ttk.Combobox(parent, values=values, state="normal", height=5,
                                style="Appointments.TCombobox")
        combobox.grid(row=row + 1, column=0, columnspan=2, padx=20, pady=(0, 4), sticky="ew")
        combobox.bind("<KeyRelease>",       self._on_client_search)
        combobox.bind("<<ComboboxSelected>>", self._on_client_selected)
        combobox.bind("<Return>",           self._on_client_selected)
        combobox.bind("<FocusOut>",
            lambda _e: self.after(120, self._hide_client_popup), add="+")
        return combobox
