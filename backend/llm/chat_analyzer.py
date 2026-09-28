"""
JobShield AI - Chat Tone & Manipulation Analyzer
Analyzes WhatsApp/Telegram chat transcripts for pressure tactics, urgency coercion, and micro-task scam patterns.
"""

import json
from shared.schemas import ChatManipulationAssessment
from .llm_client import call_llm

CHAT_PROMPT = """Analyze this recruiter communication transcript for manipulative fraud patterns:
Check for:
1. "has_urgency_coercion": boolean (high-pressure time limits, 'offer valid 15 mins')
2. "off_platform_lure": boolean (pushing candidate to Telegram/WhatsApp channels for tasks)
3. "suspicious_compensation_promise": boolean (unrealistic daily/hourly rates for low-skill tasks)
4. "rationale": concise explanation of key red flags found

Output ONLY valid JSON.

Transcript:
\"\"\"{text}\"\"\"
"""

async def analyze_chat_manipulation_llm(text: str) -> ChatManipulationAssessment:
    """Invokes LLM for chat manipulation analysis."""
    prompt = CHAT_PROMPT.format(text=text[:3000])
    response = await call_llm(prompt)
    if not response:
        # Heuristic fallback
        has_urgency = any(w in text.lower() for w in ["hurry", "valid for", "urgent", "immediate"])
        has_off_platform = any(w in text.lower() for w in ["telegram", "whatsapp", "wallet"])
        return ChatManipulationAssessment(
            has_urgency_coercion=has_urgency,
            off_platform_lure=has_off_platform,
            suspicious_compensation_promise=any(w in text.lower() for w in ["earn rs", "like youtube", "rate hotel"]),
            rationale="Pattern-matched manipulation signals in text." if (has_urgency or has_off_platform) else None
        )

    try:
        clean = response.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        data = json.loads(clean)
        return ChatManipulationAssessment(
            has_urgency_coercion=data.get("has_urgency_coercion", False),
            off_platform_lure=data.get("off_platform_lure", False),
            suspicious_compensation_promise=data.get("suspicious_compensation_promise", False),
            rationale=data.get("rationale")
        )
    except Exception:
        return ChatManipulationAssessment(
            has_urgency_coercion=False,
            off_platform_lure=False,
            suspicious_compensation_promise=False,
            rationale=None
        )
