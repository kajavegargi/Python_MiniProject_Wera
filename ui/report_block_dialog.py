"""
ui/report_block_dialog.py
──────────────────────────
A modal dialog with two tabs: "Block User" and "Report User".

Usage:

    from ui.report_block_dialog import ReportBlockDialog

    ReportBlockDialog(
        parent,
        current_user=logged_in_user,
        target_user=profile_user,
        on_block=lambda: refresh_screen(),   # optional
    )
"""

import customtkinter as ctk
from logic.moderation import (
    block_user, unblock_user, is_blocked,
    report_user, VALID_REASONS,
)
from ui.theme import (
    LAVENDER, WHITE, DARK, SAGE, FONT_HEADING, FONT_BODY,
)


class ReportBlockDialog(ctk.CTkToplevel):
    """
    Modal window with Block and Report tabs.

    Parameters
    ──────────
    parent       – parent widget (usually the main app window)
    current_user – logged-in User ORM object
    target_user  – the User being reported/blocked
    on_block     – optional callback after a successful block/unblock
    """

    def __init__(self, parent, current_user, target_user, on_block=None):
        super().__init__(parent)

        self._me = current_user
        self._them = target_user
        self._on_block = on_block

        self.title(f"Report or Block — {target_user.name}")
        self.geometry("440x420")
        self.resizable(False, False)
        self.configure(fg_color=LAVENDER)
        self.grab_set()  # modal

        self._build_header()
        self._build_tabs()

    # ── Header ────────────────────────────────────────────────────────────

    def _build_header(self):
        ctk.CTkLabel(
            self,
            text=f"@{self._them.name}",
            font=(FONT_HEADING, 16, "bold"),
            text_color=DARK,
        ).pack(pady=(20, 4))
        ctk.CTkLabel(
            self,
            text="Choose an action below",
            font=(FONT_BODY, 12),
            text_color="#888",
        ).pack(pady=(0, 10))

    # ── Tab container ─────────────────────────────────────────────────────

    def _build_tabs(self):
        tab = ctk.CTkTabview(self, fg_color=WHITE, corner_radius=12)
        tab.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        tab.add("🚫  Block")
        tab.add("⚑  Report")

        self._build_block_tab(tab.tab("🚫  Block"))
        self._build_report_tab(tab.tab("⚑  Report"))

    # ── Block tab ─────────────────────────────────────────────────────────

    def _build_block_tab(self, frame):
        currently_blocked = is_blocked(self._me.id, self._them.id)

        ctk.CTkLabel(
            frame,
            text=(
                f"You have blocked {self._them.name}.\n"
                "Their listings and messages are hidden from you."
                if currently_blocked
                else f"Blocking {self._them.name} will:\n"
                     "• Hide their listings from your feed\n"
                     "• Prevent them from messaging you\n"
                     "• Remove any mutual follows"
            ),
            font=(FONT_BODY, 12),
            text_color=DARK,
            justify="left",
            wraplength=360,
        ).pack(padx=16, pady=(16, 20), anchor="w")

        label = "Unblock User" if currently_blocked else "Block User"
        color = SAGE if currently_blocked else "#C0392B"

        self._block_btn = ctk.CTkButton(
            frame,
            text=label,
            fg_color=color,
            text_color=WHITE,
            font=(FONT_BODY, 13, "bold"),
            corner_radius=8,
            command=self._toggle_block,
        )
        self._block_btn.pack(padx=16, fill="x")

        self._block_status = ctk.CTkLabel(
            frame, text="", font=(FONT_BODY, 11), text_color=SAGE
        )
        self._block_status.pack(pady=6)

    def _toggle_block(self):
        if is_blocked(self._me.id, self._them.id):
            unblock_user(self._me.id, self._them.id)
            self._block_status.configure(
                text=f"✓ {self._them.name} has been unblocked."
            )
            self._block_btn.configure(
                text="Block User", fg_color="#C0392B"
            )
        else:
            block_user(self._me.id, self._them.id)
            self._block_status.configure(
                text=f"✓ {self._them.name} has been blocked."
            )
            self._block_btn.configure(
                text="Unblock User", fg_color=SAGE
            )

        if self._on_block:
            self._on_block()

    # ── Report tab ────────────────────────────────────────────────────────

    def _build_report_tab(self, frame):
        ctk.CTkLabel(
            frame,
            text="Why are you reporting this user?",
            font=(FONT_BODY, 12, "bold"),
            text_color=DARK,
        ).pack(padx=16, pady=(14, 6), anchor="w")

        self._reason_var = ctk.StringVar(value=VALID_REASONS[0])
        reason_menu = ctk.CTkOptionMenu(
            frame,
            values=VALID_REASONS,
            variable=self._reason_var,
            fg_color=WHITE,
            text_color=DARK,
            button_color=SAGE,
            button_hover_color="#5A7A5A",
            font=(FONT_BODY, 12),
        )
        reason_menu.pack(padx=16, fill="x")

        ctk.CTkLabel(
            frame,
            text="Additional details (optional)",
            font=(FONT_BODY, 11),
            text_color="#888",
        ).pack(padx=16, pady=(12, 4), anchor="w")

        self._details_box = ctk.CTkTextbox(
            frame,
            height=70,
            font=(FONT_BODY, 12),
            fg_color="#F5F0FF",
            text_color=DARK,
            corner_radius=8,
        )
        self._details_box.pack(padx=16, fill="x")

        self._report_btn = ctk.CTkButton(
            frame,
            text="Submit Report",
            fg_color="#E67E22",
            text_color=WHITE,
            font=(FONT_BODY, 13, "bold"),
            corner_radius=8,
            command=self._submit_report,
        )
        self._report_btn.pack(padx=16, pady=(12, 0), fill="x")

        self._report_status = ctk.CTkLabel(
            frame, text="", font=(FONT_BODY, 11), text_color=SAGE, wraplength=360
        )
        self._report_status.pack(pady=6)

    def _submit_report(self):
        reason = self._reason_var.get()
        details = self._details_box.get("1.0", "end").strip()

        ok, msg = report_user(
            reporter_id=self._me.id,
            reported_id=self._them.id,
            reason=reason,
            details=details,
        )

        color = SAGE if ok else "#C0392B"
        self._report_status.configure(text=msg, text_color=color)

        if ok:
            self._report_btn.configure(state="disabled")
