import tkinter as tk
from tkinter import messagebox, ttk

import customtkinter as ctk


class QuoteCatalogDialog(ctk.CTkToplevel):
    def __init__(self, parent, catalog_repository, on_save_callback):
        super().__init__(parent)

        self.catalog_repository = catalog_repository
        self.on_save_callback = on_save_callback
        self.selected_item_id = None
        self.is_edit_mode = False

        self.title("Catalogue produits et services")
        self.geometry("760x420")
        self.minsize(720, 380)
        self.transient(parent)
        self.grab_set()

        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)

        self._build_table()
        self._build_form()
        self.refresh_items()
        self.protocol("WM_DELETE_WINDOW", self._close_dialog)

    def _build_table(self):
        table_card = ctk.CTkFrame(self, corner_radius=16, fg_color="#f9fafb")
        table_card.grid(row=0, column=0, padx=(20, 10), pady=20, sticky="nsew")
        table_card.grid_columnconfigure(0, weight=1)
        table_card.grid_rowconfigure(0, weight=1)

        columns = ("id", "nom", "prix")
        self.tree = ttk.Treeview(table_card, columns=columns, show="headings", height=12)
        self.tree.heading("id", text="ID")
        self.tree.heading("nom", text="Produit / service")
        self.tree.heading("prix", text="Prix unitaire")
        self.tree.column("id", width=50, anchor="center")
        self.tree.column("nom", width=260)
        self.tree.column("prix", width=110, anchor="e")
        self.tree.grid(row=0, column=0, padx=16, pady=16, sticky="nsew")
        self.tree.bind("<<TreeviewSelect>>", self._on_item_select)

        vertical_scrollbar = ttk.Scrollbar(table_card, orient="vertical", command=self.tree.yview)
        horizontal_scrollbar = ttk.Scrollbar(table_card, orient="horizontal", command=self.tree.xview)
        self.tree.configure(
            yscrollcommand=vertical_scrollbar.set,
            xscrollcommand=horizontal_scrollbar.set,
        )
        vertical_scrollbar.grid(row=0, column=1, pady=16, sticky="ns")
        horizontal_scrollbar.grid(row=1, column=0, padx=16, pady=(0, 16), sticky="ew")

    def _build_form(self):
        form_card = ctk.CTkFrame(self, corner_radius=16, fg_color="#f9fafb")
        form_card.grid(row=0, column=1, padx=(10, 20), pady=20, sticky="nsew")
        form_card.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            form_card,
            text="Catalogue",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#111827",
        )
        title.grid(row=0, column=0, padx=20, pady=(20, 14), sticky="w")

        name_label = ctk.CTkLabel(form_card, text="Nom", text_color="#374151")
        name_label.grid(row=1, column=0, padx=20, pady=(0, 6), sticky="w")

        self.name_entry = ctk.CTkEntry(form_card, height=38, placeholder_text="Ex: Luminaire")
        self.name_entry.grid(row=2, column=0, padx=20, pady=(0, 12), sticky="ew")

        price_label = ctk.CTkLabel(form_card, text="Prix unitaire", text_color="#374151")
        price_label.grid(row=3, column=0, padx=20, pady=(0, 6), sticky="w")

        self.price_entry = ctk.CTkEntry(form_card, height=38, placeholder_text="Ex: 24.20")
        self.price_entry.grid(row=4, column=0, padx=20, pady=(0, 12), sticky="ew")

        buttons_frame = ctk.CTkFrame(form_card, fg_color="transparent")
        buttons_frame.grid(row=5, column=0, padx=20, pady=(6, 12), sticky="ew")
        buttons_frame.grid_columnconfigure((0, 1), weight=1)

        self.add_button = ctk.CTkButton(buttons_frame, text="Ajouter", command=self.add_item)
        self.add_button.grid(row=1, column=0, padx=(0, 6), pady=(10, 6), sticky="ew")

        self.edit_button = ctk.CTkButton(
            buttons_frame,
            text="Modifier",
            fg_color="#2563eb",
            hover_color="#1d4ed8",
            command=self.start_edit_item,
        )
        self.edit_button.grid(row=0, column=1, padx=(6, 0), pady=6, sticky="ew")

        self.validate_button = ctk.CTkButton(
            buttons_frame,
            text="Valider",
            fg_color="#059669",
            hover_color="#047857",
            command=self.update_item,
        )
        self.validate_button.grid(row=0, column=1, padx=(6, 0), pady=6, sticky="ew")

        self.delete_button = ctk.CTkButton(
            buttons_frame,
            text="Supprimer",
            fg_color="#dc2626",
            hover_color="#b91c1c",
            command=self.delete_item,
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

        self._set_form_editable(True)
        self._sync_action_buttons()

    def refresh_items(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for index, item in enumerate(self.catalog_repository.get_all_items()):
            row_tag = "evenrow" if index % 2 == 0 else "oddrow"
            self.tree.insert(
                "",
                tk.END,
                iid=str(item["id"]),
                values=(item["id"], item["nom"], f'{item["prix_unitaire"]:.2f} EUR'),
                tags=(row_tag,),
            )

        self.tree.tag_configure("evenrow", background="#ffffff")
        self.tree.tag_configure("oddrow", background="#f3f4f6")

    def _set_form_editable(self, editable):
        entry_state = "normal" if editable else "readonly"
        self.name_entry.configure(state=entry_state)
        self.price_entry.configure(state=entry_state)

    def _sync_action_buttons(self):
        has_selection = self.selected_item_id is not None

        if has_selection and not self.is_edit_mode:
            self.edit_button.grid()
            self.delete_button.grid()
            self.validate_button.grid_remove()
        elif has_selection and self.is_edit_mode:
            self.edit_button.grid_remove()
            self.delete_button.grid()
            self.validate_button.grid()
        else:
            self.edit_button.grid_remove()
            self.delete_button.grid_remove()
            self.validate_button.grid_remove()

    def add_item(self):
        data = self._get_form_data()
        if data is None:
            return

        try:
            self.catalog_repository.add_item(**data)
        except ValueError as error:
            messagebox.showwarning("Article invalide", str(error))
            return

        self.refresh_items()
        self.clear_form()
        self.on_save_callback()

    def start_edit_item(self):
        if self.selected_item_id is None:
            messagebox.showwarning("Selection requise", "Selectionnez un article a modifier.")
            return

        self.is_edit_mode = True
        self._set_form_editable(True)
        self._sync_action_buttons()

    def update_item(self):
        if self.selected_item_id is None:
            messagebox.showwarning("Selection requise", "Selectionnez un article a modifier.")
            return

        if not self.is_edit_mode:
            messagebox.showwarning("Mode edition", "Cliquez d'abord sur Modifier.")
            return

        data = self._get_form_data()
        if data is None:
            return

        try:
            self.catalog_repository.update_item(self.selected_item_id, **data)
        except ValueError as error:
            messagebox.showwarning("Article invalide", str(error))
            return

        self.refresh_items()
        self.clear_form()
        self.on_save_callback()

    def delete_item(self):
        if self.selected_item_id is None:
            messagebox.showwarning("Selection requise", "Selectionnez un article a supprimer.")
            return

        confirmed = messagebox.askyesno(
            "Confirmation",
            "Voulez-vous vraiment supprimer cet article du catalogue ?",
        )
        if not confirmed:
            return

        self.catalog_repository.delete_item(self.selected_item_id)
        self.refresh_items()
        self.clear_form()
        self.on_save_callback()

    def clear_form(self):
        self.selected_item_id = None
        self.is_edit_mode = False
        self._set_form_editable(True)
        self.name_entry.delete(0, tk.END)
        self.price_entry.delete(0, tk.END)
        self.tree.selection_remove(self.tree.selection())
        self._sync_action_buttons()

    def _get_form_data(self):
        nom = self.name_entry.get().strip()
        prix_text = self.price_entry.get().strip()

        if not nom:
            messagebox.showwarning("Champ requis", "Le nom de l'article est obligatoire.")
            return None

        try:
            prix_unitaire = float(prix_text.replace(",", "."))
        except ValueError:
            messagebox.showwarning("Valeur invalide", "Le prix unitaire doit etre numerique.")
            return None

        if prix_unitaire < 0:
            messagebox.showwarning("Valeur invalide", "Le prix unitaire doit etre positif.")
            return None

        return {"nom": nom, "prix_unitaire": prix_unitaire}

    def _on_item_select(self, _event):
        selected = self.tree.selection()
        if not selected:
            return

        item = self.catalog_repository.get_item_by_id(int(selected[0]))
        if item is None:
            return

        self.selected_item_id = item["id"]
        self.is_edit_mode = False
        self._set_form_editable(True)
        self.name_entry.delete(0, tk.END)
        self.price_entry.delete(0, tk.END)
        self.name_entry.insert(0, item["nom"])
        self.price_entry.insert(0, f'{item["prix_unitaire"]:.2f}')
        self._set_form_editable(False)
        self._sync_action_buttons()

    def _close_dialog(self):
        self.on_save_callback()
        self.destroy()
