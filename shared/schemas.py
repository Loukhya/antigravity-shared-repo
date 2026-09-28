"""
JobShield AI - Shared Pydantic Schemas
Contracts used across deterministic analysis, LLM orchestration, and frontend reporting.
"""

from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class RiskTaxonomyTier(str, Enum):
    TIER_1 = "1 🟢 Verified Legitimate"
    TIER_2 = "2 🟡 Unverified SMB/Startup"
    TIER_3 = "3 🟠 Suspicious Inconsistency"
    TIER_4 = "4 🔴 Direct Scam/Fraud"
    TIER_5 = "5 🟣 Data & PII Harvesting"
    TIER_6 = "6 🔵 Unpaid Labor/Task Harvesting"
    TIER_7 = "7 📉 Ghost Job/Resume Farming"
    TIER_8 = "8 🌍 High-Risk Overseas Recruitment"


class InputType(str, Enum):
    JOB_POSTING = "job_posting"
    CHAT_TRANSCRIPT = "chat_transcript"
    EMAIL_THREAD = "email_thread"
    OFFER_LETTER = "offer_letter"


class JobAnalysisRequest(BaseModel):
    raw_text: str = Field(..., description="Raw text of posting, email, offer letter, or chat")
    input_type: InputType = Field(default=InputType.JOB_POSTING, description="Type of user input")
    source_url: Optional[str] = Field(None, description="Optional job link or domain URL provided by user")
    company_name: Optional[str] = Field(None, description="Optional company name override")
    recruiter_email: Optional[str] = Field(None, description="Optional recruiter email address")


class ExtractedJobData(BaseModel):
    title: Optional[str] = Field(None, description="Extracted job title")
    company_name: Optional[str] = Field(None, description="Extracted company name")
    recruiter_email: Optional[str] = Field(None, description="Extracted recruiter email")
    recruiter_domain: Optional[str] = Field(None, description="Domain extracted from email or company website")
    posted_date: Optional[str] = Field(None, description="Posting date if present")
    days_open: Optional[int] = Field(None, description="Estimated days posting has been active")
    applicant_count: Optional[int] = Field(None, description="Number of applicants reported")
    ats_url: Optional[str] = Field(None, description="Direct ATS link (Greenhouse, Lever, Workday, etc.)")
    salary_text: Optional[str] = Field(None, description="Salary text found in posting")
    task_instructions: Optional[str] = Field(None, description="Assessment or take-home assignment instructions")
    extraction_method: str = Field("deterministic", description="'structured_markup', 'regex_heuristic', or 'llm_fallback'")


class DomainReport(BaseModel):
    domain: str = Field(..., description="Domain being inspected")
    is_valid_domain: bool = Field(True, description="Whether domain resolved/exists")
    domain_age_days: Optional[int] = Field(None, description="Age in days via RDAP")
    registration_date: Optional[str] = Field(None, description="ISO registration date from RDAP")
    registrar: Optional[str] = Field(None, description="Registrar name")
    is_free_provider: bool = Field(False, description="True if Gmail, Yahoo, Hotmail, etc.")
    is_typosquatted: bool = Field(False, description="True if Levenshtein distance matches a protected brand")
    impersonated_brand: Optional[str] = Field(None, description="Target brand if typosquatting detected")
    has_mx_records: bool = Field(False, description="Whether DNS MX records exist")
    has_spf_records: bool = Field(False, description="Whether DNS SPF TXT records exist")
    has_dmarc_records: bool = Field(False, description="Whether DNS DMARC TXT records exist")
    rdap_source_url: Optional[str] = Field(None, description="URL of the RDAP lookup for auditability")


class RiskPenalty(BaseModel):
    signal_key: str = Field(..., description="Unique machine key for signal (e.g. 'UPFRONT_PAYMENT')")
    signal_name: str = Field(..., description="Human readable label")
    penalty_points: int = Field(..., description="Points deducted (positive number subtracted from 100)")
    trigger_text: str = Field(..., description="Exact snippet or condition that triggered this penalty")
    evidence_citation: str = Field(..., description="Literal source quote or tool verification result")
    severity: str = Field("medium", description="'critical', 'high', 'medium', 'low'")


class VerificationBonus(BaseModel):
    signal_key: str = Field(..., description="Unique machine key for bonus (e.g. 'ATS_VERIFIED')")
    signal_name: str = Field(..., description="Human readable label")
    bonus_points: int = Field(..., description="Points added to score")
    evidence_citation: str = Field(..., description="Literal source quote or tool verification result")


class TrustScoreBreakdown(BaseModel):
    base_score: int = Field(100, description="Starting score before penalties/bonuses")
    total_penalties: int = Field(0, description="Sum of penalty points deducted")
    total_bonuses: int = Field(0, description="Sum of bonus points added")
    final_score: int = Field(100, ge=0, le=100, description="Computed score clamped to [0, 100]")
    tier: RiskTaxonomyTier = Field(..., description="Assigned 8-tier risk category")
    verdict: str = Field(..., description="'PROCEED', 'PROCEED_WITH_CAUTION', 'HIGH_RISK', 'DO_NOT_PROCEED'")
    penalties: List[RiskPenalty] = Field(default_factory=list, description="All triggered penalties")
    bonuses: List[VerificationBonus] = Field(default_factory=list, description="All awarded bonuses")


class TaskFairnessAssessment(BaseModel):
    has_task: bool = Field(False, description="Whether an assessment or take-home task was found")
    estimated_hours: Optional[int] = Field(None, description="Estimated hours required")
    is_excessive: bool = Field(False, description="True if >15 hours or clearly disproportionate")
    is_proprietary_feature: bool = Field(False, description="True if asking candidate to build company core IP/features")
    rationale: Optional[str] = Field(None, description="Evidence-backed reasoning")


class ChatManipulationAssessment(BaseModel):
    has_urgency_coercion: bool = Field(False, description="High pressure urgency / immediate money demand")
    off_platform_lure: bool = Field(False, description="Pushing to Telegram/WhatsApp immediately from job board")
    suspicious_compensation_promise: bool = Field(False, description="Unrealistic daily/hourly payout (e.g. ₹5000/hr for likes)")
    rationale: Optional[str] = Field(None, description="Key evidence snippets found in chat")


class JobShieldReport(BaseModel):
    request_id: str = Field(..., description="Unique analysis identifier")
    timestamp: str = Field(..., description="ISO 8601 generation timestamp")
    input_type: InputType = Field(..., description="Source format analyzed")
    extracted_job: ExtractedJobData = Field(..., description="Structured job details")
    domain_report: Optional[DomainReport] = Field(None, description="RDAP & DNS audit report")
    trust_score: TrustScoreBreakdown = Field(..., description="Deterministic trust score breakdown")
    task_fairness: Optional[TaskFairnessAssessment] = Field(None, description="Assessment exploitation report")
    chat_manipulation: Optional[ChatManipulationAssessment] = Field(None, description="Chat manipulation flags")
    llm_narration: str = Field(..., description="Concise, factual audit summary strictly citing computed findings")
    recommended_actions: List[str] = Field(default_factory=list, description="Actionable next steps for candidate")
    disclaimer: str = Field(
        "JobShield AI provides risk signals and evidence citations based on publicly verifiable data. "
        "It is not a legal accusation or guarantee of legitimacy.",
        description="Legal disclaimer per specification"
    )
