import tkinter as tk
from tkinter import messagebox, ttk
import unicodedata

import customtkinter as ctk
from ui.pages.quote_catalog_dialog import QuoteCatalogDialog


class QuotesManagementPage(ctk.CTkFrame):
    def __init__(self, parent, client_repository, quote_repository, catalog_repository, quote_pdf_service):
        super().__init__(parent, fg_color="transparent")

        self.client_repository = client_repository
        self.quote_repository = quote_repository
        self.catalog_repository = catalog_repository
        self.quote_pdf_service = quote_pdf_service
        self.selected_quote_id = None
        self.is_edit_mode = False
        self.quote_lines = []
        self.client_map = {}
        self.catalog_map = {}
        self.client_choices_all = []
        self.catalog_choices_all = []
        self.selected_client_name = None
        self.selected_catalog_name = None
        self.client_suggestions = []
        self.catalog_suggestions = []
        self.client_popup = None
        self.catalog_popup = None
        self.client_listbox = None
        self.catalog_listbox = None
        self.catalog_dialog = None
        self.label_width = 150
        self.layout_mode = None
        self.responsive_breakpoint = 1360
        self.form_is_editable = True

        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=0)

        self._build_header()
        self._build_quotes_table()
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
            text="Devis",
            font=ctk.CTkFont(size=30, weight="bold"),
            text_color="#0f172a",
        )
        title.grid(row=0, column=0, sticky="w")

        subtitle = ctk.CTkLabel(
            header_frame,
            text="Creation, suivi et export PDF de devis professionnels",
            font=ctk.CTkFont(size=13),
            text_color="#64748b",
        )
        subtitle.grid(row=1, column=0, pady=(4, 0), sticky="w")

    def _build_quotes_table(self):
        self.table_card = ctk.CTkFrame(self, corner_radius=20, fg_color="#f8fafc", border_width=1, border_color="#dbe2ea")
        self.table_card.grid(row=1, column=0, padx=(30, 15), pady=20, sticky="nsew")
        self.table_card.grid_columnconfigure(0, weight=1)
        self.table_card.grid_rowconfigure(1, weight=1)

        table_header = ctk.CTkFrame(self.table_card, fg_color="transparent")
        table_header.grid(row=0, column=0, columnspan=2, padx=18, pady=(16, 0), sticky="ew")
        table_header.grid_columnconfigure(0, weight=1)

        table_title = ctk.CTkLabel(
            table_header,
            text="Liste des devis",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#0f172a",
        )
        table_title.grid(row=0, column=0, sticky="w")

        table_hint = ctk.CTkLabel(
            table_header,
            text="Selectionnez un devis pour le consulter, le modifier ou l'exporter",
            font=ctk.CTkFont(size=12),
            text_color="#64748b",
        )
        table_hint.grid(row=1, column=0, pady=(3, 0), sticky="w")

        self._configure_treeview_style()

        columns = ("numero", "client", "statut", "total")
        self.tree = ttk.Treeview(
            self.table_card,
            columns=columns,
            show="headings",
            height=16,
            style="Quotes.Treeview",
        )
        self.tree.heading("numero", text="Numero")
        self.tree.heading("client", text="Client")
        self.tree.heading("statut", text="Statut")
        self.tree.heading("total", text="Total")

        self.tree.column("numero", width=130, anchor="center")
        self.tree.column("client", width=240)
        self.tree.column("statut", width=100, anchor="center")
        self.tree.column("total", width=130, anchor="e")

        self.tree.grid(row=1, column=0, padx=16, pady=16, sticky="nsew")
        self.tree.bind("<<TreeviewSelect>>", self._on_quote_select)

        vertical_scrollbar = ttk.Scrollbar(self.table_card, orient="vertical", command=self.tree.yview)
        horizontal_scrollbar = ttk.Scrollbar(self.table_card, orient="horizontal", command=self.tree.xview)
        self.tree.configure(
            yscrollcommand=vertical_scrollbar.set,
            xscrollcommand=horizontal_scrollbar.set,
        )
        vertical_scrollbar.grid(row=1, column=1, pady=16, sticky="ns")
        horizontal_scrollbar.grid(row=2, column=0, padx=16, pady=(0, 16), sticky="ew")

    def _configure_treeview_style(self):
        style = ttk.Style()
        style.configure(
            "Quotes.Treeview",
            rowheight=38,
            background="#ffffff",
            fieldbackground="#ffffff",
            borderwidth=0,
            relief="flat",
            font=("Segoe UI", 10),
        )
        style.configure(
            "Quotes.Treeview.Heading",
            background="#e8eef6",
            foreground="#374151",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            padding=(8, 6),
        )
        style.map(
            "Quotes.Treeview",
            background=[("selected", "#dbeafe")],
            foreground=[("selected", "#1e3a8a")],
        )
        style.map(
            "Quotes.Treeview.Heading",
            relief=[("active", "flat")],
        )
        style.configure(
            "QuoteLines.Treeview",
            rowheight=32,
            background="#ffffff",
            fieldbackground="#ffffff",
            borderwidth=0,
            relief="flat",
            font=("Segoe UI", 9),
        )
        style.configure(
            "QuoteLines.Treeview.Heading",
            background="#e8eef6",
            foreground="#374151",
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            padding=(6, 4),
        )
        style.map(
            "QuoteLines.Treeview",
            background=[("selected", "#dbeafe")],
            foreground=[("selected", "#1e3a8a")],
        )
        style.configure(
            "Quotes.TCombobox",
            fieldbackground="#ffffff",
            background="#ffffff",
            foreground="#0f172a",
            padding=6,
        )

    def _build_form(self):
        self.form_card = ctk.CTkFrame(self, corner_radius=20, fg_color="#f8fafc", border_width=1, border_color="#dbe2ea")
        self.form_card.grid(row=1, column=1, padx=(15, 30), pady=20, sticky="nsew")
        self.form_card.grid_columnconfigure(0, weight=1)
        self.form_card.grid_rowconfigure(1, weight=1)

        form_header = ctk.CTkFrame(self.form_card, fg_color="transparent")
        form_header.grid(row=0, column=0, padx=18, pady=(16, 0), sticky="ew")
        form_header.grid_columnconfigure(0, weight=1)

        form_title = ctk.CTkLabel(
            form_header,
            text="Edition du devis",
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
        form_scroll.grid_columnconfigure(1, weight=1)
        self.form_scroll = form_scroll
        self.form_scroll.bind("<MouseWheel>", self._on_form_scroll, add="+")
        self.form_scroll.bind("<Button-4>", self._on_form_scroll, add="+")
        self.form_scroll.bind("<Button-5>", self._on_form_scroll, add="+")
        self.form_scroll.bind("<Configure>", self._on_form_scroll, add="+")

        numero_title = ctk.CTkLabel(form_scroll, text="Numero", text_color="#334155")
        numero_title.grid(row=0, column=0, padx=20, pady=(8, 6), sticky="w")

        self.numero_label = ctk.CTkLabel(
            form_scroll,
            text=self.quote_repository.get_next_quote_number(),
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#0f172a",
        )
        self.numero_label.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="w")

        client_label = ctk.CTkLabel(form_scroll, text="Client", text_color="#334155")
        client_label.grid(row=2, column=0, padx=20, pady=(8, 6), sticky="w")

        self.client_option = ttk.Combobox(
            form_scroll,
            values=["Aucun client"],
            state="normal",
            height=5,
            style="Quotes.TCombobox",
        )
        self.client_option.grid(row=3, column=0, columnspan=2, padx=20, pady=(0, 10), sticky="ew")
        self.client_option.bind("<KeyRelease>", self._on_client_search)
        self.client_option.bind("<<ComboboxSelected>>", self._on_client_selected)
        self.client_option.bind("<Return>", self._on_client_selected)
        self.client_option.bind("<FocusOut>", lambda _event: self.after(120, self._hide_client_popup), add="+")

        status_label = ctk.CTkLabel(form_scroll, text="Statut", text_color="#334155")
        status_label.grid(row=4, column=0, padx=20, pady=(8, 6), sticky="w")

        self.status_option = ctk.CTkOptionMenu(
            form_scroll,
            values=["Brouillon", "Envoye", "Accepte"],
            fg_color="#1d4ed8",
            button_color="#1e40af",
            button_hover_color="#1e3a8a",
        )
        self.status_option.grid(row=5, column=0, columnspan=2, padx=20, pady=(0, 10), sticky="ew")

        catalog_header = ctk.CTkFrame(form_scroll, fg_color="transparent")
        catalog_header.grid(row=6, column=0, columnspan=2, padx=20, pady=(10, 6), sticky="ew")
        catalog_header.grid_columnconfigure(0, weight=1)

        line_title = ctk.CTkLabel(catalog_header, text="Nouvelle ligne", text_color="#334155")
        line_title.grid(row=0, column=0, sticky="w")

        self.catalog_button = ctk.CTkButton(
            catalog_header,
            text="Gerer le catalogue",
            width=160,
            fg_color="#0f766e",
            hover_color="#115e59",
            command=self.open_catalog_manager,
        )
        self.catalog_button.grid(row=0, column=1, sticky="e")

        item_label = ctk.CTkLabel(form_scroll, text="Produit / service", text_color="#334155")
        item_label.grid(row=7, column=0, padx=20, pady=(0, 6), sticky="w")

        self.catalog_option = ttk.Combobox(
            form_scroll,
            values=["Aucun article"],
            state="normal",
            height=5,
            style="Quotes.TCombobox",
        )
        self.catalog_option.grid(row=8, column=0, columnspan=2, padx=20, pady=(0, 10), sticky="ew")
        self.catalog_option.bind("<KeyRelease>", self._on_catalog_search)
        self.catalog_option.bind("<<ComboboxSelected>>", self._on_catalog_selected)
        self.catalog_option.bind("<Return>", self._on_catalog_selected)
        self.catalog_option.bind("<FocusOut>", lambda _event: self.after(120, self._hide_catalog_popup), add="+")

        self.quantity_entry = ctk.CTkEntry(form_scroll, placeholder_text="Quantite")
        self.quantity_entry.grid(row=9, column=0, padx=(20, 8), pady=(0, 8), sticky="ew")
        self.quantity_entry.bind("<KeyRelease>", self._on_quantity_input)

        self.unit_price_entry = ctk.CTkEntry(form_scroll, state="readonly")
        self.unit_price_entry.grid(row=9, column=1, padx=(8, 20), pady=(0, 8), sticky="ew")

        self.add_line_button = ctk.CTkButton(
            form_scroll,
            text="Ajouter la ligne",
            fg_color="#0f766e",
            hover_color="#115e59",
            command=self.add_line,
        )
        self.add_line_button.grid(row=10, column=0, columnspan=2, padx=20, pady=(0, 12), sticky="ew")

        lines_frame = ctk.CTkFrame(form_scroll, fg_color="#ffffff", corner_radius=14, border_width=1, border_color="#e2e8f0")
        lines_frame.grid(row=11, column=0, columnspan=2, padx=20, pady=(0, 12), sticky="nsew")
        lines_frame.grid_columnconfigure(0, weight=1)
        lines_frame.grid_rowconfigure(0, weight=1)

        line_columns = ("description", "quantite", "prix", "total")
        self.lines_tree = ttk.Treeview(
            lines_frame,
            columns=line_columns,
            show="headings",
            height=7,
            style="QuoteLines.Treeview",
        )
        self.lines_tree.heading("description", text="Description")
        self.lines_tree.heading("quantite", text="Qt")
        self.lines_tree.heading("prix", text="PU")
        self.lines_tree.heading("total", text="Total")
        self.lines_tree.column("description", width=220)
        self.lines_tree.column("quantite", width=70, anchor="center")
        self.lines_tree.column("prix", width=100, anchor="e")
        self.lines_tree.column("total", width=110, anchor="e")
        self.lines_tree.grid(row=0, column=0, sticky="nsew")

        line_vertical_scrollbar = ttk.Scrollbar(lines_frame, orient="vertical", command=self.lines_tree.yview)
        line_horizontal_scrollbar = ttk.Scrollbar(lines_frame, orient="horizontal", command=self.lines_tree.xview)
        self.lines_tree.configure(
            yscrollcommand=line_vertical_scrollbar.set,
            xscrollcommand=line_horizontal_scrollbar.set,
        )
        line_vertical_scrollbar.grid(row=0, column=1, sticky="ns")
        line_horizontal_scrollbar.grid(row=1, column=0, sticky="ew")

        self.remove_line_button = ctk.CTkButton(
            form_scroll,
            text="Supprimer la ligne",
            fg_color="#dc2626",
            hover_color="#b91c1c",
            command=self.remove_line,
        )
        self.remove_line_button.grid(row=12, column=0, columnspan=2, padx=20, pady=(0, 12), sticky="ew")

        self.total_label = ctk.CTkLabel(
            form_scroll,
            text="Total : 0.00 EUR",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#0f172a",
        )
        self.total_label.grid(row=13, column=0, padx=20, pady=(0, 12), sticky="w")

        conditions_frame = ctk.CTkFrame(form_scroll, fg_color="#ffffff", corner_radius=14, border_width=1, border_color="#e2e8f0")
        conditions_frame.grid(row=14, column=0, columnspan=2, padx=20, pady=(0, 12), sticky="ew")
        conditions_frame.grid_columnconfigure(1, weight=1)

        conditions_title = ctk.CTkLabel(
            conditions_frame,
            text="Conditions du devis",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#111827",
        )
        conditions_title.grid(row=0, column=0, columnspan=2, padx=12, pady=(12, 10), sticky="w")

        conditions_hint = ctk.CTkLabel(
            conditions_frame,
            text="Adaptez facilement les clauses avant impression ou export PDF.",
            font=ctk.CTkFont(size=11),
            text_color="#6b7280",
        )
        conditions_hint.grid(row=1, column=0, columnspan=2, padx=12, pady=(0, 8), sticky="w")

        self.delai_entry = self._create_condition_entry(conditions_frame, 2, "Delai")

        materiel_label = ctk.CTkLabel(conditions_frame, text="Materiel", text_color="#374151")
        materiel_label.grid(row=3, column=0, padx=12, pady=6, sticky="w")
        self.materiel_option = ctk.CTkOptionMenu(
            conditions_frame,
            values=["Client", "Electricien"],
            fg_color="#1d4ed8",
            button_color="#1e40af",
            button_hover_color="#1e3a8a",
        )
        self.materiel_option.grid(row=3, column=1, padx=12, pady=6, sticky="ew")

        self.acompte_entry = self._create_condition_entry(conditions_frame, 4, "Acompte (%)")
        self.validite_entry = self._create_condition_entry(conditions_frame, 5, "Validite")

        exceptional_label = ctk.CTkLabel(
            conditions_frame,
            text="Condition(s) exceptionnelle(s)",
            text_color="#374151",
        )
        exceptional_label.grid(row=6, column=0, padx=12, pady=(6, 6), sticky="nw")
        self.conditions_exceptionnelles_text = ctk.CTkTextbox(
            conditions_frame,
            height=96,
            fg_color="#ffffff",
            border_width=1,
            border_color="#9ca3af",
            text_color="#111827",
        )
        self.conditions_exceptionnelles_text.grid(row=6, column=1, padx=12, pady=(6, 12), sticky="ew")

        buttons_frame = ctk.CTkFrame(form_scroll, fg_color="transparent")
        buttons_frame.grid(row=15, column=0, columnspan=2, padx=20, pady=(0, 20), sticky="ew")
        buttons_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.save_button = ctk.CTkButton(buttons_frame, text="Creer le devis", command=self.save_quote)
        self.save_button.grid(row=1, column=0, padx=(0, 6), pady=(10, 0), sticky="ew")

        self.edit_button = ctk.CTkButton(
            buttons_frame,
            text="Modifier",
            fg_color="#2563eb",
            hover_color="#1d4ed8",
            command=self.start_edit_quote,
        )
        self.edit_button.grid(row=0, column=1, padx=6, sticky="ew")

        self.validate_button = ctk.CTkButton(
            buttons_frame,
            text="Valider",
            fg_color="#059669",
            hover_color="#047857",
            command=self.update_quote,
        )
        self.validate_button.grid(row=0, column=1, padx=6, sticky="ew")

        self.delete_button = ctk.CTkButton(
            buttons_frame,
            text="Supprimer",
            fg_color="#dc2626",
            hover_color="#b91c1c",
            command=self.delete_quote,
        )
        self.delete_button.grid(row=0, column=0, padx=(0, 6), sticky="ew")

        self.export_button = ctk.CTkButton(
            buttons_frame,
            text="Exporter en PDF",
            fg_color="#0f766e",
            hover_color="#115e59",
            command=self.export_quote_pdf,
        )
        self.export_button.grid(row=0, column=2, padx=(6, 0), sticky="ew")

        self.new_button = ctk.CTkButton(
            buttons_frame,
            text="Nouveau",
            fg_color="#6b7280",
            hover_color="#4b5563",
            command=self.reset_form,
        )
        self.new_button.grid(row=1, column=1, padx=6, pady=(10, 0), sticky="ew")

        self.refresh_client_choices()
        self.refresh_catalog_choices()
        self.refresh_quotes()
        self._reset_conditions_defaults()

    def _on_resize(self, _event):
        self._close_open_dropdowns()
        self.after_idle(self._apply_responsive_layout)

    def _on_form_scroll(self, _event):
        self._close_open_dropdowns()

    def _close_open_dropdowns(self):
        for widget in (getattr(self, "client_option", None), getattr(self, "catalog_option", None)):
            if widget is None:
                continue
            try:
                widget.event_generate("<Escape>")
            except Exception:
                pass
        self._hide_client_popup()
        self._hide_catalog_popup()

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

    def _set_form_editable(self, editable):
        self.form_is_editable = editable
        state = "normal" if editable else "disabled"
        combobox_state = "normal" if editable else "disabled"

        self.client_option.configure(state=combobox_state)
        self.status_option.configure(state=state)
        self.catalog_option.configure(state=combobox_state)
        self.quantity_entry.configure(state=state)
        self.add_line_button.configure(state=state)
        self.remove_line_button.configure(state=state)
        self.catalog_button.configure(state=state)
        self.delai_entry.configure(state=state)
        self.materiel_option.configure(state=state)
        self.acompte_entry.configure(state=state)
        self.validite_entry.configure(state=state)
        self.conditions_exceptionnelles_text.configure(state=state)

    def _sync_action_buttons(self):
        has_selection = self.selected_quote_id is not None

        if has_selection and not self.is_edit_mode:
            self.edit_button.grid()
            self.delete_button.grid()
            self.export_button.grid()
            self.validate_button.grid_remove()
        elif has_selection and self.is_edit_mode:
            self.edit_button.grid_remove()
            self.delete_button.grid()
            self.export_button.grid_remove()
            self.validate_button.grid()
        else:
            self.edit_button.grid_remove()
            self.delete_button.grid_remove()
            self.export_button.grid_remove()
            self.validate_button.grid_remove()

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
            f'{client["nom"]} (ID {client["id"]})': client["id"]
            for client in clients
        }
        self.client_choices_all = list(self.client_map.keys())
        self.client_option.configure(values=self.client_choices_all)

        current_value = self.client_option.get()
        if current_value not in self.client_map:
            self.client_option.set(self.client_choices_all[0])
            current_value = self.client_choices_all[0]
        self.selected_client_name = current_value

    def refresh_catalog_choices(self):
        items = self.catalog_repository.get_all_items()
        if not items:
            self.catalog_map = {}
            self.catalog_choices_all = ["Aucun article"]
            self.catalog_option.configure(values=self.catalog_choices_all)
            self.catalog_option.set("Aucun article")
            self.selected_catalog_name = "Aucun article"
            self._set_unit_price_display(None)
            return

        self.catalog_map = {item["nom"]: item for item in items}
        self.catalog_choices_all = list(self.catalog_map.keys())
        self.catalog_option.configure(values=self.catalog_choices_all)

        current_value = self.catalog_option.get()
        if current_value not in self.catalog_map:
            current_value = self.catalog_choices_all[0]
            self.catalog_option.set(current_value)
        self.selected_catalog_name = current_value

        self._set_unit_price_display(self.catalog_map[current_value]["prix_unitaire"])

    def open_catalog_manager(self):
        if self.catalog_dialog is not None and self.catalog_dialog.winfo_exists():
            self.catalog_dialog.focus()
            return

        self.catalog_dialog = QuoteCatalogDialog(
            self,
            self.catalog_repository,
            self.refresh_catalog_choices,
        )

    def refresh_quotes(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        quotes = self.quote_repository.get_all_quotes()
        for index, quote in enumerate(quotes):
            row_tag = "evenrow" if index % 2 == 0 else "oddrow"
            status_tag = self._get_status_tag(quote["statut"])
            self.tree.insert(
                "",
                tk.END,
                iid=str(quote["id"]),
                values=(
                    quote["numero"],
                    quote["client_nom"],
                    quote["statut"],
                    self._format_currency(quote["total"]),
                ),
                tags=(row_tag, status_tag),
            )
        self.tree.tag_configure("evenrow", background="#ffffff")
        self.tree.tag_configure("oddrow", background="#f3f4f6")
        self.tree.tag_configure("status_brouillon", foreground="#6b7280")
        self.tree.tag_configure("status_envoye", foreground="#2563eb")
        self.tree.tag_configure("status_accepte", foreground="#059669")

        if self.selected_quote_id is None:
            self.numero_label.configure(text=self.quote_repository.get_next_quote_number())

    def add_line(self):
        if not self.catalog_map:
            messagebox.showwarning("Catalogue vide", "Ajoutez d'abord un produit ou service dans le catalogue.")
            return

        self._on_catalog_focus_out()
        selected_name = self.catalog_option.get()
        item = self.catalog_map.get(selected_name)
        if item is None:
            messagebox.showwarning("Article requis", "Selectionnez un produit ou service valide.")
            return

        quantity_text = self.quantity_entry.get().strip()
        try:
            quantite = float(quantity_text.replace(",", "."))
        except ValueError:
            messagebox.showwarning("Valeur invalide", "La quantite doit etre numerique.")
            return

        if quantite <= 0:
            messagebox.showwarning("Valeur invalide", "La quantite doit etre positive.")
            return

        prix_unitaire = item["prix_unitaire"]
        line = {
            "description": item["nom"],
            "quantite": quantite,
            "prix_unitaire": prix_unitaire,
            "total_ligne": quantite * prix_unitaire,
        }
        self.quote_lines.append(line)
        self._refresh_lines_table()
        self._clear_line_inputs()

    def remove_line(self):
        selected = self.lines_tree.selection()
        if not selected:
            messagebox.showwarning("Selection requise", "Selectionnez une ligne a supprimer.")
            return

        index = self.lines_tree.index(selected[0])
        del self.quote_lines[index]
        self._refresh_lines_table()

    def save_quote(self):
        if self.selected_quote_id is not None:
            messagebox.showwarning("Mode creation", "Cliquez sur Nouveau pour creer un autre devis.")
            return

        client_id = self._validate_quote_form()
        if client_id is None:
            return

        quote_id = self.quote_repository.create_quote(
            client_id=client_id,
            statut=self.status_option.get(),
            lignes=self.quote_lines,
            conditions=self._get_conditions_data(),
        )
        self.refresh_quotes()
        self.reset_form()
        messagebox.showinfo("Devis cree", f"Le devis a bien ete enregistre (ID {quote_id}).")

    def start_edit_quote(self):
        if self.selected_quote_id is None:
            messagebox.showwarning("Selection requise", "Selectionnez un devis a modifier.")
            return

        self.is_edit_mode = True
        self._set_form_editable(True)
        self._sync_action_buttons()

    def update_quote(self):
        if self.selected_quote_id is None:
            messagebox.showwarning("Selection requise", "Selectionnez un devis a modifier.")
            return

        if not self.is_edit_mode:
            messagebox.showwarning("Mode edition", "Cliquez d'abord sur Modifier.")
            return

        client_id = self._validate_quote_form()
        if client_id is None:
            return

        self.quote_repository.update_quote(
            quote_id=self.selected_quote_id,
            client_id=client_id,
            statut=self.status_option.get(),
            lignes=self.quote_lines,
            conditions=self._get_conditions_data(),
        )
        self.refresh_quotes()
        self.reset_form()
        messagebox.showinfo("Devis modifie", "Le devis a bien ete mis a jour.")

    def delete_quote(self):
        if self.selected_quote_id is None:
            messagebox.showwarning("Selection requise", "Selectionnez un devis a supprimer.")
            return

        confirmed = messagebox.askyesno(
            "Confirmation",
            "Voulez-vous vraiment supprimer ce devis ?",
        )
        if not confirmed:
            return

        self.quote_repository.delete_quote(self.selected_quote_id)
        self.refresh_quotes()
        self.reset_form()
        messagebox.showinfo("Devis supprime", "Le devis a bien ete supprime.")

    def export_quote_pdf(self):
        if self.selected_quote_id is None:
            messagebox.showwarning("Selection requise", "Selectionnez un devis a exporter.")
            return

        if self.is_edit_mode:
            messagebox.showwarning("Mode edition", "Validez les modifications avant d'exporter le devis.")
            return

        quote = self.quote_repository.get_quote_by_id(self.selected_quote_id)
        if quote is None:
            messagebox.showerror("Devis introuvable", "Le devis selectionne n'existe plus.")
            return

        client = self.client_repository.get_client_by_id(quote["client_id"])
        if client is None:
            messagebox.showerror("Client introuvable", "Impossible de retrouver le client associe a ce devis.")
            return

        try:
            output_path = self.quote_pdf_service.export_quote_pdf(quote, client)
        except Exception as error:
            messagebox.showerror("Export PDF", f"Echec de l'export PDF : {error}")
            return

        messagebox.showinfo("Export PDF", f"Le devis a ete exporte dans :\n{output_path}")

    def reset_form(self):
        self.selected_quote_id = None
        self.is_edit_mode = False
        self.quote_lines = []
        self.status_option.set("Brouillon")
        self._reset_conditions_defaults()
        self._clear_line_inputs()
        self._refresh_lines_table()
        self.refresh_client_choices()
        self.refresh_catalog_choices()
        self.numero_label.configure(text=self.quote_repository.get_next_quote_number())
        self.tree.selection_remove(self.tree.selection())
        self._set_form_editable(True)
        self._sync_action_buttons()

    def _refresh_lines_table(self):
        for item in self.lines_tree.get_children():
            self.lines_tree.delete(item)

        for index, line in enumerate(self.quote_lines):
            row_tag = "evenrow" if index % 2 == 0 else "oddrow"
            self.lines_tree.insert(
                "",
                tk.END,
                values=(
                    line["description"],
                    self._format_number(line["quantite"]),
                    self._format_currency(line["prix_unitaire"]),
                    self._format_currency(line["total_ligne"]),
                ),
                tags=(row_tag,),
            )
        self.lines_tree.tag_configure("evenrow", background="#ffffff")
        self.lines_tree.tag_configure("oddrow", background="#f3f4f6")

        total = sum(line["total_ligne"] for line in self.quote_lines)
        self.total_label.configure(text=f"Total : {self._format_currency(total)}")

    def _clear_line_inputs(self):
        self.quantity_entry.delete(0, tk.END)
        if self.catalog_map:
            selected_name = self.catalog_option.get()
            if selected_name in self.catalog_map:
                self._set_unit_price_display(self.catalog_map[selected_name]["prix_unitaire"])
                return
        self._set_unit_price_display(None)

    def _on_quantity_input(self, _event=None):
        text = self.quantity_entry.get()
        filtered_characters = []
        separator_used = False
        for character in text:
            if character.isdigit():
                filtered_characters.append(character)
                continue
            if character in {".", ","} and not separator_used:
                filtered_characters.append(character)
                separator_used = True

        filtered = "".join(filtered_characters)
        if filtered != text:
            cursor_position = self.quantity_entry.index(tk.INSERT)
            self.quantity_entry.delete(0, tk.END)
            self.quantity_entry.insert(0, filtered)
            self.quantity_entry.icursor(max(0, min(cursor_position - (len(text) - len(filtered)), len(filtered))))

    def _set_unit_price_display(self, value):
        self.unit_price_entry.configure(state="normal")
        self.unit_price_entry.delete(0, tk.END)
        if value is not None:
            self.unit_price_entry.insert(0, self._format_currency(value))
        self.unit_price_entry.configure(state="readonly")

    def _on_catalog_selected(self, selected_name=None):
        if isinstance(selected_name, tk.Event):
            selected_name = self.catalog_option.get()
        if selected_name is None:
            selected_name = self.catalog_option.get()

        self.catalog_option.configure(values=self.catalog_choices_all)
        item = self.catalog_map.get(selected_name)
        if item is None:
            self._set_unit_price_display(None)
            return

        self.selected_catalog_name = selected_name
        self._hide_catalog_popup()
        self._set_unit_price_display(item["prix_unitaire"])

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

    def _on_catalog_search(self, event):
        self._filter_combobox_values(self.catalog_option, self.catalog_choices_all)
        if event.keysym == "Escape":
            self._hide_catalog_popup()
            return
        if event.keysym == "Return":
            if self.catalog_suggestions:
                self.catalog_option.set(self.catalog_suggestions[0])
            self._on_catalog_selected()
            return
        if event.keysym in {"Up", "Down", "Tab"}:
            return
        self._show_catalog_popup()

    def _on_client_selected(self, _event=None):
        selected_name = self._enforce_combobox_selection(
            self.client_option,
            self.client_choices_all,
            self.selected_client_name,
        )
        if selected_name:
            self.selected_client_name = selected_name
        self.client_option.configure(values=self.client_choices_all)
        self._hide_client_popup()

    def _on_catalog_focus_out(self, _event=None):
        selected_name = self._enforce_combobox_selection(
            self.catalog_option,
            self.catalog_choices_all,
            self.selected_catalog_name,
        )
        if selected_name:
            self.selected_catalog_name = selected_name
        self.catalog_option.configure(values=self.catalog_choices_all)
        self._hide_catalog_popup()
        self._on_catalog_selected()

    def _filter_combobox_values(self, combobox, all_values):
        if not all_values:
            return

        current_text = combobox.get()
        try:
            cursor_position = combobox.index(tk.INSERT)
        except tk.TclError:
            cursor_position = len(current_text)

        query = self._normalize_search_text(combobox.get())
        if not query:
            filtered_values = all_values
        else:
            filtered_values = [
                value
                for value in all_values
                if query in self._normalize_search_text(value)
            ]
        if tuple(combobox.cget("values")) != tuple(filtered_values):
            combobox.configure(values=filtered_values)

        # Preserve user input after list refresh to avoid losing typed text.
        if combobox.get() != current_text:
            combobox.delete(0, tk.END)
            combobox.insert(0, current_text)
            safe_position = max(0, min(cursor_position, len(current_text)))
            combobox.icursor(safe_position)

    def _show_client_popup(self):
        self.client_suggestions = list(self.client_option.cget("values"))
        if not self.client_suggestions:
            self._hide_client_popup()
            return
        popup, listbox = self._ensure_suggestion_popup("client")
        self._fill_suggestion_listbox(listbox, self.client_suggestions)
        self._place_popup_for_combobox(popup, self.client_option)

    def _show_catalog_popup(self):
        self.catalog_suggestions = list(self.catalog_option.cget("values"))
        if not self.catalog_suggestions:
            self._hide_catalog_popup()
            return
        popup, listbox = self._ensure_suggestion_popup("catalog")
        self._fill_suggestion_listbox(listbox, self.catalog_suggestions)
        self._place_popup_for_combobox(popup, self.catalog_option)

    def _hide_client_popup(self):
        if self.client_popup is not None and self.client_popup.winfo_exists():
            self.client_popup.withdraw()

    def _hide_catalog_popup(self):
        if self.catalog_popup is not None and self.catalog_popup.winfo_exists():
            self.catalog_popup.withdraw()

    def _ensure_suggestion_popup(self, kind):
        popup_attr = f"{kind}_popup"
        listbox_attr = f"{kind}_listbox"
        popup = getattr(self, popup_attr)
        listbox = getattr(self, listbox_attr)
        if popup is not None and popup.winfo_exists() and listbox is not None and listbox.winfo_exists():
            return popup, listbox

        popup = tk.Toplevel(self)
        popup.withdraw()
        popup.overrideredirect(True)
        popup.configure(background="#cbd5e1")

        listbox = tk.Listbox(
            popup,
            relief="flat",
            borderwidth=0,
            exportselection=False,
            activestyle="none",
            font=("Segoe UI", 10),
        )
        listbox.pack(fill="both", expand=True, padx=1, pady=1)
        listbox.bind("<ButtonRelease-1>", lambda _event, value=kind: self._on_popup_item_click(value))
        listbox.bind("<Return>", lambda _event, value=kind: self._on_popup_item_click(value))
        setattr(self, popup_attr, popup)
        setattr(self, listbox_attr, listbox)
        return popup, listbox

    def _fill_suggestion_listbox(self, listbox, values):
        listbox.delete(0, tk.END)
        for value in values:
            listbox.insert(tk.END, value)
        if values:
            listbox.selection_set(0)
            listbox.activate(0)

    def _place_popup_for_combobox(self, popup, combobox):
        combobox.update_idletasks()
        width = max(combobox.winfo_width(), 200)
        row_height = 22
        visible_rows = min(max(len(combobox.cget("values")), 1), 8)
        height = max(visible_rows * row_height + 4, 28)
        x = combobox.winfo_rootx()
        y = combobox.winfo_rooty() + combobox.winfo_height()
        popup.geometry(f"{width}x{height}+{x}+{y}")
        popup.deiconify()
        popup.lift()

    def _on_popup_item_click(self, kind):
        listbox = self.client_listbox if kind == "client" else self.catalog_listbox
        combobox = self.client_option if kind == "client" else self.catalog_option
        if listbox is None or not listbox.winfo_exists():
            return
        selection = listbox.curselection()
        if not selection:
            return
        selected_value = listbox.get(selection[0])
        combobox.set(selected_value)
        if kind == "client":
            self._on_client_selected()
        else:
            self._on_catalog_selected()

    def _enforce_combobox_selection(self, combobox, all_values, fallback_value):
        if not all_values:
            combobox.set("")
            return ""

        current_value = combobox.get().strip()
        if current_value in all_values:
            return current_value

        if fallback_value in all_values:
            selected_value = fallback_value
        else:
            selected_value = all_values[0]

        combobox.set(selected_value)
        return selected_value

    def _normalize_search_text(self, value):
        text = (value or "").strip().lower()
        return "".join(
            character
            for character in unicodedata.normalize("NFD", text)
            if unicodedata.category(character) != "Mn"
        )

    def _on_quote_select(self, _event):
        selected = self.tree.selection()
        if not selected:
            return

        quote = self.quote_repository.get_quote_by_id(int(selected[0]))
        if quote is None:
            return

        self._load_quote(quote)

    def _load_quote(self, quote):
        self.selected_quote_id = quote["id"]
        self.is_edit_mode = False
        self.refresh_client_choices()
        self.refresh_catalog_choices()
        self._set_form_editable(True)

        for name, client_id in self.client_map.items():
            if client_id == quote["client_id"]:
                self.client_option.set(name)
                self.selected_client_name = name
                break

        self.status_option.set(quote["statut"])
        self.numero_label.configure(text=quote["numero"])
        self._load_conditions(quote)
        self.quote_lines = [
            {
                "description": line["description"],
                "quantite": line["quantite"],
                "prix_unitaire": line["prix_unitaire"],
                "total_ligne": line["total_ligne"],
            }
            for line in quote["lignes"]
        ]
        self._refresh_lines_table()
        self._clear_line_inputs()
        self._set_form_editable(False)
        self._sync_action_buttons()

    def _validate_quote_form(self):
        if not self.client_map:
            messagebox.showwarning("Client requis", "Ajoutez d'abord un client dans le module Clients.")
            return None
        self._on_client_selected()

        if not self.quote_lines:
            messagebox.showwarning("Lignes requises", "Ajoutez au moins une ligne de devis.")
            return None

        conditions = self._get_conditions_data()
        if not conditions["delai"]:
            messagebox.showwarning("Delai requis", "Le delai doit etre renseigne.")
            return None

        if conditions["acompte_percent"] is None:
            messagebox.showwarning("Acompte invalide", "L'acompte doit etre un nombre entier.")
            return None

        if conditions["acompte_percent"] < 0 or conditions["acompte_percent"] > 100:
            messagebox.showwarning("Acompte invalide", "L'acompte doit etre compris entre 0 et 100.")
            return None

        if not conditions["validite"]:
            messagebox.showwarning("Validite requise", "La validite doit etre renseignee.")
            return None

        client_name = self.client_option.get()
        client_id = self.client_map.get(client_name)
        if client_id is None:
            messagebox.showwarning("Client requis", "Selectionnez un client valide.")
            return None

        return client_id

    def _format_currency(self, value):
        return f"{value:.2f} EUR"

    def _format_number(self, value):
        if int(value) == value:
            return str(int(value))
        return f"{value:.2f}"

    def _get_status_tag(self, status):
        normalized = (status or "").strip().lower()
        if normalized == "brouillon":
            return "status_brouillon"
        if normalized == "envoye":
            return "status_envoye"
        if normalized == "accepte":
            return "status_accepte"
        return "status_brouillon"

    def _create_condition_entry(self, parent, row, label_text):
        label = ctk.CTkLabel(parent, text=label_text, text_color="#374151")
        label.grid(row=row, column=0, padx=12, pady=6, sticky="w")

        entry = ctk.CTkEntry(parent)
        entry.grid(row=row, column=1, padx=12, pady=6, sticky="ew")
        return entry

    def _reset_conditions_defaults(self):
        self._set_entry_value(self.delai_entry, "2 jours")
        self.materiel_option.set("Client")
        self._set_entry_value(self.acompte_entry, "30")
        self._set_entry_value(self.validite_entry, "30 jours")
        self._set_textbox_value(self.conditions_exceptionnelles_text, "")

    def _get_conditions_data(self):
        acompte_text = self.acompte_entry.get().strip()
        try:
            acompte_percent = int(acompte_text)
        except ValueError:
            acompte_percent = None

        materiel_charge = "electricien" if self.materiel_option.get().strip().lower() == "electricien" else "client"

        return {
            "delai": self.delai_entry.get().strip(),
            "materiel_charge": materiel_charge,
            "acompte_percent": acompte_percent,
            "validite": self.validite_entry.get().strip(),
            "conditions_exceptionnelles": self.conditions_exceptionnelles_text.get("1.0", tk.END).strip(),
        }

    def _load_conditions(self, quote):
        self._set_entry_value(self.delai_entry, quote.get("delai") or "2 jours")
        self.materiel_option.set("Electricien" if quote.get("materiel_charge") == "electricien" else "Client")
        self._set_entry_value(self.acompte_entry, str(quote.get("acompte_percent", 30)))
        self._set_entry_value(self.validite_entry, quote.get("validite") or "30 jours")
        self._set_textbox_value(self.conditions_exceptionnelles_text, quote.get("conditions_exceptionnelles") or "")

    def _set_entry_value(self, entry, value):
        restore_disabled = not self.form_is_editable
        if restore_disabled:
            entry.configure(state="normal")
        entry.delete(0, tk.END)
        entry.insert(0, value)
        if restore_disabled:
            entry.configure(state="disabled")

    def _set_textbox_value(self, textbox, value):
        restore_disabled = not self.form_is_editable
        if restore_disabled:
            textbox.configure(state="normal")
        textbox.delete("1.0", tk.END)
        textbox.insert("1.0", value)
        if restore_disabled:
            textbox.configure(state="disabled")
