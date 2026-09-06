"""Gemini AI helper — uses the new google-genai SDK."""

import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

_client = None


def _get_client():
    global _client
    if _client is None:
        api_key = os.getenv("GEMINI_API_KEY", "")
        if not api_key:
            return None
        _client = genai.Client(api_key=api_key)
    return _client


def ask_gemini(prompt: str, hospital_context: str = "") -> str:
    """
    Send a prompt to Gemini 2.0 Flash with optional hospital data context.
    Returns the text response or an error message string.
    """
    client = _get_client()
    if client is None:
        return (
            "⚠️ Gemini API key not configured. "
            "Please set GEMINI_API_KEY in your .env file or sidebar input."
        )

    system_prompt = (
        "You are an expert hospital operations AI assistant. "
        "You analyze real-time hospital resource data (bed occupancy, ICU availability, "
        "and equipment status) and provide concise, actionable clinical/operational insights. "
        "Always be specific, professional, and prioritize patient safety recommendations.\n\n"
    )

    if hospital_context:
        full_prompt = (
            f"{system_prompt}"
            f"Current Hospital Resource Snapshot:\n{hospital_context}\n\n"
            f"User Question: {prompt}"
        )
    else:
        full_prompt = f"{system_prompt}User Question: {prompt}"

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=full_prompt,
        )
        return response.text
    except Exception as exc:
        return f"❌ Gemini API error: {exc}"


def generate_alert_summary(kpi: dict) -> str:
    """Ask Gemini to produce a one-paragraph operational alert summary."""
    context = (
        f"- Total beds: {kpi['total_beds']}, occupied: {kpi['occupied_beds']}, "
        f"available: {kpi['available_beds']}, avg occupancy: {kpi['avg_occupancy']}%\n"
        f"- ICU: {kpi['icu_total']} total, {kpi['icu_occupied']} occupied, "
        f"{kpi['icu_available']} available ({kpi['icu_pct']}% occupancy)\n"
        f"- Equipment: {kpi['total_equip']} units — "
        f"{kpi['op_equipment']} operational, {kpi['in_use_equip']} in use, "
        f"{kpi['maint_equip']} under maintenance, {kpi['offline_equip']} offline\n"
        f"- Critical departments (>=90% occupancy): "
        f"{', '.join(kpi['critical_depts']) if kpi['critical_depts'] else 'None'}\n"
    )
    prompt = (
        "Based on the snapshot above, write a concise (3-5 sentence) operational "
        "alert summary for the charge nurse or hospital administrator. "
        "Highlight the most urgent issues and suggest immediate actions."
    )
    return ask_gemini(prompt, context)
