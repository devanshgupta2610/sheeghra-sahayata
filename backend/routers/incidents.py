"""Incidents API — used by the Authority Dashboard."""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from supabase_client import get_supabase

router = APIRouter()

VALID_STATUSES = {"active", "acknowledged", "resolved"}


class IncidentStatusUpdate(BaseModel):
    status: str  # active | acknowledged | resolved


@router.get("")
@router.get("/")
def list_incidents(status: Optional[str] = None):
    """
    List incidents for the authority dashboard.
    Poll this every ~5 seconds from the frontend.
    Optional filter: ?status=active
    """
    sb = get_supabase()
    query = (
        sb.table("incidents")
        .select("*, profiles(name, phone, emergency_contact, medical_info)")
        .order("created_at", desc=True)
    )
    if status:
        query = query.eq("status", status)
    result = query.execute()
    return {"incidents": result.data or [], "count": len(result.data or [])}


@router.patch("/{incident_id}")
def update_incident(incident_id: str, body: IncidentStatusUpdate):
    if body.status not in VALID_STATUSES:
        raise HTTPException(
            status_code=400,
            detail=f"status must be one of {sorted(VALID_STATUSES)}",
        )

    sb = get_supabase()
    existing = sb.table("incidents").select("id").eq("id", incident_id).execute()
    if not existing.data:
        raise HTTPException(status_code=404, detail="Incident not found")

    result = (
        sb.table("incidents")
        .update({"status": body.status, "updated_at": datetime.utcnow().isoformat()})
        .eq("id", incident_id)
        .execute()
    )
    return {"message": f"Incident marked {body.status}", "incident": result.data[0]}
