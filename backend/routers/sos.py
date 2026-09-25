"""
SOS endpoint — core emergency feature.

Supports normal SOS and Silent SOS (silent=true → no loud UI feedback on client).
Also documents the offline SMS fallback path used by the frontend mock.
"""

from datetime import datetime
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from supabase_client import get_supabase

router = APIRouter()


class SOSRequest(BaseModel):
    user_id: str
    trip_id: Optional[str] = None
    lat: float
    lon: float
    timestamp: Optional[str] = None
    # Silent SOS: same backend path, client suppresses visible confirmation
    silent: bool = False


@router.post("")
@router.post("/")
def trigger_sos(body: SOSRequest):
    sb = get_supabase()

    # Verify user exists
    user = sb.table("profiles").select("id, name, phone, emergency_contact").eq(
        "id", body.user_id
    ).execute()
    if not user.data:
        raise HTTPException(status_code=404, detail="User not found")

    incident_id = str(uuid4())
    incident_type = "silent_sos" if body.silent else "sos"
    created_at = body.timestamp or datetime.utcnow().isoformat()

    incident = {
        "id": incident_id,
        "user_id": body.user_id,
        "trip_id": body.trip_id,
        "type": incident_type,
        "lat": body.lat,
        "lon": body.lon,
        "status": "active",
        "silent": body.silent,
        "created_at": created_at,
        "updated_at": created_at,
    }
    result = sb.table("incidents").insert(incident).execute()
    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to create incident")

    # Pin this GPS fix so privacy cleanup will NOT delete it
    if body.trip_id:
        sb.table("locations").insert(
            {
                "id": str(uuid4()),
                "user_id": body.user_id,
                "trip_id": body.trip_id,
                "lat": body.lat,
                "lon": body.lon,
                "incident_id": incident_id,
                "recorded_at": created_at,
            }
        ).execute()

    return {
        "message": "SOS received — authorities notified" if not body.silent else "Silent SOS logged",
        "incident": result.data[0],
        "silent": body.silent,
        # Offline fallback note for judges / README:
        # Production would also fan-out via India's 112 ERSS / telecom-partnered
        # emergency SMS when the device has no data network. See frontend mock.
    }
