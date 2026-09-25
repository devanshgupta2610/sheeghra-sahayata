"""
Sheeghra Sahayata — Reflex Frontend
Python web app: Login → Tourist Home (SOS) → Authority Dashboard
"""

import reflex as rx

from sheeghra_sahayata import styles
from sheeghra_sahayata.pages import login, home, dashboard


app = rx.App(
    style=styles.base_style,
    stylesheets=[
        "https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Noto+Sans+Devanagari:wght@400;600;700&display=swap",
        "https://unpkg.com/leaflet@1.9.4/dist/leaflet.css",
    ],
    head_components=[
        rx.script(src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"),
    ],
)

app.add_page(login.page, route="/", title="Sheeghra Sahayata — Login")
app.add_page(home.page, route="/home", title="Sheeghra Sahayata — Safety")
app.add_page(dashboard.page, route="/dashboard", title="Authority Dashboard")