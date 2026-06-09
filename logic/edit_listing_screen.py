import customtkinter as ctk
from ui.theme import (DEEP_PURPLE, HOT_PINK, ELECTRIC_BLUE, NEON_LIME,
                      LAVENDER, LIGHT_PURPLE, MUTED_PURPLE, WHITE,
                      DARK, LIGHT_GRAY, GRAPE, FONTS)
from logic.points import WEAR_LABELS, BRAND_TIERS


class EditListingScreen(ctk.CTkToplevel):
    """Edit an existing listing — updates title, condition, wear, brand, price."""

    def __init__(self, master, listing, user, on_save=None):
        super().__init__(master)
        self.listing = listing
        self.user    = user
        self.on_save = on_save

        self.title("Edit Listing")
        self.geometry("520x600")
        self.configure(fg_color=LAVENDER)
        self.grab_set()
        self.resizable(False, False)
        self._build()

    def _build(self):
        header = ctk.CTkFrame(self, fg_color=DEEP_PURPLE, height=56, corner_radius=0)
        header.pack(fill="x")
        header.pack_propagate(False)

        ctk.CTkButton(header, text="✕ Cancel", width=90, height=32,
                      fg_color="transparent", border_width=1,
                      border_color=MUTED_PURPLE, text_color=MUTED_PURPLE,
                      hover_color="#2D0A4E", font=FONTS["small"], corner_radius=10,
                      command=self.destroy).pack(side="left", padx=16, pady=10)

        ctk.CTkLabel(header, text="✏ Edit Listing",
                     font=("Outfit", 18, "bold"),
                     text_color=WHITE).pack(side="left", padx=8)

        ctk.CTkFrame(self, fg_color=HOT_PINK, height=3,
                     corner_radius=0).pack(fill="x")

        scroll = ctk.CTkScrollableFrame(self, fg_color=LAVENDER)
        scroll.pack(fill="both", expand=True, padx=30, pady=16)

        def label(text):
            ctk.CTkLabel(scroll, text=text, font=FONTS["small"],
                         text_color=MUTED_PURPLE, anchor="w").pack(fill="x", pady=(8, 2))

        # Title
        label("Title")
        self.title_entry = ctk.CTkEntry(scroll, width=440, height=44,
                                        fg_color=LIGHT_PURPLE, border_color=LIGHT_PURPLE,
                                        text_color=DARK, corner_radius=12)
        self.title_entry.insert(0, self.listing.title or "")
        self.title_entry.pack(fill="x")

        # Condition
        label("Condition")
        self.cond_var = ctk.StringVar(value=self.listing.condition or "Good")
        ctk.CTkSegmentedButton(scroll, values=["Like New", "Good", "Fair"],
                               variable=self.cond_var,
                               selected_color=DEEP_PURPLE,
                               unselected_color=LIGHT_PURPLE,
                               font=FONTS["small"],
                               height=38, corner_radius=10).pack(fill="x")

        # Wear label
        label("How often worn")
        self.wear_var = ctk.StringVar(value=self.listing.wear_label or WEAR_LABELS[0])
        ctk.CTkOptionMenu(scroll, values=WEAR_LABELS, variable=self.wear_var,
                          width=440, height=42,
                          fg_color=LIGHT_PURPLE, button_color=DEEP_PURPLE,
                          text_color=DARK, corner_radius=12).pack(fill="x")

        # Brand tier
        label("Brand")
        self.brand_var = ctk.StringVar(value=self.listing.brand_tier or BRAND_TIERS[0])
        ctk.CTkOptionMenu(scroll, values=BRAND_TIERS, variable=self.brand_var,
                          width=440, height=42,
                          fg_color=LIGHT_PURPLE, button_color=DEEP_PURPLE,
                          text_color=DARK, corner_radius=12).pack(fill="x")

        # Price (sell mode only)
        self.price_entry = None
        if self.listing.mode == "sell" and self.listing.accepts_money:
            label("Price (₹)")
            self.price_entry = ctk.CTkEntry(scroll, width=440, height=44,
                                            fg_color=LIGHT_PURPLE, border_color=LIGHT_PURPLE,
                                            text_color=DARK, corner_radius=12)
            self.price_entry.insert(0, str(self.listing.price or ""))
            self.price_entry.pack(fill="x")

        # Swap condition (swap/cloth mode)
        self.swap_entry = None
        if self.listing.mode == "swap" and (self.listing.swap_type or "") == "cloth":
            label("What cloth do you want in return?")
            self.swap_entry = ctk.CTkEntry(scroll, width=440, height=44,
                                           fg_color=LIGHT_PURPLE, border_color=LIGHT_PURPLE,
                                           text_color=DARK, corner_radius=12)
            self.swap_entry.insert(0, self.listing.swap_condition or "")
            self.swap_entry.pack(fill="x")

        self.feedback = ctk.CTkLabel(scroll, text="", font=FONTS["small"],
                                     text_color=HOT_PINK)
        self.feedback.pack(pady=(12, 0))

        ctk.CTkButton(scroll, text="Save Changes ✅",
                      width=440, height=48,
                      fg_color=DEEP_PURPLE, hover_color=GRAPE,
                      text_color=WHITE, font=FONTS["button"], corner_radius=14,
                      command=self._save).pack(pady=(8, 0))

    def _save(self):
        from logic.listings import update_listing
        title = self.title_entry.get().strip()
        if not title:
            self.feedback.configure(text="⚠ Title cannot be empty")
            return

        fields = dict(
            title=title,
            condition=self.cond_var.get(),
            wear_label=self.wear_var.get(),
            brand_tier=self.brand_var.get(),
        )

        if self.price_entry:
            try:
                fields["price"] = float(self.price_entry.get().strip() or 0)
            except ValueError:
                self.feedback.configure(text="⚠ Price must be a number")
                return

        if self.swap_entry:
            fields["swap_condition"] = self.swap_entry.get().strip()

        ok, msg = update_listing(self.listing.id, self.user.id, **fields)
        self.feedback.configure(text=msg,
                                text_color=ELECTRIC_BLUE if ok else HOT_PINK)
        if ok:
            self.after(1200, self.destroy)
            if self.on_save:
                self.after(1300, self.on_save)