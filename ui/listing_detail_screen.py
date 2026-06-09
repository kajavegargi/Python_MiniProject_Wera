import os
import customtkinter as ctk
from PIL import Image
from ui.theme import (DEEP_PURPLE, HOT_PINK, ELECTRIC_BLUE, NEON_LIME,
                      LAVENDER, LIGHT_PURPLE, MUTED_PURPLE, WHITE,
                      DARK, LIGHT_GRAY, GRAPE, FONTS)


class ListingDetailScreen(ctk.CTkToplevel):
    """Full-page popup showing all listing details + match request + wishlist."""

    def __init__(self, master, listing, user, on_wishlist_toggle=None):
        super().__init__(master)
        self.listing           = listing
        self.user              = user
        self.on_wishlist_toggle = on_wishlist_toggle

        self.title(listing.title)
        self.geometry("820x680")
        self.configure(fg_color=LAVENDER)
        self.grab_set()
        self.resizable(False, False)
        self._build()

    def _build(self):
        # ── Header bar ────────────────────────────────────────
        header = ctk.CTkFrame(self, fg_color=DEEP_PURPLE, height=56, corner_radius=0)
        header.pack(fill="x")
        header.pack_propagate(False)

        ctk.CTkButton(header, text="✕ Close", width=90, height=32,
                      fg_color="transparent", border_width=1,
                      border_color=MUTED_PURPLE, text_color=MUTED_PURPLE,
                      hover_color="#2D0A4E", font=FONTS["small"], corner_radius=10,
                      command=self.destroy).pack(side="left", padx=16, pady=10)

        ctk.CTkLabel(header, text=self.listing.title,
                     font=("Outfit", 18, "bold"),
                     text_color=WHITE).pack(side="left", padx=8)

        ctk.CTkFrame(self, fg_color=HOT_PINK, height=3,
                     corner_radius=0).pack(fill="x")

        # ── Scrollable body ───────────────────────────────────
        scroll = ctk.CTkScrollableFrame(self, fg_color=LAVENDER)
        scroll.pack(fill="both", expand=True, padx=24, pady=16)

        # Two-column layout
        scroll.grid_columnconfigure(0, weight=2)
        scroll.grid_columnconfigure(1, weight=3)

        # ── Left: image ───────────────────────────────────────
        img_scroll = ctk.CTkScrollableFrame(scroll, fg_color="transparent", width=290, height=400)
        img_scroll.grid(row=0, column=0, padx=(0, 16), pady=8, sticky="n")

        image_paths = [p for p in (self.listing.image_path.split(",") if self.listing.image_path else []) if p]
        
        if image_paths:
            for path in image_paths:
                img_frame = ctk.CTkFrame(img_scroll, fg_color=LIGHT_PURPLE,
                                         width=280, height=320, corner_radius=18)
                img_frame.pack(pady=(0, 12))
                img_frame.pack_propagate(False)
                if os.path.exists(path):
                    try:
                        pil = Image.open(path)
                        pil.thumbnail((280, 320))
                        ctk_img = ctk.CTkImage(light_image=pil, size=(280, 320))
                        ctk.CTkLabel(img_frame, image=ctk_img, text="").place(
                            relx=0.5, rely=0.5, anchor="center")
                    except Exception:
                        self._placeholder(img_frame)
                else:
                    self._placeholder(img_frame)
        else:
            img_frame = ctk.CTkFrame(img_scroll, fg_color=LIGHT_PURPLE,
                                     width=280, height=320, corner_radius=18)
            img_frame.pack()
            img_frame.pack_propagate(False)
            self._placeholder(img_frame)

        # ── Wishlist heart button ─────────────────────────────
        from logic.listings import is_in_wishlist, toggle_wishlist
        saved = is_in_wishlist(self.user.id, self.listing.id)
        self._heart_saved = saved

        self.heart_btn = ctk.CTkButton(
            scroll,
            text="❤  Saved" if saved else "🤍  Save",
            width=130, height=36,
            fg_color=HOT_PINK if saved else WHITE,
            hover_color="#D4245F",
            text_color=WHITE if saved else HOT_PINK,
            border_width=2 if not saved else 0,
            border_color=HOT_PINK,
            font=FONTS["small"], corner_radius=12,
            command=self._toggle_heart,
        )
        self.heart_btn.grid(row=1, column=0, pady=(8, 0), sticky="w")

        # ── Right: details ────────────────────────────────────
        detail = ctk.CTkFrame(scroll, fg_color=WHITE, corner_radius=18,
                              border_width=2, border_color=LIGHT_PURPLE)
        detail.grid(row=0, column=1, rowspan=2, pady=8, sticky="nsew")

        inner = ctk.CTkFrame(detail, fg_color="transparent")
        inner.pack(padx=24, pady=20, fill="both", expand=True)

        # Mode badge
        badge_color = HOT_PINK if self.listing.mode == "sell" else ELECTRIC_BLUE
        badge = ctk.CTkFrame(inner, fg_color=badge_color,
                             corner_radius=8, height=26)
        badge.pack(anchor="w", pady=(0, 8))
        badge.pack_propagate(False)
        ctk.CTkLabel(badge, text=f"  {self.listing.mode.upper()}  ",
                     font=FONTS["tag"], text_color=WHITE).pack(padx=6, pady=2)

        # Title + points
        ctk.CTkLabel(inner, text=self.listing.title,
                     font=("Outfit", 22, "bold"),
                     text_color=DEEP_PURPLE, wraplength=380,
                     justify="left").pack(anchor="w")

        pts = self.listing.points_value or 0
        pts_row = ctk.CTkFrame(inner, fg_color="transparent")
        pts_row.pack(anchor="w", pady=(6, 0))
        ctk.CTkLabel(pts_row, text=f"💎 {pts:.0f} pts",
                     font=("Outfit", 20, "bold"),
                     text_color=ELECTRIC_BLUE).pack(side="left")
        if self.listing.mode == "sell" and self.listing.accepts_money and self.listing.price:
            ctk.CTkLabel(pts_row, text=f"  ·  ₹{self.listing.price:.0f}",
                         font=("Outfit", 16, "bold"),
                         text_color=HOT_PINK).pack(side="left")

        # Divider
        ctk.CTkFrame(inner, fg_color=LIGHT_PURPLE,
                     height=2, corner_radius=1).pack(fill="x", pady=12)

        # Detail grid
        details = [
            ("Category",  self.listing.category  or "—"),
            ("Size",      self.listing.size       or "—"),
            ("Condition", self.listing.condition  or "—"),
            ("Material",  self.listing.material   or "—"),
            ("Worn",      self.listing.wear_label or "—"),
            ("Brand",     self.listing.brand_tier or "—"),
        ]
        if self.listing.mode == "swap":
            swap_type = self.listing.swap_type or "cloth"
            details.append(("Swap for", swap_type.title()))
            if swap_type == "cloth" and self.listing.swap_condition:
                details.append(("Wants",  self.listing.swap_condition))

        grid = ctk.CTkFrame(inner, fg_color="transparent")
        grid.pack(fill="x", anchor="w")
        for label, val in details:
            row = ctk.CTkFrame(grid, fg_color="transparent")
            row.pack(fill="x", pady=3)
            ctk.CTkLabel(row, text=f"{label}:",
                         font=FONTS["small"], text_color=MUTED_PURPLE,
                         width=90, anchor="w").pack(side="left")
            ctk.CTkLabel(row, text=val,
                         font=FONTS["body"], text_color=DARK,
                         anchor="w").pack(side="left")

        # Seller info + rating
        ctk.CTkFrame(inner, fg_color=LIGHT_PURPLE,
                     height=2, corner_radius=1).pack(fill="x", pady=12)

        seller_name = self.listing.seller.name if self.listing.seller else "Unknown"
        seller_city = self.listing.seller.city if self.listing.seller else ""
        seller_id   = self.listing.seller.id   if self.listing.seller else None

        ctk.CTkLabel(inner, text=f"👤  {seller_name}  ·  {seller_city}",
                     font=FONTS["body"], text_color=DEEP_PURPLE).pack(anchor="w")

        if seller_id:
            from logic.reviews import get_seller_reviews
            reviews, avg = get_seller_reviews(seller_id)
            stars = "★" * int(avg) + "☆" * (5 - int(avg))
            rating_text = (f"{stars}  {avg}/5  ({len(reviews)} reviews)"
                           if reviews else "No reviews yet")
            ctk.CTkLabel(inner, text=rating_text,
                         font=FONTS["small"],
                         text_color=NEON_LIME if reviews else MUTED_PURPLE).pack(anchor="w", pady=(2, 0))

        # ── Match request button ──────────────────────────────
        ctk.CTkFrame(inner, fg_color=LIGHT_PURPLE,
                     height=2, corner_radius=1).pack(fill="x", pady=12)

        self.feedback = ctk.CTkLabel(inner, text="",
                                     font=FONTS["small"], text_color=HOT_PINK)
        self.feedback.pack()

        # Don't show match button for your own listing
        if self.listing.seller_id != self.user.id:
            self._build_match_section(inner)
        else:
            ctk.CTkLabel(inner, text="📌 This is your listing",
                         font=FONTS["small"],
                         text_color=MUTED_PURPLE).pack(pady=8)

    def _build_match_section(self, parent):
        listing = self.listing
        pts_val = listing.points_value or 0

        def do_request(payment_type, offer=""):
            from logic.match import send_match_request
            m, msg = send_match_request(listing.id, self.user.id, payment_type, offer)
            color = ELECTRIC_BLUE if m else HOT_PINK
            self.feedback.configure(text=msg, text_color=color)
            if m:
                self.after(1500, self.destroy)

        if listing.mode == "sell":
            ctk.CTkButton(parent,
                          text=f"💎  Pay with Points  ({pts_val:.0f} pts)",
                          width=340, height=46,
                          fg_color=ELECTRIC_BLUE, hover_color="#2C1FBF",
                          text_color=WHITE, font=FONTS["button"], corner_radius=12,
                          command=lambda: do_request("points")).pack(pady=4)

            if listing.accepts_money and listing.price:
                ctk.CTkButton(parent,
                              text=f"₹  Pay with Money  (₹{listing.price:.0f})",
                              width=340, height=46,
                              fg_color=HOT_PINK, hover_color="#D4245F",
                              text_color=WHITE, font=FONTS["button"], corner_radius=12,
                              command=lambda: do_request("money")).pack(pady=4)
        else:
            swap_type = listing.swap_type or "cloth"
            if swap_type == "cloth":
                want_text = listing.swap_condition or "a cloth in return"
                ctk.CTkLabel(parent,
                             text=f"Seller wants: {want_text}",
                             font=FONTS["small"], text_color=MUTED_PURPLE,
                             wraplength=340).pack(pady=(0, 6))

                offer_entry = ctk.CTkEntry(
                    parent,
                    placeholder_text="Describe the cloth you're offering...",
                    width=340, height=44,
                    fg_color=LIGHT_PURPLE, border_color=LIGHT_PURPLE,
                    text_color=DARK, placeholder_text_color=MUTED_PURPLE,
                    corner_radius=12)
                offer_entry.pack(pady=4)

                def send_cloth():
                    offer = offer_entry.get().strip()
                    if not offer:
                        self.feedback.configure(
                            text="⚠ Please describe your offer")
                        return
                    do_request("cloth_swap", offer)

                ctk.CTkButton(parent, text="👗  Send Swap Offer",
                              width=340, height=46,
                              fg_color=ELECTRIC_BLUE, hover_color="#2C1FBF",
                              text_color=WHITE, font=FONTS["button"], corner_radius=12,
                              command=send_cloth).pack(pady=4)
            else:
                ctk.CTkButton(parent,
                              text=f"💎  Pay {pts_val:.0f} pts for Swap",
                              width=340, height=46,
                              fg_color=ELECTRIC_BLUE, hover_color="#2C1FBF",
                              text_color=WHITE, font=FONTS["button"], corner_radius=12,
                              command=lambda: do_request("points_swap")).pack(pady=4)

    def _toggle_heart(self):
        from logic.listings import toggle_wishlist
        saved, msg = toggle_wishlist(self.user.id, self.listing.id)
        self._heart_saved = saved
        self.heart_btn.configure(
            text="❤  Saved" if saved else "🤍  Save",
            fg_color=HOT_PINK if saved else WHITE,
            text_color=WHITE if saved else HOT_PINK,
            border_width=0 if saved else 2,
        )
        if self.on_wishlist_toggle:
            self.on_wishlist_toggle()

    def _placeholder(self, frame):
        ctk.CTkLabel(frame, text="📷", font=("Outfit", 40),
                     text_color=MUTED_PURPLE).place(relx=0.5, rely=0.4, anchor="center")
        ctk.CTkLabel(frame, text="No image", font=FONTS["small"],
                     text_color=MUTED_PURPLE).place(relx=0.5, rely=0.6, anchor="center")