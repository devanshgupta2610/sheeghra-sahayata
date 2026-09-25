"""Auth router — phone signup / login with mocked OTP (any 6-digit code)."""

from datetime import datetime
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from supabase_client import get_supabase

router = APIRouter()


class SignupRequest(BaseModel):
    phone: str = Field(..., min_length=10, description="Phone with country code, e.g. +919876543210")
    name: Optional[str] = None
    emergency_contact: Optional[str] = None
    medical_info: Optional[dict] = None  # {blood_group, allergies}
    language_pref: str = "en"
    age_range: Optional[str] = None
    gender: Optional[str] = None  # optional / skippable
    otp: str = Field(..., min_length=6, max_length=6, description="Any 6-digit code for demo")


class LoginRequest(BaseModel):
    phone: str
    otp: str = Field(..., min_length=6, max_length=6)


def _otp_ok(otp: str) -> bool:
    """DEMO: accept any 6-digit numeric code. Production would verify via Supabase Auth OTP / SMS."""
    return otp.isdigit() and len(otp) == 6


@router.post("/signup")
def signup(body: SignupRequest):
    if not _otp_ok(body.otp):
        raise HTTPException(status_code=400, detail="OTP must be a 6-digit code")

    sb = get_supabase()

    # Upsert profile by phone
    existing = sb.table("profiles").select("*").eq("phone", body.phone).execute()
    if existing.data:
        raise HTTPException(status_code=409, detail="Phone already registered — use /auth/login")

    profile = {
        "id": str(uuid4()),
        "phone": body.phone,
        "name": body.name,
        "emergency_contact": body.emergency_contact,
        "medical_info": body.medical_info or {},
        "language_pref": body.language_pref or "en",
        "age_range": body.age_range,
        "gender": body.gender,
        "created_at": datetime.utcnow().isoformat(),
    }
    result = sb.table("profiles").insert(profile).execute()
    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to create profile")

    user = result.data[0]
    return {
        "message": "Signup successful",
        "user": user,
        # Demo session token — frontend stores this as user_id
        "session": {"user_id": user["id"], "phone": user["phone"]},
    }


@router.post("/login")
def login(body: LoginRequest):
    if not _otp_ok(body.otp):
        raise HTTPException(status_code=400, detail="OTP must be a 6-digit code")

    sb = get_supabase()
    result = sb.table("profiles").select("*").eq("phone", body.phone).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="User not found — please signup first")

    user = result.data[0]
    return {
        "message": "Login successful",
        "user": user,
        "session": {"user_id": user["id"], "phone": user["phone"]},
    }
