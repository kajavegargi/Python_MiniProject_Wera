"""
ui/reviews_panel.py
────────────────────
Two reusable widgets:

1. SellerRatingBadge   — compact star badge (e.g. ★ 4.3 · 12 reviews)
   Used in listing cards, search results, etc.

2. ReviewsPanel        — full scrollable review panel with rating breakdown
   Used in the seller profile view.

3. WriteReviewDialog   — modal form to submit a new review
   Triggered after a completed match.

Usage examples
──────────────
# Compact badge in a listing card:
    from ui.reviews_panel import SellerRatingBadge
    SellerRatingBadge(card_frame, seller_id=listing.seller_id).pack()

# Full panel in a profile page:
    from ui.reviews_panel import ReviewsPanel
    ReviewsPanel(profile_frame, seller_id=user.id).pack(fill="both")

# Write-review button in match history:
    from ui.reviews_panel import WriteReviewDialog
    WriteReviewDialog(
        parent,
        match_id=match.id,
        reviewer=current_user,
        seller=seller_user,
        on_success=refresh_callback,
    )
"""

import customtkinter as ctk
from datetime import datetime
from logic.reviews import (
    get_review_summary, can_review, submit_review, get_average_rating
)
from ui.theme import LAVENDER, WHITE, DARK, SAGE, FONT_HEADING, FONT_BODY


# ── Helpers ───────────────────────────────────────────────────────────────

def _star_string(rating: float, filled="★", empty="☆") -> str:
    """Convert a numeric rating to a star string, e.g. '★★★★☆'."""
    full = round(rating)
    return filled * full + empty * (5 - full)


# ── 1. SellerRatingBadge ──────────────────────────────────────────────────

class SellerRatingBadge(ctk.CTkFrame):
    """
    A small inline badge showing average stars and review count.
    Shows "No reviews yet" when there are none.
    """

    def __init__(self, parent, seller_id: int, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)

        avg = get_average_rating(seller_id)
        summary = get_review_summary(seller_id)
        count = summary["count"]

        if avg is None:
            text = "☆  No reviews yet"
            color = "#AAA"
        else:
            text = f"{_star_string(avg)}  {avg} · {count} review{'s' if count != 1 else ''}"
            color = "#E6A817"

        ctk.CTkLabel(
            self,
            text=text,
            font=(FONT_BODY, 12),
            text_color=color,
        ).pack()


# ── 2. ReviewsPanel ───────────────────────────────────────────────────────

class ReviewsPanel(ctk.CTkFrame):
    """
    Full review panel for a seller's profile page.
    Shows: overall score, star distribution bar chart, individual reviews.
    """

    def __init__(self, parent, seller_id: int, **kwargs):
        super().__init__(parent, fg_color=WHITE, corner_radius=12, **kwargs)
        self._seller_id = seller_id
        self._build()

    def _build(self):
        summary = get_review_summary(self._seller_id)

        # ── Section heading
        ctk.CTkLabel(
            self,
            text="Ratings & Reviews",
            font=(FONT_HEADING, 15, "bold"),
            text_color=DARK,
        ).pack(anchor="w", padx=16, pady=(14, 6))

        if summary["count"] == 0:
            ctk.CTkLabel(
                self,
                text="No reviews yet. Be the first to review!",
                font=(FONT_BODY, 12),
                text_color="#AAA",
            ).pack(padx=16, pady=(0, 14))
            return

        # ── Score + distribution row
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=16, pady=(0, 10))

        # Big score on the left
        score_frame = ctk.CTkFrame(top, fg_color="#F5F0FF", corner_radius=10, width=90)
        score_frame.pack(side="left", padx=(0, 16), pady=4)
        score_frame.pack_propagate(False)

        ctk.CTkLabel(
            score_frame,
            text=str(summary["average"]),
            font=(FONT_HEADING, 28, "bold"),
            text_color=DARK,
        ).pack(pady=(10, 0))
        ctk.CTkLabel(
            score_frame,
            text=_star_string(summary["average"]),
            font=(FONT_BODY, 14),
            text_color="#E6A817",
        ).pack()
        ctk.CTkLabel(
            score_frame,
            text=f"{summary['count']} reviews",
            font=(FONT_BODY, 10),
            text_color="#888",
        ).pack(pady=(0, 10))

        # Distribution bars on the right
        dist_frame = ctk.CTkFrame(top, fg_color="transparent")
        dist_frame.pack(side="left", fill="both", expand=True)

        for star in range(5, 0, -1):
            count = summary["distribution"].get(star, 0)
            row = ctk.CTkFrame(dist_frame, fg_color="transparent")
            row.pack(fill="x", pady=1)

            ctk.CTkLabel(
                row,
                text=f"{'★'*star}",
                font=(FONT_BODY, 11),
                text_color="#E6A817",
                width=60,
            ).pack(side="left")

            total = summary["count"] or 1
            fill_ratio = count / total

            bar_bg = ctk.CTkFrame(row, fg_color="#EEE", height=8, corner_radius=4)
            bar_bg.pack(side="left", fill="x", expand=True, padx=(4, 8))

            bar_fill_width = max(4, int(fill_ratio * 160))
            ctk.CTkFrame(
                bar_bg,
                fg_color=SAGE,
                height=8,
                width=bar_fill_width,
                corner_radius=4,
            ).place(x=0, y=0)

            ctk.CTkLabel(
                row,
                text=str(count),
                font=(FONT_BODY, 11),
                text_color="#888",
                width=20,
            ).pack(side="left")

        # ── Divider
        ctk.CTkFrame(self, fg_color="#EEE", height=1).pack(fill="x", padx=16, pady=8)

        # ── Scrollable individual reviews
        scroll = ctk.CTkScrollableFrame(
            self, fg_color="transparent", height=220
        )
        scroll.pack(fill="both", expand=True, padx=8, pady=(0, 12))

        for rev in summary["reviews"]:
            self._review_card(scroll, rev)

    def _review_card(self, parent, review):
        card = ctk.CTkFrame(
            parent, fg_color="#F9F6FF", corner_radius=8
        )
        card.pack(fill="x", padx=8, pady=4)

        # Stars + date header
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=12, pady=(10, 2))

        ctk.CTkLabel(
            header,
            text=_star_string(review.rating),
            font=(FONT_BODY, 13),
            text_color="#E6A817",
        ).pack(side="left")

        date_str = (
            review.created_at.strftime("%d %b %Y")
            if isinstance(review.created_at, datetime)
            else str(review.created_at)
        )
        ctk.CTkLabel(
            header,
            text=date_str,
            font=(FONT_BODY, 10),
            text_color="#AAA",
        ).pack(side="right")

        # Comment
        if review.comment:
            ctk.CTkLabel(
                card,
                text=review.comment,
                font=(FONT_BODY, 12),
                text_color=DARK,
                justify="left",
                wraplength=340,
            ).pack(anchor="w", padx=12, pady=(0, 10))
        else:
            ctk.CTkLabel(
                card,
                text="(no comment)",
                font=(FONT_BODY, 11),
                text_color="#BBB",
            ).pack(anchor="w", padx=12, pady=(0, 10))


# ── 3. WriteReviewDialog ──────────────────────────────────────────────────

class WriteReviewDialog(ctk.CTkToplevel):
    """
    Modal form for submitting a review after a completed match.

    Parameters
    ──────────
    match_id   – ID of the completed Match
    reviewer   – logged-in User ORM object (the buyer)
    seller     – User ORM object (the seller)
    on_success – optional callback() after successful submission
    """

    def __init__(self, parent, match_id: int, reviewer, seller, on_success=None):
        super().__init__(parent)

        self._match_id = match_id
        self._reviewer = reviewer
        self._seller = seller
        self._on_success = on_success
        self._selected_rating = 0

        self.title(f"Review — {seller.name}")
        self.geometry("400x380")
        self.resizable(False, False)
        self.configure(fg_color=LAVENDER)
        self.grab_set()

        self._build()

    def _build(self):
        ctk.CTkLabel(
            self,
            text=f"How was your experience with\n{self._seller.name}?",
            font=(FONT_HEADING, 14, "bold"),
            text_color=DARK,
            justify="center",
        ).pack(pady=(20, 10))

        # Star picker row
        star_row = ctk.CTkFrame(self, fg_color="transparent")
        star_row.pack(pady=(0, 12))

        self._star_buttons = []
        for i in range(1, 6):
            btn = ctk.CTkButton(
                star_row,
                text="☆",
                width=40,
                height=40,
                fg_color="transparent",
                text_color="#E6A817",
                hover_color="#F5F0FF",
                font=(FONT_BODY, 22),
                command=lambda n=i: self._set_rating(n),
            )
            btn.pack(side="left", padx=2)
            self._star_buttons.append(btn)

        self._rating_label = ctk.CTkLabel(
            self,
            text="Tap a star to rate",
            font=(FONT_BODY, 11),
            text_color="#888",
        )
        self._rating_label.pack(pady=(0, 8))

        # Comment box
        ctk.CTkLabel(
            self,
            text="Leave a comment (optional)",
            font=(FONT_BODY, 11),
            text_color=DARK,
        ).pack(anchor="w", padx=24)

        self._comment_box = ctk.CTkTextbox(
            self,
            height=80,
            font=(FONT_BODY, 12),
            fg_color=WHITE,
            text_color=DARK,
            corner_radius=8,
        )
        self._comment_box.pack(fill="x", padx=24, pady=(4, 12))

        # Submit button
        self._submit_btn = ctk.CTkButton(
            self,
            text="Submit Review",
            fg_color=SAGE,
            text_color=WHITE,
            font=(FONT_BODY, 13, "bold"),
            corner_radius=8,
            state="disabled",
            command=self._submit,
        )
        self._submit_btn.pack(fill="x", padx=24)

        self._status = ctk.CTkLabel(
            self, text="", font=(FONT_BODY, 11), text_color=SAGE, wraplength=340
        )
        self._status.pack(pady=8)

    def _set_rating(self, n: int):
        self._selected_rating = n
        labels = ["Terrible", "Poor", "Okay", "Good", "Excellent!"]
        self._rating_label.configure(
            text=f"{'★' * n}{'☆' * (5-n)}  —  {labels[n-1]}"
        )
        for i, btn in enumerate(self._star_buttons):
            btn.configure(text="★" if i < n else "☆")

        self._submit_btn.configure(state="normal")

    def _submit(self):
        if self._selected_rating == 0:
            return

        comment = self._comment_box.get("1.0", "end").strip()
        ok, msg = submit_review(
            match_id=self._match_id,
            reviewer_id=self._reviewer.id,
            seller_id=self._seller.id,
            rating=self._selected_rating,
            comment=comment,
        )

        self._status.configure(
            text=msg,
            text_color=SAGE if ok else "#C0392B",
        )

        if ok:
            self._submit_btn.configure(state="disabled")
            if self._on_success:
                self.after(800, self._on_success)
