"""
ui/user_profile_screen.py
──────────────────────────
A full user profile view that integrates all three new features:
  • Follow / Unfollow button
  • Block / Report dialog (⋯ menu button)
  • Ratings & Reviews panel

Usage — open from any listing card or search result:

    from ui.user_profile_screen import UserProfileScreen

    UserProfileScreen(
        parent_frame,
        viewer=current_user,      # logged-in User ORM object
        subject=seller_user,      # the User whose profile we're viewing
        on_back=go_back_callback,
    ).pack(fill="both", expand=True)
"""

import customtkinter as ctk
from ui.theme import LAVENDER, WHITE, DARK, SAGE, FONT_HEADING, FONT_BODY
from ui.follow_button import FollowButton
from ui.report_block_dialog import ReportBlockDialog
from ui.reviews_panel import ReviewsPanel, SellerRatingBadge
from logic.follow import get_follower_count, get_following_count
from logic.moderation import is_blocked_either_way


class UserProfileScreen(ctk.CTkFrame):
    """
    Full profile page for any user.

    Shows: avatar placeholder, name, college/city, follower stats,
           follow button, more-options menu (block/report),
           and the full reviews panel.
    """

    def __init__(self, parent, viewer, subject, on_back=None):
        super().__init__(parent, fg_color=LAVENDER)

        self._viewer = viewer
        self._subject = subject
        self._on_back = on_back

        # If the viewer has been blocked by the subject, show a generic page
        if is_blocked_either_way(viewer.id, subject.id):
            self._build_blocked_placeholder()
        else:
            self._build_profile()

    # ── Blocked state ─────────────────────────────────────────────────────

    def _build_blocked_placeholder(self):
        ctk.CTkLabel(
            self,
            text="This profile is unavailable.",
            font=(FONT_BODY, 13),
            text_color="#888",
        ).pack(expand=True)

        if self._on_back:
            ctk.CTkButton(
                self,
                text="← Back",
                fg_color="transparent",
                text_color=DARK,
                command=self._on_back,
            ).pack(pady=10)

    # ── Full profile ──────────────────────────────────────────────────────

    def _build_profile(self):
        # ── Top bar with back button
        top_bar = ctk.CTkFrame(self, fg_color="transparent")
        top_bar.pack(fill="x", padx=16, pady=(12, 0))

        if self._on_back:
            ctk.CTkButton(
                top_bar,
                text="← Back",
                fg_color="transparent",
                text_color=DARK,
                font=(FONT_BODY, 12),
                width=60,
                command=self._on_back,
            ).pack(side="left")

        # ⋯  More options (opens block/report dialog)
        ctk.CTkButton(
            top_bar,
            text="⋯",
            fg_color="transparent",
            text_color=DARK,
            font=(FONT_BODY, 18),
            width=36,
            command=self._open_moderation_dialog,
        ).pack(side="right")

        # ── Avatar placeholder
        avatar = ctk.CTkFrame(
            self, width=80, height=80,
            fg_color=SAGE, corner_radius=40
        )
        avatar.pack(pady=(10, 6))
        avatar.pack_propagate(False)

        initials = (self._subject.name or "?")[0].upper()
        ctk.CTkLabel(
            avatar,
            text=initials,
            font=(FONT_HEADING, 28, "bold"),
            text_color=WHITE,
        ).place(relx=0.5, rely=0.5, anchor="center")

        # ── Name + location
        ctk.CTkLabel(
            self,
            text=self._subject.name,
            font=(FONT_HEADING, 18, "bold"),
            text_color=DARK,
        ).pack()

        sub_parts = [
            p for p in [
                getattr(self._subject, "college_or_company", None),
                getattr(self._subject, "city", None),
            ] if p
        ]
        if sub_parts:
            ctk.CTkLabel(
                self,
                text="  ·  ".join(sub_parts),
                font=(FONT_BODY, 12),
                text_color="#888",
            ).pack(pady=(2, 4))

        # ── Rating badge
        SellerRatingBadge(self, seller_id=self._subject.id).pack(pady=(0, 8))

        # ── Follower stats row
        stats_row = ctk.CTkFrame(self, fg_color="transparent")
        stats_row.pack(pady=(0, 10))

        followers = get_follower_count(self._subject.id)
        following = get_following_count(self._subject.id)

        for label, count in [("Followers", followers), ("Following", following)]:
            stat = ctk.CTkFrame(stats_row, fg_color="#EDE8FF", corner_radius=8)
            stat.pack(side="left", padx=8, ipadx=12, ipady=6)
            ctk.CTkLabel(
                stat,
                text=str(count),
                font=(FONT_HEADING, 16, "bold"),
                text_color=DARK,
            ).pack()
            ctk.CTkLabel(
                stat,
                text=label,
                font=(FONT_BODY, 10),
                text_color="#888",
            ).pack()

        # ── Follow button (only shown when viewing someone else's profile)
        if self._viewer.id != self._subject.id:
            FollowButton(
                self,
                current_user=self._viewer,
                target_user=self._subject,
                on_change=self._on_follow_change,
            ).pack(pady=(0, 14))

        # ── Reviews panel
        ctk.CTkFrame(self, fg_color="#DDD", height=1).pack(fill="x", padx=20, pady=4)

        ReviewsPanel(self, seller_id=self._subject.id).pack(
            fill="both", expand=True, padx=16, pady=(8, 16)
        )

    # ── Callbacks ─────────────────────────────────────────────────────────

    def _open_moderation_dialog(self):
        ReportBlockDialog(
            self,
            current_user=self._viewer,
            target_user=self._subject,
            on_block=self._on_blocked,
        )

    def _on_blocked(self):
        """After blocking, rebuild the screen showing the placeholder."""
        for w in self.winfo_children():
            w.destroy()
        self._build_blocked_placeholder()

    def _on_follow_change(self, is_now_following: bool):
        """Optionally refresh follower count display on follow toggle."""
        # Full rebuild is the simplest approach for now
        for w in self.winfo_children():
            w.destroy()
        self._build_profile()
