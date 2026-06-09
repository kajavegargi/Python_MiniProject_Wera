import customtkinter as ctk
from ui.theme import (DEEP_PURPLE, HOT_PINK, ELECTRIC_BLUE, NEON_LIME,
                      LAVENDER, LIGHT_PURPLE, MUTED_PURPLE, WHITE,
                      DARK, LIGHT_GRAY, GRAPE, FONTS)


class ProfileScreen(ctk.CTkToplevel):
    """Profile popup — stats, reviews received, and leave a review."""

    def __init__(self, master, user):
        super().__init__(master)
        self.user = user
        self.title("My Profile")
        self.geometry("700x640")
        self.configure(fg_color=LAVENDER)
        self.grab_set()
        self.resizable(False, False)
        self._build()

    def _build(self):
        # Header
        header = ctk.CTkFrame(self, fg_color=DEEP_PURPLE, height=56, corner_radius=0)
        header.pack(fill="x")
        header.pack_propagate(False)

        ctk.CTkButton(header, text="✕ Close", width=90, height=32,
                      fg_color="transparent", border_width=1,
                      border_color=MUTED_PURPLE, text_color=MUTED_PURPLE,
                      hover_color="#2D0A4E", font=FONTS["small"], corner_radius=10,
                      command=self.destroy).pack(side="left", padx=16, pady=10)

        ctk.CTkLabel(header, text="👤 My Profile",
                     font=("Outfit", 18, "bold"),
                     text_color=WHITE).pack(side="left", padx=8)

        ctk.CTkFrame(self, fg_color=HOT_PINK, height=3,
                     corner_radius=0).pack(fill="x")

        scroll = ctk.CTkScrollableFrame(self, fg_color=LAVENDER)
        scroll.pack(fill="both", expand=True, padx=24, pady=16)

        # ── Identity card ─────────────────────────────────────
        id_card = ctk.CTkFrame(scroll, fg_color=DEEP_PURPLE, corner_radius=18)
        id_card.pack(fill="x", pady=(0, 16))

        inner = ctk.CTkFrame(id_card, fg_color="transparent")
        inner.pack(padx=28, pady=20)

        ctk.CTkLabel(inner, text=self.user.name,
                     font=("Outfit", 26, "bold"),
                     text_color=WHITE).pack(anchor="w")
        ctk.CTkLabel(inner, text=self.user.email,
                     font=FONTS["body"], text_color=MUTED_PURPLE).pack(anchor="w")
        ctk.CTkLabel(inner,
                     text=f"🏫  {self.user.college_or_company or '—'}   📍  {self.user.city or '—'}",
                     font=FONTS["small"], text_color=NEON_LIME).pack(anchor="w", pady=(4, 0))

        # ── Stats grid ────────────────────────────────────────
        from logic.listings import get_user_stats
        stats = get_user_stats(self.user.id)

        stat_items = [
            ("💎", f"{stats['points']:.0f}", "Points Balance"),
            ("🏷", str(stats["total_listings"]),  "Total Listings"),
            ("✅", str(stats["active_listings"]),  "Active"),
            ("📦", str(stats["sold_listings"]),    "Sold"),
            ("🤝", str(stats["matches_completed"]), "Sales Done"),
            ("🛍", str(stats["buys_completed"]),   "Purchases Done"),
        ]

        grid = ctk.CTkFrame(scroll, fg_color="transparent")
        grid.pack(fill="x", pady=(0, 16))
        for i, (icon, val, label) in enumerate(stat_items):
            col = i % 3
            row = i // 3
            card = ctk.CTkFrame(grid, fg_color=WHITE, corner_radius=14,
                                border_width=2, border_color=LIGHT_PURPLE)
            card.grid(row=row, column=col, padx=6, pady=6, sticky="nsew")
            grid.grid_columnconfigure(col, weight=1)
            ctk.CTkLabel(card, text=icon,
                         font=("Outfit", 22)).pack(pady=(14, 0))
            ctk.CTkLabel(card, text=val,
                         font=("Outfit", 22, "bold"),
                         text_color=DEEP_PURPLE).pack()
            ctk.CTkLabel(card, text=label,
                         font=FONTS["tag"],
                         text_color=MUTED_PURPLE).pack(pady=(0, 14))

        # ── Reviews received ──────────────────────────────────
        from logic.reviews import get_seller_reviews
        reviews, avg = get_seller_reviews(self.user.id)

        rev_header = ctk.CTkFrame(scroll, fg_color="transparent")
        rev_header.pack(fill="x", pady=(8, 6))

        ctk.CTkLabel(rev_header, text="⭐ Reviews",
                     font=("Outfit", 18, "bold"),
                     text_color=DEEP_PURPLE).pack(side="left")

        if reviews:
            stars = "★" * int(avg) + "☆" * (5 - int(avg))
            ctk.CTkLabel(rev_header,
                         text=f"  {stars}  {avg}/5  ({len(reviews)})",
                         font=FONTS["body"],
                         text_color=NEON_LIME).pack(side="left", padx=8)

        if not reviews:
            ctk.CTkLabel(scroll, text="No reviews yet.",
                         font=FONTS["small"],
                         text_color=MUTED_PURPLE).pack(anchor="w", padx=4)
        else:
            for rev in reviews:
                r_card = ctk.CTkFrame(scroll, fg_color=WHITE, corner_radius=12,
                                      border_width=1, border_color=LIGHT_PURPLE)
                r_card.pack(fill="x", pady=4)
                r_inner = ctk.CTkFrame(r_card, fg_color="transparent")
                r_inner.pack(padx=16, pady=10, fill="x")
                stars_str = "★" * rev.rating + "☆" * (5 - rev.rating)
                ctk.CTkLabel(r_inner, text=stars_str,
                             font=("Outfit", 14),
                             text_color=NEON_LIME).pack(anchor="w")
                if rev.comment:
                    ctk.CTkLabel(r_inner, text=f'"{rev.comment}"',
                                 font=FONTS["small"],
                                 text_color=DARK, wraplength=560,
                                 justify="left").pack(anchor="w", pady=(2, 0))

        # ── Leave a review (for completed purchases) ──────────
        self._build_review_section(scroll)

    def _build_review_section(self, parent):
        """Show completed matches where the user was buyer and hasn't reviewed yet."""
        from database.db import get_session
        from database.models import Match, Listing, User as UserModel
        from logic.reviews import get_review_for_match, submit_review

        db = get_session()
        completed = (
            db.query(Match)
            .filter_by(buyer_id=self.user.id, status="completed")
            .all()
        )
        unreviewed = [m for m in completed if not get_review_for_match(m.id)]
        for m in completed:
            db.expunge(m)

        if not unreviewed:
            return

        ctk.CTkFrame(parent, fg_color=LIGHT_PURPLE,
                     height=2, corner_radius=1).pack(fill="x", pady=12)
        ctk.CTkLabel(parent, text="✍ Leave a Review",
                     font=("Outfit", 18, "bold"),
                     text_color=DEEP_PURPLE).pack(anchor="w", pady=(0, 8))

        for match in unreviewed:
            listing = db.query(Listing).get(match.listing_id)
            seller  = db.query(UserModel).get(listing.seller_id) if listing else None
            if not listing or not seller:
                continue

            r_card = ctk.CTkFrame(parent, fg_color=WHITE, corner_radius=14,
                                  border_width=2, border_color=LIGHT_PURPLE)
            r_card.pack(fill="x", pady=6)
            r_inner = ctk.CTkFrame(r_card, fg_color="transparent")
            r_inner.pack(padx=16, pady=12, fill="x")

            ctk.CTkLabel(r_inner,
                         text=f"{listing.title}  ·  by {seller.name}",
                         font=FONTS["body"], text_color=DEEP_PURPLE).pack(anchor="w")

            rating_var = ctk.IntVar(value=5)
            stars_row = ctk.CTkFrame(r_inner, fg_color="transparent")
            stars_row.pack(anchor="w", pady=(6, 4))
            ctk.CTkLabel(stars_row, text="Rating:",
                         font=FONTS["small"],
                         text_color=MUTED_PURPLE).pack(side="left", padx=(0, 8))
            for star in range(1, 6):
                ctk.CTkRadioButton(stars_row, text=str(star),
                                   variable=rating_var, value=star,
                                   fg_color=NEON_LIME,
                                   border_color=DEEP_PURPLE,
                                   font=FONTS["small"],
                                   text_color=DARK).pack(side="left", padx=4)

            comment_entry = ctk.CTkEntry(
                r_inner,
                placeholder_text="Leave a comment (optional)...",
                width=480, height=40,
                fg_color=LIGHT_PURPLE, border_color=LIGHT_PURPLE,
                text_color=DARK, placeholder_text_color=MUTED_PURPLE,
                corner_radius=10)
            comment_entry.pack(anchor="w", pady=(4, 6))

            feedback_lbl = ctk.CTkLabel(r_inner, text="",
                                        font=FONTS["small"], text_color=HOT_PINK)
            feedback_lbl.pack(anchor="w")

            def submit(m=match, s=seller, rv=rating_var, ce=comment_entry, fb=feedback_lbl, rc=r_card):
                ok, msg = submit_review(
                    match_id=m.id,
                    reviewer_id=self.user.id,
                    seller_id=s.id,
                    rating=rv.get(),
                    comment=ce.get().strip(),
                )
                fb.configure(text=msg,
                             text_color=ELECTRIC_BLUE if ok else HOT_PINK)
                if ok:
                    self.after(1200, rc.destroy)

            ctk.CTkButton(r_inner, text="Submit Review ⭐",
                          width=160, height=36,
                          fg_color=DEEP_PURPLE, hover_color=GRAPE,
                          text_color=WHITE, font=FONTS["small"], corner_radius=10,
                          command=submit).pack(anchor="w")