from pathlib import Path
from tkinter import filedialog

import customtkinter as ctk

from services.settings_service import get_exports_dir, set_exports_dir


class SettingsPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        self._build()

    def _build(self):
        # En-tête
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
        card = ctk.CTkFrame(self, fg_color="white", corner_radius=12)
        card.grid(row=1, column=0, padx=30, pady=(16, 0), sticky="ew")
        card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            card,
            text="Dossier des documents générés",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#0f172a",
        ).grid(row=0, column=0, columnspan=2, padx=20, pady=(18, 4), sticky="w")

        ctk.CTkLabel(
            card,
            text="Les devis PDF seront enregistrés dans ce dossier.",
            font=ctk.CTkFont(size=12),
            text_color="#64748b",
        ).grid(row=1, column=0, columnspan=2, padx=20, pady=(0, 12), sticky="w")

        path_frame = ctk.CTkFrame(card, fg_color="#f1f5f9", corner_radius=8)
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

        self._feedback = ctk.CTkLabel(
            card,
            text="",
            font=ctk.CTkFont(size=12),
            text_color="#16a34a",
        )
        self._feedback.grid(row=3, column=0, columnspan=2, padx=20, pady=(0, 8), sticky="w")

    def _pick_folder(self):
        chosen = filedialog.askdirectory(initialdir=str(get_exports_dir()), title="Choisir le dossier des exports")
        if not chosen:
            return
        set_exports_dir(Path(chosen))
        self._path_label.configure(text=chosen)
        self._feedback.configure(text="✓ Dossier enregistré", text_color="#16a34a")
        self.after(3000, lambda: self._feedback.configure(text=""))

    def _open_folder(self):
        import subprocess
        folder = get_exports_dir()
        folder.mkdir(parents=True, exist_ok=True)
        subprocess.Popen(["explorer", str(folder)])
