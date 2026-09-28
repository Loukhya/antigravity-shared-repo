"""
JobShield AI - DNS MX, SPF, and DMARC Verifier
Inspects DNS records for recruiter domain to ensure mail legitimacy and spoofing defenses.
"""

from typing import Tuple, Dict, Any
import dns.resolver

def check_domain_dns_records(domain: str) -> Dict[str, bool]:
    """
    Checks MX, SPF, and DMARC records for a domain.
    Returns: {"has_mx": bool, "has_spf": bool, "has_dmarc": bool}
    """
    domain_clean = domain.lower().strip()
    result = {"has_mx": False, "has_spf": False, "has_dmarc": False}
    
    if not domain_clean or "." not in domain_clean:
        return result

    resolver = dns.resolver.Resolver()
    resolver.timeout = 2.0
    resolver.lifetime = 2.0

    # 1. Check MX records
    try:
        mx_answers = resolver.resolve(domain_clean, 'MX')
        if len(mx_answers) > 0:
            result["has_mx"] = True
    except Exception:
        result["has_mx"] = False

    # 2. Check SPF in TXT records
    try:
        txt_answers = resolver.resolve(domain_clean, 'TXT')
        for rdata in txt_answers:
            txt_str = rdata.to_text().lower()
            if "v=spf1" in txt_str:
                result["has_spf"] = True
                break
    except Exception:
        result["has_spf"] = False

    # 3. Check DMARC record (_dmarc.domain)
    try:
        dmarc_domain = f"_dmarc.{domain_clean}"
        dmarc_answers = resolver.resolve(dmarc_domain, 'TXT')
        for rdata in dmarc_answers:
            txt_str = rdata.to_text().lower()
            if "v=dmarc1" in txt_str:
                result["has_dmarc"] = True
                break
    except Exception:
        result["has_dmarc"] = False

    return result
