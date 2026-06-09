import customtkinter as ctk
from ui.theme import (DEEP_PURPLE, HOT_PINK, ELECTRIC_BLUE, NEON_LIME,
                      LAVENDER, LIGHT_PURPLE, MUTED_PURPLE, WHITE,
                      DARK, LIGHT_GRAY, FONTS)
from logic.chat import send_message, get_messages


class ChatScreen(ctk.CTkFrame):
    def __init__(self, master, user, match, listing, other_user, on_back):
        super().__init__(master, fg_color=LAVENDER)
        self.user       = user
        self.match      = match
        self.listing    = listing
        self.other_user = other_user
        self.on_back    = on_back
        self._poll_id   = None
        self._build()
        self._schedule_poll()

    def _build(self):
        self._build_navbar()
        self._build_safety_bar()
        self._build_message_area()
        self._build_input_bar()
        self._load_messages()

    # ── Navbar ────────────────────────────────────────────────
    def _build_navbar(self):
        nav = ctk.CTkFrame(self, fg_color=DEEP_PURPLE, height=60, corner_radius=0)
        nav.pack(fill="x")
        nav.pack_propagate(False)

        ctk.CTkButton(nav, text="← Back", width=90, height=34,
                      fg_color="transparent",
                      border_width=1, border_color=MUTED_PURPLE,
                      text_color=MUTED_PURPLE,
                      hover_color="#2D0A4E",
                      font=FONTS["small"], corner_radius=10,
                      command=self._go_back).pack(side="left", padx=16)

        title_col = ctk.CTkFrame(nav, fg_color="transparent")
        title_col.pack(side="left", padx=8)
        ctk.CTkLabel(title_col,
                     text=f"💬 {self.listing.title}",
                     font=("Outfit", 16, "bold"),
                     text_color=WHITE).pack(anchor="w")
        ctk.CTkLabel(title_col,
                     text=f"with {self.other_user.name}",
                     font=FONTS["small"],
                     text_color=NEON_LIME).pack(anchor="w")

        dot_row = ctk.CTkFrame(nav, fg_color="transparent")
        dot_row.pack(side="right", padx=20)
        ctk.CTkFrame(dot_row, fg_color=NEON_LIME,
                     width=10, height=10, corner_radius=5).pack(side="left")
        ctk.CTkLabel(dot_row, text="  Active",
                     font=FONTS["small"], text_color=NEON_LIME).pack(side="left")

        ctk.CTkFrame(self, fg_color=HOT_PINK, height=3, corner_radius=0).pack(fill="x")

    # ── Safety notice ─────────────────────────────────────────
    def _build_safety_bar(self):
        bar = ctk.CTkFrame(self, fg_color="#FFF3E0", height=34, corner_radius=0)
        bar.pack(fill="x")
        bar.pack_propagate(False)
        ctk.CTkLabel(bar,
                     text="⚠️  For your safety, do not share personal contact details inside Wera chat.",
                     font=FONTS["small"],
                     text_color="#A0522D").pack(side="left", padx=16)

    # ── Message area ──────────────────────────────────────────
    def _build_message_area(self):
        self.msg_frame = ctk.CTkScrollableFrame(self, fg_color=LAVENDER)
        self.msg_frame.pack(fill="both", expand=True, padx=16, pady=12)

    # ── Input bar ─────────────────────────────────────────────
    def _build_input_bar(self):
        bar = ctk.CTkFrame(self, fg_color=WHITE, height=70, corner_radius=0)
        bar.pack(fill="x")
        bar.pack_propagate(False)

        inner = ctk.CTkFrame(bar, fg_color="transparent")
        inner.pack(fill="x", padx=16, pady=12)

        self.msg_entry = ctk.CTkEntry(inner,
                                      placeholder_text="Type a message...",
                                      height=44,
                                      fg_color=LIGHT_PURPLE,
                                      border_color=LIGHT_PURPLE,
                                      text_color=DARK,
                                      placeholder_text_color=MUTED_PURPLE,
                                      corner_radius=14)
        self.msg_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.msg_entry.bind("<Return>", lambda e: self._send())

        ctk.CTkButton(inner, text="Send 💌", width=100, height=44,
                      fg_color=HOT_PINK, hover_color="#D4245F",
                      text_color=WHITE, font=FONTS["button"],
                      corner_radius=14,
                      command=self._send).pack(side="right")

    # ── Message loading ───────────────────────────────────────
    def _load_messages(self):
        for w in self.msg_frame.winfo_children():
            w.destroy()

        messages = get_messages(self.match.id)

        if not messages:
            ctk.CTkLabel(self.msg_frame,
                         text="👋  No messages yet. Say hello!",
                         font=FONTS["body"], text_color=MUTED_PURPLE).pack(pady=60)
            return

        last_date = None
        for msg in messages:
            if msg.sent_at:
                msg_date = msg.sent_at.date()
                if msg_date != last_date:
                    self._render_date_divider(msg.sent_at.strftime("%A, %d %b"))
                    last_date = msg_date
            is_me = msg.sender_id == self.user.id
            self._render_bubble(msg, is_me)

        self.msg_frame.after(100,
            lambda: self.msg_frame._parent_canvas.yview_moveto(1.0))

    def _render_date_divider(self, date_str):
        row = ctk.CTkFrame(self.msg_frame, fg_color="transparent")
        row.pack(fill="x", pady=8)
        ctk.CTkFrame(row, fg_color=LIGHT_GRAY, height=1).pack(fill="x", padx=80, pady=6)
        pill = ctk.CTkFrame(row, fg_color=LIGHT_PURPLE, corner_radius=8)
        pill.pack()
        ctk.CTkLabel(pill, text=f"  {date_str}  ",
                     font=FONTS["tag"], text_color=MUTED_PURPLE).pack(padx=8, pady=3)

    def _render_bubble(self, msg, is_me):
        row = ctk.CTkFrame(self.msg_frame, fg_color="transparent")
        row.pack(fill="x", pady=3)

        if is_me:
            bg, txt, ts, bw, bc = DEEP_PURPLE, WHITE, NEON_LIME, 0, "transparent"
        else:
            bg, txt, ts, bw, bc = WHITE, DARK, MUTED_PURPLE, 2, LIGHT_PURPLE

        bubble = ctk.CTkFrame(row, fg_color=bg, corner_radius=18,
                              border_width=bw, border_color=bc)
        if is_me:
            bubble.pack(side="right", padx=(80, 6))
        else:
            bubble.pack(side="left", padx=(6, 80))

        ctk.CTkLabel(bubble, text=msg.content,
                     font=FONTS["body"], text_color=txt,
                     wraplength=300, justify="left").pack(padx=16, pady=(10, 4))

        time_str = msg.sent_at.strftime("%I:%M %p") if msg.sent_at else ""
        ctk.CTkLabel(bubble, text=time_str,
                     font=FONTS["small"], text_color=ts).pack(
                         anchor="e", padx=16, pady=(0, 8))

    # ── Send ──────────────────────────────────────────────────
    def _send(self):
        content = self.msg_entry.get().strip()
        if not content:
            return
        send_message(self.match.id, self.user.id, content)
        self.msg_entry.delete(0, "end")
        self._load_messages()

    # ── Back — cancel poll before navigating ──────────────────
    def _go_back(self):
        if self._poll_id is not None:
            self.after_cancel(self._poll_id)
            self._poll_id = None
        self.on_back()

    # ── Poll ──────────────────────────────────────────────────
    def _schedule_poll(self):
        self._poll_id = self.after(5000, self._poll)

    def _poll(self):
        # Only poll if widget still exists
        try:
            self.winfo_exists()
        except Exception:
            return
        self._load_messages()
        self._schedule_poll()