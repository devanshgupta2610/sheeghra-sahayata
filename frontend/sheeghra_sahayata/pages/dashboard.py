"""Authority Dashboard — live Leaflet map + incident table."""

import reflex as rx

from sheeghra_sahayata.state import DashboardState
from sheeghra_sahayata.styles import COLORS


def _status_badge(status: rx.Var) -> rx.Component:
    return rx.badge(
        status,
        color_scheme=rx.cond(
            status == "active",
            "red",
            rx.cond(status == "acknowledged", "orange", "green"),
        ),
        variant="solid",
    )


def _incident_row(inc: rx.Var) -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.vstack(
                rx.hstack(
                    rx.text(inc["type"], font_weight="700", text_transform="uppercase"),
                    _status_badge(inc["status"]),
                    spacing="2",
                    align="center",
                ),
                rx.text(
                    inc["lat"].to_string() + ", " + inc["lon"].to_string(),
                    font_size="0.8rem",
                    color=COLORS["muted"],
                ),
                rx.text(
                    inc["created_at"].to_string(),
                    font_size="0.75rem",
                    color=COLORS["muted"],
                ),
                align_items="start",
                spacing="1",
                flex="1",
            ),
            rx.vstack(
                rx.cond(
                    inc["status"] == "active",
                    rx.button(
                        "Acknowledge",
                        on_click=DashboardState.acknowledge(inc["id"]),
                        size="1",
                        color_scheme="orange",
                    ),
                ),
                rx.cond(
                    (inc["status"] == "active") | (inc["status"] == "acknowledged"),
                    rx.button(
                        "Resolve",
                        on_click=DashboardState.resolve(inc["id"]),
                        size="1",
                        color_scheme="green",
                    ),
                ),
                spacing="2",
            ),
            width="100%",
            align="start",
        ),
        padding="1rem",
        background=COLORS["card"],
        border=f"1px solid {COLORS['border']}",
        border_radius="12px",
        width="100%",
        margin_bottom="0.75rem",
    )


def page() -> rx.Component:
    return rx.box(
        rx.container(
            rx.hstack(
                rx.vstack(
                    rx.heading("Authority Dashboard", size="7", color=COLORS["teal"]),
                    rx.text(
                        "Live incidents · polling every 5s",
                        color=COLORS["muted"],
                    ),
                    align_items="start",
                    spacing="1",
                ),
                rx.spacer(),
                rx.link("← Tourist app", href="/home", color=COLORS["teal"]),
                rx.badge(
                    rx.cond(DashboardState.polling, "● LIVE", "○ idle"),
                    color_scheme=rx.cond(DashboardState.polling, "green", "gray"),
                ),
                width="100%",
                align="center",
                margin_bottom="1.25rem",
            ),
            # Leaflet map (full HTML document in iframe so JS executes)
            rx.el.iframe(
                src_doc=DashboardState.map_html,
                width="100%",
                height="360px",
                style={
                    "border": f"1px solid {COLORS['border']}",
                    "border_radius": "12px",
                    "margin_bottom": "1.25rem",
                    "background": COLORS["card"],
                },
            ),
            rx.cond(
                DashboardState.message != "",
                rx.callout(DashboardState.message, icon="info", margin_bottom="0.75rem"),
            ),
            rx.hstack(
                rx.heading("Incidents", size="4"),
                rx.spacer(),
                rx.button("Refresh", on_click=DashboardState.fetch_incidents, size="1"),
                width="100%",
                margin_bottom="0.75rem",
            ),
            rx.foreach(DashboardState.incidents, _incident_row),
            max_width="900px",
            padding_y="1.5rem",
        ),
        background=(
            f"linear-gradient(180deg, {COLORS['bg']} 0%, #DCE8E6 100%)"
        ),
        min_height="100vh",
        width="100%",
        on_mount=DashboardState.on_load,
    )
