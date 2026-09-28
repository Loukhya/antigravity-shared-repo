"""
JobShield AI - RDAP Domain Age & Registration Verifier
Queries the standard IETF RDAP (Registration Data Access Protocol) to verify domain age and registrar.
Replaces legacy WHOIS per project specification.
"""

from datetime import datetime, timezone
from typing import Optional, Tuple
import httpx
from shared.schemas import DomainReport, RiskPenalty

RDAP_BOOTSTRAP_URL = "https://rdap.org/domain"

async def lookup_domain_rdap(domain: str, simulated_age_days: Optional[int] = None) -> Tuple[DomainReport, Optional[RiskPenalty]]:
    """
    Performs RDAP lookup for the given domain.
    Returns: (DomainReport, Optional[RiskPenalty])
    """
    domain_clean = domain.lower().strip()
    
    # Handle simulated age for testing without live network delay
    if simulated_age_days is not None:
        report = DomainReport(
            domain=domain_clean,
            is_valid_domain=True,
            domain_age_days=simulated_age_days,
            registration_date=(datetime.now(timezone.utc)).isoformat(),
            registrar="Mock Registrar",
            rdap_source_url=f"{RDAP_BOOTSTRAP_URL}/{domain_clean}"
        )
        penalty = None
        if simulated_age_days < 14:
            penalty = RiskPenalty(
                signal_key="DOMAIN_RECENTLY_REGISTERED",
                signal_name="Domain Created Less Than 14 Days Ago",
                penalty_points=35,
                trigger_text=f"Domain '{domain_clean}' age is {simulated_age_days} days (< 14 days)",
                evidence_citation=f"RDAP registry indicates domain '{domain_clean}' was created only {simulated_age_days} days ago, a common marker for burner scam domains.",
                severity="high"
            )
        return report, penalty

    # Query public RDAP endpoint
    lookup_url = f"{RDAP_BOOTSTRAP_URL}/{domain_clean}"
    try:
        async with httpx.AsyncClient(timeout=4.0) as client:
            resp = await client.get(lookup_url, headers={"Accept": "application/rdap+json"})
            if resp.status_code == 200:
                data = resp.json()
                events = data.get("events", [])
                registration_date = None
                for ev in events:
                    if ev.get("eventAction") in ("registration", "created"):
                        registration_date = ev.get("eventDate")
                        break

                registrar_name = None
                for entity in data.get("entities", []):
                    if "registrar" in entity.get("roles", []):
                        vcard = entity.get("vcardArray", [])
                        if len(vcard) > 1:
                            for item in vcard[1]:
                                if item[0] == "fn":
                                    registrar_name = item[3]
                                    break

                age_days = None
                penalty = None
                if registration_date:
                    try:
                        # Normalize ISO timestamp
                        reg_dt = datetime.fromisoformat(registration_date.replace("Z", "+00:00"))
                        now = datetime.now(timezone.utc)
                        age_days = max(0, (now - reg_dt).days)
                        if age_days < 14:
                            penalty = RiskPenalty(
                                signal_key="DOMAIN_RECENTLY_REGISTERED",
                                signal_name="Domain Created Less Than 14 Days Ago",
                                penalty_points=35,
                                trigger_text=f"Domain '{domain_clean}' age is {age_days} days",
                                evidence_citation=f"RDAP registry confirmed creation on {registration_date} ({age_days} days ago).",
                                severity="high"
                            )
                    except Exception:
                        pass

                return DomainReport(
                    domain=domain_clean,
                    is_valid_domain=True,
                    domain_age_days=age_days,
                    registration_date=registration_date,
                    registrar=registrar_name,
                    rdap_source_url=lookup_url
                ), penalty

    except Exception:
        # Graceful fallback if RDAP query times out or domain is private
        pass

    return DomainReport(
        domain=domain_clean,
        is_valid_domain=True,
        domain_age_days=None,
        registration_date=None,
        registrar=None,
        rdap_source_url=lookup_url
    ), None
