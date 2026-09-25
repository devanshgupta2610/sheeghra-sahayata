"""
Reflex application state — Auth, Tourist (SOS/trip), Authority Dashboard.
"""

from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone
from typing import Any, Optional

import reflex as rx

from sheeghra_sahayata.api import api, inside_danger_zone, DANGER_ZONE
from sheeghra_sahayata.i18n import t


class AuthState(rx.State):
    """Phone OTP signup / login (OTP mocked — any 6 digits)."""

    phone: str = ""
    otp: str = ""
    name: str = ""
    emergency_contact: str = ""
    blood_group: str = ""
    allergies: str = ""
    age_range: str = "18-35"
    gender: str = ""  # optional / skippable
    language: str = "en"
    mode: str = "login"  # login | signup

    user_id: str = rx.LocalStorage("", name="ss_user_id")
    user_name: str = rx.LocalStorage("", name="ss_user_name")
    user_phone: str = rx.LocalStorage("", name="ss_user_phone")
    user_gender: str = rx.LocalStorage("", name="ss_user_gender")
    user_age_range: str = rx.LocalStorage("", name="ss_user_age")
    user_lang: str = rx.LocalStorage("en", name="ss_user_lang")

    error: str = ""
    loading: bool = False

    def set_phone(self, value: str):
        self.phone = value

    def set_otp(self, value: str):
        self.otp = value

    def set_name(self, value: str):
        self.name = value

    def set_emergency_contact(self, value: str):
        self.emergency_contact = value

    def set_blood_group(self, value: str):
        self.blood_group = value

    def set_allergies(self, value: str):
        self.allergies = value

    def set_age_range(self, value: str):
        self.age_range = value

    def set_gender(self, value: str):
        self.gender = value

    def tr(self, key: str) -> str:
        return t(self.user_lang or self.language or "en", key)

    def set_mode(self, mode: str):
        self.mode = mode
        self.error = ""

    def toggle_lang(self):
        new = "hi" if (self.user_lang or self.language) == "en" else "en"
        self.language = new
        self.user_lang = new

    def skip_gender(self):
        self.gender = ""

    async def submit(self):
        self.loading = True
        self.error = ""
        try:
            if len(self.otp) != 6 or not self.otp.isdigit():
                self.error = "Enter any 6-digit OTP (demo)"
                return
            if self.mode == "signup":
                payload = {
                    "phone": self.phone.strip(),
                    "otp": self.otp,
                    "name": self.name or None,
                    "emergency_contact": self.emergency_contact or None,
                    "medical_info": {
                        "blood_group": self.blood_group,
                        "allergies": self.allergies,
                    },
                    "language_pref": self.language,
                    "age_range": self.age_range or None,
                    "gender": self.gender or None,
                }
                data = api("POST", "/auth/signup", payload)
            else:
                data = api(
                    "POST",
                    "/auth/login",
                    {"phone": self.phone.strip(), "otp": self.otp},
                )

            user = data["user"]
            self.user_id = user["id"]
            self.user_name = user.get("name") or ""
            self.user_phone = user.get("phone") or self.phone
            self.user_gender = user.get("gender") or ""
            self.user_age_range = user.get("age_range") or ""
            self.user_lang = user.get("language_pref") or self.language
            return rx.redirect("/home")
        except ConnectionError:
            self.error = "Cannot reach server — check backend is running"
        except Exception as e:
            self.error = str(e)
        finally:
            self.loading = False

    def logout(self):
        self.user_id = ""
        self.user_name = ""
        self.user_phone = ""
        return rx.redirect("/")


class TouristState(rx.State):
    """Home screen: trip controls, SOS, geofence, offline SMS mock."""

    trip_id: str = rx.LocalStorage("", name="ss_trip_id")
    trip_active: bool = False
    lat: float = 28.6139
    lon: float = 77.2090
    geo_ready: bool = False
    in_danger_zone: bool = False

    sos_flash: bool = False  # visible confirmation (NOT for silent)
    toast_msg: str = ""
    offline_mode: bool = False
    offline_screen: bool = False
    accessible_mode: bool = False
    last_sos_id: str = ""

    async def on_load(self):
        auth = await self.get_state(AuthState)
        if not auth.user_id:
            return rx.redirect("/")
        # Restore active trip from backend
        try:
            data = api("GET", f"/trip/active/{auth.user_id}")
            trip = data.get("trip")
            if trip:
                self.trip_id = trip["id"]
                self.trip_active = True
            else:
                self.trip_active = False
                self.trip_id = ""
        except Exception:
            pass
        return TouristState.request_geo

    def request_geo(self):
        """Ask browser for GPS via JS; callback fills lat/lon."""
        return rx.call_script(
            """
            new Promise((resolve) => {
              if (!navigator.geolocation) {
                resolve({lat: 28.6139, lon: 77.2090, ok: false});
                return;
              }
              navigator.geolocation.getCurrentPosition(
                (pos) => resolve({
                  lat: pos.coords.latitude,
                  lon: pos.coords.longitude,
                  ok: true
                }),
                () => resolve({lat: 28.6139, lon: 77.2090, ok: false}),
                {enableHighAccuracy: true, timeout: 8000}
              );
            })
            """,
            callback=TouristState.apply_geo,
        )

    def apply_geo(self, result: dict):
        if not result:
            return
        self.lat = float(result.get("lat", self.lat))
        self.lon = float(result.get("lon", self.lon))
        self.geo_ready = bool(result.get("ok", False))
        self.in_danger_zone = inside_danger_zone(self.lat, self.lon)

    async def start_trip(self):
        auth = await self.get_state(AuthState)
        try:
            data = api("POST", "/trip/start", {"user_id": auth.user_id})
            self.trip_id = data["trip"]["id"]
            self.trip_active = True
            self.toast_msg = "Trip started"
            return TouristState.share_location_once
        except ConnectionError:
            self.offline_mode = True
            self.toast_msg = "Offline — trip start queued (demo)"
        except Exception as e:
            self.toast_msg = str(e)

    async def end_trip(self):
        auth = await self.get_state(AuthState)
        if not self.trip_id:
            return
        try:
            api(
                "POST",
                "/trip/end",
                {"trip_id": self.trip_id, "user_id": auth.user_id},
            )
            self.trip_active = False
            self.trip_id = ""
            self.toast_msg = "Trip ended — locations will be purged (privacy)"
        except Exception as e:
            self.toast_msg = str(e)

    async def share_location_once(self):
        """POST /location only while trip is active (backend also enforces 403)."""
        if not self.trip_active or not self.trip_id:
            return
        auth = await self.get_state(AuthState)
        try:
            api(
                "POST",
                "/location",
                {
                    "user_id": auth.user_id,
                    "trip_id": self.trip_id,
                    "lat": self.lat,
                    "lon": self.lon,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                },
            )
        except Exception:
            pass

    async def trigger_sos(self, silent: bool = False):
        """
        Core demo moment: capture GPS → POST /sos → dashboard picks it up.
        silent=True → no flash animation, quiet toast only.
        """
        auth = await self.get_state(AuthState)
        # Refresh geo via browser script (do not yield raw functions)
        yield TouristState.request_geo
        await asyncio.sleep(0.4)

        payload = {
            "user_id": auth.user_id,
            "trip_id": self.trip_id or None,
            "lat": self.lat,
            "lon": self.lon,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "silent": silent,
        }
        try:
            data = api("POST", "/sos", payload)
            self.last_sos_id = data.get("incident", {}).get("id", "")
            if silent:
                self.sos_flash = False
                self.toast_msg = t(auth.user_lang, "silent_ok")
            else:
                self.sos_flash = True
                self.toast_msg = t(auth.user_lang, "sos_sent")
            # Clear flash without yielding a function reference
            if not silent:
                async with self:
                    pass
                await asyncio.sleep(2.5)
                self.sos_flash = False
        except ConnectionError:
            self.offline_mode = True
            self.offline_screen = True
            print(
                f"[OFFLINE SMS MOCK] Would SMS 112/ERSS with "
                f"lat={self.lat}, lon={self.lon}, user={auth.user_id}"
            )
        except Exception as e:
            self.toast_msg = str(e)

    async def _clear_flash(self):
        await asyncio.sleep(2.5)
        self.sos_flash = False

    async def dismiss_offline(self):
        auth = await self.get_state(AuthState)
        self.offline_screen = False
        self.toast_msg = t(auth.user_lang, "offline_ok")

    def toggle_accessible(self, value: bool = None):
        if value is None:
            self.accessible_mode = not self.accessible_mode
        else:
            self.accessible_mode = bool(value)

    @rx.var
    def safety_persona(self) -> str:
        """Rule-based inclusive access layer."""
        # gender + age from AuthState local storage mirrored fields — use sync read
        return "default"

    async def persona_label(self) -> str:
        auth = await self.get_state(AuthState)
        g = (auth.user_gender or "").lower()
        age = auth.user_age_range or ""
        if g == "female" and age in ("18-35", "18-25", "26-35"):
            return "women"
        if age in ("60+", "60-100") or age.startswith("60"):
            return "senior"
        return "default"


class DashboardState(rx.State):
    """Authority view — poll incidents every 5s + Leaflet markers."""

    incidents: list[dict[str, Any]] = []
    polling: bool = False
    map_html: str = ""
    status_filter: str = ""
    message: str = ""

    async def on_load(self):
        await self.fetch_incidents()
        return DashboardState.poll_loop

    async def fetch_incidents(self):
        try:
            path = "/incidents"
            if self.status_filter:
                path += f"?status={self.status_filter}"
            data = api("GET", path)
            self.incidents = data.get("incidents") or []
            self._rebuild_map()
        except Exception as e:
            self.message = str(e)

    def _rebuild_map(self):
        """Build a full Leaflet HTML document (iframe-safe) for active incidents."""
        markers = []
        for inc in self.incidents:
            if inc.get("status") == "resolved":
                color = "gray"
            elif inc.get("status") == "acknowledged":
                color = "orange"
            else:
                color = "red"
            markers.append(
                {
                    "lat": inc["lat"],
                    "lon": inc["lon"],
                    "color": color,
                    "label": f"{inc.get('type','sos').upper()} · {inc.get('status')}",
                    "id": str(inc.get("id", ""))[:8],
                }
            )
        markers_json = json.dumps(markers)
        center_lat = markers[0]["lat"] if markers else 28.6139
        center_lon = markers[0]["lon"] if markers else 77.2090
        # Full HTML document so Leaflet JS runs inside an iframe
        self.map_html = f"""<!DOCTYPE html>
<html><head>
<meta charset="utf-8"/>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>html,body,#map{{margin:0;height:100%;width:100%;background:#e8e0d4}}</style>
</head><body>
<div id="map"></div>
<script>
var map = L.map('map').setView([{center_lat}, {center_lon}], 11);
L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
  attribution: '&copy; OpenStreetMap', maxZoom: 19
}}).addTo(map);
var pts = {markers_json};
pts.forEach(function(p) {{
  var icon = L.divIcon({{
    className: '',
    html: '<div style="background:'+p.color+';width:16px;height:16px;border-radius:50%;border:2px solid #fff;box-shadow:0 1px 4px rgba(0,0,0,.4)"></div>',
    iconSize: [16,16], iconAnchor: [8,8]
  }});
  L.marker([p.lat, p.lon], {{icon: icon}}).addTo(map)
    .bindPopup('<b>'+p.label+'</b><br/>#'+p.id);
}});
</script>
</body></html>"""

    @rx.event(background=True)
    async def poll_loop(self):
        """Poll GET /incidents every 5 seconds while on dashboard."""
        async with self:
            self.polling = True
        for _ in range(360):  # ~30 min max for a demo session
            try:
                async with self:
                    await self.fetch_incidents()
            except Exception:
                pass
            await asyncio.sleep(5)
        async with self:
            self.polling = False

    async def set_status(self, incident_id: str, status: str):
        try:
            api("PATCH", f"/incidents/{incident_id}", {"status": status})
            self.message = f"Marked {status}"
            await self.fetch_incidents()
        except Exception as e:
            self.message = str(e)

    def acknowledge(self, incident_id: str):
        return DashboardState.set_status(incident_id, "acknowledged")

    def resolve(self, incident_id: str):
        return DashboardState.set_status(incident_id, "resolved")
