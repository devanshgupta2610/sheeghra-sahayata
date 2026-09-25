# Reflex config — Sheeghra Sahayata frontend
import reflex as rx
from reflex.plugins.sitemap import SitemapPlugin
from reflex.plugins import RadixThemesPlugin

config = rx.Config(
    app_name="sheeghra_sahayata",
    frontend_port=3000,
    backend_port=3001,
    api_url="http://localhost:3001",
    plugins=[RadixThemesPlugin()],
    disable_plugins=[SitemapPlugin],
)
