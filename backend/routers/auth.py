"""Auth router — phone signup / login with mocked OTP (any 6-digit code)."""

from datetime import datetime
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from supabase_client import get_supabase

router = APIRouter()


class SignupRequest(BaseModel):
    phone: str = Field(..., description="10-digit mobile or +91XXXXXXXXXX")
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


def _normalize_phone(phone: str) -> str:
    """
    Accept 10-digit Indian mobiles (or +91 / 91 prefixed) and store as +91XXXXXXXXXX.
    Rejects anything that does not resolve to exactly 10 national digits.
    """
    digits = "".join(ch for ch in (phone or "") if ch.isdigit())
    if digits.startswith("91") and len(digits) == 12:
        digits = digits[2:]
    if len(digits) != 10:
        raise HTTPException(
            status_code=400,
            detail="Phone must be a 10-digit mobile number",
        )
    return f"+91{digits}"


@router.post("/signup")
def signup(body: SignupRequest):
    if not _otp_ok(body.otp):
        raise HTTPException(status_code=400, detail="OTP must be a 6-digit code")

    phone = _normalize_phone(body.phone)
    sb = get_supabase()

    existing = sb.table("profiles").select("*").eq("phone", phone).execute()
    if existing.data:
        raise HTTPException(status_code=409, detail="Phone already registered — use /auth/login")

    profile = {
        "id": str(uuid4()),
        "phone": phone,
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
        "session": {"user_id": user["id"], "phone": user["phone"]},
    }


@router.post("/login")
def login(body: LoginRequest):
    if not _otp_ok(body.otp):
        raise HTTPException(status_code=400, detail="OTP must be a 6-digit code")

    phone = _normalize_phone(body.phone)
    sb = get_supabase()
    result = sb.table("profiles").select("*").eq("phone", phone).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="User not found — please signup first")

    user = result.data[0]
    return {
        "message": "Login successful",
        "user": user,
        "session": {"user_id": user["id"], "phone": user["phone"]},
    }
