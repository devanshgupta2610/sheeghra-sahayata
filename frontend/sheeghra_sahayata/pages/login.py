"""Login / Signup page — phone + mocked OTP."""

import reflex as rx

from sheeghra_sahayata.state import AuthState
from sheeghra_sahayata.styles import COLORS
from sheeghra_sahayata.i18n import t


def page() -> rx.Component:
    return rx.box(
        rx.center(
            rx.vstack(
                rx.hstack(
                    rx.heading("Sheeghra Sahayata", size="7", color=COLORS["teal"]),
                    rx.spacer(),
                    rx.button(
                        rx.cond(AuthState.language == "hi", "EN", "हि"),
                        on_click=AuthState.toggle_lang,
                        variant="outline",
                        size="2",
                    ),
                    width="100%",
                    align="center",
                ),
                rx.text(
                    rx.cond(
                        AuthState.language == "hi",
                        t("hi", "tagline"),
                        t("en", "tagline"),
                    ),
                    color=COLORS["muted"],
                    margin_top="-0.5rem",
                ),
                rx.hstack(
                    rx.button(
                        rx.cond(
                            AuthState.language == "hi", t("hi", "login"), t("en", "login")
                        ),
                        on_click=lambda: AuthState.set_mode("login"),
                        variant=rx.cond(AuthState.mode == "login", "solid", "ghost"),
                        color_scheme="teal",
                    ),
                    rx.button(
                        rx.cond(
                            AuthState.language == "hi",
                            t("hi", "signup"),
                            t("en", "signup"),
                        ),
                        on_click=lambda: AuthState.set_mode("signup"),
                        variant=rx.cond(AuthState.mode == "signup", "solid", "ghost"),
                        color_scheme="teal",
                    ),
                    spacing="2",
                ),
                rx.input(
                    placeholder=rx.cond(
                        AuthState.language == "hi", t("hi", "phone"), t("en", "phone")
                    ),
                    value=AuthState.phone,
                    on_change=AuthState.set_phone,
                    width="100%",
                    size="3",
                ),
                rx.input(
                    placeholder=rx.cond(
                        AuthState.language == "hi", t("hi", "otp"), t("en", "otp")
                    ),
                    value=AuthState.otp,
                    on_change=AuthState.set_otp,
                    max_length=6,
                    width="100%",
                    size="3",
                ),
                rx.cond(
                    AuthState.mode == "signup",
                    rx.vstack(
                        rx.input(
                            placeholder=rx.cond(
                                AuthState.language == "hi", t("hi", "name"), t("en", "name")
                            ),
                            value=AuthState.name,
                            on_change=AuthState.set_name,
                            width="100%",
                        ),
                        rx.input(
                            placeholder=rx.cond(
                                AuthState.language == "hi",
                                t("hi", "emergency_contact"),
                                t("en", "emergency_contact"),
                            ),
                            value=AuthState.emergency_contact,
                            on_change=AuthState.set_emergency_contact,
                            width="100%",
                        ),
                        rx.hstack(
                            rx.input(
                                placeholder=rx.cond(
                                    AuthState.language == "hi",
                                    t("hi", "blood_group"),
                                    t("en", "blood_group"),
                                ),
                                value=AuthState.blood_group,
                                on_change=AuthState.set_blood_group,
                                width="50%",
                            ),
                            rx.input(
                                placeholder=rx.cond(
                                    AuthState.language == "hi",
                                    t("hi", "allergies"),
                                    t("en", "allergies"),
                                ),
                                value=AuthState.allergies,
                                on_change=AuthState.set_allergies,
                                width="50%",
                            ),
                            width="100%",
                        ),
                        rx.select(
                            ["18-35", "36-59", "60+", "under-18"],
                            value=AuthState.age_range,
                            on_change=AuthState.set_age_range,
                            width="100%",
                        ),
                        rx.hstack(
                            rx.select(
                                ["", "female", "male", "other"],
                                placeholder=rx.cond(
                                    AuthState.language == "hi",
                                    t("hi", "gender"),
                                    t("en", "gender"),
                                ),
                                value=AuthState.gender,
                                on_change=AuthState.set_gender,
                                width="70%",
                            ),
                            rx.button(
                                "Skip",
                                on_click=AuthState.skip_gender,
                                variant="soft",
                                size="2",
                            ),
                            width="100%",
                            align="center",
                        ),
                        width="100%",
                        spacing="3",
                    ),
                ),
                rx.cond(
                    AuthState.error != "",
                    rx.callout(AuthState.error, icon="triangle_alert", color_scheme="red"),
                ),
                rx.button(
                    rx.cond(
                        AuthState.loading,
                        "…",
                        rx.cond(
                            AuthState.mode == "signup",
                            rx.cond(
                                AuthState.language == "hi",
                                t("hi", "signup"),
                                t("en", "signup"),
                            ),
                            rx.cond(
                                AuthState.language == "hi",
                                t("hi", "login"),
                                t("en", "login"),
                            ),
                        ),
                    ),
                    on_click=AuthState.submit,
                    width="100%",
                    size="3",
                    background=COLORS["teal"],
                    color="white",
                    _hover={"background": COLORS["teal_light"]},
                ),
                rx.link(
                    rx.cond(
                        AuthState.language == "hi",
                        t("hi", "dashboard"),
                        t("en", "dashboard"),
                    ),
                    href="/dashboard",
                    color=COLORS["muted"],
                    font_size="0.9rem",
                    margin_top="0.5rem",
                ),
                spacing="4",
                width="100%",
                max_width="420px",
                padding="2rem",
                background=COLORS["card"],
                border_radius="20px",
                border=f"1px solid {COLORS['border']}",
                box_shadow="0 20px 50px rgba(15,92,86,0.12)",
            ),
            min_height="100vh",
            padding="1.5rem",
        ),
        # Full-bleed atmospheric background
        background=(
            f"radial-gradient(ellipse at 20% 10%, #C8E6E2 0%, transparent 45%),"
            f"radial-gradient(ellipse at 90% 80%, #F0D5C8 0%, transparent 40%),"
            f"linear-gradient(165deg, {COLORS['bg']} 0%, {COLORS['bg_deep']} 100%)"
        ),
        min_height="100vh",
        width="100%",
    )
