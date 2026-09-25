"""
Location ingestion — PRIVACY-BY-DESIGN.

Backend REJECTS location posts unless the trip is currently 'active' (HTTP 403).
Rows are deleted by scripts/cleanup_locations.py once a trip ends, unless
linked to an incident (incident_id IS NOT NULL).
"""

from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from supabase_client import get_supabase

router = APIRouter()


class LocationRequest(BaseModel):
    user_id: str
    trip_id: str
    lat: float
    lon: float
    timestamp: str | None = None


@router.post("")
@router.post("/")
def post_location(body: LocationRequest):
    sb = get_supabase()

    # --- ENFORCE active trip on the SERVER (not just UI) ---
    trip = (
        sb.table("trips")
        .select("id, status, user_id")
        .eq("id", body.trip_id)
        .execute()
    )
    if not trip.data:
        raise HTTPException(status_code=404, detail="Trip not found")

    t = trip.data[0]
    if t["user_id"] != body.user_id:
        raise HTTPException(status_code=403, detail="Trip does not belong to this user")
    if t["status"] != "active":
        # Deliberate privacy gate — no breadcrumbs after End Trip
        raise HTTPException(
            status_code=403,
            detail="Location sharing only allowed while trip.status == 'active'",
        )

    row = {
        "id": str(uuid4()),
        "user_id": body.user_id,
        "trip_id": body.trip_id,
        "lat": body.lat,
        "lon": body.lon,
        "recorded_at": body.timestamp or datetime.utcnow().isoformat(),
        # incident_id left null — cleanup job will delete these after trip ends
    }
    result = sb.table("locations").insert(row).execute()
    return {"message": "Location stored", "location": result.data[0] if result.data else row}
