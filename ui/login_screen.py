import customtkinter as ctk
from ui.theme import (DEEP_PURPLE, HOT_PINK, ELECTRIC_BLUE, NEON_LIME,
                      LAVENDER, LIGHT_PURPLE, MUTED_PURPLE, WHITE,
                      DARK, LIGHT_GRAY, GRAPE, FONTS)
from logic.auth import login


class LoginScreen(ctk.CTkFrame):
    def __init__(self, master, on_login, on_register):
        super().__init__(master, fg_color=LAVENDER)
        self.on_login    = on_login
        self.on_register = on_register
        self._build()

    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self._build_brand_panel()
        self._build_form_panel()

    # ── Left brand panel ──────────────────────────────────────
    def _build_brand_panel(self):
        panel = ctk.CTkFrame(self, fg_color=DEEP_PURPLE, corner_radius=0)
        panel.grid(row=0, column=0, sticky="nsew")

        ctk.CTkLabel(panel, text="WERA",
                     font=("Outfit", 72, "bold"),
                     text_color=WHITE).pack(pady=(80, 0))

        tag_frame = ctk.CTkFrame(panel, fg_color=HOT_PINK, corner_radius=40, height=36)
        tag_frame.pack(pady=(10, 0))
        tag_frame.pack_propagate(False)
        ctk.CTkLabel(tag_frame, text="  Swap. Style. Sustain.  ",
                     font=FONTS["subhead"], text_color=WHITE).pack(padx=16, pady=6)

        deco = ctk.CTkFrame(panel, fg_color=NEON_LIME, corner_radius=40, height=28)
        deco.pack(pady=(16, 0))
        deco.pack_propagate(False)
        ctk.CTkLabel(deco, text="  India's peer-to-peer fashion resale  ",
                     font=FONTS["small"], text_color=DARK).pack(padx=12, pady=4)

        stats = ctk.CTkFrame(panel, fg_color="#2D0A4E", corner_radius=16)
        stats.pack(padx=40, pady=(60, 0), fill="x")
        for label, val in [("listings", "2,400+"), ("cities", "2"), ("swaps", "500+")]:
            col = ctk.CTkFrame(stats, fg_color="transparent")
            col.pack(side="left", expand=True, pady=20)
            ctk.CTkLabel(col, text=val,
                         font=("Outfit", 22, "bold"),
                         text_color=NEON_LIME).pack()
            ctk.CTkLabel(col, text=label,
                         font=FONTS["small"],
                         text_color=MUTED_PURPLE).pack()

        ctk.CTkFrame(panel, fg_color=HOT_PINK, height=6,
                     corner_radius=0).pack(side="bottom", fill="x")

    # ── Right form panel ──────────────────────────────────────
    def _build_form_panel(self):
        panel = ctk.CTkFrame(self, fg_color=LAVENDER, corner_radius=0)
        panel.grid(row=0, column=1, sticky="nsew")
        panel.grid_rowconfigure(0, weight=1)
        panel.grid_columnconfigure(0, weight=1)

        card = ctk.CTkFrame(panel, fg_color=WHITE,
                            corner_radius=24,
                            border_width=2, border_color=LIGHT_PURPLE)
        card.grid(row=0, column=0, padx=60, pady=60, sticky="nsew")
        card.grid_rowconfigure(0, weight=1)
        card.grid_columnconfigure(0, weight=1)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(inner, text="Welcome back 👋",
                     font=("Outfit", 28, "bold"),
                     text_color=DEEP_PURPLE).pack(pady=(0, 4))
        ctk.CTkLabel(inner, text="Log in to your Wera account",
                     font=FONTS["small"], text_color=MUTED_PURPLE).pack(pady=(0, 30))

        self.email_entry = self._field(inner, "✉  Email")
        self.pass_entry  = self._field(inner, "🔒  Password", show="*")

        # Bind Enter key on both fields
        self.email_entry.bind("<Return>", lambda e: self._login())
        self.pass_entry.bind("<Return>",  lambda e: self._login())

        self.error_label = ctk.CTkLabel(inner, text="",
                                        text_color=HOT_PINK,
                                        font=FONTS["small"])
        self.error_label.pack(pady=(4, 0))

        ctk.CTkButton(inner, text="Log In →", width=320, height=48,
                      fg_color=DEEP_PURPLE, hover_color=GRAPE,
                      text_color=WHITE, font=FONTS["button"],
                      corner_radius=14,
                      command=self._login).pack(pady=(12, 0))

        sep_frame = ctk.CTkFrame(inner, fg_color="transparent")
        sep_frame.pack(fill="x", pady=(20, 0))
        ctk.CTkFrame(sep_frame, fg_color=LIGHT_GRAY, height=1).pack(fill="x")
        ctk.CTkLabel(sep_frame, text="Don't have an account?",
                     font=FONTS["small"], text_color=MUTED_PURPLE).pack(pady=8)

        ctk.CTkButton(inner, text="Create Account ✨", width=320, height=48,
                      fg_color=HOT_PINK, hover_color="#D4245F",
                      text_color=WHITE, font=FONTS["button"],
                      corner_radius=14,
                      command=self.on_register).pack()

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
        e.pack(pady=8)
        return e

    def _login(self):
        # Clear previous error
        self.error_label.configure(text="")

        email    = self.email_entry.get().strip()
        password = self.pass_entry.get()

        if not email:
            self.error_label.configure(text="⚠ Please enter your email")
            self.email_entry.focus()
            return
        if not password:
            self.error_label.configure(text="⚠ Please enter your password")
            self.pass_entry.focus()
            return

        ok, result = login(email, password)
        if ok:
            self.on_login(result)
        else:
            # Wrong credentials — show error, clear password, allow retry
            self.error_label.configure(text=f"⚠ {result}")
            self.pass_entry.delete(0, "end")
            self.pass_entry.focus()