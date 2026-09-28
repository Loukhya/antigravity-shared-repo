"""
JobShield AI - Typosquatting & Impersonation Detector
Computes Levenshtein distance & leet-speak character substitutions against known legitimate employer domains.
"""

from typing import Optional, Tuple
from shared.schemas import RiskPenalty

# Target high-value brand domain stems often targeted by job scammers
PROTECTED_BRANDS = {
    "google": "google.com",
    "microsoft": "microsoft.com",
    "amazon": "amazon.com",
    "apple": "apple.com",
    "meta": "meta.com",
    "stripe": "stripe.com",
    "netflix": "netflix.com",
    "uber": "uber.com",
    "tcs": "tcs.com",
    "infosys": "infosys.com",
    "wipro": "wipro.com",
    "accenture": "accenture.com",
    "cognizant": "cognizant.com",
    "figma": "figma.com",
    "gitlab": "gitlab.com",
    "github": "github.com",
    "techmahindra": "techmahindra.com"
}

def normalize_variants(stem: str) -> list[str]:
    """Generates normalized variants handling ambiguous homoglyphs like 1 -> [i, l]."""
    variants = [stem.lower()]
    # Normalize 0 -> o, 3 -> e, 4 -> a, 5 -> s, @ -> a
    base = stem.lower().replace('0', 'o').replace('3', 'e').replace('4', 'a').replace('5', 's').replace('@', 'a').replace('$', 's')
    # If contains '1', branch into both 'i' and 'l'
    if '1' in base:
        variants.append(base.replace('1', 'i'))
        variants.append(base.replace('1', 'l'))
    else:
        variants.append(base)
    return list(set(variants))


def levenshtein_distance(s1: str, s2: str) -> int:
    """Standard dynamic programming Levenshtein distance."""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)
    
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]


def check_typosquatting(domain: str) -> Tuple[bool, Optional[str], Optional[RiskPenalty]]:
    """
    Evaluates whether the provided domain is a typosquatted lookalike of a legitimate brand.
    Returns: (is_typosquatted, impersonated_brand, RiskPenalty)
    """
    if not domain:
        return False, None, None

    domain_clean = domain.lower().strip()
    
    # Strip common subdomains and TLD
    parts = domain_clean.split(".")
    if len(parts) < 2:
        return False, None, None

    stem = parts[0]
    full_stem = "-".join(parts[:-1]) # Handles hyphens like g00gle-careers

    # Check direct match with legitimate domain
    for brand, official_domain in PROTECTED_BRANDS.items():
        if domain_clean == official_domain:
            return False, brand, None # Exact legitimate domain match

    stem_variants = normalize_variants(stem)
    full_variants = normalize_variants(full_stem)

    for brand, official_domain in PROTECTED_BRANDS.items():
        # Check if leet-speak was used to mimic brand (e.g. g00gle, amaz0n, netfl1x)
        matches_leet = any(
            (s != brand and (s == brand or brand in f))
            for s in stem_variants
            for f in full_variants
        )
        if matches_leet:
            penalty = RiskPenalty(
                signal_key="TYPOSQUATTED_DOMAIN",
                signal_name="Typosquatted / Spoofed Domain Detected",
                penalty_points=45,
                trigger_text=f"Domain '{domain_clean}' mimics brand '{brand}' ({official_domain})",
                evidence_citation=(
                    f"Domain '{domain_clean}' uses homoglyphs or lookalike keywords resembling "
                    f"official corporate domain '{official_domain}'."
                ),
                severity="critical"
            )
            return True, brand, penalty

        # Check Levenshtein distance on stem
        dist = levenshtein_distance(stem, brand)
        if 1 <= dist <= 2 and len(brand) >= 4 and stem != brand:
            penalty = RiskPenalty(
                signal_key="TYPOSQUATTED_DOMAIN",
                signal_name="Typosquatted / Spoofed Domain Detected",
                penalty_points=45,
                trigger_text=f"Domain stem '{stem}' edit distance is {dist} from '{brand}'",
                evidence_citation=(
                    f"Domain '{domain_clean}' has an edit distance of {dist} from official "
                    f"brand '{brand}' ({official_domain}), indicating typosquatting."
                ),
                severity="critical"
            )
            return True, brand, penalty

    return False, None, None
