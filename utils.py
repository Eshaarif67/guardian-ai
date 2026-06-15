"""GuardianAI v2 — Utilities"""

import random
import math
from datetime import datetime

# ── RISK ENGINE ───────────────────────────────────────────────
RISK_WEIGHTS = {
    "Emergency Keyword": 40,
    "Scream Detected":   40,
    "Gunshot Detected":  80,
    "Fall Detected":     50,
    "No Response":       30,
    "Manual SOS":       100,
}

KEYWORDS = [
    "help", "bachao", "save me", "emergency", "stop", "sos",
    "mayday", "danger", "fire", "attack", "bachao mujhe",
    "مدد", "بچاو", "help me", "somebody help",
]


def calculate_risk(events: list) -> int:
    return min(sum(RISK_WEIGHTS.get(e, 0) for e in events), 100)


def get_risk_level(score: int):
    if score <= 40:
        return "SAFE",      "#22C55E", "🟢"
    elif score <= 70:
        return "WARNING",   "#F59E0B", "🟡"
    else:
        return "EMERGENCY", "#EF4444", "🔴"


def check_keywords(text: str):
    t = text.lower().strip()
    for kw in KEYWORDS:
        if kw in t:
            return kw
    return None


# ── GPS ────────────────────────────────────────────────────────
def get_simulated_location():
    """Karachi base + small random offset."""
    lat = 24.8607 + random.uniform(-0.02, 0.02)
    lon = 67.0011 + random.uniform(-0.02, 0.02)
    return round(lat, 6), round(lon, 6)


def get_maps_link(lat, lon):
    return f"https://maps.google.com/?q={lat},{lon}"


def get_location_string(lat, lon):
    return f"{lat}° N, {lon}° E"


# ── AUDIO SIMULATION ──────────────────────────────────────────
def simulate_audio_analysis():
    classes  = ["Normal", "Scream Detected", "Gunshot Detected"]
    weights  = [0.70, 0.22, 0.08]
    label    = random.choices(classes, weights=weights)[0]
    conf     = random.uniform(0.78, 0.99) if label != "Normal" else random.uniform(0.88, 0.99)
    return label, round(conf * 100, 1)


# ── FALL SIMULATION ───────────────────────────────────────────
def simulate_accelerometer():
    mode    = random.choices(["normal", "fall"], weights=[0.88, 0.12])[0]
    g_force = round(random.uniform(2.9, 4.6), 2) if mode == "fall" \
              else round(random.uniform(0.85, 1.15), 2)
    return g_force, mode == "fall"


# ── HELPERS ───────────────────────────────────────────────────
def format_timestamp(ts: str) -> str:
    try:
        dt = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
        return dt.strftime("%b %d, %Y · %I:%M %p")
    except Exception:
        return ts


RELATIONSHIP_OPTIONS = ["Family", "Friend", "Spouse", "Parent", "Sibling",
                         "Doctor", "Neighbor", "Colleague", "Other"]
BLOOD_GROUPS = ["A+", "A−", "B+", "B−", "AB+", "AB−", "O+", "O−", "Unknown"]
