"""
API helpers + pure-Python geofence (haversine).

DANGER ZONE (demo): circle around Connaught Place, New Delhi.
"""

from __future__ import annotations

import math
import os
from typing import Any, Optional

import httpx
from dotenv import load_dotenv

load_dotenv()

# Backend URL — override with SHEEGHRA_API_URL env / Reflex config
API_URL = os.getenv("SHEEGHRA_API_URL", "http://localhost:8000")

# --- Hardcoded danger zone for geofence demo ---
DANGER_ZONE = {
    "name": "Connaught Place High-Risk Demo Zone",
    "lat": 28.6315,
    "lon": 77.2167,
    "radius_m": 800,  # metres
}


def haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance in metres (pure Python)."""
    r = 6371000.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def inside_danger_zone(lat: float, lon: float) -> bool:
    d = haversine_m(lat, lon, DANGER_ZONE["lat"], DANGER_ZONE["lon"])
    return d <= DANGER_ZONE["radius_m"]


def api(method: str, path: str, json: Optional[dict] = None, timeout: float = 12.0) -> dict[str, Any]:
    url = f"{API_URL.rstrip('/')}{path}"
    try:
        with httpx.Client(timeout=timeout) as client:
            r = client.request(method, url, json=json)
            data = r.json() if r.content else {}
            if r.status_code >= 400:
                detail = data.get("detail", r.text)
                raise RuntimeError(f"{r.status_code}: {detail}")
            return data
    except httpx.HTTPError as e:
        # Signal offline to caller
        raise ConnectionError(str(e)) from e
