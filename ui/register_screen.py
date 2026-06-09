import re
import customtkinter as ctk
from ui.theme import (DEEP_PURPLE, HOT_PINK, ELECTRIC_BLUE, NEON_LIME,
                      LAVENDER, LIGHT_PURPLE, MUTED_PURPLE, WHITE,
                      DARK, LIGHT_GRAY, GRAPE, FONTS)
from logic.auth import register as auth_register

COLLEGES = {
    "Pune": [
        "Symbiosis Institute of Technology",
        "College of Engineering Pune (COEP)",
        "MIT World Peace University",
        "Savitribai Phule Pune University",
        "Fergusson College",
        "Modern College of Arts, Science & Commerce",
        "Bharati Vidyapeeth",
        "Indira College of Engineering",
        "Other / Working Professional",
    ],
    "Mumbai": [
        "IIT Bombay",
        "NMIMS Mumbai",
        "St. Xavier's College Mumbai",
        "SNDT Women's University",
        "University of Mumbai",
        "Narsee Monjee College",
        "HR College of Commerce",
        "Jai Hind College",
        "Other / Working Professional",
    ],
}


class RegisterScreen(ctk.CTkFrame):
    def __init__(self, master, on_success, on_back):
        super().__init__(master, fg_color=LAVENDER)
        self.on_success = on_success
        self.on_back    = on_back
        self._build()

    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self._build_brand_panel()
        self._build_form_panel()

    # ── Left panel ────────────────────────────────────────────
    def _build_brand_panel(self):
        panel = ctk.CTkFrame(self, fg_color=DEEP_PURPLE, corner_radius=0)
        panel.grid(row=0, column=0, sticky="nsew")

        ctk.CTkLabel(panel, text="WERA",
                     font=("Outfit", 72, "bold"),
                     text_color=WHITE).pack(pady=(80, 0))

        dots = ctk.CTkFrame(panel, fg_color="transparent")
        dots.pack(pady=20)
        for color in [HOT_PINK, NEON_LIME, ELECTRIC_BLUE, WHITE]:
            ctk.CTkFrame(dots, fg_color=color,
                         width=14, height=14,
                         corner_radius=7).pack(side="left", padx=6)

        ctk.CTkLabel(panel,
                     text="Join the circular\nfashion revolution.",
                     font=("Outfit", 22, "bold"),
                     text_color=NEON_LIME,
                     justify="center").pack(pady=(20, 0))

        ctk.CTkLabel(panel,
                     text="Buy, sell & swap preloved clothes\nwith students & young professionals\nacross Pune & Mumbai.",
                     font=FONTS["body"],
                     text_color=MUTED_PURPLE,
                     justify="center").pack(pady=(14, 0))

        features = ["♻  Zero waste fashion",
                    "💸  Earn from your wardrobe",
                    "🔄  Swap & refresh your style"]
        pill_frame = ctk.CTkFrame(panel, fg_color="transparent")
        pill_frame.pack(pady=(36, 0))
        for feat in features:
            p = ctk.CTkFrame(pill_frame, fg_color="#2D0A4E", corner_radius=20)
            p.pack(fill="x", pady=5, padx=30)
            ctk.CTkLabel(p, text=feat,
                         font=FONTS["small"],
                         text_color=WHITE).pack(padx=18, pady=8)

        ctk.CTkFrame(panel, fg_color=NEON_LIME, height=6,
                     corner_radius=0).pack(side="bottom", fill="x")

    # ── Right form panel ──────────────────────────────────────
    def _build_form_panel(self):
        panel = ctk.CTkFrame(self, fg_color=LAVENDER, corner_radius=0)
        panel.grid(row=0, column=1, sticky="nsew")

        scroll = ctk.CTkScrollableFrame(panel, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=50, pady=40)

        card = ctk.CTkFrame(scroll, fg_color=WHITE,
                            corner_radius=24,
                            border_width=2, border_color=LIGHT_PURPLE)
        card.pack(fill="x")

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(padx=40, pady=(32, 36))

        ctk.CTkLabel(inner, text="Create Account ✨",
                     font=("Outfit", 26, "bold"),
                     text_color=DEEP_PURPLE).pack(pady=(0, 4))
        ctk.CTkLabel(inner, text="Join the Wera community today",
                     font=FONTS["small"], text_color=MUTED_PURPLE).pack(pady=(0, 24))

        self.name_entry  = self._field(inner, "👤  Full Name")
        self.email_entry = self._field(inner, "✉  Email")

        # ── City selector ──────────────────────────────────────
        self._section_label(inner, "📍 City")
        self.city_var = ctk.StringVar(value="Pune")
        ctk.CTkSegmentedButton(
            inner, values=["Pune", "Mumbai"],
            variable=self.city_var,
            width=320, height=40,
            selected_color=DEEP_PURPLE,
            unselected_color=LIGHT_PURPLE,
            font=FONTS["button"],
            corner_radius=12,
            command=self._on_city_change,
        ).pack(pady=(4, 10))

        # ── College dropdown (updates when city changes) ───────
        self._section_label(inner, "🏫 College / Company")
        self.college_var = ctk.StringVar(value=COLLEGES["Pune"][0])
        self.college_menu = ctk.CTkOptionMenu(
            inner,
            values=COLLEGES["Pune"],
            variable=self.college_var,
            width=320, height=46,
            fg_color=LIGHT_PURPLE,
            button_color=DEEP_PURPLE,
            text_color=DARK,
            dropdown_fg_color=WHITE,
            dropdown_text_color=DARK,
            dropdown_hover_color=LIGHT_PURPLE,
            corner_radius=12,
        )
        self.college_menu.pack(pady=7)

        self.pass_entry = self._field(inner, "🔒  Password", show="*")

        self.error_label = ctk.CTkLabel(inner, text="",
                                        text_color=HOT_PINK,
                                        font=FONTS["small"])
        self.error_label.pack(pady=(4, 0))

        ctk.CTkButton(inner, text="Sign Up →", width=320, height=48,
                      fg_color=HOT_PINK, hover_color="#D4245F",
                      text_color=WHITE, font=FONTS["button"],
                      corner_radius=14,
                      command=self._do_register).pack(pady=(14, 0))

        ctk.CTkButton(inner, text="← Back to Login",
                      width=320, height=38,
                      fg_color="transparent",
                      text_color=MUTED_PURPLE,
                      hover_color=LIGHT_PURPLE,
                      font=FONTS["small"],
                      corner_radius=14,
                      command=self.on_back).pack(pady=(10, 0))

    def _on_city_change(self, city):
        """Swap college options when user switches city."""
        options = COLLEGES[city]
        self.college_var.set(options[0])
        self.college_menu.configure(values=options)

    def _field(self, parent, placeholder, show=None):
        kwargs = {"show": show} if show else {}
        e = ctk.CTkEntry(parent, placeholder_text=placeholder,
                         width=320, height=46,
                         border_color=LIGHT_PURPLE,
                         fg_color=LIGHT_PURPLE,
                         text_color=DARK,
                         placeholder_text_color=MUTED_PURPLE,
                         corner_radius=12,
                         **kwargs)
        e.pack(pady=7)
        return e

    def _section_label(self, parent, text):
        ctk.CTkLabel(parent, text=text,
                     font=FONTS["small"],
                     text_color=MUTED_PURPLE,
                     anchor="w").pack(fill="x", pady=(4, 0))

    def _do_register(self):
        self.error_label.configure(text="")

        name     = self.name_entry.get().strip()
        email    = self.email_entry.get().strip()
        college  = self.college_var.get()
        city     = self.city_var.get()
        password = self.pass_entry.get()

        if not name:
            self.error_label.configure(text="⚠ Please enter your name")
            return
        if not email:
            self.error_label.configure(text="⚠ Please enter your email")
            return
        if not college:
            self.error_label.configure(text="⚠ Please select your college / company")
            return
        if not password:
            self.error_label.configure(text="⚠ Please enter a password")
            return
        if len(password) < 8:
            self.error_label.configure(text="⚠ Password must be at least 8 characters")
            return
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>_\-+=~`\[\]\\\/;']", password):
            self.error_label.configure(text="⚠ Password must include at least one special character")
            return

        ok, result = auth_register(name, email, password, city, college)
        if ok:
            self.on_success(result)
        else:
            self.error_label.configure(text=f"⚠ {result}")