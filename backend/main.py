"""
JobShield AI - FastAPI Backend Orchestrator
Recruitment Integrity & Opportunity Trust Engine
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, List
import uuid
import json
from pathlib import Path
from datetime import datetime, timezone

from shared.schemas import (
    JobAnalysisRequest,
    JobShieldReport,
    ExtractedJobData,
    DomainReport,
    TrustScoreBreakdown,
    TaskFairnessAssessment,
    ChatManipulationAssessment
)
from backend.deterministic.pipeline import run_deterministic_pipeline
from backend.llm.fallback_extractor import extract_via_llm_fallback
from backend.llm.task_judge import judge_task_fairness_llm
from backend.llm.chat_analyzer import analyze_chat_manipulation_llm
from backend.llm.report_narrator import narrate_report

app = FastAPI(
    title="JobShield AI",
    description="Recruitment Integrity & Opportunity Trust Engine API",
    version="1.0.0"
)

# Enable CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
async def health_check():
    return {
        "status": "online",
        "service": "JobShield AI",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.get("/api/test-set")
async def get_test_set():
    """Returns the benchmark labeled test set for UI testing and demos."""
    test_set_path = Path(__file__).resolve().parent.parent / "data" / "labeled_test_set.json"
    if not test_set_path.exists():
        raise HTTPException(status_code=404, detail="Test set not found")
    with open(test_set_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data

@app.post("/api/analyze", response_model=JobShieldReport)
async def analyze_job(request: JobAnalysisRequest):
    """
    Main analysis pipeline:
    1. Runs deterministic tool layer (RDAP, DNS, Typosquat, Regex, ATS, Scoring).
    2. Runs narrow LLM calls (Metadata fallback, Task judgment, Chat analysis, Report narration).
    3. Assembles evidence-linked JobShieldReport.
    """
    if not request.raw_text or len(request.raw_text.strip()) < 10:
        raise HTTPException(status_code=400, detail="Please provide job text or communication transcript (at least 10 characters).")

    # Step 1: Run Deterministic Core (Always runs first, no LLM)
    deterministic_result = await run_deterministic_pipeline(request)
    extracted: ExtractedJobData = deterministic_result["extracted_job"]
    domain_report: Optional[DomainReport] = deterministic_result["domain_report"]
    task_fairness: TaskFairnessAssessment = deterministic_result["task_fairness"]
    score_breakdown: TrustScoreBreakdown = deterministic_result["trust_score"]

    # Step 2: Narrow LLM Calls (Only for hard judgment)
    # A. Metadata Fallback Extractor if company/title missing
    extracted = await extract_via_llm_fallback(request.raw_text, extracted)

    # B. Task Fairness judgment if take-home detected
    if task_fairness.has_task:
        task_fairness = await judge_task_fairness_llm(request.raw_text, task_fairness)

    # C. Chat tone & coercion analyzer for chats/emails
    chat_manipulation = None
    if request.input_type.value in ("chat_transcript", "email_thread"):
        chat_manipulation = await analyze_chat_manipulation_llm(request.raw_text)

    # D. Narrative generation (strictly citing computed findings)
    narration = await narrate_report(score_breakdown, extracted, domain_report)

    # Step 3: Recommended Action items based on verdict
    recommendations = []
    if score_breakdown.verdict == "DO_NOT_PROCEED":
        recommendations = [
            "DO NOT send money, deposits, or pay for training/equipment kits under any circumstance.",
            "DO NOT provide sensitive identification documents (Aadhaar, Passport, PAN) or bank account details.",
            "Report this posting/profile to the job board and block further contact.",
            "If communication occurred on WhatsApp/Telegram, flag the number for recruitment fraud."
        ]
    elif score_breakdown.verdict == "PROCEED_WITH_CAUTION":
        recommendations = [
            "Verify recruiter identity via company's official LinkedIn page or employee directory.",
            "Check if this vacancy is listed on the company's official website careers portal.",
            "Do not begin extensive unpaid tasks (>10 hours) without an signed contract or phone interview.",
            "Request official corporate email communication from the hiring manager."
        ]
    else:
        recommendations = [
            "Vacancy verified on legitimate enterprise recruiting channel.",
            "Standard interview preparation recommended.",
            "Bookmark the official ATS confirmation link for tracking your application status."
        ]

    return JobShieldReport(
        request_id=f"JS-{uuid.uuid4().hex[:8].upper()}",
        timestamp=datetime.now(timezone.utc).isoformat(),
        input_type=request.input_type,
        extracted_job=extracted,
        domain_report=domain_report,
        trust_score=score_breakdown,
        task_fairness=task_fairness,
        chat_manipulation=chat_manipulation,
        llm_narration=narration,
        recommended_actions=recommendations
    )
