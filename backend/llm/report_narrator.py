"""
JobShield AI - Evidence-Grounded Report Narrator
Synthesizes the deterministic audit score into clear, transparent human prose.
STRICT RULE: Explains the computed score; never hallucinates or invents facts not present in tool findings.
"""

from typing import List
from shared.schemas import TrustScoreBreakdown, ExtractedJobData, DomainReport
from .llm_client import call_llm

NARRATION_PROMPT = """You are JobShield AI's audit reporter. Write a concise, professional 3-sentence summary of this recruitment risk evaluation.
CRITICAL RULES:
1. Ground every sentence exclusively in the provided findings.
2. DO NOT invent or assume any facts.
3. State the assigned risk tier ({tier}), score ({score}/100), and specific evidence triggers.
4. Conclude with a direct recommendation.

Audit Data:
- Score: {score}/100
- Risk Tier: {tier}
- Verdict: {verdict}
- Company: {company}
- Domain: {domain}
- Penalties: {penalties}
- Bonuses: {bonuses}

Write a clear, objective assessment for the job seeker:
"""

def generate_deterministic_summary(
    score_breakdown: TrustScoreBreakdown,
    job: ExtractedJobData,
    domain_report: DomainReport
) -> str:
    """Fallback narrative generated deterministically without LLM."""
    tier = score_breakdown.tier.value
    score = score_breakdown.final_score
    verdict = score_breakdown.verdict

    if verdict == "DO_NOT_PROCEED":
        triggers = "; ".join([p.trigger_text for p in score_breakdown.penalties])
        return (
            f"CRITICAL WARNING (Score: {score}/100 | {tier}): "
            f"This recruitment inquiry triggered critical fraud/exploitation flags: [{triggers}]. "
            f"Do not transfer any money, do not provide sensitive PII documents, and cease communication immediately."
        )
    elif verdict == "PROCEED_WITH_CAUTION":
        reasons = "; ".join([p.signal_name for p in score_breakdown.penalties]) or "Unverified SMB without public enterprise ATS"
        return (
            f"NOTICE (Score: {score}/100 | {tier}): "
            f"Posting shows potential inconsistencies or unverified signals: [{reasons}]. "
            f"Proceed with caution: verify the recruiter's identity on official company channels before sharing sensitive information."
        )
    else:
        bonuses = "; ".join([b.signal_name for b in score_breakdown.bonuses]) or "Corporate domain matches registered records"
        return (
            f"VERIFIED (Score: {score}/100 | {tier}): "
            f"The vacancy is verified with legitimate recruitment indicators: [{bonuses}]. "
            f"Zero malicious signals detected. Safe to proceed with standard interview preparation."
        )

async def narrate_report(
    score_breakdown: TrustScoreBreakdown,
    job: ExtractedJobData,
    domain_report: DomainReport
) -> str:
    """Generates human-readable audit narrative using LLM if available, falling back to deterministic template."""
    penalties_str = ", ".join([f"{p.signal_name} (-{p.penalty_points} pts: {p.trigger_text})" for p in score_breakdown.penalties]) or "None"
    bonuses_str = ", ".join([f"{b.signal_name} (+{b.bonus_points} pts)" for b in score_breakdown.bonuses]) or "None"

    prompt = NARRATION_PROMPT.format(
        score=score_breakdown.final_score,
        tier=score_breakdown.tier.value,
        verdict=score_breakdown.verdict,
        company=job.company_name or "Unknown Company",
        domain=domain_report.domain if domain_report else (job.recruiter_domain or "Unknown"),
        penalties=penalties_str,
        bonuses=bonuses_str
    )

    llm_text = await call_llm(prompt)
    if llm_text and len(llm_text.strip()) > 20:
        return llm_text.strip()

    return generate_deterministic_summary(score_breakdown, job, domain_report)
