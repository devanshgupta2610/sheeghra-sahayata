"""Trip management — start / end trips. Location sharing only allowed while active."""

from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from supabase_client import get_supabase

router = APIRouter()


class TripStartRequest(BaseModel):
    user_id: str


class TripEndRequest(BaseModel):
    trip_id: str
    user_id: str


@router.post("/start")
def start_trip(body: TripStartRequest):
    sb = get_supabase()

    # End any already-active trips for this user (one active trip at a time)
    active = (
        sb.table("trips")
        .select("id")
        .eq("user_id", body.user_id)
        .eq("status", "active")
        .execute()
    )
    if active.data:
        for t in active.data:
            sb.table("trips").update(
                {"status": "ended", "end_time": datetime.utcnow().isoformat()}
            ).eq("id", t["id"]).execute()

    trip = {
        "id": str(uuid4()),
        "user_id": body.user_id,
        "start_time": datetime.utcnow().isoformat(),
        "status": "active",
    }
    result = sb.table("trips").insert(trip).execute()
    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to start trip")

    return {"message": "Trip started", "trip": result.data[0]}


@router.post("/end")
def end_trip(body: TripEndRequest):
    sb = get_supabase()

    existing = (
        sb.table("trips")
        .select("*")
        .eq("id", body.trip_id)
        .eq("user_id", body.user_id)
        .execute()
    )
    if not existing.data:
        raise HTTPException(status_code=404, detail="Trip not found")

    trip = existing.data[0]
    if trip["status"] != "active":
        raise HTTPException(status_code=400, detail="Trip is already ended")

    result = (
        sb.table("trips")
        .update({"status": "ended", "end_time": datetime.utcnow().isoformat()})
        .eq("id", body.trip_id)
        .execute()
    )

    # PRIVACY NOTE: location rows for this trip will be purged by
    # scripts/cleanup_locations.py (or a Supabase cron) UNLESS linked to an incident.
    return {
        "message": "Trip ended — location history will be purged (privacy cleanup)",
        "trip": result.data[0] if result.data else trip,
    }


@router.get("/active/{user_id}")
def get_active_trip(user_id: str):
    """Helper for the frontend to restore active-trip state on reload."""
    sb = get_supabase()
    result = (
        sb.table("trips")
        .select("*")
        .eq("user_id", user_id)
        .eq("status", "active")
        .order("start_time", desc=True)
        .limit(1)
        .execute()
    )
    return {"trip": result.data[0] if result.data else None}
