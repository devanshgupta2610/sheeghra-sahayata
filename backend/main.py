"""
Sheeghra Sahayata — FastAPI Backend
Serves API + the HTML frontend (senior-friendly web UI).
"""

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from routers import auth, trip, sos, incidents, location, ai

# Prefer backend/web (Railway single-service), else repo-root /web
_HERE = Path(__file__).resolve().parent
_CANDIDATES = [_HERE / "web", _HERE.parent / "web"]
WEB_DIR = next((p for p in _CANDIDATES if p.exists()), _CANDIDATES[-1])

app = FastAPI(
    title="Sheeghra Sahayata API",
    description="Smart Tourist Safety & Emergency Response — Hackathon MVP",
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(trip.router, prefix="/trip", tags=["trip"])
app.include_router(sos.router, prefix="/sos", tags=["sos"])
app.include_router(incidents.router, prefix="/incidents", tags=["incidents"])
app.include_router(location.router, prefix="/location", tags=["location"])
app.include_router(ai.router, prefix="/ai", tags=["ai"])


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/api")
def api_root():
    return {"app": "Sheeghra Sahayata", "status": "ok", "docs": "/docs"}


# --- HTML pages ---
@app.get("/")
def page_landing():
    return FileResponse(WEB_DIR / "index.html")


@app.get("/login")
def page_login():
    return FileResponse(WEB_DIR / "login.html")


@app.get("/home")
def page_home():
    return FileResponse(WEB_DIR / "home.html")


@app.get("/dashboard")
def page_dashboard():
    return FileResponse(WEB_DIR / "dashboard.html")


# Static assets: /static/css, /static/js
if WEB_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(WEB_DIR)), name="static")
