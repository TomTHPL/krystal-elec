import subprocess
import sys
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk

from services.backup_service import BACKUP_EXTENSION, create_backup, restore_backup, validate_backup
from services.settings_service import get_exports_dir, set_exports_dir


class SettingsPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        self._build()

    def _build(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, padx=30, pady=(26, 8), sticky="ew")
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header,
            text="Paramètres",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#0f172a",
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            header,
            text="Configuration de l'application",
            font=ctk.CTkFont(size=13),
            text_color="#64748b",
        ).grid(row=1, column=0, sticky="w")

        # Carte dossier exports
        exports_card = ctk.CTkFrame(self, fg_color="white", corner_radius=12)
        exports_card.grid(row=1, column=0, padx=30, pady=(16, 0), sticky="ew")
        exports_card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            exports_card,
            text="Dossier des documents générés",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#0f172a",
        ).grid(row=0, column=0, columnspan=2, padx=20, pady=(18, 4), sticky="w")

        ctk.CTkLabel(
            exports_card,
            text="Les devis PDF seront enregistrés dans ce dossier.",
            font=ctk.CTkFont(size=12),
            text_color="#64748b",
        ).grid(row=1, column=0, columnspan=2, padx=20, pady=(0, 12), sticky="w")

        path_frame = ctk.CTkFrame(exports_card, fg_color="#f1f5f9", corner_radius=8)
        path_frame.grid(row=2, column=0, columnspan=2, padx=20, pady=(0, 18), sticky="ew")
        path_frame.grid_columnconfigure(0, weight=1)

        self._path_label = ctk.CTkLabel(
            path_frame,
            text=str(get_exports_dir()),
            font=ctk.CTkFont(size=12),
            text_color="#334155",
            anchor="w",
        )
        self._path_label.grid(row=0, column=0, padx=12, pady=10, sticky="ew")

        btn_frame = ctk.CTkFrame(path_frame, fg_color="transparent")
        btn_frame.grid(row=0, column=1, padx=(0, 8), pady=6)

        ctk.CTkButton(
            btn_frame,
            text="Changer",
            width=90,
            height=32,
            command=self._pick_folder,
        ).pack(side="left", padx=(0, 6))

        ctk.CTkButton(
            btn_frame,
            text="Ouvrir",
            width=80,
            height=32,
            fg_color="#e2e8f0",
            hover_color="#cbd5e1",
            text_color="#334155",
            command=self._open_folder,
        ).pack(side="left")

        self._exports_feedback = ctk.CTkLabel(
            exports_card,
            text="",
            font=ctk.CTkFont(size=12),
            text_color="#16a34a",
        )
        self._exports_feedback.grid(row=3, column=0, columnspan=2, padx=20, pady=(0, 8), sticky="w")

        # Carte sauvegarde
        backup_card = ctk.CTkFrame(self, fg_color="white", corner_radius=12)
        backup_card.grid(row=2, column=0, padx=30, pady=(16, 0), sticky="ew")
        backup_card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            backup_card,
            text="Sauvegarde des données",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#0f172a",
        ).grid(row=0, column=0, padx=20, pady=(18, 4), sticky="w")

        ctk.CTkLabel(
            backup_card,
            text="Exportez ou restaurez l'ensemble de vos données : clients, devis, catalogue et rendez-vous.",
            font=ctk.CTkFont(size=12),
            text_color="#64748b",
            wraplength=600,
            justify="left",
        ).grid(row=1, column=0, padx=20, pady=(0, 16), sticky="w")

        backup_btn_frame = ctk.CTkFrame(backup_card, fg_color="transparent")
        backup_btn_frame.grid(row=2, column=0, padx=20, pady=(0, 18), sticky="w")

        ctk.CTkButton(
            backup_btn_frame,
            text="⬇  Générer une sauvegarde",
            width=210,
            height=38,
            corner_radius=10,
            fg_color="#2563eb",
            hover_color="#1d4ed8",
            command=self._generate_backup,
        ).pack(side="left", padx=(0, 12))

        ctk.CTkButton(
            backup_btn_frame,
            text="⬆  Charger une sauvegarde",
            width=210,
            height=38,
            corner_radius=10,
            fg_color="#e2e8f0",
            hover_color="#cbd5e1",
            text_color="#334155",
            command=self._load_backup,
        ).pack(side="left")

        self._backup_feedback = ctk.CTkLabel(
            backup_card,
            text="",
            font=ctk.CTkFont(size=12),
            text_color="#16a34a",
            wraplength=600,
            justify="left",
        )
        self._backup_feedback.grid(row=3, column=0, padx=20, pady=(0, 8), sticky="w")

    # ------------------------------------------------------------------
    # Dossier exports
    # ------------------------------------------------------------------

    def _pick_folder(self):
        chosen = filedialog.askdirectory(
            initialdir=str(get_exports_dir()),
            title="Choisir le dossier des exports",
        )
        if not chosen:
            return
        set_exports_dir(Path(chosen))
        self._path_label.configure(text=chosen)
        self._exports_feedback.configure(text="✓ Dossier enregistré", text_color="#16a34a")
        self.after(3000, lambda: self._exports_feedback.configure(text=""))

    def _open_folder(self):
        folder = get_exports_dir()
        folder.mkdir(parents=True, exist_ok=True)
        subprocess.Popen(["explorer", str(folder)])

    # ------------------------------------------------------------------
    # Sauvegarde
    # ------------------------------------------------------------------

    def _generate_backup(self):
        destination = filedialog.askdirectory(title="Choisir le dossier de destination de la sauvegarde")
        if not destination:
            return

        try:
            backup_path = create_backup(Path(destination))
        except Exception as exc:
            self._set_backup_feedback(f"✗ Erreur : {exc}", "#dc2626")
            return

        self._set_backup_feedback(f"✓ Sauvegarde enregistrée : {backup_path.name}", "#16a34a")

    def _load_backup(self):
        backup_path_str = filedialog.askopenfilename(
            title="Sélectionner une sauvegarde CrystalElec",
            filetypes=[("Sauvegarde CrystalElec", f"*{BACKUP_EXTENSION}"), ("Tous les fichiers", "*.*")],
        )
        if not backup_path_str:
            return

        backup_path = Path(backup_path_str)

        try:
            manifest = validate_backup(backup_path)
        except ValueError as exc:
            messagebox.showerror(
                "Fichier incompatible",
                f"Impossible de charger cette sauvegarde :\n\n{exc}",
            )
            return

        created_at = manifest.get("created_at", "date inconnue")
        app_version = manifest.get("app_version", "?")

        confirmed = messagebox.askyesno(
            "Confirmer le chargement",
            f"Vous êtes sur le point de charger la sauvegarde :\n\n"
            f"  Fichier : {backup_path.name}\n"
            f"  Créée le : {created_at}\n"
            f"  Version : {app_version}\n\n"
            "⚠  Le chargement de cette sauvegarde remplacera toutes les données actuelles\n"
            "(clients, devis, catalogue, rendez-vous). Ces données seront perdues.\n\n"
            "Voulez-vous continuer ?",
            icon="warning",
        )
        if not confirmed:
            return

        try:
            restore_backup(backup_path)
        except Exception as exc:
            messagebox.showerror("Erreur de restauration", f"La restauration a échoué :\n\n{exc}")
            return

        messagebox.showinfo(
            "Sauvegarde chargée",
            "La sauvegarde a été restaurée avec succès.\n\n"
            "L'application va redémarrer pour appliquer les changements.",
        )
        self._restart_app()

    def _restart_app(self):
        self.winfo_toplevel().destroy()
        subprocess.Popen([sys.executable] + sys.argv)

    def _set_backup_feedback(self, text: str, color: str):
        self._backup_feedback.configure(text=text, text_color=color)
        self.after(5000, lambda: self._backup_feedback.configure(text=""))
