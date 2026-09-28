"""
JobShield AI - Free-Text Extraction Fallback
Uses LLM only when deterministic regex/heuristics fail to extract company or job title.
"""

import json
from typing import Optional, Dict
from shared.schemas import ExtractedJobData
from .llm_client import call_llm

EXTRACTION_PROMPT = """You are a job posting metadata extractor. Given this text, extract:
1. "title": Job title (e.g. "Senior Python Developer") or null
2. "company_name": Company name or null
3. "recruiter_email": Recruiter email address or null
4. "salary_text": Mentioned salary or compensation or null

Output ONLY a valid JSON object matching these keys. Do not include markdown codeblocks or explanation.

Input text:
\"\"\"{text}\"\"\"
"""

async def extract_via_llm_fallback(text: str, current_extracted: ExtractedJobData) -> ExtractedJobData:
    """Invokes LLM if crucial fields like company_name or title are missing."""
    if current_extracted.company_name and current_extracted.title:
        return current_extracted

    prompt = EXTRACTION_PROMPT.format(text=text[:3000])
    response = await call_llm(prompt)
    if not response:
        return current_extracted

    try:
        # Strip potential markdown fences
        clean = response.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        data = json.loads(clean)
        if not current_extracted.title and data.get("title"):
            current_extracted.title = data["title"]
        if not current_extracted.company_name and data.get("company_name"):
            current_extracted.company_name = data["company_name"]
        if not current_extracted.recruiter_email and data.get("recruiter_email"):
            current_extracted.recruiter_email = data["recruiter_email"]
            if "@" in data["recruiter_email"]:
                current_extracted.recruiter_domain = data["recruiter_email"].split("@")[1].lower()
        if not current_extracted.salary_text and data.get("salary_text"):
            current_extracted.salary_text = data["salary_text"]
        current_extracted.extraction_method = "llm_fallback"
    except Exception:
        pass

    return current_extracted
