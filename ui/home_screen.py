import os
import customtkinter as ctk
from PIL import Image


from ui.theme import (DEEP_PURPLE, HOT_PINK, ELECTRIC_BLUE, NEON_LIME,
                      LAVENDER, LIGHT_PURPLE, MUTED_PURPLE, WHITE,
                      DARK, LIGHT_GRAY, GRAPE, FONTS)
from logic.listings import browse_listings
from logic.points import calculate_points, WEAR_LABELS, BRAND_TIERS
from database.db_example import get_session
from database.models import User as UserModel

UPLOAD_DIR = "assets/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


class HomeScreen(ctk.CTkFrame):
    def __init__(self, master, user, on_logout):
        super().__init__(master, fg_color=LAVENDER)
        self.user       = user
        self.on_logout  = on_logout
        self.active_tab = "browse"
        self._build()

    def _build(self):
        self._build_navbar()
        self._build_body()

    # ── Helpers ───────────────────────────────────────────────
    def _get_points(self) -> float:
        """Fetch user's current points balance fresh from DB."""
        try:
            db = get_session()
            u  = db.query(UserModel).get(self.user.id)
            return (u.points_balance or 0) if u else 0
        except Exception:
            return 0

    # ── Navbar ────────────────────────────────────────────────
    def _build_navbar(self):
        nav = ctk.CTkFrame(self, fg_color=DEEP_PURPLE, height=60, corner_radius=0)
        nav.pack(fill="x")
        nav.pack_propagate(False)

        # Logo
        logo_frame = ctk.CTkFrame(nav, fg_color="transparent")
        logo_frame.pack(side="left", padx=20)
        ctk.CTkLabel(logo_frame, text="WERA",
                     font=("Outfit", 26, "bold"), text_color=WHITE).pack(side="left")
        ctk.CTkFrame(logo_frame, fg_color=HOT_PINK,
                     width=8, height=8, corner_radius=4).pack(
                         side="left", padx=4, pady=(0, 14))

        right = ctk.CTkFrame(nav, fg_color="transparent")
        right.pack(side="right", padx=16)

        ctk.CTkButton(right, text="Logout", width=80, height=32,
                      fg_color="transparent",
                      border_width=1, border_color=MUTED_PURPLE,
                      text_color=MUTED_PURPLE, hover_color="#2D0A4E",
                      font=FONTS["small"], corner_radius=10,
                      command=self.on_logout).pack(side="right", padx=(8, 0))

        ctk.CTkButton(right, text="👤 Profile", width=100, height=36,
                      fg_color=ELECTRIC_BLUE, hover_color="#2C1FBF",
                      text_color=WHITE, font=FONTS["small"],
                      corner_radius=10,
                      command=self._open_profile).pack(side="right", padx=8)

        ctk.CTkButton(right, text="💬 Matches & Chat",
                      width=150, height=36,
                      fg_color=HOT_PINK, hover_color="#D4245F",
                      text_color=WHITE, font=FONTS["small"],
                      corner_radius=10,
                      command=self._open_matches).pack(side="right", padx=8)

        # Points balance pill
        pts = self._get_points()
        pts_pill = ctk.CTkFrame(right, fg_color="#1A0A2E", corner_radius=20, height=34)
        pts_pill.pack(side="right", padx=(0, 4))
        pts_pill.pack_propagate(False)
        ctk.CTkLabel(pts_pill, text=f"  💎 {pts:.0f} pts  ",
                     font=FONTS["small"], text_color=NEON_LIME).pack(padx=8, pady=4)

        # User pill
        pill = ctk.CTkFrame(right, fg_color="#2D0A4E", corner_radius=20, height=34)
        pill.pack(side="right", padx=(0, 8))
        pill.pack_propagate(False)
        ctk.CTkLabel(pill,
                     text=f"  👋 {self.user.name}  ·  {self.user.city}  ",
                     font=FONTS["small"], text_color=NEON_LIME).pack(padx=10, pady=4)

        ctk.CTkFrame(self, fg_color=HOT_PINK, height=3, corner_radius=0).pack(fill="x")

    def _open_matches(self):
        from ui.match_screen import MatchScreen
        for w in self.master.winfo_children():
            w.destroy()
        MatchScreen(self.master, user=self.user,
                    on_back=self._restore_home).pack(fill="both", expand=True)

    def _restore_home(self):
        for w in self.master.winfo_children():
            w.destroy()
        HomeScreen(self.master, user=self.user,
                   on_logout=self.on_logout).pack(fill="both", expand=True)

    # ── Body / tabs ───────────────────────────────────────────
    def _build_body(self):
        self.body = ctk.CTkFrame(self, fg_color=LAVENDER, corner_radius=0)
        self.body.pack(fill="both", expand=True)
        self._show_tab("browse")

    def _show_tab(self, tab):
        self.active_tab = tab
        for w in self.body.winfo_children():
            w.destroy()
        self._build_tabs()
        if tab == "browse":
            self._build_browse()
        elif tab == "sell":
            self._build_sell()
        elif tab == "mylistings":
            self._build_mylistings()
        elif tab == "wishlist":
            self._build_wishlist()

    def _build_tabs(self):
        bar = ctk.CTkFrame(self.body, fg_color=WHITE, height=50, corner_radius=0)
        bar.pack(fill="x")
        bar.pack_propagate(False)
        for key, label in [("browse", "🔍 Browse"),
                            ("sell",   "🏷 Sell / Swap"),
                            ("mylistings", "👗 My Listings"),
                            ("wishlist", "❤ Wishlist")]:
            is_active = self.active_tab == key
            ctk.CTkButton(bar, text=label, width=180, height=50,
                          fg_color=DEEP_PURPLE if is_active else WHITE,
                          text_color=WHITE if is_active else MUTED_PURPLE,
                          hover_color=LIGHT_PURPLE if not is_active else GRAPE,
                          corner_radius=0, font=FONTS["button"],
                          command=lambda t=key: self._show_tab(t)).pack(side="left")
        ctk.CTkFrame(self.body, fg_color=NEON_LIME, height=3, corner_radius=0).pack(fill="x")

    # ═══════════════════════════════════════════════════════════
    # BROWSE TAB
    # ═══════════════════════════════════════════════════════════
    def _build_browse(self):
        filter_bar = ctk.CTkFrame(self.body, fg_color=WHITE, height=56, corner_radius=0)
        filter_bar.pack(fill="x")
        filter_bar.pack_propagate(False)

        def flabel(text):
            ctk.CTkLabel(filter_bar, text=text,
                         font=FONTS["tag"], text_color=MUTED_PURPLE).pack(
                             side="left", padx=(16, 4))

        flabel("MODE")
        self.mode_var = ctk.StringVar(value="all")
        ctk.CTkSegmentedButton(filter_bar, values=["all", "sell", "swap"],
                               variable=self.mode_var, width=200, height=32,
                               selected_color=DEEP_PURPLE,
                               unselected_color=LIGHT_PURPLE,
                               font=FONTS["small"], corner_radius=10,
                               command=self._apply_filters).pack(side="left", padx=8)

        flabel("SIZE")
        self.size_var = ctk.StringVar(value="all")
        ctk.CTkOptionMenu(filter_bar, values=["all", "XS", "S", "M", "L", "XL"],
                          variable=self.size_var, fg_color=LIGHT_PURPLE,
                          button_color=DEEP_PURPLE, text_color=DARK,
                          width=90, corner_radius=10,
                          command=self._apply_filters).pack(side="left", padx=4)

        flabel("CATEGORY")
        self.cat_var = ctk.StringVar(value="all")
        ctk.CTkOptionMenu(filter_bar,
                          values=["all", "tops", "dresses", "bottoms",
                                  "outerwear", "ethnic", "accessories"],
                          variable=self.cat_var, fg_color=LIGHT_PURPLE,
                          button_color=DEEP_PURPLE, text_color=DARK,
                          width=140, corner_radius=10,
                          command=self._apply_filters).pack(side="left", padx=4)

        self.scroll = ctk.CTkScrollableFrame(self.body, fg_color=LAVENDER)
        self.scroll.pack(fill="both", expand=True, padx=20, pady=16)
        self._load_listings()

    def _apply_filters(self, _=None):
        for w in self.scroll.winfo_children():
            w.destroy()
        self._load_listings()

    def _load_listings(self):
        mode = self.mode_var.get()
        size = self.size_var.get()
        cat  = self.cat_var.get()
        listings = browse_listings(
            mode=None if mode == "all" else mode,
            size=None if size == "all" else size,
            category=None if cat == "all" else cat,
            exclude_user_id=self.user.id,
        )
        if not listings:
            ctk.CTkLabel(self.scroll,
                         text="🌀  No listings found yet!\nBe the first to list something.",
                         font=FONTS["body"], text_color=MUTED_PURPLE,
                         justify="center").pack(pady=80)
            return
        for i, listing in enumerate(listings):
            row, col = divmod(i, 3)
            self._listing_card(self.scroll, listing, row, col)

    def _listing_card(self, parent, listing, row, col):
        card = ctk.CTkFrame(parent, fg_color=WHITE, corner_radius=20,
                            border_width=2, border_color=LIGHT_PURPLE)
        card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        parent.grid_columnconfigure(col, weight=1)

        # ── Thumbnail ─────────────────────────────────────────
        img_frame = ctk.CTkFrame(card, fg_color=LIGHT_PURPLE,
                                 width=220, height=200, corner_radius=14)
        img_frame.pack(padx=12, pady=(12, 0))
        img_frame.pack_propagate(False)

        first_img_path = listing.image_path.split(",")[0] if listing.image_path else ""
        if first_img_path and os.path.exists(first_img_path):
            try:
                pil_img = Image.open(first_img_path)
                pil_img.thumbnail((220, 200))
                ctk_img = ctk.CTkImage(light_image=pil_img, size=(220, 200))
                ctk.CTkLabel(img_frame, image=ctk_img, text="").place(
                    relx=0.5, rely=0.5, anchor="center")
            except Exception:
                self._no_image_placeholder(img_frame)
        else:
            self._no_image_placeholder(img_frame)

        # ── Mode badge ────────────────────────────────────────
        badge_color = HOT_PINK if listing.mode == "sell" else ELECTRIC_BLUE
        badge = ctk.CTkFrame(card, fg_color=badge_color, corner_radius=8, height=26)
        badge.pack(anchor="ne", padx=10, pady=6)
        badge.pack_propagate(False)
        ctk.CTkLabel(badge, text=f"  {listing.mode.upper()}  ",
                     font=FONTS["tag"], text_color=WHITE).pack(padx=6, pady=2)

        # ── Title ─────────────────────────────────────────────
        ctk.CTkLabel(card, text=listing.title,
                     font=FONTS["subhead"], text_color=DEEP_PURPLE,
                     wraplength=200).pack(anchor="w", padx=14, pady=(2, 2))

        # ── Meta chips ────────────────────────────────────────
        meta = ctk.CTkFrame(card, fg_color="transparent")
        meta.pack(anchor="w", padx=14, pady=(0, 4))
        for chip_text in [listing.category or "—",
                          f"Size {listing.size or '—'}",
                          listing.condition or "—"]:
            chip = ctk.CTkFrame(meta, fg_color=LIGHT_PURPLE,
                                corner_radius=8, height=22)
            chip.pack(side="left", padx=(0, 4))
            chip.pack_propagate(False)
            ctk.CTkLabel(chip, text=f" {chip_text} ",
                         font=FONTS["tag"], text_color=DEEP_PURPLE).pack(padx=6, pady=2)

        # ── Points value (always shown) ───────────────────────
        pts_val = listing.points_value or 0
        pts_row = ctk.CTkFrame(card, fg_color="transparent")
        pts_row.pack(anchor="w", padx=14, pady=(4, 2))

        ctk.CTkLabel(pts_row, text=f"💎 {pts_val:.0f} pts",
                     font=("Outfit", 18, "bold"),
                     text_color=ELECTRIC_BLUE).pack(side="left")

        if listing.mode == "sell" and listing.accepts_money and listing.price:
            ctk.CTkLabel(pts_row, text=f"  ·  ₹{listing.price:.0f}",
                         font=("Outfit", 15, "bold"),
                         text_color=HOT_PINK).pack(side="left")

        # ── Swap-specific info ────────────────────────────────
        if listing.mode == "swap":
            swap_type = listing.swap_type or "cloth"
            if swap_type == "cloth":
                label_text = "↔  Cloth Swap"
                if listing.swap_condition:
                    label_text += f"  ·  Wants: {listing.swap_condition}"
            else:
                label_text = f"↔  Swap for {pts_val:.0f} pts"
            ctk.CTkLabel(card, text=label_text,
                         font=FONTS["small"], text_color=MUTED_PURPLE,
                         wraplength=200).pack(anchor="w", padx=14, pady=(0, 2))

        # ── Seller info ───────────────────────────────────────
        seller_name = listing.seller.name if listing.seller else "Unknown"
        seller_city = listing.seller.city if listing.seller else ""
        ctk.CTkLabel(card, text=f"by {seller_name}  ·  {seller_city}",
                     font=FONTS["small"], text_color=MUTED_PURPLE).pack(
                         anchor="w", padx=14, pady=(2, 6))

        btn_row = ctk.CTkFrame(card, fg_color="transparent")
        btn_row.pack(fill="x", padx=14, pady=(4, 14))

        ctk.CTkButton(btn_row, text="👁 View Details",
                      fg_color=DEEP_PURPLE, hover_color=GRAPE,
                      text_color=WHITE, font=FONTS["small"], height=38,
                      corner_radius=12,
                      command=lambda l=listing: self._open_detail(l)).pack(
                          side="left", fill="x", expand=True, padx=(0, 4))

        from logic.listings import is_in_wishlist
        saved = is_in_wishlist(self.user.id, listing.id)
        heart = "❤" if saved else "🤍"
        ctk.CTkButton(btn_row, text=heart, width=38, height=38,
                      fg_color=HOT_PINK if saved else LIGHT_PURPLE,
                      hover_color="#D4245F",
                      text_color=WHITE if saved else HOT_PINK,
                      font=("Outfit", 16), corner_radius=12,
                      command=lambda l=listing: self._quick_wishlist(l)).pack(side="left")

    def _no_image_placeholder(self, frame):
        ctk.CTkLabel(frame, text="📷", font=("Outfit", 32),
                     text_color=MUTED_PURPLE).place(relx=0.5, rely=0.4, anchor="center")
        ctk.CTkLabel(frame, text="No image", font=FONTS["small"],
                     text_color=MUTED_PURPLE).place(relx=0.5, rely=0.65, anchor="center")

    # ── Match request popup ───────────────────────────────────
    def _send_match(self, listing):
        from logic.match import send_match_request

        popup = ctk.CTkToplevel(self)
        popup.title("Match Request")
        popup.configure(fg_color=LAVENDER)
        popup.grab_set()

        ctk.CTkLabel(popup, text="💌 Send Match Request",
                     font=("Outfit", 20, "bold"),
                     text_color=DEEP_PURPLE).pack(pady=(24, 2))
        ctk.CTkLabel(popup, text=listing.title,
                     font=FONTS["subhead"],
                     text_color=MUTED_PURPLE).pack()

        feedback = ctk.CTkLabel(popup, text="",
                                font=FONTS["small"], text_color=HOT_PINK)
        feedback.pack(pady=(8, 0))

        inner = ctk.CTkFrame(popup, fg_color="transparent")
        inner.pack(padx=24, pady=10, fill="x")

        pts_val = listing.points_value or 0

        def do_request(pt, offer=""):
            m, msg = send_match_request(listing.id, self.user.id, pt, offer)
            color = ELECTRIC_BLUE if m else HOT_PINK
            feedback.configure(text=msg, text_color=color)
            if m:
                popup.after(1500, popup.destroy)

        # ── Sell listing ──────────────────────────────────────
        if listing.mode == "sell":
            ctk.CTkLabel(inner, text="Choose how you'd like to pay:",
                         font=FONTS["body"], text_color=DARK).pack(pady=(0, 8))

            ctk.CTkButton(inner,
                          text=f"💎  Pay with Points  ({pts_val:.0f} pts)",
                          width=320, height=46,
                          fg_color=ELECTRIC_BLUE, hover_color="#2C1FBF",
                          text_color=WHITE, font=FONTS["button"], corner_radius=12,
                          command=lambda: do_request("points")).pack(pady=4)

            if listing.accepts_money and listing.price:
                ctk.CTkButton(inner,
                              text=f"₹  Pay with Money  (₹{listing.price:.0f})",
                              width=320, height=46,
                              fg_color=HOT_PINK, hover_color="#D4245F",
                              text_color=WHITE, font=FONTS["button"], corner_radius=12,
                              command=lambda: do_request("money")).pack(pady=4)

        # ── Swap listing ──────────────────────────────────────
        else:
            swap_type = listing.swap_type or "cloth"

            if swap_type == "cloth":
                want_text = listing.swap_condition or "a cloth in return"
                ctk.CTkLabel(inner,
                             text=f"Seller is looking for:\n{want_text}",
                             font=FONTS["body"], text_color=DARK,
                             wraplength=320, justify="center").pack(pady=(0, 8))

                offer_entry = ctk.CTkEntry(
                    inner,
                    placeholder_text="Describe the cloth you're offering...",
                    width=320, height=44,
                    fg_color=LIGHT_PURPLE, border_color=LIGHT_PURPLE,
                    text_color=DARK, placeholder_text_color=MUTED_PURPLE,
                    corner_radius=12)
                offer_entry.pack(pady=4)

                def send_cloth_swap():
                    offer = offer_entry.get().strip()
                    if not offer:
                        feedback.configure(
                            text="⚠ Please describe what you're offering",
                            text_color=HOT_PINK)
                        return
                    do_request("cloth_swap", offer)

                ctk.CTkButton(inner, text="👗  Send Swap Offer",
                              width=320, height=46,
                              fg_color=ELECTRIC_BLUE, hover_color="#2C1FBF",
                              text_color=WHITE, font=FONTS["button"], corner_radius=12,
                              command=send_cloth_swap).pack(pady=4)

            else:  # points_swap
                ctk.CTkLabel(inner,
                             text="This seller wants points in exchange.",
                             font=FONTS["body"], text_color=DARK).pack(pady=(0, 4))
                ctk.CTkLabel(inner,
                             text=f"Cost: {pts_val:.0f} pts",
                             font=("Outfit", 18, "bold"),
                             text_color=ELECTRIC_BLUE).pack(pady=(0, 8))

                ctk.CTkButton(inner,
                              text=f"💎  Pay {pts_val:.0f} pts",
                              width=320, height=46,
                              fg_color=ELECTRIC_BLUE, hover_color="#2C1FBF",
                              text_color=WHITE, font=FONTS["button"], corner_radius=12,
                              command=lambda: do_request("points_swap")).pack(pady=4)

        popup.geometry("420x400")
        ctk.CTkButton(popup, text="Cancel", width=100, height=34,
                      fg_color="transparent",
                      border_width=1, border_color=MUTED_PURPLE,
                      text_color=MUTED_PURPLE, corner_radius=10,
                      command=popup.destroy).pack(pady=(4, 16))

    # ═══════════════════════════════════════════════════════════
    # SELL / SWAP TAB  (completely restructured)
    # ═══════════════════════════════════════════════════════════
    def _build_sell(self):
        self.selected_image_paths = []
        # mode-section widget refs (reset in _rebuild_mode_section)
        self.s_accepts_money  = ctk.StringVar(value="No")
        self.s_price_entry    = None
        self.s_swap_type      = ctk.StringVar(value="Swap for Cloth")
        self.s_swap_cond      = None

        outer = ctk.CTkScrollableFrame(self.body, fg_color=LAVENDER)
        outer.pack(fill="both", expand=True)

        form = ctk.CTkFrame(outer, fg_color=WHITE, corner_radius=20,
                            border_width=2, border_color=LIGHT_PURPLE)
        form.pack(padx=80, pady=30, fill="x")
        self._sell_form = form

        # ── Header ────────────────────────────────────────────
        ctk.CTkLabel(form, text="List an Item 🏷",
                     font=("Outfit", 24, "bold"),
                     text_color=DEEP_PURPLE).pack(pady=(28, 2))
        ctk.CTkLabel(form, text="Fill in the details below to list your item",
                     font=FONTS["small"], text_color=MUTED_PURPLE).pack(pady=(0, 16))

        def entry(ph):
            e = ctk.CTkEntry(form, placeholder_text=ph, width=440, height=44,
                             border_color=LIGHT_PURPLE, fg_color=LIGHT_PURPLE,
                             text_color=DARK, placeholder_text_color=MUTED_PURPLE,
                             corner_radius=12)
            e.pack(pady=6)
            return e

        self.s_title    = entry("Item title  e.g. Floral Kurta Set")
        self.s_material = entry("Material  e.g. Cotton, Silk")

        # ── Points Calculation section ────────────────────────
        self._sell_divider(form, "💎  Points Value Calculation")

        ctk.CTkLabel(form,
                     text="These 3 inputs determine how many points your item is worth.",
                     font=FONTS["small"], text_color=MUTED_PURPLE).pack(pady=(0, 6))

        self.s_og_price = entry("Original / Retail Price ₹  (what you paid for it)")
        self.s_og_price.bind("<KeyRelease>", self._update_pts_preview)

        self.s_wear = ctk.StringVar(value="Few times")
        self._sell_seg_row(form, "HOW OFTEN WORN", WEAR_LABELS,
                   self.s_wear,
                   command=self._update_pts_preview)

        ctk.CTkLabel(form, text="BRAND TIER",
                     font=FONTS["tag"], text_color=MUTED_PURPLE,
                     anchor="w").pack(fill="x", padx=90, pady=(6, 0))
        self.s_brand = ctk.StringVar(value="No brand / Local")
        ctk.CTkOptionMenu(form, values=BRAND_TIERS,
                          variable=self.s_brand,
                          fg_color=LIGHT_PURPLE, button_color=DEEP_PURPLE,
                          text_color=DARK, width=440, corner_radius=10,
                          command=self._update_pts_preview).pack(pady=4)

        # Live preview
        self._pts_preview = ctk.CTkLabel(
            form, text="💎  Points Value: fill in the 3 fields above",
            font=("Outfit", 14, "bold"), text_color=ELECTRIC_BLUE)
        self._pts_preview.pack(pady=(6, 12))

        # ── Item details ──────────────────────────────────────
        self._sell_divider(form, "👗  Item Details")

        self.s_size = ctk.StringVar(value="S")
        self._sell_seg_row(form, "SIZE", ["XS", "S", "M", "L", "XL"], self.s_size)

        self.s_condition = ctk.StringVar(value="Like New")
        self._sell_seg_row(form, "CONDITION", ["Like New", "Good", "Fair"],
                           self.s_condition, command=self._update_pts_preview)

        ctk.CTkLabel(form, text="CATEGORY",
                     font=FONTS["tag"], text_color=MUTED_PURPLE,
                     anchor="w").pack(fill="x", padx=90, pady=(6, 0))
        self.s_cat = ctk.StringVar(value="tops")
        ctk.CTkOptionMenu(form,
                          values=["tops", "dresses", "bottoms",
                                  "outerwear", "ethnic", "accessories"],
                          variable=self.s_cat,
                          fg_color=LIGHT_PURPLE, button_color=DEEP_PURPLE,
                          text_color=DARK, width=440, corner_radius=10).pack(pady=4)

        # ── Mode ──────────────────────────────────────────────
        self._sell_divider(form, "🏷  Listing Mode")

        self.s_mode = ctk.StringVar(value="sell")
        ctk.CTkSegmentedButton(form, values=["sell", "swap"],
                               variable=self.s_mode,
                               width=440, height=38,
                               selected_color=DEEP_PURPLE,
                               unselected_color=LIGHT_PURPLE,
                               font=FONTS["button"], corner_radius=10,
                               command=self._rebuild_mode_section).pack(pady=4)

        # Dynamic section (sell or swap specific fields)
        self._mode_frame = ctk.CTkFrame(form, fg_color="transparent")
        self._mode_frame.pack(fill="x")
        self._rebuild_mode_section()

        # ── Photo ─────────────────────────────────────────────
        self._sell_divider(form, "📷  Photo")

        self.img_preview = ctk.CTkScrollableFrame(form, orientation="horizontal", fg_color=LIGHT_PURPLE,
                                        width=440, height=200, corner_radius=14)
        self.img_preview.pack(pady=6)
        
        self._refresh_image_preview()

        btn_row = ctk.CTkFrame(form, fg_color="transparent")
        btn_row.pack(pady=(4, 8))
        
        ctk.CTkButton(btn_row, text="Upload Photo 📎", width=215, height=42,
                      fg_color="transparent",
                      border_width=2, border_color=DEEP_PURPLE,
                      text_color=DEEP_PURPLE, hover_color=LIGHT_PURPLE,
                      font=FONTS["button"], corner_radius=12,
                      command=self._pick_image).pack(side="left", padx=5)
                      
        ctk.CTkButton(btn_row, text="Scan for cloth grade 📸", width=215, height=42,
                      fg_color=ELECTRIC_BLUE, hover_color="#2C1FBF",
                      text_color=WHITE, font=FONTS["button"], corner_radius=12,
                      command=self._open_camera).pack(side="left", padx=5)

        # ── Feedback + submit ─────────────────────────────────
        self.s_feedback = ctk.CTkLabel(form, text="",
                                       font=FONTS["small"], text_color=HOT_PINK)
        self.s_feedback.pack(pady=4)

        ctk.CTkButton(form, text="List Item →", width=440, height=48,
                      fg_color=HOT_PINK, hover_color="#D4245F",
                      text_color=WHITE, font=FONTS["button"], corner_radius=14,
                      command=self._submit_listing).pack(pady=(8, 32))

    # ── Sell-tab helper widgets ───────────────────────────────
    def _sell_divider(self, parent, text):
        ctk.CTkFrame(parent, fg_color=LIGHT_PURPLE, height=1).pack(
            fill="x", padx=60, pady=(16, 0))
        ctk.CTkLabel(parent, text=text,
                     font=FONTS["subhead"], text_color=DEEP_PURPLE,
                     anchor="w").pack(fill="x", padx=90, pady=(6, 4))

    def _sell_seg_row(self, parent, label, values, var, command=None):
        ctk.CTkLabel(parent, text=label,
                     font=FONTS["tag"], text_color=MUTED_PURPLE,
                     anchor="w").pack(fill="x", padx=90, pady=(6, 0))
        kwargs = {"command": command} if command else {}
        ctk.CTkSegmentedButton(
            parent, values=values, variable=var,
            width=440, height=38,
            selected_color=DEEP_PURPLE, unselected_color=LIGHT_PURPLE,
            font=FONTS["small"], corner_radius=10, **kwargs).pack(pady=4)

    def _update_pts_preview(self, *_):
        try:
            og = float(self.s_og_price.get() or 0)
        except ValueError:
            og = 0
        pts = calculate_points(
            og, self.s_condition.get(), self.s_wear.get(), self.s_brand.get()
        )
        self._pts_preview.configure(
            text=f"💎  Points Value: {pts:.0f} pts")

    # ── Dynamic mode section ──────────────────────────────────
    def _rebuild_mode_section(self, _=None):
        for w in self._mode_frame.winfo_children():
            w.destroy()
        # Reset widget refs
        self.s_accepts_money = ctk.StringVar(value="No")
        self.s_price_entry   = None
        self.s_swap_type     = ctk.StringVar(value="Swap for Cloth")
        self.s_swap_cond     = None

        if self.s_mode.get() == "sell":
            self._build_sell_mode(self._mode_frame)
        else:
            self._build_swap_mode(self._mode_frame)

    def _build_sell_mode(self, parent):
        """Fields shown when mode == 'sell'."""
        ctk.CTkLabel(parent, text="ACCEPT MONEY PAYMENT TOO?",
                     font=FONTS["tag"], text_color=MUTED_PURPLE,
                     anchor="w").pack(fill="x", padx=90, pady=(10, 0))
        ctk.CTkLabel(parent,
                     text="By default buyers pay with points. Enable this to also accept ₹.",
                     font=FONTS["small"], text_color=MUTED_PURPLE).pack(pady=(0, 2))

        # Hidden money-price frame
        money_frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.s_price_entry = ctk.CTkEntry(
            money_frame,
            placeholder_text="Money price ₹  (shown alongside points option)",
            width=440, height=44,
            border_color=LIGHT_PURPLE, fg_color=LIGHT_PURPLE,
            text_color=DARK, placeholder_text_color=MUTED_PURPLE,
            corner_radius=12)
        self.s_price_entry.pack(pady=4)

        def on_toggle(val):
            if val == "Yes":
                money_frame.pack(fill="x")
            else:
                money_frame.pack_forget()

        ctk.CTkSegmentedButton(parent, values=["No", "Yes"],
                               variable=self.s_accepts_money,
                               width=200, height=36,
                               selected_color=DEEP_PURPLE,
                               unselected_color=LIGHT_PURPLE,
                               font=FONTS["small"], corner_radius=10,
                               command=on_toggle).pack(pady=4)
        # money_frame hidden by default until "Yes" selected

    def _build_swap_mode(self, parent):
        """Fields shown when mode == 'swap'."""
        ctk.CTkLabel(parent, text="WHAT DO YOU WANT IN RETURN?",
                     font=FONTS["tag"], text_color=MUTED_PURPLE,
                     anchor="w").pack(fill="x", padx=90, pady=(10, 0))

        # Cloth frame (visible by default)
        cloth_frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.s_swap_cond = ctk.CTkEntry(
            cloth_frame,
            placeholder_text="Describe the cloth you want  e.g. White top in size S",
            width=440, height=44,
            border_color=LIGHT_PURPLE, fg_color=LIGHT_PURPLE,
            text_color=DARK, placeholder_text_color=MUTED_PURPLE,
            corner_radius=12)
        self.s_swap_cond.pack(pady=4)

        # Points note frame (hidden by default)
        pts_note_frame = ctk.CTkFrame(parent, fg_color="transparent")
        ctk.CTkLabel(pts_note_frame,
                     text="💎  Buyer will pay your item's calculated points value",
                     font=FONTS["body"], text_color=ELECTRIC_BLUE).pack(pady=6)

        def on_swap_type(val):
            if val == "Swap for Cloth":
                pts_note_frame.pack_forget()
                cloth_frame.pack(fill="x")
            else:
                cloth_frame.pack_forget()
                pts_note_frame.pack()

        ctk.CTkSegmentedButton(parent,
                               values=["Swap for Cloth", "Swap for Points"],
                               variable=self.s_swap_type,
                               width=440, height=36,
                               selected_color=ELECTRIC_BLUE,
                               unselected_color=LIGHT_PURPLE,
                               font=FONTS["small"], corner_radius=10,
                               command=on_swap_type).pack(pady=4)

        cloth_frame.pack(fill="x")   # visible by default

    # ── Image pick ────────────────────────────────────────────
    def _refresh_image_preview(self):
        for w in self.img_preview.winfo_children():
            w.destroy()
            
        if not self.selected_image_paths:
            lbl = ctk.CTkLabel(
                self.img_preview, text="📷\nNo image selected",
                font=FONTS["body"], text_color=MUTED_PURPLE, justify="center")
            lbl.pack(expand=True, fill="both", pady=70)
            return
            
        for path in self.selected_image_paths:
            try:
                pil_img = Image.open(path)
                pil_img.thumbnail((200, 200))
                ctk_img = ctk.CTkImage(light_image=pil_img, size=(200, 200))
                
                frame = ctk.CTkFrame(self.img_preview, fg_color="transparent")
                frame.pack(side="left", padx=5)
                
                lbl = ctk.CTkLabel(frame, image=ctk_img, text="")
                lbl.image = ctk_img
                lbl.pack()
            except Exception:
                pass

    def _pick_image(self):
        import shutil
        from tkinter import filedialog
        paths = filedialog.askopenfilenames(
            title="Select clothing photos",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.webp")])
        if not paths:
            return
            
        for path in paths:
            filename = f"{self.user.id}_{os.path.basename(path)}"
            dest = os.path.join(UPLOAD_DIR, filename)
            shutil.copy2(path, dest)
            if dest not in self.selected_image_paths:
                self.selected_image_paths.append(dest)
                
        self._refresh_image_preview()

    def _open_camera(self):
        from ui.camera_popup import CameraPopup
        def on_capture(frame):
            from ui.analysis_screen import AnalysisScreen
            def on_complete(path, condition):
                self.selected_image_paths.append(path)
                self._refresh_image_preview()
                self.s_condition.set(condition)
                self._update_pts_preview()

            AnalysisScreen(self, frame, on_complete)

        CameraPopup(self, on_capture)

    # ── Submit listing ────────────────────────────────────────
    def _submit_listing(self):
        from logic.listings import create_listing

        self.s_feedback.configure(text="")

        title = self.s_title.get().strip()
        if not title:
            self.s_feedback.configure(text="⚠ Please enter a title",
                                      text_color=HOT_PINK)
            return

        try:
            og_price = float(self.s_og_price.get().strip() or 0)
        except ValueError:
            self.s_feedback.configure(text="⚠ Original price must be a number",
                                      text_color=HOT_PINK)
            return

        mode = self.s_mode.get()

        # Sell-mode extras
        accepts_money = (mode == "sell" and self.s_accepts_money.get() == "Yes")
        price = 0.0
        if accepts_money and self.s_price_entry:
            try:
                price = float(self.s_price_entry.get().strip() or 0)
            except ValueError:
                self.s_feedback.configure(text="⚠ Money price must be a number",
                                          text_color=HOT_PINK)
                return

        # Swap-mode extras
        swap_type = (
            "cloth" if self.s_swap_type.get() == "Swap for Cloth" else "points"
        )
        swap_condition = ""
        if mode == "swap" and swap_type == "cloth" and self.s_swap_cond:
            swap_condition = self.s_swap_cond.get().strip()

        create_listing(
            seller_id=self.user.id,
            mode=mode,
            title=title,
            category=self.s_cat.get(),
            size=self.s_size.get(),
            material=self.s_material.get().strip(),
            condition=self.s_condition.get(),
            og_price=og_price,
            wear_label=self.s_wear.get(),
            brand_tier=self.s_brand.get(),
            accepts_money=accepts_money,
            price=price,
            swap_type=swap_type,
            swap_condition=swap_condition,
            image_path=",".join(self.selected_image_paths) if self.selected_image_paths else "",
        )

        self.s_feedback.configure(text="✅ Item listed successfully!",
                                  text_color=ELECTRIC_BLUE)
        for e in [self.s_title, self.s_material, self.s_og_price]:
            e.delete(0, "end")
        self.selected_image_paths = []
        self._refresh_image_preview()
        self._pts_preview.configure(
            text="💎  Points Value: fill in the 3 fields above")

    # ═══════════════════════════════════════════════════════════
    # MY LISTINGS TAB
    # ═══════════════════════════════════════════════════════════
    def _build_mylistings(self):
        from logic.listings import get_my_listings, delete_listing

        scroll = ctk.CTkScrollableFrame(self.body, fg_color=LAVENDER)
        scroll.pack(fill="both", expand=True, padx=20, pady=16)

        listings = get_my_listings(self.user.id)
        if not listings:
            ctk.CTkLabel(scroll, text="👗  You haven't listed anything yet.",
                         font=FONTS["body"], text_color=MUTED_PURPLE).pack(pady=80)
            return

        for listing in listings:
            row = ctk.CTkFrame(scroll, fg_color=WHITE, corner_radius=16,
                               border_width=2, border_color=LIGHT_PURPLE)
            row.pack(fill="x", pady=8, padx=4)

            thumb = ctk.CTkFrame(row, fg_color=LIGHT_PURPLE,
                                 width=80, height=80, corner_radius=12)
            thumb.pack(side="left", padx=14, pady=14)
            thumb.pack_propagate(False)

            first_img_path = listing.image_path.split(",")[0] if listing.image_path else ""
            if first_img_path and os.path.exists(first_img_path):
                try:
                    pil_img = Image.open(first_img_path)
                    pil_img.thumbnail((80, 80))
                    ctk_img = ctk.CTkImage(light_image=pil_img, size=(80, 80))
                    ctk.CTkLabel(thumb, image=ctk_img, text="").place(
                        relx=0.5, rely=0.5, anchor="center")
                except Exception:
                    ctk.CTkLabel(thumb, text="📷", font=("Outfit", 22),
                                 text_color=MUTED_PURPLE).place(
                                     relx=0.5, rely=0.5, anchor="center")
            else:
                ctk.CTkLabel(thumb, text="📷", font=("Outfit", 22),
                             text_color=MUTED_PURPLE).place(
                                 relx=0.5, rely=0.5, anchor="center")

            info = ctk.CTkFrame(row, fg_color="transparent")
            info.pack(side="left", fill="both", expand=True, pady=14)

            ctk.CTkLabel(info, text=listing.title,
                         font=FONTS["subhead"], text_color=DEEP_PURPLE).pack(anchor="w")

            # Points value
            pts_val = listing.points_value or 0
            ctk.CTkLabel(info, text=f"💎 {pts_val:.0f} pts",
                         font=("Outfit", 13, "bold"),
                         text_color=ELECTRIC_BLUE).pack(anchor="w")

            status_colors = {
                "active":    (NEON_LIME,     DARK),
                "matched":   (ELECTRIC_BLUE, WHITE),
                "sold":      (HOT_PINK,      WHITE),
            }
            pill_bg, pill_fg = status_colors.get(
                listing.status, (LIGHT_PURPLE, MUTED_PURPLE))
            spill = ctk.CTkFrame(info, fg_color=pill_bg,
                                 corner_radius=6, height=20)
            spill.pack(anchor="w", pady=(2, 0))
            spill.pack_propagate(False)

            swap_suffix = (
                f"  ·  {listing.swap_type or 'cloth'} swap"
                if listing.mode == "swap" else ""
            )
            ctk.CTkLabel(spill,
                         text=(f"  {listing.status.upper()}  ·  {listing.mode.upper()}"
                               f"{swap_suffix}  ·  {listing.category}"
                               f"  ·  Size {listing.size}  "),
                         font=FONTS["tag"], text_color=pill_fg).pack(padx=8, pady=2)

            ctk.CTkButton(row, text="Delete 🗑", width=90, height=34,
                          fg_color="#FF2D78", hover_color="#D4245F",
                          text_color=WHITE, font=FONTS["small"], corner_radius=10,
                          command=lambda lid=listing.id: self._delete_and_refresh(
                              lid, delete_listing)).pack(side="right", padx=(4, 16), pady=14)

            ctk.CTkButton(row, text="Edit ✏", width=80, height=34,
                          fg_color=ELECTRIC_BLUE, hover_color="#2C1FBF",
                          text_color=WHITE, font=FONTS["small"], corner_radius=10,
                          command=lambda l=listing: self._open_edit(l)).pack(
                              side="right", padx=4, pady=14)

    def _open_profile(self):
        from ui.profile_screen import ProfileScreen
        ProfileScreen(self.master, user=self.user)

    def _open_detail(self, listing):
        from ui.listing_detail_screen import ListingDetailScreen
        ListingDetailScreen(self.master, listing=listing, user=self.user,
                            on_wishlist_toggle=lambda: self._show_tab("browse"))

    def _quick_wishlist(self, listing):
        from logic.listings import toggle_wishlist
        toggle_wishlist(self.user.id, listing.id)
        self._show_tab("browse")

    def _open_edit(self, listing):
        from ui.edit_listing_screen import EditListingScreen
        EditListingScreen(self.master, listing=listing, user=self.user,
                          on_save=lambda: self._show_tab("mylistings"))

    def _build_wishlist(self):
        from logic.listings import get_wishlist
        scroll = ctk.CTkScrollableFrame(self.body, fg_color=LAVENDER)
        scroll.pack(fill="both", expand=True, padx=20, pady=16)
        listings = get_wishlist(self.user.id)
        if not listings:
            ctk.CTkLabel(scroll, text="🤍  Your wishlist is empty.\nHeart a listing to save it!",
                         font=FONTS["body"], text_color=MUTED_PURPLE,
                         justify="center").pack(pady=80)
            return
        scroll.grid_columnconfigure(0, weight=1)
        scroll.grid_columnconfigure(1, weight=1)
        scroll.grid_columnconfigure(2, weight=1)
        for i, listing in enumerate(listings):
            row, col = divmod(i, 3)
            self._listing_card(scroll, listing, row, col)

    def _delete_and_refresh(self, listing_id, delete_fn):
        delete_fn(listing_id, self.user.id)
        self._show_tab("mylistings")