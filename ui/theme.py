import customtkinter as ctk

# ── Wera Gen-Z Palette ─────────────────────────────────────────
DEEP_PURPLE   = "#1A0533"   # primary dark — replaces MAROON
HOT_PINK      = "#FF2D78"   # hero accent
ELECTRIC_BLUE = "#3D2BFF"   # secondary action
NEON_LIME     = "#C6F135"   # highlight / pop
LAVENDER      = "#F3EEFF"   # page background — replaces CREAM
LIGHT_PURPLE  = "#E4D5FF"   # card / panel bg
MUTED_PURPLE  = "#9B89C4"   # muted / placeholder text
WHITE         = "#FFFFFF"
DARK          = "#0D0020"   # near-black text
LIGHT_GRAY    = "#EDE8F7"   # subtle borders
GRAPE         = "#6B21A8"   # mid-tone purple for hover states
SAGE          = "#7AEACB"   # keep sage but make it mintier (chat timestamps etc.)
MUTED         = "#9B89C4"   # alias

# Legacy aliases so old imports don't break
CREAM         = LAVENDER
MAROON        = DEEP_PURPLE

# ── Typography ─────────────────────────────────────────────────
# Outfit = geometric sans that reads as modern/youthful in Tkinter
# Fallback chain: Outfit → DM Sans → Helvetica
_DISPLAY = "Outfit"
_BODY    = "DM Sans"
_MONO    = "JetBrains Mono"   # used for price / codes

FONTS = {
    "headline":  (_DISPLAY, 26, "bold"),
    "subhead":   (_DISPLAY, 15, "bold"),
    "body":      (_BODY,    13),
    "small":     (_BODY,    11),
    "button":    (_DISPLAY, 13, "bold"),
    "tag":       (_DISPLAY, 10, "bold"),
    "price":     (_DISPLAY, 20, "bold"),
    "hero":      (_DISPLAY, 42, "bold"),
    "mono":      (_MONO,    12),
}

def apply_theme():
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("dark-blue")