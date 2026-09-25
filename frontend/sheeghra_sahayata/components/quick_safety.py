"""Quick Safety Panel — persona-based inclusive access layer."""

from __future__ import annotations

import reflex as rx

from sheeghra_sahayata.state import AuthState, TouristState
from sheeghra_sahayata.styles import COLORS
from sheeghra_sahayata.i18n import t


def _women_panel(lang: rx.Var) -> rx.Component:
    return rx.vstack(
        rx.text(
            rx.cond(lang == "hi", t("hi", "helpline_women"), t("en", "helpline_women")),
            font_weight="700",
            color=COLORS["coral"],
            font_size="1.1rem",
        ),
        rx.link(
            "📞 181",
            href="tel:181",
            color=COLORS["teal"],
            font_weight="600",
            font_size="1.25rem",
        ),
        rx.link(
            rx.cond(lang == "hi", t("hi", "police"), t("en", "police")),
            href="https://www.google.com/maps/search/police+station+near+me",
            is_external=True,
            color=COLORS["teal_light"],
        ),
        align_items="start",
        spacing="2",
        width="100%",
    )


def _senior_panel(lang: rx.Var) -> rx.Component:
    """Senior / 60+ demo panel — hospital, ambulance, elder helpline, Accessible Mode."""
    return rx.vstack(
        rx.text(
            rx.cond(
                lang == "hi",
                "वरिष्ठ नागरिक सुरक्षा",
                "Senior Citizen Safety",
            ),
            font_weight="700",
            color=COLORS["teal"],
            font_size="1.15rem",
        ),
        rx.link(
            rx.cond(lang == "hi", "🏥 निकटतम अस्पताल", "🏥 Nearest hospital"),
            href="https://www.google.com/maps/search/hospital+near+me",
            is_external=True,
            color=COLORS["teal"],
            font_weight="700",
            font_size="1.15rem",
        ),
        rx.link(
            rx.cond(lang == "hi", "🚑 एम्बुलेंस 108", "🚑 Ambulance 108"),
            href="tel:108",
            color=COLORS["coral"],
            font_weight="700",
            font_size="1.25rem",
        ),
        rx.link(
            rx.cond(
                lang == "hi",
                "📞 वरिष्ठ नागरिक हेल्पलाइन 14567",
                "📞 Elder Helpline 14567",
            ),
            href="tel:14567",
            color=COLORS["teal_light"],
            font_weight="600",
            font_size="1.05rem",
        ),
        rx.box(
            height="1px",
            width="100%",
            background=COLORS["border"],
            margin_y="0.35rem",
        ),
        rx.hstack(
            rx.vstack(
                rx.text(
                    rx.cond(lang == "hi", t("hi", "accessible"), t("en", "accessible")),
                    font_weight="600",
                    font_size="1.05rem",
                ),
                rx.text(
                    rx.cond(
                        lang == "hi",
                        "बड़ा फ़ॉन्ट · उच्च कंट्रास्ट",
                        "Larger text · higher contrast",
                    ),
                    font_size="0.85rem",
                    color=COLORS["muted"],
                ),
                align_items="start",
                spacing="0",
            ),
            rx.spacer(),
            rx.switch(
                checked=TouristState.accessible_mode,
                on_change=TouristState.toggle_accessible,
                size="3",
            ),
            width="100%",
            align="center",
        ),
        align_items="start",
        spacing="3",
        width="100%",
    )


def _default_panel(lang: rx.Var) -> rx.Component:
    return rx.vstack(
        rx.text(
            rx.cond(lang == "hi", t("hi", "std_emergency"), t("en", "std_emergency")),
            font_weight="600",
        ),
        rx.text("112  ·  Police 100  ·  Ambulance 108  ·  Fire 101", color=COLORS["muted"]),
        align_items="start",
        spacing="2",
        width="100%",
    )


def quick_safety_panel() -> rx.Component:
    """
    Persona rules (demo):
      - female + age 18-35 → Women's Helpline 181 + police
      - age >= 60 → hospital + ambulance + elder helpline + Accessible Mode
      - default → standard emergency numbers
    """
    is_women = (AuthState.user_gender == "female") & (
        (AuthState.user_age_range == "18-35")
        | (AuthState.user_age_range == "18-25")
        | (AuthState.user_age_range == "26-35")
    )
    is_senior = (
        (AuthState.user_age_range == "60+")
        | (AuthState.user_age_range == "60-100")
        | AuthState.user_age_range.contains("60")
    )

    return rx.box(
        rx.heading(
            rx.cond(
                AuthState.user_lang == "hi",
                t("hi", "quick_safety"),
                t("en", "quick_safety"),
            ),
            size="4",
            color=COLORS["teal"],
            margin_bottom="0.75rem",
        ),
        rx.cond(
            is_women,
            _women_panel(AuthState.user_lang),
            rx.cond(
                is_senior,
                _senior_panel(AuthState.user_lang),
                _default_panel(AuthState.user_lang),
            ),
        ),
        padding="1.25rem",
        background=COLORS["card"],
        border=f"1px solid {COLORS['border']}",
        border_radius="16px",
        width="100%",
        box_shadow="0 8px 24px rgba(26,43,42,0.06)",
    )
