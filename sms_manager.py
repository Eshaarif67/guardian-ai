"""
GuardianAI v2 — SMS Manager
Real SMS via Twilio. Falls back to simulation if credentials not set.
"""

import os
import streamlit as st
from datetime import datetime

EMERGENCY_TEMPLATE = """🆘 EMERGENCY ALERT — GuardianAI

{name} may be in DANGER and needs immediate help!

📍 Location: {location}
🗺️ Maps: {maps_link}
⚡ Detected: {trigger}
🔴 Risk Score: {score}/100
⏰ Time: {time}

Please call them or go to their location immediately!
— GuardianAI Safety System"""


def build_message(user_name, location_str, maps_link, trigger, score):
    return EMERGENCY_TEMPLATE.format(
        name=user_name,
        location=location_str,
        maps_link=maps_link,
        trigger=trigger,
        score=score,
        time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )


def send_sms_twilio(to_number: str, message: str, account_sid: str,
                    auth_token: str, from_number: str) -> tuple[bool, str]:
    """Send real SMS via Twilio."""
    try:
        from twilio.rest import Client
        client = Client(account_sid, auth_token)
        msg = client.messages.create(
            body=message,
            from_=from_number,
            to=to_number
        )
        return True, f"SID: {msg.sid}"
    except Exception as e:
        return False, str(e)


def send_alerts_to_all(contacts: list, user_name: str, location_str: str,
                        maps_link: str, trigger: str, score: int) -> list:
    """
    Send SMS to all emergency contacts.
    Uses Twilio if credentials are configured in st.secrets or session_state,
    otherwise logs simulation result.
    """
    message = build_message(user_name, location_str, maps_link, trigger, score)

    # Try to get Twilio creds from secrets or session
    try:
        sid   = st.secrets.get("TWILIO_SID", "")
        token = st.secrets.get("TWILIO_TOKEN", "")
        from_ = st.secrets.get("TWILIO_FROM", "")
    except Exception:
        sid = token = from_ = ""

    # Override with user-entered creds if present
    sid   = st.session_state.get("twilio_sid",   sid)
    token = st.session_state.get("twilio_token", token)
    from_ = st.session_state.get("twilio_from",  from_)

    use_twilio = bool(sid and token and from_)
    results = []

    for c in contacts:
        phone = c["phone"].strip()
        if use_twilio:
            ok, detail = send_sms_twilio(phone, message, sid, token, from_)
            status = "✅ Sent (Twilio)" if ok else f"❌ Failed: {detail}"
        else:
            # Simulation mode — log to console
            print(f"[SMS SIM] To: {phone}\n{message}\n")
            ok = True
            status = "📋 Logged (Add Twilio credentials to send real SMS)"

        results.append({
            "name":   c["name"],
            "phone":  phone,
            "status": status,
            "ok":     ok,
            "time":   datetime.now().strftime("%H:%M:%S"),
            "real":   use_twilio,
        })

    return results, message
