"""
JobShield AI - Deterministic Pipeline Runner
Executes the pure deterministic tool layer (zero LLM calls) to produce an evidence-backed trust report.
"""

from typing import Optional, Dict, Any
from shared.schemas import (
    JobAnalysisRequest,
    ExtractedJobData,
    DomainReport,
    TrustScoreBreakdown,
    TaskFairnessAssessment,
    JobShieldReport
)
from .regex_rules import extract_deterministic_fields, scan_regex_penalties
from .typosquat import check_typosquatting, PROTECTED_BRANDS
from .rdap_verifier import lookup_domain_rdap
from .ats_verifier import verify_ats_vacancy
from .task_evaluator import evaluate_task_fairness, evaluate_ghost_job
from .scoring_engine import compute_trust_score
from datetime import datetime, timezone
import uuid

async def run_deterministic_pipeline(
    request: JobAnalysisRequest,
    simulated_domain_age: Optional[int] = None
) -> Dict[str, Any]:
    """
    Runs all deterministic tools without any LLM involvement.
    """
    raw_text = request.raw_text
    
    # 1. Extraction via heuristics
    extracted = extract_deterministic_fields(raw_text)
    if request.company_name:
        extracted.company_name = request.company_name
    if request.recruiter_email:
        extracted.recruiter_email = request.recruiter_email
        if "@" in request.recruiter_email:
            extracted.recruiter_domain = request.recruiter_email.split("@")[1].lower()

    target_domain = extracted.recruiter_domain

    penalties = []
    bonuses = []

    # 2. Regex Penalties
    regex_penalties = scan_regex_penalties(
        text=raw_text,
        company=extracted.company_name,
        domain=target_domain
    )
    penalties.extend(regex_penalties)

    # 3. Typosquatting Check
    domain_report = None
    is_official_domain = False
    if target_domain:
        is_typo, impersonated, typo_penalty = check_typosquatting(target_domain)
        if typo_penalty:
            penalties.append(typo_penalty)
        elif impersonated and target_domain in PROTECTED_BRANDS.values():
            is_official_domain = True

        # 4. RDAP Domain Lookup
        report, rdap_penalty = await lookup_domain_rdap(target_domain, simulated_age_days=simulated_domain_age)
        domain_report = report
        if is_typo:
            domain_report.is_typosquatted = True
            domain_report.impersonated_brand = impersonated
        if rdap_penalty:
            penalties.append(rdap_penalty)

    # 5. ATS Verification
    has_ats = False
    ats_url = extracted.ats_url or request.source_url
    if ats_url:
        is_ats_valid, ats_bonus = await verify_ats_vacancy(ats_url)
        if ats_bonus:
            bonuses.append(ats_bonus)
            has_ats = is_ats_valid

    # 6. Task Fairness Evaluation
    task_assessment, task_penalty = evaluate_task_fairness(raw_text)
    if task_penalty:
        penalties.append(task_penalty)

    # 7. Ghost Job Evaluation
    ghost_penalty = evaluate_ghost_job(
        days_open=extracted.days_open,
        applicant_count=extracted.applicant_count,
        raw_text=raw_text
    )
    if ghost_penalty:
        penalties.append(ghost_penalty)

    # 8. Deterministic Trust Score Computation
    score_breakdown = compute_trust_score(
        penalties=penalties,
        bonuses=bonuses,
        has_ats_confirmation=has_ats,
        is_official_domain=is_official_domain
    )

    return {
        "extracted_job": extracted,
        "domain_report": domain_report,
        "task_fairness": task_assessment,
        "trust_score": score_breakdown
    }
