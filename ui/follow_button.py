"""
ui/follow_button.py
────────────────────
A self-contained Follow / Unfollow button widget.

Usage (drop it anywhere you show another user's profile):

    from ui.follow_button import FollowButton

    FollowButton(
        parent,
        current_user=logged_in_user,   # User ORM object
        target_user=profile_user,       # User ORM object
    ).pack()
"""

import customtkinter as ctk
from logic.follow import follow_user, unfollow_user, is_following
from ui.theme import SAGE, WHITE, DARK, FONT_BODY


class FollowButton(ctk.CTkButton):
    """
    A toggle button that handles Follow ↔ Unfollow.

    Parameters
    ──────────
    parent       – parent widget
    current_user – the logged-in User ORM object
    target_user  – the User being viewed
    on_change    – optional callback(is_now_following: bool) after toggle
    """

    def __init__(
        self,
        parent,
        current_user,
        target_user,
        on_change=None,
        **kwargs,
    ):
        self._current = current_user
        self._target = target_user
        self._on_change = on_change
        self._following = is_following(current_user.id, target_user.id)

        super().__init__(
            parent,
            text=self._label(),
            fg_color=self._bg(),
            text_color=self._fg(),
            hover_color=self._hover(),
            font=(FONT_BODY, 13, "bold"),
            corner_radius=20,
            width=110,
            height=34,
            command=self._toggle,
            **kwargs,
        )

    # ── Helpers ──────────────────────────────────────────────────────────

    def _label(self) -> str:
        return "✓ Following" if self._following else "+ Follow"

    def _bg(self) -> str:
        return "#E8E0F0" if self._following else SAGE

    def _fg(self) -> str:
        return DARK if self._following else WHITE

    def _hover(self) -> str:
        return "#D5CAEC" if self._following else "#5A7A5A"

    def _toggle(self):
        if self._following:
            unfollow_user(self._current.id, self._target.id)
            self._following = False
        else:
            follow_user(self._current.id, self._target.id)
            self._following = True

        # Refresh button appearance
        self.configure(
            text=self._label(),
            fg_color=self._bg(),
            text_color=self._fg(),
            hover_color=self._hover(),
        )

        if self._on_change:
            self._on_change(self._following)
