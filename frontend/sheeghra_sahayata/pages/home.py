"""Tourist home — SOS, trip controls, geofence banner, offline SMS mock."""

import reflex as rx

from sheeghra_sahayata.state import AuthState, TouristState
from sheeghra_sahayata.styles import COLORS
from sheeghra_sahayata.i18n import t
from sheeghra_sahayata.components.quick_safety import quick_safety_panel
from sheeghra_sahayata.api import DANGER_ZONE


def _nav() -> rx.Component:
    return rx.hstack(
        rx.heading("Sheeghra Sahayata", size="5", color=COLORS["teal"]),
        rx.spacer(),
        rx.button(
            rx.cond(AuthState.user_lang == "hi", "EN", "हि"),
            on_click=AuthState.toggle_lang,
            variant="soft",
            size="1",
        ),
        rx.link("Dashboard", href="/dashboard", color=COLORS["muted"], font_size="0.85rem"),
        rx.button(
            rx.cond(AuthState.user_lang == "hi", t("hi", "logout"), t("en", "logout")),
            on_click=AuthState.logout,
            variant="ghost",
            size="1",
        ),
        width="100%",
        align="center",
        padding_y="0.5rem",
    )


def _geofence_banner() -> rx.Component:
    return rx.cond(
        TouristState.in_danger_zone,
        rx.box(
            rx.text(
                rx.cond(
                    AuthState.user_lang == "hi",
                    t("hi", "geofence_warn"),
                    t("en", "geofence_warn"),
                ),
                font_weight="700",
                color="white",
                text_align="center",
            ),
            background=COLORS["coral"],
            padding="0.85rem 1rem",
            border_radius="12px",
            width="100%",
            animation="pulse 1.5s ease-in-out infinite",
        ),
    )


def _trip_controls() -> rx.Component:
    return rx.hstack(
        rx.cond(
            TouristState.trip_active,
            rx.button(
                rx.cond(
                    AuthState.user_lang == "hi", t("hi", "end_trip"), t("en", "end_trip")
                ),
                on_click=TouristState.end_trip,
                background=COLORS["amber"],
                color="white",
                size="3",
                flex="1",
            ),
            rx.button(
                rx.cond(
                    AuthState.user_lang == "hi",
                    t("hi", "start_trip"),
                    t("en", "start_trip"),
                ),
                on_click=TouristState.start_trip,
                background=COLORS["teal"],
                color="white",
                size="3",
                flex="1",
            ),
        ),
        rx.button(
            "📍 GPS",
            on_click=TouristState.request_geo,
            variant="outline",
            size="3",
        ),
        width="100%",
        spacing="3",
    )


def _sos_button() -> rx.Component:
    # Accessible Mode (seniors): larger SOS target for easier tapping
    sos_size = rx.cond(TouristState.accessible_mode, "200px", "160px")
    sos_font = rx.cond(TouristState.accessible_mode, "2.4rem", "2rem")
    return rx.center(
        rx.vstack(
            rx.box(
                rx.button(
                    rx.cond(
                        AuthState.user_lang == "hi", t("hi", "sos"), t("en", "sos")
                    ),
                    on_click=TouristState.trigger_sos(False),
                    width=sos_size,
                    height=sos_size,
                    border_radius="50%",
                    background=COLORS["coral"],
                    color="white",
                    font_size=sos_font,
                    font_weight="800",
                    letter_spacing="0.05em",
                    box_shadow="0 12px 40px rgba(214,69,69,0.45)",
                    _hover={"background": COLORS["coral_dark"], "transform": "scale(1.04)"},
                    transition="all 0.2s ease",
                ),
                # Visible SOS confirmation flash (NOT shown for Silent SOS)
                rx.cond(
                    TouristState.sos_flash,
                    rx.box(
                        position="absolute",
                        top="-8px",
                        left="-8px",
                        right="-8px",
                        bottom="-8px",
                        border_radius="50%",
                        border="4px solid #FF6B6B",
                        animation="ping 1s cubic-bezier(0,0,0.2,1) infinite",
                        pointer_events="none",
                    ),
                ),
                position="relative",
            ),
            rx.button(
                rx.cond(
                    AuthState.user_lang == "hi",
                    t("hi", "silent_sos"),
                    t("en", "silent_sos"),
                ),
                on_click=TouristState.trigger_sos(True),
                variant="soft",
                color_scheme="gray",
                size="2",
            ),
            rx.text(
                TouristState.lat.to_string() + ", " + TouristState.lon.to_string(),
                font_size="0.75rem",
                color=COLORS["muted"],
            ),
            align="center",
            spacing="3",
        ),
        padding_y="1.5rem",
    )


def _offline_modal() -> rx.Component:
    """
    Offline fallback UI (demo mock).
    Production would route through India's 112 ERSS / telecom-partnered
    emergency SMS system — not a paid Twilio-style API.
    """
    return rx.cond(
        TouristState.offline_screen,
        rx.box(
            rx.center(
                rx.vstack(
                    rx.heading(
                        rx.cond(
                            AuthState.user_lang == "hi",
                            t("hi", "offline_sms"),
                            t("en", "offline_sms"),
                        ),
                        size="5",
                        color="white",
                    ),
                    rx.text(
                        f"lat={TouristState.lat}, lon={TouristState.lon}",
                        color="#ccc",
                        font_size="0.85rem",
                    ),
                    rx.text(
                        "Demo mock — logged locally. Production → 112 ERSS SMS.",
                        color="#aaa",
                        font_size="0.8rem",
                        text_align="center",
                    ),
                    rx.button(
                        "OK",
                        on_click=TouristState.dismiss_offline,
                        margin_top="1rem",
                        background="white",
                        color=COLORS["ink"],
                    ),
                    align="center",
                    padding="2rem",
                    background="rgba(20,20,20,0.92)",
                    border_radius="16px",
                    max_width="360px",
                ),
                min_height="100vh",
            ),
            position="fixed",
            inset="0",
            z_index="1000",
            background="rgba(0,0,0,0.55)",
        ),
    )


def page() -> rx.Component:
    return rx.box(
        rx.container(
            _nav(),
            rx.text(
                rx.cond(
                    AuthState.user_name != "",
                    "Hi, " + AuthState.user_name,
                    AuthState.user_phone,
                ),
                color=COLORS["muted"],
                margin_bottom="0.5rem",
            ),
            _geofence_banner(),
            rx.box(
                rx.text(
                    rx.cond(
                        TouristState.trip_active,
                        rx.cond(
                            AuthState.user_lang == "hi",
                            t("hi", "trip_active"),
                            t("en", "trip_active"),
                        ),
                        rx.cond(
                            AuthState.user_lang == "hi",
                            t("hi", "trip_inactive"),
                            t("en", "trip_inactive"),
                        ),
                    ),
                    font_weight="600",
                    color=rx.cond(
                        TouristState.trip_active, COLORS["ok"], COLORS["muted"]
                    ),
                ),
                rx.text(
                    f"Demo danger zone: {DANGER_ZONE['name']} "
                    f"({DANGER_ZONE['radius_m']}m)",
                    font_size="0.75rem",
                    color=COLORS["muted"],
                    margin_top="0.25rem",
                ),
                padding="0.75rem 0",
            ),
            _trip_controls(),
            _sos_button(),
            rx.cond(
                TouristState.toast_msg != "",
                rx.callout(
                    TouristState.toast_msg,
                    icon="info",
                    color_scheme="teal",
                    margin_y="0.5rem",
                ),
            ),
            quick_safety_panel(),
            max_width="480px",
            padding_y="1.25rem",
        ),
        _offline_modal(),
        # Accessible mode theme toggle (larger / higher contrast)
        style=rx.cond(
            TouristState.accessible_mode,
            {
                "font_size": "1.25rem",
                "background": "#0A0A0A",
                "color": "#FFFF00",
                "min_height": "100vh",
            },
            {
                "background": (
                    f"radial-gradient(ellipse at 10% 0%, #C8E6E2 0%, transparent 40%),"
                    f"linear-gradient(180deg, {COLORS['bg']} 0%, {COLORS['bg_deep']} 100%)"
                ),
                "min_height": "100vh",
            },
        ),
        width="100%",
        on_mount=TouristState.on_load,
    )
