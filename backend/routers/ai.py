"""
AI Safety Helper — answers tourist safety questions (EN/HI).

Uses a curated knowledge base for reliable demo answers.
If OPENAI_API_KEY is set, can optionally enhance replies (optional).
"""

from __future__ import annotations

import os
import re
from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter()


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)
    language: str = "en"  # en | hi
    user_name: Optional[str] = None
    age_range: Optional[str] = None


class ChatResponse(BaseModel):
    reply: str
    suggestions: list[str] = []


# Curated demo knowledge (no paid API required)
KB = [
    {
        "keys": ["sos", "emergency", "help", "danger", "खतरा", "मदद", "आपात"],
        "en": (
            "If you feel unsafe, tap the red SOS button. It sends your live GPS "
            "location to authorities immediately. Use Silent SOS if you cannot "
            "draw attention. You can also dial 112 (national emergency)."
        ),
        "hi": (
            "अगर आप असुरक्षित महसूस करें तो लाल SOS बटन दबाएँ। यह आपका GPS स्थान "
            "तुरंत प्राधिकरण को भेजता है। ध्यान न खींचना हो तो मूक SOS उपयोग करें। "
            "आप 112 भी डायल कर सकते हैं।"
        ),
    },
    {
        "keys": ["hospital", "ambulance", "108", "doctor", "medical", "अस्पताल", "एम्बुलेंस", "डॉक्टर"],
        "en": (
            "For medical emergencies dial Ambulance 108. Open 'Nearest hospital' "
            "in the Quick Safety Panel for maps. Share your blood group and "
            "allergies in your profile so responders know your needs."
        ),
        "hi": (
            "मेडिकल आपात में एम्बुलेंस 108 डायल करें। त्वरित सुरक्षा पैनल में "
            "'निकटतम अस्पताल' खोलें। प्रोफ़ाइल में ब्लड ग्रुप और एलर्जी भरें ताकि "
            "मदद करने वालों को जानकारी मिले।"
        ),
    },
    {
        "keys": ["senior", "elder", "old", "accessible", "font", "वरिष्ठ", "बुजुर्ग", "सुलभ"],
        "en": (
            "Senior mode shows hospital, Ambulance 108, and Elder Helpline 14567. "
            "Turn on Accessible Mode for larger text and higher contrast. "
            "The SOS button also becomes easier to tap."
        ),
        "hi": (
            "वरिष्ठ मोड में अस्पताल, एम्बुलेंस 108 और हेल्पलाइन 14567 दिखते हैं। "
            "सुलभ मोड चालू करें — बड़ा फ़ॉन्ट और अधिक कंट्रास्ट। SOS बटन दबाना भी आसान होगा।"
        ),
    },
    {
        "keys": ["women", "181", "harass", "महिला", "सुरक्षा"],
        "en": (
            "Women travellers (18–35 persona) see Women's Helpline 181 and a "
            "nearest police station link. In any emergency also use SOS or dial 112."
        ),
        "hi": (
            "महिला यात्रियों के लिए महिला हेल्पलाइन 181 और निकटतम पुलिस स्टेशन लिंक दिखता है। "
            "किसी भी आपात में SOS या 112 का उपयोग करें।"
        ),
    },
    {
        "keys": ["trip", "location", "share", "privacy", "यात्रा", "लोकेशन", "गोपनीयता"],
        "en": (
            "Start Trip to enable location sharing while you travel. End Trip stops "
            "sharing. For privacy, location history is deleted after the trip ends "
            "unless it is linked to an SOS incident."
        ),
        "hi": (
            "यात्रा शुरू करने पर लोकेशन शेयरिंग चालू होती है। यात्रा समाप्त पर बंद हो जाती है। "
            "गोपनीयता के लिए यात्रा के बाद लोकेशन इतिहास मिट जाता है — SOS से जुड़ी लोकेशन छोड़कर।"
        ),
    },
    {
        "keys": ["geofence", "risk", "zone", "danger zone", "जोखिम", "क्षेत्र"],
        "en": (
            "If you enter a high-risk demo zone, a red warning banner appears. "
            "Stay alert, consider ending outdoor plans, or tap SOS if you feel unsafe."
        ),
        "hi": (
            "उच्च-जोखिम क्षेत्र में प्रवेश पर लाल चेतावनी दिखती है। सावधान रहें, "
            "यात्रा योजना बदलें, या असुरक्षित लगने पर SOS दबाएँ।"
        ),
    },
    {
        "keys": ["112", "police", "100", "fire", "101", "पुलिस", "फायर"],
        "en": (
            "India emergency numbers: 112 (all emergencies), Police 100, "
            "Ambulance 108, Fire 101, Women 181, Elder Helpline 14567."
        ),
        "hi": (
            "आपातकालीन नंबर: 112 (सभी आपात), पुलिस 100, एम्बुलेंस 108, "
            "फायर 101, महिला 181, वरिष्ठ नागरिक 14567।"
        ),
    },
    {
        "keys": ["silent", "quiet", "मूक", "चुप"],
        "en": (
            "Silent SOS alerts authorities without a loud confirmation animation — "
            "useful when you need help discreetly. Your location is still sent."
        ),
        "hi": (
            "मूक SOS प्राधिकरण को चुपचाप अलर्ट करता है — ज़ोरदार एनीमेशन के बिना। "
            "आपका स्थान फिर भी भेजा जाता है।"
        ),
    },
]


DEFAULT = {
    "en": (
        "I'm your Sheeghra Sahayata safety helper. Ask me about SOS, trips, "
        "hospitals, helplines, privacy, or Accessible Mode. In immediate danger, "
        "tap SOS or dial 112."
    ),
    "hi": (
        "मैं शीघ्र सहायता का सुरक्षा सहायक हूँ। SOS, यात्रा, अस्पताल, हेल्पलाइन, "
        "गोपनीयता या सुलभ मोड के बारे में पूछें। तुरंत खतरे में SOS दबाएँ या 112 डायल करें।"
    ),
}

SUGGESTIONS = {
    "en": [
        "How does SOS work?",
        "Nearest hospital help",
        "Senior accessible mode",
        "Emergency numbers",
    ],
    "hi": [
        "SOS कैसे काम करता है?",
        "अस्पताल की मदद",
        "सुलभ मोड क्या है?",
        "आपात नंबर बताएँ",
    ],
}


def _match_reply(message: str, lang: str) -> str:
    text = message.lower()
    best = None
    best_hits = 0
    for item in KB:
        hits = sum(1 for k in item["keys"] if k.lower() in text)
        if hits > best_hits:
            best_hits = hits
            best = item
    if best and best_hits > 0:
        return best.get(lang) or best["en"]
    return DEFAULT.get(lang) or DEFAULT["en"]


def _optional_openai(message: str, lang: str, fallback: str) -> str:
    """Optional enhancement if OPENAI_API_KEY is present — otherwise return fallback."""
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        return fallback
    try:
        import httpx

        system = (
            "You are Sheeghra Sahayata, a calm tourist safety assistant for India. "
            "Give short, clear advice. Prefer emergency numbers 112, 108, 181, 14567. "
            f"Reply in {'Hindi' if lang == 'hi' else 'English'}."
        )
        r = httpx.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {key}"},
            json={
                "model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": message},
                ],
                "max_tokens": 220,
            },
            timeout=12.0,
        )
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"].strip()
    except Exception:
        pass
    return fallback


@router.post("/chat", response_model=ChatResponse)
def chat(body: ChatRequest):
    lang = "hi" if body.language.startswith("hi") else "en"
    msg = body.message.strip()
    base = _match_reply(msg, lang)

    # Soft personalization for seniors
    if body.age_range and ("60" in body.age_range):
        extra = (
            " Elder Helpline: 14567."
            if lang == "en"
            else " वरिष्ठ हेल्पलाइन: 14567।"
        )
        if "14567" not in base:
            base = base.rstrip() + extra

    reply = _optional_openai(msg, lang, base)
    return ChatResponse(reply=reply, suggestions=SUGGESTIONS[lang])
