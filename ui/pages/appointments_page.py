import customtkinter as ctk


class AppointmentsPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")

        title = ctk.CTkLabel(
            self,
            text="Rendez-vous",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#111827",
        )
        title.pack(anchor="w", padx=30, pady=(30, 10))

        info = ctk.CTkLabel(
            self,
            text="Section prête pour une future implémentation.",
            text_color="#4b5563",
            font=ctk.CTkFont(size=15),
        )
        info.pack(anchor="w", padx=30)
