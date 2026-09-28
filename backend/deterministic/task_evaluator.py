"""
JobShield AI - Task Fairness & Ghost Job Evaluator
Evaluates take-home assignment scope (hours, proprietary work) and ghost job indicators (days open, applicant volume).
"""

import re
from typing import Optional, Tuple, List
from shared.schemas import TaskFairnessAssessment, RiskPenalty

TASK_HOURS_REGEX = re.compile(
    r"(?:estimated\s*(?:completion\s*)?time|takes?|requires?|spend|over|duration)\s*[:\s]*(\d+)\s*(?:-\s*(\d+))?\s*(?:hours|hrs)",
    re.IGNORECASE
)

EXPLOITATION_KEYWORDS = [
    "grant our github organization write access",
    "becomes property of the company",
    "build our entire",
    "production microservice",
    "real stripe subscription billing",
    "deploy it to aws with terraform",
    "live staging database"
]

def evaluate_task_fairness(text: str) -> Tuple[TaskFairnessAssessment, Optional[RiskPenalty]]:
    """
    Evaluates whether an assignment is an excessive unpaid labor trap (>15 hours or proprietary code).
    """
    estimated_hours = None
    match = TASK_HOURS_REGEX.search(text)
    if match:
        h1 = int(match.group(1))
        h2 = int(match.group(2)) if match.group(2) else h1
        estimated_hours = max(h1, h2)

    has_proprietary_flags = any(kw in text.lower() for kw in EXPLOITATION_KEYWORDS)
    is_excessive = (estimated_hours is not None and estimated_hours > 15) or has_proprietary_flags

    penalty = None
    rationale = None

    if is_excessive:
        hours_str = f"{estimated_hours} hours" if estimated_hours else "disproportionate scope"
        rationale = f"Assessment requires {hours_str} and appears to solicit free production engineering labor."
        penalty = RiskPenalty(
            signal_key="EXCESSIVE_UNPAID_TASK",
            signal_name="Excessive Unpaid Labor / Task Harvesting",
            penalty_points=20,
            trigger_text=f"Estimated task duration > 15 hours ({hours_str})",
            evidence_citation=rationale,
            severity="medium"
        )
    elif estimated_hours is not None and estimated_hours <= 15:
        rationale = f"Take-home assessment estimated at reasonable duration ({estimated_hours} hrs)."

    assessment = TaskFairnessAssessment(
        has_task=bool(estimated_hours or has_proprietary_flags or "take-home" in text.lower() or "assessment" in text.lower()),
        estimated_hours=estimated_hours,
        is_excessive=is_excessive,
        is_proprietary_feature=has_proprietary_flags,
        rationale=rationale
    )

    return assessment, penalty


def evaluate_ghost_job(
    days_open: Optional[int], 
    applicant_count: Optional[int],
    raw_text: str
) -> Optional[RiskPenalty]:
    """
    Evaluates whether posting is a Ghost Job / Resume Farming posting (>90 days active AND >2,500 applicants).
    Penalty: -15 points.
    """
    # Check if days_open and applicant_count can be parsed from text if not provided
    if days_open is None:
        match_days = re.search(r"(\d+)\s*days?\s*ago", raw_text, re.IGNORECASE)
        if match_days:
            days_open = int(match_days.group(1))

    if applicant_count is None:
        match_apps = re.search(r"(\d[\d,]*)\s*applicants?", raw_text, re.IGNORECASE)
        if match_apps:
            applicant_count = int(match_apps.group(1).replace(",", ""))

    if days_open and applicant_count:
        if days_open > 90 and applicant_count > 2500:
            return RiskPenalty(
                signal_key="GHOST_JOB_INACTIVITY",
                signal_name="Ghost Job / Resume Farming Pattern",
                penalty_points=15,
                trigger_text=f"Posting active for {days_open} days with {applicant_count} applicants",
                evidence_citation=(
                    f"Job has remained open for {days_open} days (>90 days threshold) and accumulated "
                    f"{applicant_count} applicants (>2,500 threshold) with no hiring closure."
                ),
                severity="low"
            )

    return None
