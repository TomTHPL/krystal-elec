import threading

import customtkinter as ctk

try:
    from PIL import Image, ImageChops
except ImportError:  # pragma: no cover - optional dependency fallback
    Image = None
    ImageChops = None

from app_paths import get_app_paths
from database import init_database
from services.updater_service import check_for_update, download_installer, open_installer_location
from version import __version__, GITHUB_REPO
from repositories.appointment_repository import AppointmentRepository
from repositories.catalog_item_repository import CatalogItemRepository
from repositories.client_repository import ClientRepository
from repositories.quote_repository import QuoteRepository
from services.quote_pdf_reportlab_service import QuotePdfService
from ui.pages.appointments_scheduler_page import AppointmentsSchedulerPage
from ui.pages.clients_page import ClientsPage
from ui.pages.home_page import HomePage
from ui.pages.quotes_management_page import QuotesManagementPage
from ui.pages.settings_page import SettingsPage


ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class KrystalElecApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        init_database()
        self.configure(fg_color="#f1f5f9")
        self.app_paths = get_app_paths()

        self.title("Krystal Elec")
        self.geometry("1100x680")
        self.minsize(980, 620)

        self.client_repository = ClientRepository()
        self.quote_repository = QuoteRepository()
        self.catalog_item_repository = CatalogItemRepository()
        self.appointment_repository = AppointmentRepository()
        self.quote_pdf_service = QuotePdfService()
        self.current_page = None
        self.menu_buttons = {}
        self.logo_source_image = None
        self.logo_ctk_image = None

        self.logo_source_image = self._load_logo_image()

        self.grid_columnconfigure(1, weight=1)

        # Vérification des mises à jour en arrière-plan
        threading.Thread(target=self._check_update_async, daemon=True).start()
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()
        self._build_pages_container()
        self.show_page("Accueil")

    def _build_sidebar(self):
        self.sidebar = ctk.CTkFrame(
            self,
            width=260,
            corner_radius=0,
            fg_color="#1c2f45",
            border_width=0,
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        self.sidebar.grid_rowconfigure(2, weight=1)
        self.sidebar.grid_columnconfigure(0, weight=1)

        brand_shell = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        brand_shell.grid(row=0, column=0, padx=16, pady=(16, 14), sticky="ew")
        brand_shell.grid_columnconfigure(0, weight=1)

        brand_card = ctk.CTkFrame(
            brand_shell,
            width=186,
            height=112,
            corner_radius=14,
            fg_color="#f8fafc",
            border_width=1,
            border_color="#c8d6e8",
        )
        brand_card.grid(row=0, column=0, sticky="")
        brand_card.grid_propagate(False)
        brand_card.grid_columnconfigure(0, weight=1)
        brand_card.grid_rowconfigure(0, weight=1)

        if self.logo_source_image is not None:
            logo_size = self._fit_image_size(self.logo_source_image, max_width=152, max_height=84)
            grown_size = (max(1, int(logo_size[0] * 1.5)), max(1, int(logo_size[1] * 1.5)))
            # Keep the enlarged logo inside the white card so rounded borders stay visually intact.
            logo_size = (min(grown_size[0], 160), min(grown_size[1], 96))
            self.logo_ctk_image = ctk.CTkImage(
                light_image=self.logo_source_image,
                dark_image=self.logo_source_image,
                size=logo_size,
            )
            logo_label = ctk.CTkLabel(brand_card, text="", image=self.logo_ctk_image, fg_color="transparent")
            logo_label.place(relx=0.5, rely=0.5, anchor="center")
        else:
            logo_fallback = ctk.CTkLabel(
                brand_card,
                text="Krystal Elec",
                font=ctk.CTkFont(size=22, weight="bold"),
                text_color="#0f172a",
                fg_color="transparent",
            )
            logo_fallback.place(relx=0.5, rely=0.5, anchor="center")

        nav_label = ctk.CTkLabel(
            self.sidebar,
            text="NAVIGATION",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color="#526e8a",
        )
        nav_label.grid(row=1, column=0, padx=20, pady=(6, 6), sticky="w")

        nav_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        nav_frame.grid(row=2, column=0, padx=12, pady=(0, 14), sticky="nsew")
        nav_frame.grid_columnconfigure(0, weight=1)
        nav_frame.grid_rowconfigure(6, weight=1)

        nav_items = [
            ("Accueil",      "⌂   Accueil"),
            ("Clients",      "◈   Clients"),
            ("Devis",        "≡   Devis"),
            ("Rendez-vous",  "⊙   Rendez-vous"),
            ("Paramètres",   "⚙   Paramètres"),
        ]
        for index, (page_name, label) in enumerate(nav_items):
            button = ctk.CTkButton(
                nav_frame,
                text=label,
                height=44,
                corner_radius=10,
                anchor="w",
                border_spacing=14,
                fg_color="#27415c",
                hover_color="#34516f",
                text_color="#8faec9",
                border_width=1,
                border_color="#3a5270",
                font=ctk.CTkFont(size=14, weight="bold"),
                command=lambda name=page_name: self.show_page(name),
            )
            button.grid(row=index, column=0, padx=0, pady=5, sticky="ew")
            self.menu_buttons[page_name] = button

        footer = ctk.CTkLabel(
            self.sidebar,
            text=f"Krystal Elec  ·  v{__version__}",
            font=ctk.CTkFont(size=10),
            text_color="#3f5a74",
        )
        footer.grid(row=3, column=0, padx=22, pady=(0, 18), sticky="sw")

    def _find_logo_path(self):
        assets_dir = self.app_paths.bundle_root / "assets" / "quotes"
        candidates = [
            assets_dir / "logo.png",
            assets_dir / "logo2.png",
            assets_dir / "logo.jpg",
            assets_dir / "logo.jpeg",
            assets_dir / "logo.webp",
            assets_dir / "logo.svg",
        ]
        for path in candidates:
            if path.exists():
                return path
        return None

    def _fit_image_size(self, image, max_width, max_height):
        width, height = image.size
        if width <= 0 or height <= 0:
            return max_width, max_height

        ratio = min(max_width / width, max_height / height)
        return max(1, int(width * ratio)), max(1, int(height * ratio))

    def _trim_logo_image(self, image):
        if ImageChops is None:
            return image

        working_image = image.convert("RGB")
        background = Image.new("RGB", working_image.size, (255, 255, 255))
        difference = ImageChops.difference(working_image, background)
        bbox = difference.getbbox()
        if bbox is None:
            return image
        return image.crop(bbox)

    def _build_pages_container(self):
        self.pages_container = ctk.CTkFrame(
            self,
            fg_color="#eef2f7",
            corner_radius=0,
            border_width=0,
        )
        self.pages_container.grid(row=0, column=1, sticky="nsew")

        self.pages = {
            "Accueil": HomePage(
                self.pages_container,
                self.client_repository,
                self.quote_repository,
                self.appointment_repository,
                on_navigate=self.show_page,
            ),
            "Clients": ClientsPage(self.pages_container, self.client_repository, self.quote_repository),
            "Devis": QuotesManagementPage(
                self.pages_container,
                self.client_repository,
                self.quote_repository,
                self.catalog_item_repository,
                self.quote_pdf_service,
            ),
            "Rendez-vous": AppointmentsSchedulerPage(
                self.pages_container,
                self.client_repository,
                self.appointment_repository,
            ),
            "Paramètres": SettingsPage(self.pages_container),
        }

        self.pages_container.grid_rowconfigure(0, weight=1)
        self.pages_container.grid_columnconfigure(0, weight=1)

        for page in self.pages.values():
            page.grid(row=0, column=0, sticky="nsew")
            page.grid_remove()

    def show_page(self, page_name):
        if self.current_page:
            self.pages[self.current_page].grid_remove()

        self.pages[page_name].grid()
        self.current_page = page_name
        self._update_menu_style(page_name)

        if hasattr(self.pages[page_name], "refresh_clients"):
            self.pages[page_name].refresh_clients()
        if hasattr(self.pages[page_name], "refresh_client_choices"):
            self.pages[page_name].refresh_client_choices()
        if hasattr(self.pages[page_name], "refresh_catalog_choices"):
            self.pages[page_name].refresh_catalog_choices()
        if hasattr(self.pages[page_name], "refresh_quotes"):
            self.pages[page_name].refresh_quotes()
        if hasattr(self.pages[page_name], "refresh_appointments"):
            self.pages[page_name].refresh_appointments()
        if hasattr(self.pages[page_name], "refresh_dashboard"):
            self.pages[page_name].refresh_dashboard()

    def _update_menu_style(self, active_page):
        for page_name, button in self.menu_buttons.items():
            if page_name == active_page:
                button.configure(
                    fg_color="#163554",
                    hover_color="#163554",
                    text_color="#e8f4ff",
                    border_color="#3b82f6",
                    border_width=2,
                )
            else:
                button.configure(
                    fg_color="#27415c",
                    hover_color="#34516f",
                    text_color="#8faec9",
                    border_color="#3a5270",
                    border_width=1,
                )

    def _load_logo_image(self):
        if Image is None:
            return None

        logo_path = self._find_logo_path()
        if logo_path is None:
            return None

        image = Image.open(logo_path)
        return self._trim_logo_image(image)

    def _check_update_async(self):
        available, latest_version, download_url = check_for_update(__version__, GITHUB_REPO)
        if available and download_url:
            self.after(0, lambda: self._show_update_dialog(latest_version, download_url))

    def _show_update_dialog(self, latest_version: str, download_url: str):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Mise à jour disponible")
        dialog.geometry("420x240")
        dialog.resizable(False, False)
        dialog.grab_set()

        ctk.CTkLabel(
            dialog,
            text=f"Nouvelle version disponible : {latest_version}",
            font=ctk.CTkFont(size=14, weight="bold"),
            wraplength=380,
        ).pack(pady=(28, 6))

        status_label = ctk.CTkLabel(
            dialog,
            text="Cliquez sur Télécharger pour récupérer la mise à jour.",
            wraplength=380,
            font=ctk.CTkFont(size=12),
            text_color="#64748b",
        )
        status_label.pack(pady=(0, 16))

        progress_bar = ctk.CTkProgressBar(dialog, width=380)

        def on_progress(ratio):
            if ratio == -1:
                self.after(0, lambda: status_label.configure(text="Erreur lors du téléchargement.", text_color="#dc2626"))
            else:
                progress_bar.pack(pady=(0, 10))
                progress_bar.set(ratio)

        def on_done(path):
            self.after(0, lambda: _show_done(path))

        def _show_done(path):
            progress_bar.pack_forget()
            status_label.configure(
                text=f"Téléchargé dans : {path}\n\nLancez le fichier KrystalElec_Setup.exe pour installer.",
                text_color="#16a34a",
            )
            btn_yes.configure(text="Ouvrir le dossier", state="normal", command=lambda: open_installer_location(path))
            btn_no.configure(text="Fermer")

        def start_download():
            btn_yes.configure(state="disabled")
            btn_no.configure(state="disabled")
            status_label.configure(text="Téléchargement en cours...", text_color="#64748b")
            progress_bar.pack(pady=(0, 10))
            progress_bar.set(0)
            download_installer(
                download_url,
                on_progress=lambda r: self.after(0, lambda: on_progress(r)),
                on_done=on_done,
            )

        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack()
        btn_yes = ctk.CTkButton(btn_frame, text="Télécharger", command=start_download)
        btn_yes.pack(side="left", padx=8)
        btn_no = ctk.CTkButton(btn_frame, text="Plus tard", fg_color="gray", command=dialog.destroy)
        btn_no.pack(side="left", padx=8)
