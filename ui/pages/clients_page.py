import csv
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import customtkinter as ctk


class ClientsPage(ctk.CTkFrame):
    def __init__(self, parent, client_repository, quote_repository=None):
        super().__init__(parent, fg_color="transparent")

        self.client_repository = client_repository
        self.quote_repository = quote_repository
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

        ctk.CTkLabel(
            header_frame,
            text="Clients",
            font=ctk.CTkFont(size=30, weight="bold"),
            text_color="#0f172a",
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            header_frame,
            text="Base clients professionnelle avec fiches detaillees, notes et edition rapide",
            font=ctk.CTkFont(size=13),
            text_color="#64748b",
        ).grid(row=1, column=0, pady=(4, 0), sticky="w")

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

        ctk.CTkLabel(
            table_header,
            text="Liste des clients",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#0f172a",
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkButton(
            table_header,
            text="↓ Exporter CSV",
            width=130,
            height=30,
            corner_radius=8,
            fg_color="#e2e8f0",
            hover_color="#cbd5e1",
            text_color="#334155",
            command=self._export_clients_csv,
        ).grid(row=0, column=1, sticky="e")

        ctk.CTkLabel(
            table_header,
            text="Selectionnez une fiche pour la consulter, la modifier ou completer ses notes",
            font=ctk.CTkFont(size=12),
            text_color="#64748b",
        ).grid(row=1, column=0, columnspan=2, pady=(3, 0), sticky="w")

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

        ctk.CTkLabel(
            form_header,
            text="Fiche client",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#0f172a",
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            form_header,
            text="Le panneau reste accessible en entier grace au defilement vertical",
            font=ctk.CTkFont(size=12),
            text_color="#64748b",
        ).grid(row=1, column=0, pady=(3, 0), sticky="w")

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

        # Coordonnées
        identity_card = ctk.CTkFrame(
            form_scroll,
            fg_color="#ffffff",
            corner_radius=14,
            border_width=1,
            border_color="#e2e8f0",
        )
        identity_card.grid(row=0, column=0, padx=20, pady=(6, 12), sticky="ew")
        identity_card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            identity_card,
            text="Coordonnees principales",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#111827",
        ).grid(row=0, column=0, padx=16, pady=(14, 4), sticky="w")

        ctk.CTkLabel(
            identity_card,
            text="Une fiche claire accelere la creation des devis, rendez-vous et suivis.",
            font=ctk.CTkFont(size=11),
            text_color="#6b7280",
        ).grid(row=1, column=0, padx=16, pady=(0, 8), sticky="w")

        self.nom_entry = self._create_field(identity_card, 2, "Nom")
        self.telephone_entry = self._create_field(identity_card, 4, "Telephone")
        self.email_entry = self._create_field(identity_card, 6, "Email")
        self.adresse_entry = self._create_field(identity_card, 8, "Adresse")

        # Notes
        notes_card = ctk.CTkFrame(
            form_scroll,
            fg_color="#ffffff",
            corner_radius=14,
            border_width=1,
            border_color="#e2e8f0",
        )
        notes_card.grid(row=1, column=0, padx=20, pady=(0, 12), sticky="ew")
        notes_card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            notes_card,
            text="Notes et contexte",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#111827",
        ).grid(row=0, column=0, padx=16, pady=(14, 4), sticky="w")

        ctk.CTkLabel(
            notes_card,
            text="Ajoutez des precisions utiles pour les prochains contacts ou interventions.",
            font=ctk.CTkFont(size=11),
            text_color="#6b7280",
        ).grid(row=1, column=0, padx=16, pady=(0, 8), sticky="w")

        ctk.CTkLabel(notes_card, text="Notes", text_color="#374151").grid(row=2, column=0, padx=16, pady=(6, 6), sticky="w")

        self.notes_text = ctk.CTkTextbox(
            notes_card,
            height=160,
            fg_color="#ffffff",
            border_width=1,
            border_color="#9ca3af",
            text_color="#111827",
        )
        self.notes_text.grid(row=3, column=0, padx=16, pady=(0, 14), sticky="ew")

        # Historique des devis
        self.history_card = ctk.CTkFrame(
            form_scroll,
            fg_color="#ffffff",
            corner_radius=14,
            border_width=1,
            border_color="#e2e8f0",
        )
        self.history_card.grid(row=2, column=0, padx=20, pady=(0, 12), sticky="ew")
        self.history_card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self.history_card,
            text="Historique des devis",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#111827",
        ).grid(row=0, column=0, padx=16, pady=(14, 4), sticky="w")

        history_tree_frame = ctk.CTkFrame(self.history_card, fg_color="transparent")
        history_tree_frame.grid(row=1, column=0, padx=16, pady=(0, 14), sticky="ew")
        history_tree_frame.grid_columnconfigure(0, weight=1)

        self.history_tree = ttk.Treeview(
            history_tree_frame,
            columns=("numero", "statut", "total", "date"),
            show="headings",
            height=5,
            style="ClientHistory.Treeview",
        )
        self.history_tree.heading("numero", text="Numéro")
        self.history_tree.heading("statut", text="Statut")
        self.history_tree.heading("total", text="Total")
        self.history_tree.heading("date", text="Date")
        self.history_tree.column("numero", width=90, anchor="center")
        self.history_tree.column("statut", width=80, anchor="center")
        self.history_tree.column("total", width=100, anchor="e")
        self.history_tree.column("date", width=90, anchor="center")
        self.history_tree.grid(row=0, column=0, sticky="ew")

        history_vsb = ttk.Scrollbar(history_tree_frame, orient="vertical", command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=history_vsb.set)
        history_vsb.grid(row=0, column=1, sticky="ns")

        self._history_empty_label = ctk.CTkLabel(
            self.history_card,
            text="Sélectionnez un client pour voir ses devis.",
            font=ctk.CTkFont(size=12),
            text_color="#94a3b8",
        )
        self._history_empty_label.grid(row=2, column=0, padx=16, pady=(0, 10), sticky="w")

        # Boutons
        buttons_frame = ctk.CTkFrame(form_scroll, fg_color="transparent")
        buttons_frame.grid(row=3, column=0, padx=20, pady=(0, 20), sticky="ew")
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
        ctk.CTkLabel(parent, text=label_text, text_color="#374151").grid(row=row, column=0, padx=16, pady=(12, 6), sticky="w")
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
        style.map("Clients.Treeview.Heading", relief=[("active", "flat")])

        style.configure(
            "ClientHistory.Treeview",
            rowheight=30,
            background="#ffffff",
            fieldbackground="#ffffff",
            borderwidth=0,
            relief="flat",
            font=("Segoe UI", 9),
        )
        style.configure(
            "ClientHistory.Treeview.Heading",
            background="#e8eef6",
            foreground="#374151",
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            padding=(6, 4),
        )
        style.map(
            "ClientHistory.Treeview",
            background=[("selected", "#dbeafe")],
            foreground=[("selected", "#1e3a8a")],
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

    # ------------------------------------------------------------------
    # Rafraîchissement
    # ------------------------------------------------------------------

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

    def _refresh_quote_history(self, client_id):
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)

        self._history_empty_label.grid_remove()

        if self.quote_repository is None:
            self._history_empty_label.configure(text="Module devis non disponible.")
            self._history_empty_label.grid()
            return

        quotes = self.quote_repository.get_quotes_for_client(client_id)

        if not quotes:
            self._history_empty_label.configure(text="Aucun devis pour ce client.")
            self._history_empty_label.grid()
            return

        for index, q in enumerate(quotes):
            row_tag = "evenrow" if index % 2 == 0 else "oddrow"
            date_str = (q.get("created_at") or "")[:10]
            self.history_tree.insert(
                "",
                tk.END,
                values=(
                    q["numero"],
                    q["statut"],
                    f"{q['total']:.2f} EUR",
                    date_str,
                ),
                tags=(row_tag,),
            )
        self.history_tree.tag_configure("evenrow", background="#ffffff")
        self.history_tree.tag_configure("oddrow", background="#f3f4f6")

    def _clear_quote_history(self):
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        self._history_empty_label.configure(text="Sélectionnez un client pour voir ses devis.")
        self._history_empty_label.grid()

    # ------------------------------------------------------------------
    # Export CSV clients
    # ------------------------------------------------------------------

    def _export_clients_csv(self):
        clients = self.client_repository.get_all_clients()
        if not clients:
            messagebox.showwarning("Aucune donnée", "Aucun client à exporter.")
            return

        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv"), ("Tous les fichiers", "*.*")],
            initialfile="clients_export.csv",
            title="Exporter les clients en CSV",
        )
        if not path:
            return

        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerow(["ID", "Nom", "Téléphone", "Email", "Adresse", "Notes"])
            for c in clients:
                writer.writerow([
                    c["id"],
                    c["nom"] or "",
                    c["telephone"] or "",
                    c["email"] or "",
                    c["adresse"] or "",
                    (c["notes"] or "").replace("\n", " "),
                ])

        messagebox.showinfo("Export CSV", f"Clients exportés dans :\n{path}")

    # ------------------------------------------------------------------
    # CRUD clients
    # ------------------------------------------------------------------

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

        quotes_count = self.client_repository.get_quotes_count_for_client(self.selected_client_id)

        if quotes_count > 0:
            confirmed = messagebox.askyesno(
                "Client avec devis associés",
                f"Ce client possède {quotes_count} devis associé{'s' if quotes_count > 1 else ''}.\n\n"
                "Il est impossible de supprimer un client tant que ses devis existent.\n\n"
                "Souhaitez-vous supprimer le client ainsi que tous ses devis ?",
                icon="warning",
            )
            if not confirmed:
                return
            self.client_repository.delete_client_with_quotes(self.selected_client_id)
        else:
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
        self._clear_quote_history()

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
        self._refresh_quote_history(self.selected_client_id)

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
