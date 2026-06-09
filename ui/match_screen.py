import customtkinter as ctk
from ui.theme import (DEEP_PURPLE, HOT_PINK, ELECTRIC_BLUE, NEON_LIME,
                      LAVENDER, LIGHT_PURPLE, MUTED_PURPLE, WHITE,
                      DARK, LIGHT_GRAY, GRAPE, FONTS)
from logic.match import get_matches_for_seller, get_matches_for_buyer, accept_match, complete_transaction
from database.db_example import get_session
from database.models import Listing, User


class MatchScreen(ctk.CTkFrame):
    def __init__(self, master, user, on_back):
        super().__init__(master, fg_color=LAVENDER)
        self.user       = user
        self.on_back    = on_back
        self.active_tab = "incoming"
        self._build()

    def _build(self):
        self._build_navbar()
        self._build_tab_bar()
        self.body = ctk.CTkFrame(self, fg_color=LAVENDER, corner_radius=0)
        self.body.pack(fill="both", expand=True)
        self._load_tab()

    # ── Navbar ────────────────────────────────────────────────
    def _build_navbar(self):
        nav = ctk.CTkFrame(self, fg_color=DEEP_PURPLE, height=60, corner_radius=0)
        nav.pack(fill="x")
        nav.pack_propagate(False)

        ctk.CTkButton(nav, text="← Back", width=90, height=34,
                      fg_color="transparent",
                      border_width=1, border_color=MUTED_PURPLE,
                      text_color=MUTED_PURPLE, hover_color="#2D0A4E",
                      font=FONTS["small"], corner_radius=10,
                      command=self.on_back).pack(side="left", padx=16)

        ctk.CTkLabel(nav, text="💬 Matches",
                     font=("Outfit", 22, "bold"),
                     text_color=WHITE).pack(side="left", padx=8)

        # Points balance
        from database.db_example import get_session as _gs
        from database.models import User as _U
        try:
            db  = _gs()
            u   = db.query(_U).get(self.user.id)
            pts = f"{(u.points_balance or 0):.0f}" if u else "—"
        except Exception:
            pts = "—"

        pts_pill = ctk.CTkFrame(nav, fg_color="#1A0A2E", corner_radius=20, height=34)
        pts_pill.pack(side="right", padx=(0, 4))
        pts_pill.pack_propagate(False)
        ctk.CTkLabel(pts_pill, text=f"  💎 {pts} pts  ",
                     font=FONTS["small"], text_color=NEON_LIME).pack(padx=8, pady=4)

        pill = ctk.CTkFrame(nav, fg_color="#2D0A4E", corner_radius=20, height=34)
        pill.pack(side="right", padx=16)
        pill.pack_propagate(False)
        ctk.CTkLabel(pill, text=f"  👋 {self.user.name}  ",
                     font=FONTS["small"], text_color=NEON_LIME).pack(padx=10, pady=4)

        ctk.CTkFrame(self, fg_color=HOT_PINK, height=3, corner_radius=0).pack(fill="x")

    # ── Tab bar ───────────────────────────────────────────────
    def _build_tab_bar(self):
        bar = ctk.CTkFrame(self, fg_color=WHITE, height=50, corner_radius=0)
        bar.pack(fill="x")
        bar.pack_propagate(False)

        for key, label in [("incoming", "📥 Incoming Requests"),
                            ("sent",     "📤 Sent Requests")]:
            is_active = self.active_tab == key
            ctk.CTkButton(bar, text=label, width=220, height=50,
                          fg_color=DEEP_PURPLE if is_active else WHITE,
                          text_color=WHITE if is_active else MUTED_PURPLE,
                          hover_color=LIGHT_PURPLE if not is_active else GRAPE,
                          corner_radius=0, font=FONTS["button"],
                          command=lambda t=key: self._switch_tab(t)).pack(side="left")

        ctk.CTkFrame(self, fg_color=NEON_LIME, height=3, corner_radius=0).pack(fill="x")

    def _switch_tab(self, tab):
        self.active_tab = tab
        for w in self.winfo_children():
            w.destroy()
        self._build()

    # ── Match cards ───────────────────────────────────────────
    def _load_tab(self):
        for w in self.body.winfo_children():
            w.destroy()

        scroll = ctk.CTkScrollableFrame(self.body, fg_color=LAVENDER)
        scroll.pack(fill="both", expand=True, padx=24, pady=20)

        matches = (get_matches_for_seller(self.user.id)
                   if self.active_tab == "incoming"
                   else get_matches_for_buyer(self.user.id))

        if not matches:
            ctk.CTkLabel(scroll, text="🌀  No matches here yet.",
                         font=FONTS["body"], text_color=MUTED_PURPLE).pack(pady=80)
            return

        db = get_session()
        for match in matches:
            listing = db.query(Listing).get(match.listing_id)
            buyer   = db.query(User).get(match.buyer_id)
            seller  = db.query(User).get(listing.seller_id) if listing else None
            self._match_card(scroll, match, listing, buyer, seller)

    def _match_card(self, parent, match, listing, buyer, seller):
        card = ctk.CTkFrame(parent, fg_color=WHITE, corner_radius=20,
                            border_width=2, border_color=LIGHT_PURPLE)
        card.pack(fill="x", pady=10)

        # ── Top row: title + status badge ─────────────────────
        top = ctk.CTkFrame(card, fg_color="transparent")
        top.pack(fill="x", padx=18, pady=(16, 4))

        if listing:
            ctk.CTkLabel(top, text=listing.title,
                         font=FONTS["subhead"], text_color=DEEP_PURPLE).pack(side="left")

        status_styles = {
            "pending":   (NEON_LIME,     DARK,  "⏳ PENDING"),
            "accepted":  (ELECTRIC_BLUE, WHITE, "✅ ACCEPTED"),
            "completed": (HOT_PINK,      WHITE, "🏁 COMPLETED"),
        }
        pill_bg, pill_fg, pill_text = status_styles.get(
            match.status, (LIGHT_PURPLE, MUTED_PURPLE, match.status.upper()))
        badge = ctk.CTkFrame(top, fg_color=pill_bg, corner_radius=8, height=28)
        badge.pack(side="right")
        badge.pack_propagate(False)
        ctk.CTkLabel(badge, text=f"  {pill_text}  ",
                     font=FONTS["tag"], text_color=pill_fg).pack(padx=10, pady=4)

        # ── Who row ───────────────────────────────────────────
        if self.active_tab == "incoming":
            who = (f"Request from: {buyer.name if buyer else '—'}"
                   f"  ·  {buyer.college_or_company or '' if buyer else ''}"
                   f"  ·  {buyer.city if buyer else ''}")
        else:
            who = (f"Listed by: {seller.name if seller else '—'}"
                   f"  ·  {listing.category or '' if listing else ''}"
                   f"  ·  Size {listing.size or '—' if listing else '—'}")

        ctk.CTkLabel(card, text=who, font=FONTS["small"], text_color=MUTED_PURPLE).pack(
            anchor="w", padx=18, pady=(0, 4))

        # ── Payment type + value row ───────────────────────────
        pt = match.payment_type or "money"
        pt_labels = {
            "money":       ("💵 Money Payment",  HOT_PINK),
            "points":      ("💎 Points Payment", ELECTRIC_BLUE),
            "cloth_swap":  ("👗 Cloth Swap",     NEON_LIME),
            "points_swap": ("💎 Points Swap",    ELECTRIC_BLUE),
        }
        pt_text, pt_color = pt_labels.get(pt, (pt.upper(), MUTED_PURPLE))

        pay_row = ctk.CTkFrame(card, fg_color="transparent")
        pay_row.pack(anchor="w", padx=18, pady=(0, 4))

        if pt == "money":
            price_text = f"₹{listing.price:.0f}" if listing and listing.price else "₹0"
            fee_text   = (f"  ·  Platform fee: "
                          f"₹{(match.fee_on_match or 0) + (match.fee_on_complete or 0):.0f}")
            ctk.CTkLabel(pay_row, text=f"  Price: {price_text}",
                         font=("Outfit", 15, "bold"),
                         text_color=HOT_PINK).pack(side="left")
            ctk.CTkLabel(pay_row, text=fee_text,
                         font=FONTS["small"], text_color=MUTED_PURPLE).pack(side="left")
        elif pt in ("points", "points_swap"):
            pts_val = listing.points_value if listing else 0
            ctk.CTkLabel(pay_row, text=f"  💎  {pts_val:.0f} pts",
                         font=("Outfit", 15, "bold"),
                         text_color=ELECTRIC_BLUE).pack(side="left")
        elif pt == "cloth_swap":
            ctk.CTkLabel(pay_row, text="  👗  Cloth for Cloth",
                         font=("Outfit", 15, "bold"),
                         text_color=ELECTRIC_BLUE).pack(side="left")

        # Payment type badge
        pt_badge = ctk.CTkFrame(pay_row, fg_color=LIGHT_PURPLE, corner_radius=6)
        pt_badge.pack(side="left", padx=8)
        ctk.CTkLabel(pt_badge, text=f"  {pt_text}  ",
                     font=FONTS["tag"], text_color=pt_color).pack(padx=6, pady=2)

        # ── Swap offer (cloth_swap only) ───────────────────────
        if pt == "cloth_swap" and match.swap_offer:
            ctk.CTkLabel(card,
                         text=f"Buyer offers: {match.swap_offer}",
                         font=FONTS["small"], text_color=MUTED_PURPLE,
                         wraplength=600).pack(anchor="w", padx=18, pady=(0, 4))

        # ── Action buttons ────────────────────────────────────
        actions = ctk.CTkFrame(card, fg_color="transparent")
        actions.pack(fill="x", padx=18, pady=(4, 16))

        if match.status in ("accepted", "completed"):
            ctk.CTkButton(actions, text="💬 Open Chat", width=150, height=38,
                          fg_color=ELECTRIC_BLUE, hover_color="#2C1FBF",
                          text_color=WHITE, font=FONTS["small"], corner_radius=12,
                          command=lambda m=match, l=listing, b=buyer, s=seller:
                              self._open_chat(m, l, b, s)).pack(side="left", padx=(0, 10))

        if self.active_tab == "incoming" and match.status == "pending":
            ctk.CTkButton(actions, text="✅ Accept", width=130, height=38,
                          fg_color=DEEP_PURPLE, hover_color=GRAPE,
                          text_color=WHITE, font=FONTS["small"], corner_radius=12,
                          command=lambda mid=match.id: self._accept(mid)).pack(
                              side="left", padx=(0, 10))

        if match.status == "accepted":
            ctk.CTkButton(actions, text="🏁 Mark Complete", width=160, height=38,
                          fg_color=HOT_PINK, hover_color="#D4245F",
                          text_color=WHITE, font=FONTS["small"], corner_radius=12,
                          command=lambda mid=match.id: self._complete(mid)).pack(side="left")

    def _accept(self, match_id):
        accept_match(match_id)
        self._load_tab()

    def _complete(self, match_id):
        complete_transaction(match_id)
        self._load_tab()

    def _open_chat(self, match, listing, buyer, seller):
        from ui.chat_screen import ChatScreen
        other_user = buyer if self.active_tab == "incoming" else seller
        for w in self.master.winfo_children():
            w.destroy()
        ChatScreen(self.master, user=self.user, match=match,
                   listing=listing, other_user=other_user,
                   on_back=self._restore).pack(fill="both", expand=True)

    def _restore(self):
        for w in self.master.winfo_children():
            w.destroy()
        MatchScreen(self.master, user=self.user,
                    on_back=self.on_back).pack(fill="both", expand=True)