"""Shared styles — warm safekeeping palette (not purple-default AI look)."""

# Deep teal + coral emergency accent on soft sand atmosphere
COLORS = {
    "bg": "#F7F3EC",
    "bg_deep": "#E8E0D4",
    "ink": "#1A2B2A",
    "muted": "#5C6B6A",
    "teal": "#0F5C56",
    "teal_light": "#1A7A72",
    "coral": "#D64545",
    "coral_dark": "#B83232",
    "amber": "#C47A1A",
    "ok": "#2D6A4F",
    "card": "#FFFDF9",
    "border": "#D9CFC0",
    "hi_contrast_bg": "#0A0A0A",
    "hi_contrast_fg": "#FFFF00",
}

base_style = {
    "font_family": "'DM Sans', 'Noto Sans Devanagari', sans-serif",
    "background": f"linear-gradient(165deg, {COLORS['bg']} 0%, {COLORS['bg_deep']} 55%, #D4E5E2 100%)",
    "color": COLORS["ink"],
    "min_height": "100vh",
}

accessible_style = {
    "font_size": "1.25rem",
    "background": COLORS["hi_contrast_bg"],
    "color": COLORS["hi_contrast_fg"],
}
