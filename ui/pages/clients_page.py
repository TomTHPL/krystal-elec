import tkinter as tk
from tkinter import messagebox, ttk

import customtkinter as ctk


class ClientsPage(ctk.CTkFrame):
    def __init__(self, parent, client_repository):
        super().__init__(parent, fg_color="transparent")

        self.client_repository = client_repository
        self.selected_client_id = None
        self.is_edit_mode = False
        self.layout_mode = None
        self.responsive_breakpoint = 1360
        self.form_is_editable = True

        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=0)

        self._build_header()
        self._build_clients_table()
        self._build_form()
        self._set_form_editable(True)
        self._sync_action_buttons()
        self.bind("<Configure>", self._on_resize)
        self.after(50, self._apply_responsive_layout)

    def _build_header(self):
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, columnspan=2, padx=30, pady=(28, 8), sticky="ew")
        header_frame.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            header_frame,
            text="Clients",
            font=ctk.CTkFont(size=30, weight="bold"),
            text_color="#0f172a",
        )
        title.grid(row=0, column=0, sticky="w")

        subtitle = ctk.CTkLabel(
            header_frame,
            text="Base clients professionnelle avec fiches detaillees, notes et edition rapide",
            font=ctk.CTkFont(size=13),
            text_color="#64748b",
        )
        subtitle.grid(row=1, column=0, pady=(4, 0), sticky="w")

    def _build_clients_table(self):
        self.table_card = ctk.CTkFrame(
            self,
            corner_radius=20,
            fg_color="#f8fafc",
            border_width=1,
            border_color="#dbe2ea",
        )
        self.table_card.grid(row=1, column=0, padx=(30, 15), pady=20, sticky="nsew")
        self.table_card.grid_columnconfigure(0, weight=1)
        self.table_card.grid_rowconfigure(1, weight=1)

        table_header = ctk.CTkFrame(self.table_card, fg_color="transparent")
        table_header.grid(row=0, column=0, columnspan=2, padx=18, pady=(16, 0), sticky="ew")
        table_header.grid_columnconfigure(0, weight=1)

        table_title = ctk.CTkLabel(
            table_header,
            text="Liste des clients",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#0f172a",
        )
        table_title.grid(row=0, column=0, sticky="w")

        table_hint = ctk.CTkLabel(
            table_header,
            text="Selectionnez une fiche pour la consulter, la modifier ou completer ses notes",
            font=ctk.CTkFont(size=12),
            text_color="#64748b",
        )
        table_hint.grid(row=1, column=0, pady=(3, 0), sticky="w")

        self._configure_treeview_style()

        columns = ("id", "nom", "telephone", "email")
        self.tree = ttk.Treeview(
            self.table_card,
            columns=columns,
            show="headings",
            height=16,
            style="Clients.Treeview",
        )
        self.tree.heading("id", text="ID")
        self.tree.heading("nom", text="Nom")
        self.tree.heading("telephone", text="Telephone")
        self.tree.heading("email", text="Email")

        self.tree.column("id", width=60, anchor="center")
        self.tree.column("nom", width=220)
        self.tree.column("telephone", width=150)
        self.tree.column("email", width=240)

        self.tree.grid(row=1, column=0, padx=16, pady=16, sticky="nsew")
        self.tree.bind("<<TreeviewSelect>>", self._on_client_select)

        vertical_scrollbar = ttk.Scrollbar(self.table_card, orient="vertical", command=self.tree.yview)
        horizontal_scrollbar = ttk.Scrollbar(self.table_card, orient="horizontal", command=self.tree.xview)
        self.tree.configure(
            yscrollcommand=vertical_scrollbar.set,
            xscrollcommand=horizontal_scrollbar.set,
        )
        vertical_scrollbar.grid(row=1, column=1, pady=16, sticky="ns")
        horizontal_scrollbar.grid(row=2, column=0, padx=16, pady=(0, 16), sticky="ew")

    def _build_form(self):
        self.form_card = ctk.CTkFrame(
            self,
            corner_radius=20,
            fg_color="#f8fafc",
            border_width=1,
            border_color="#dbe2ea",
        )
        self.form_card.grid(row=1, column=1, padx=(15, 30), pady=20, sticky="nsew")
        self.form_card.grid_columnconfigure(0, weight=1)
        self.form_card.grid_rowconfigure(1, weight=1)

        form_header = ctk.CTkFrame(self.form_card, fg_color="transparent")
        form_header.grid(row=0, column=0, padx=18, pady=(16, 0), sticky="ew")
        form_header.grid_columnconfigure(0, weight=1)

        form_title = ctk.CTkLabel(
            form_header,
            text="Fiche client",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#0f172a",
        )
        form_title.grid(row=0, column=0, sticky="w")

        form_hint = ctk.CTkLabel(
            form_header,
            text="Le panneau reste accessible en entier grace au defilement vertical",
            font=ctk.CTkFont(size=12),
            text_color="#64748b",
        )
        form_hint.grid(row=1, column=0, pady=(3, 0), sticky="w")

        form_scroll = ctk.CTkScrollableFrame(
            self.form_card,
            fg_color="transparent",
            corner_radius=0,
            scrollbar_button_color="#cbd5e1",
            scrollbar_button_hover_color="#94a3b8",
        )
        form_scroll.grid(row=1, column=0, padx=6, pady=(10, 8), sticky="nsew")
        form_scroll.grid_columnconfigure(0, weight=1)
        self.form_scroll = form_scroll

        identity_card = ctk.CTkFrame(
            form_scroll,
            fg_color="#ffffff",
            corner_radius=14,
            border_width=1,
            border_color="#e2e8f0",
        )
        identity_card.grid(row=0, column=0, padx=20, pady=(6, 12), sticky="ew")
        identity_card.grid_columnconfigure(0, weight=1)

        identity_title = ctk.CTkLabel(
            identity_card,
            text="Coordonnees principales",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#111827",
        )
        identity_title.grid(row=0, column=0, padx=16, pady=(14, 4), sticky="w")

        identity_hint = ctk.CTkLabel(
            identity_card,
            text="Une fiche claire accelere la creation des devis, rendez-vous et suivis.",
            font=ctk.CTkFont(size=11),
            text_color="#6b7280",
        )
        identity_hint.grid(row=1, column=0, padx=16, pady=(0, 8), sticky="w")

        self.nom_entry = self._create_field(identity_card, 2, "Nom")
        self.telephone_entry = self._create_field(identity_card, 4, "Telephone")
        self.email_entry = self._create_field(identity_card, 6, "Email")
        self.adresse_entry = self._create_field(identity_card, 8, "Adresse")

        notes_card = ctk.CTkFrame(
            form_scroll,
            fg_color="#ffffff",
            corner_radius=14,
            border_width=1,
            border_color="#e2e8f0",
        )
        notes_card.grid(row=1, column=0, padx=20, pady=(0, 12), sticky="ew")
        notes_card.grid_columnconfigure(0, weight=1)

        notes_title = ctk.CTkLabel(
            notes_card,
            text="Notes et contexte",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#111827",
        )
        notes_title.grid(row=0, column=0, padx=16, pady=(14, 4), sticky="w")

        notes_hint = ctk.CTkLabel(
            notes_card,
            text="Ajoutez des precisions utiles pour les prochains contacts ou interventions.",
            font=ctk.CTkFont(size=11),
            text_color="#6b7280",
        )
        notes_hint.grid(row=1, column=0, padx=16, pady=(0, 8), sticky="w")

        notes_label = ctk.CTkLabel(notes_card, text="Notes", text_color="#374151")
        notes_label.grid(row=2, column=0, padx=16, pady=(6, 6), sticky="w")

        self.notes_text = ctk.CTkTextbox(
            notes_card,
            height=160,
            fg_color="#ffffff",
            border_width=1,
            border_color="#9ca3af",
            text_color="#111827",
        )
        self.notes_text.grid(row=3, column=0, padx=16, pady=(0, 14), sticky="ew")

        buttons_frame = ctk.CTkFrame(form_scroll, fg_color="transparent")
        buttons_frame.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="ew")
        buttons_frame.grid_columnconfigure((0, 1), weight=1)

        self.add_button = ctk.CTkButton(buttons_frame, text="Ajouter", command=self.add_client)
        self.add_button.grid(row=1, column=0, padx=(0, 6), pady=(10, 6), sticky="ew")

        self.edit_button = ctk.CTkButton(
            buttons_frame,
            text="Modifier",
            fg_color="#2563eb",
            hover_color="#1d4ed8",
            command=self.start_edit_client,
        )
        self.edit_button.grid(row=0, column=1, padx=(6, 0), pady=6, sticky="ew")

        self.save_button = ctk.CTkButton(
            buttons_frame,
            text="Valider",
            fg_color="#059669",
            hover_color="#047857",
            command=self.update_client,
        )
        self.save_button.grid(row=0, column=1, padx=(6, 0), pady=6, sticky="ew")

        self.delete_button = ctk.CTkButton(
            buttons_frame,
            text="Supprimer",
            fg_color="#dc2626",
            hover_color="#b91c1c",
            command=self.delete_client,
        )
        self.delete_button.grid(row=0, column=0, padx=(0, 6), pady=6, sticky="ew")

        self.clear_button = ctk.CTkButton(
            buttons_frame,
            text="Vider",
            fg_color="#6b7280",
            hover_color="#4b5563",
            command=self.clear_form,
        )
        self.clear_button.grid(row=1, column=1, padx=(6, 0), pady=(10, 6), sticky="ew")

    def _create_field(self, parent, row, label_text):
        label = ctk.CTkLabel(parent, text=label_text, text_color="#374151")
        label.grid(row=row, column=0, padx=16, pady=(12, 6), sticky="w")

        entry = ctk.CTkEntry(parent, height=38)
        entry.grid(row=row + 1, column=0, padx=16, pady=(0, 4), sticky="ew")
        return entry

    def _configure_treeview_style(self):
        style = ttk.Style()
        style.configure(
            "Clients.Treeview",
            rowheight=38,
            background="#ffffff",
            fieldbackground="#ffffff",
            borderwidth=0,
            relief="flat",
            font=("Segoe UI", 10),
        )
        style.configure(
            "Clients.Treeview.Heading",
            background="#e8eef6",
            foreground="#374151",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            padding=(8, 6),
        )
        style.map(
            "Clients.Treeview",
            background=[("selected", "#dbeafe")],
            foreground=[("selected", "#1e3a8a")],
        )
        style.map(
            "Clients.Treeview.Heading",
            relief=[("active", "flat")],
        )

    def _set_form_editable(self, editable):
        self.form_is_editable = editable
        entry_state = "normal" if editable else "readonly"
        text_state = "normal" if editable else "disabled"

        for entry in (self.nom_entry, self.telephone_entry, self.email_entry, self.adresse_entry):
            entry.configure(state=entry_state)

        self.notes_text.configure(state=text_state)

    def _on_resize(self, _event):
        self.after_idle(self._apply_responsive_layout)

    def _apply_responsive_layout(self):
        width = self.winfo_width()
        if width <= 1:
            return

        target_mode = "stacked" if width < self.responsive_breakpoint else "split"
        if target_mode == self.layout_mode:
            return

        if target_mode == "stacked":
            self.grid_columnconfigure(0, weight=1)
            self.grid_columnconfigure(1, weight=1)
            self.grid_rowconfigure(1, weight=1)
            self.grid_rowconfigure(2, weight=1)
            self.table_card.grid_configure(row=1, column=0, columnspan=2, padx=30, pady=(20, 10), sticky="nsew")
            self.form_card.grid_configure(row=2, column=0, columnspan=2, padx=30, pady=(10, 20), sticky="nsew")
        else:
            self.grid_columnconfigure(0, weight=3)
            self.grid_columnconfigure(1, weight=2)
            self.grid_rowconfigure(1, weight=1)
            self.grid_rowconfigure(2, weight=0)
            self.table_card.grid_configure(row=1, column=0, columnspan=1, padx=(30, 15), pady=20, sticky="nsew")
            self.form_card.grid_configure(row=1, column=1, columnspan=1, padx=(15, 30), pady=20, sticky="nsew")

        self.layout_mode = target_mode

    def _sync_action_buttons(self):
        has_selection = self.selected_client_id is not None

        if has_selection and not self.is_edit_mode:
            self.edit_button.grid()
            self.delete_button.grid()
            self.save_button.grid_remove()
        elif has_selection and self.is_edit_mode:
            self.edit_button.grid_remove()
            self.delete_button.grid()
            self.save_button.grid()
        else:
            self.edit_button.grid_remove()
            self.delete_button.grid_remove()
            self.save_button.grid_remove()

    def refresh_clients(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        clients = self.client_repository.get_all_clients()
        for index, client in enumerate(clients):
            row_tag = "evenrow" if index % 2 == 0 else "oddrow"
            self.tree.insert(
                "",
                tk.END,
                values=(
                    client["id"],
                    client["nom"],
                    client["telephone"],
                    client["email"],
                ),
                tags=(row_tag,),
            )
        self.tree.tag_configure("evenrow", background="#ffffff")
        self.tree.tag_configure("oddrow", background="#f3f4f6")

    def add_client(self):
        data = self._get_form_data()
        if not data["nom"]:
            messagebox.showwarning("Champ requis", "Le nom du client est obligatoire.")
            return

        self.client_repository.add_client(**data)
        self.refresh_clients()
        self.clear_form()

    def start_edit_client(self):
        if self.selected_client_id is None:
            messagebox.showwarning("Selection requise", "Selectionnez un client a modifier.")
            return

        self.is_edit_mode = True
        self._set_form_editable(True)
        self._sync_action_buttons()

    def update_client(self):
        if self.selected_client_id is None:
            messagebox.showwarning("Selection requise", "Selectionnez un client a modifier.")
            return

        if not self.is_edit_mode:
            messagebox.showwarning("Mode edition", "Cliquez d'abord sur Modifier.")
            return

        data = self._get_form_data()
        if not data["nom"]:
            messagebox.showwarning("Champ requis", "Le nom du client est obligatoire.")
            return

        self.client_repository.update_client(self.selected_client_id, **data)
        self.refresh_clients()
        self.clear_form()

    def delete_client(self):
        if self.selected_client_id is None:
            messagebox.showwarning("Selection requise", "Selectionnez un client a supprimer.")
            return

        confirmed = messagebox.askyesno(
            "Confirmation",
            "Voulez-vous vraiment supprimer ce client ?",
        )
        if not confirmed:
            return

        self.client_repository.delete_client(self.selected_client_id)
        self.refresh_clients()
        self.clear_form()

    def clear_form(self):
        self.selected_client_id = None
        self.is_edit_mode = False

        self._set_form_editable(True)
        self._set_entry_value(self.nom_entry, "")
        self._set_entry_value(self.telephone_entry, "")
        self._set_entry_value(self.email_entry, "")
        self._set_entry_value(self.adresse_entry, "")
        self._set_textbox_value(self.notes_text, "")

        self.tree.selection_remove(self.tree.selection())
        self._sync_action_buttons()

    def _on_client_select(self, _event):
        selected_item = self.tree.selection()
        if not selected_item:
            return

        values = self.tree.item(selected_item[0], "values")
        self.selected_client_id = int(values[0])
        self.is_edit_mode = False

        client = self.client_repository.get_client_by_id(self.selected_client_id)
        if client is None:
            return

        self._fill_form(client)

    def _fill_form(self, client):
        self._set_form_editable(True)

        self._set_entry_value(self.nom_entry, client["nom"] or "")
        self._set_entry_value(self.telephone_entry, client["telephone"] or "")
        self._set_entry_value(self.email_entry, client["email"] or "")
        self._set_entry_value(self.adresse_entry, client["adresse"] or "")
        self._set_textbox_value(self.notes_text, client["notes"] or "")

        self._set_form_editable(False)
        self._sync_action_buttons()

    def _get_form_data(self):
        return {
            "nom": self.nom_entry.get().strip(),
            "telephone": self.telephone_entry.get().strip(),
            "email": self.email_entry.get().strip(),
            "adresse": self.adresse_entry.get().strip(),
            "notes": self.notes_text.get("1.0", tk.END).strip(),
        }

    def _set_entry_value(self, entry, value):
        restore_readonly = not self.form_is_editable
        if restore_readonly:
            entry.configure(state="normal")
        entry.delete(0, tk.END)
        entry.insert(0, value)
        if restore_readonly:
            entry.configure(state="readonly")

    def _set_textbox_value(self, textbox, value):
        restore_disabled = not self.form_is_editable
        if restore_disabled:
            textbox.configure(state="normal")
        textbox.delete("1.0", tk.END)
        textbox.insert("1.0", value)
        if restore_disabled:
            textbox.configure(state="disabled")
