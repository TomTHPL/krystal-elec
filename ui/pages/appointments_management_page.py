from datetime import datetime

import customtkinter as ctk
from tkinter import messagebox


class AppointmentsManagementPage(ctk.CTkFrame):
    def __init__(self, parent, client_repository, appointment_repository):
        super().__init__(parent, fg_color="transparent")

        self.client_repository = client_repository
        self.appointment_repository = appointment_repository
        self.client_map = {}

        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(2, weight=1)

        self._build_header()
        self._build_calendar_panel()
        self._build_form_panel()

    def _build_header(self):
        title = ctk.CTkLabel(
            self,
            text="Rendez-vous",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#111827",
        )
        title.grid(row=0, column=0, columnspan=2, padx=30, pady=(26, 6), sticky="w")

        subtitle = ctk.CTkLabel(
            self,
            text="Agenda clients trie par date",
            font=ctk.CTkFont(size=14),
            text_color="#6b7280",
        )
        subtitle.grid(row=1, column=0, columnspan=2, padx=30, pady=(0, 10), sticky="w")

    def _build_calendar_panel(self):
        calendar_card = ctk.CTkFrame(self, corner_radius=18, fg_color="#f8fafc")
        calendar_card.grid(row=2, column=0, padx=(30, 15), pady=20, sticky="nsew")
        calendar_card.grid_columnconfigure(0, weight=1)
        calendar_card.grid_rowconfigure(1, weight=1)

        strip = ctk.CTkFrame(calendar_card, fg_color="transparent")
        strip.grid(row=0, column=0, padx=18, pady=(18, 10), sticky="ew")
        for index in range(7):
            strip.grid_columnconfigure(index, weight=1)

        day_names = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]
        today = datetime.now().date()
        for index, day_name in enumerate(day_names):
            current_day = today.fromordinal(today.toordinal() + index)
            chip = ctk.CTkFrame(
                strip,
                corner_radius=14,
                fg_color="#dbeafe" if index == 0 else "#ffffff",
                border_width=1,
                border_color="#dbeafe" if index == 0 else "#e5e7eb",
            )
            chip.grid(row=0, column=index, padx=4, sticky="ew")

            label = ctk.CTkLabel(
                chip,
                text=f"{day_name}\n{current_day.day:02d}",
                justify="center",
                text_color="#1d4ed8" if index == 0 else "#374151",
                font=ctk.CTkFont(size=13, weight="bold"),
            )
            label.pack(padx=8, pady=10)

        self.appointments_scroll = ctk.CTkScrollableFrame(
            calendar_card,
            corner_radius=14,
            fg_color="#ffffff",
        )
        self.appointments_scroll.grid(row=1, column=0, padx=18, pady=(0, 18), sticky="nsew")
        self.appointments_scroll.grid_columnconfigure(0, weight=1)

    def _build_form_panel(self):
        form_card = ctk.CTkFrame(self, corner_radius=18, fg_color="#f9fafb")
        form_card.grid(row=2, column=1, padx=(15, 30), pady=20, sticky="nsew")
        form_card.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            form_card,
            text="Nouveau rendez-vous",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#111827",
        )
        title.grid(row=0, column=0, padx=20, pady=(18, 14), sticky="w")

        self.client_option = self._create_option_field(form_card, 1, "Client", ["Aucun client"])
        self.date_entry = self._create_entry_field(form_card, 3, "Date", "YYYY-MM-DD")
        self.time_entry = self._create_entry_field(form_card, 5, "Heure", "HH:MM")
        self.address_entry = self._create_entry_field(form_card, 7, "Adresse", "Adresse du rendez-vous")

        note_label = ctk.CTkLabel(form_card, text="Note", text_color="#374151")
        note_label.grid(row=9, column=0, padx=20, pady=(12, 6), sticky="w")

        self.note_text = ctk.CTkTextbox(form_card, height=140)
        self.note_text.grid(row=10, column=0, padx=20, pady=(0, 14), sticky="ew")

        save_button = ctk.CTkButton(
            form_card,
            text="Creer le rendez-vous",
            fg_color="#0f766e",
            hover_color="#115e59",
            command=self.create_appointment,
        )
        save_button.grid(row=11, column=0, padx=20, pady=(0, 10), sticky="ew")

        clear_button = ctk.CTkButton(
            form_card,
            text="Vider",
            fg_color="#6b7280",
            hover_color="#4b5563",
            command=self.reset_form,
        )
        clear_button.grid(row=12, column=0, padx=20, pady=(0, 20), sticky="ew")

        hint = ctk.CTkLabel(
            form_card,
            text="Formats attendus : 2026-04-07 et 14:30",
            text_color="#6b7280",
            font=ctk.CTkFont(size=12),
        )
        hint.grid(row=13, column=0, padx=20, pady=(0, 18), sticky="w")

        self.refresh_client_choices()
        self.refresh_appointments()

    def _create_entry_field(self, parent, row, label_text, placeholder):
        label = ctk.CTkLabel(parent, text=label_text, text_color="#374151")
        label.grid(row=row, column=0, padx=20, pady=(8, 6), sticky="w")

        entry = ctk.CTkEntry(parent, placeholder_text=placeholder, height=38)
        entry.grid(row=row + 1, column=0, padx=20, pady=(0, 4), sticky="ew")
        return entry

    def _create_option_field(self, parent, row, label_text, values):
        label = ctk.CTkLabel(parent, text=label_text, text_color="#374151")
        label.grid(row=row, column=0, padx=20, pady=(8, 6), sticky="w")

        option = ctk.CTkOptionMenu(parent, values=values)
        option.grid(row=row + 1, column=0, padx=20, pady=(0, 4), sticky="ew")
        return option

    def refresh_client_choices(self):
        clients = self.client_repository.get_all_clients()
        if not clients:
            self.client_map = {}
            self.client_option.configure(values=["Aucun client"])
            self.client_option.set("Aucun client")
            return

        self.client_map = {
            f'{client["nom"]} (ID {client["id"]})': client["id"]
            for client in clients
        }
        choices = list(self.client_map.keys())
        self.client_option.configure(values=choices)

        current_value = self.client_option.get()
        if current_value not in self.client_map:
            self.client_option.set(choices[0])

    def refresh_appointments(self):
        for widget in self.appointments_scroll.winfo_children():
            widget.destroy()

        appointments = self.appointment_repository.get_all_appointments()
        if not appointments:
            empty = ctk.CTkLabel(
                self.appointments_scroll,
                text="Aucun rendez-vous pour le moment.",
                text_color="#6b7280",
                font=ctk.CTkFont(size=15),
            )
            empty.grid(row=0, column=0, padx=18, pady=20, sticky="w")
            return

        current_date = None
        row_index = 0
        for appointment in appointments:
            if appointment["date_rdv"] != current_date:
                current_date = appointment["date_rdv"]
                date_card = ctk.CTkFrame(
                    self.appointments_scroll,
                    corner_radius=14,
                    fg_color="#eef6ff",
                )
                date_card.grid(row=row_index, column=0, padx=14, pady=(14, 8), sticky="ew")
                date_card.grid_columnconfigure(0, weight=1)

                date_label = ctk.CTkLabel(
                    date_card,
                    text=self._format_display_date(current_date),
                    font=ctk.CTkFont(size=17, weight="bold"),
                    text_color="#1d4ed8",
                )
                date_label.grid(row=0, column=0, padx=16, pady=12, sticky="w")
                row_index += 1

            item_card = ctk.CTkFrame(
                self.appointments_scroll,
                corner_radius=14,
                fg_color="#ffffff",
                border_width=1,
                border_color="#e5e7eb",
            )
            item_card.grid(row=row_index, column=0, padx=14, pady=(0, 10), sticky="ew")
            item_card.grid_columnconfigure(1, weight=1)

            time_badge = ctk.CTkFrame(item_card, corner_radius=12, fg_color="#0f766e")
            time_badge.grid(row=0, column=0, padx=(14, 12), pady=14, sticky="ns")

            time_label = ctk.CTkLabel(
                time_badge,
                text=appointment["heure_rdv"],
                text_color="#ffffff",
                font=ctk.CTkFont(size=14, weight="bold"),
            )
            time_label.pack(padx=12, pady=10)

            content = ctk.CTkFrame(item_card, fg_color="transparent")
            content.grid(row=0, column=1, padx=(0, 14), pady=12, sticky="ew")
            content.grid_columnconfigure(0, weight=1)

            title = ctk.CTkLabel(
                content,
                text=appointment["client_nom"],
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color="#111827",
            )
            title.grid(row=0, column=0, sticky="w")

            address = ctk.CTkLabel(
                content,
                text=appointment["adresse"],
                text_color="#374151",
                justify="left",
                wraplength=360,
            )
            address.grid(row=1, column=0, pady=(4, 4), sticky="w")

            note_value = appointment["note"] or "Aucune note"
            note = ctk.CTkLabel(
                content,
                text=note_value,
                text_color="#6b7280",
                justify="left",
                wraplength=360,
            )
            note.grid(row=2, column=0, sticky="w")

            row_index += 1

    def create_appointment(self):
        if not self.client_map:
            messagebox.showwarning("Client requis", "Ajoutez d'abord un client dans le module Clients.")
            return

        client_name = self.client_option.get()
        client_id = self.client_map.get(client_name)
        date_rdv = self.date_entry.get().strip()
        heure_rdv = self.time_entry.get().strip()
        adresse = self.address_entry.get().strip()
        note = self.note_text.get("1.0", "end").strip()

        if client_id is None:
            messagebox.showwarning("Client requis", "Selectionnez un client valide.")
            return
        if not adresse:
            messagebox.showwarning("Champ requis", "L'adresse du rendez-vous est obligatoire.")
            return

        if not self._is_valid_date(date_rdv):
            messagebox.showwarning("Date invalide", "Utilisez le format YYYY-MM-DD.")
            return

        if not self._is_valid_time(heure_rdv):
            messagebox.showwarning("Heure invalide", "Utilisez le format HH:MM.")
            return

        self.appointment_repository.create_appointment(
            client_id=client_id,
            date_rdv=date_rdv,
            heure_rdv=heure_rdv,
            adresse=adresse,
            note=note,
        )
        self.refresh_appointments()
        self.reset_form()
        messagebox.showinfo("Rendez-vous cree", "Le rendez-vous a bien ete enregistre.")

    def reset_form(self):
        self.date_entry.delete(0, "end")
        self.time_entry.delete(0, "end")
        self.address_entry.delete(0, "end")
        self.note_text.delete("1.0", "end")
        self.refresh_client_choices()

    def _is_valid_date(self, value):
        try:
            datetime.strptime(value, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def _is_valid_time(self, value):
        try:
            datetime.strptime(value, "%H:%M")
            return True
        except ValueError:
            return False

    def _format_display_date(self, value):
        date_value = datetime.strptime(value, "%Y-%m-%d")
        day_names = [
            "Lundi",
            "Mardi",
            "Mercredi",
            "Jeudi",
            "Vendredi",
            "Samedi",
            "Dimanche",
        ]
        month_names = [
            "janvier",
            "fevrier",
            "mars",
            "avril",
            "mai",
            "juin",
            "juillet",
            "aout",
            "septembre",
            "octobre",
            "novembre",
            "decembre",
        ]
        return (
            f"{day_names[date_value.weekday()]} "
            f"{date_value.day:02d} "
            f"{month_names[date_value.month - 1]} "
            f"{date_value.year}"
        )
