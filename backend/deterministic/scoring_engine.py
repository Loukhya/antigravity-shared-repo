"""
JobShield AI - Deterministic Trust Scoring Engine
Computes audit-transparent trust score: 100 - sum(penalties) + sum(bonuses)
Maps findings deterministically to the 8 Risk Taxonomy Tiers.
"""

from typing import List, Tuple, Optional
from shared.schemas import (
    RiskTaxonomyTier,
    RiskPenalty,
    VerificationBonus,
    TrustScoreBreakdown,
    DomainReport
)

def compute_trust_score(
    penalties: List[RiskPenalty],
    bonuses: List[VerificationBonus],
    has_ats_confirmation: bool = False,
    is_official_domain: bool = False
) -> TrustScoreBreakdown:
    """
    Computes trust score strictly by deterministic code per specification.
    Trust Score = 100 - sum(Penalties) + sum(Bonuses), clamped to [0, 100].
    """
    base_score = 100
    total_penalties = sum(p.penalty_points for p in penalties)
    total_bonuses = sum(b.bonus_points for b in bonuses)
    
    # Official corporate domain bonus (+20) if verified and no domain penalties
    has_domain_penalties = any(p.signal_key in ("TYPOSQUATTED_DOMAIN", "DOMAIN_RECENTLY_REGISTERED", "FREE_EMAIL_FOR_CORPORATE") for p in penalties)
    if is_official_domain and not has_domain_penalties:
        if not any(b.signal_key == "OFFICIAL_DOMAIN_VERIFIED" for b in bonuses):
            bonus = VerificationBonus(
                signal_key="OFFICIAL_DOMAIN_VERIFIED",
                signal_name="Official Corporate Domain Verified",
                bonus_points=20,
                evidence_citation="Authenticated email / recruitment domain matches registered corporate identity."
            )
            bonuses.append(bonus)
            total_bonuses += 20

    raw_score = base_score - total_penalties + total_bonuses
    final_score = max(0, min(100, raw_score))

    # Determine 8-Tier Taxonomy & Verdict
    penalty_keys = {p.signal_key for p in penalties}

    # Tier 8: High Risk Overseas Recruitment
    if "HIGH_RISK_OVERSEAS_FEE" in penalty_keys:
        tier = RiskTaxonomyTier.TIER_8
        verdict = "DO_NOT_PROCEED"

    # Tier 4: Direct Scam / Fraud (Upfront payments / deposits / fake checks)
    elif "UPFRONT_PAYMENT_DEMANDED" in penalty_keys:
        tier = RiskTaxonomyTier.TIER_4
        verdict = "DO_NOT_PROCEED"

    # Tier 5: Data & PII Harvesting
    elif "SENSITIVE_PII_REQUESTED" in penalty_keys:
        tier = RiskTaxonomyTier.TIER_5
        verdict = "DO_NOT_PROCEED"

    # Tier 3: Suspicious Inconsistency (Typosquatting, recent domain, free corporate email)
    elif any(k in penalty_keys for k in ("TYPOSQUATTED_DOMAIN", "DOMAIN_RECENTLY_REGISTERED", "FREE_EMAIL_FOR_CORPORATE")):
        tier = RiskTaxonomyTier.TIER_3
        verdict = "DO_NOT_PROCEED" if "TYPOSQUATTED_DOMAIN" in penalty_keys else "PROCEED_WITH_CAUTION"

    # Tier 6: Unpaid Labor / Task Harvesting
    elif "EXCESSIVE_UNPAID_TASK" in penalty_keys:
        tier = RiskTaxonomyTier.TIER_6
        verdict = "PROCEED_WITH_CAUTION"

    # Tier 7: Ghost Job / Resume Farming
    elif "GHOST_JOB_INACTIVITY" in penalty_keys:
        tier = RiskTaxonomyTier.TIER_7
        verdict = "PROCEED_WITH_CAUTION"

    # Tier 1: Verified Legitimate (ATS verified or official corporate domain with no penalties)
    elif has_ats_confirmation or (is_official_domain and len(penalties) == 0):
        tier = RiskTaxonomyTier.TIER_1
        verdict = "PROCEED"

    # Tier 2: Unverified SMB / Startup (zero malicious indicators)
    else:
        tier = RiskTaxonomyTier.TIER_2
        verdict = "PROCEED_WITH_CAUTION"

    return TrustScoreBreakdown(
        base_score=base_score,
        total_penalties=total_penalties,
        total_bonuses=total_bonuses,
        final_score=final_score,
        tier=tier,
        verdict=verdict,
        penalties=penalties,
        bonuses=bonuses
    )
