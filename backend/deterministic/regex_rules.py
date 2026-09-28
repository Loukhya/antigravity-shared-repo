"""
JobShield AI - Regex & Heuristic Rule Engine
Detects deterministic scam, payment, PII, and exploitation triggers.
"""

import re
from typing import List, Tuple, Dict, Any, Optional
from shared.schemas import RiskPenalty, ExtractedJobData

# Known free email providers
FREE_EMAIL_DOMAINS = {
    "gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "icloud.com",
    "rediffmail.com", "mail.com", "proton.me", "protonmail.com", "zoho.com",
    "yandex.com", "aol.com", "gmx.com"
}

# Major enterprise brands that NEVER hire using personal/free email accounts
TOP_CORPORATE_BRANDS = {
    "google", "microsoft", "amazon", "apple", "meta", "facebook", "stripe",
    "netflix", "tcs", "tata consultancy services", "infosys", "wipro", "cognizant",
    "accenture", "ibm", "uber", "figma", "airbnb", "salesforce", "oracle", "cisco",
    "intel", "tech mahindra", "hcl", "deloitte", "kpmg", "pwc", "ey"
}

# 1. UPFRONT PAYMENT / DEPOSIT PATTERNS (Penalty: -60)
PAYMENT_PATTERNS = [
    (r"(?:security|caution|laptop|equipment|training|gate|registration|interview|processing|visa|badge|uniform)\s+(?:deposit|fee|charge|cost|amount|money)", "Security / registration / equipment fee demanded"),
    (r"(?:deposit|transfer|pay|send|wire)\s+(?:rs\.?|inr|₹|\$|usd|eur|aed)\s*[\d,]+", "Specific monetary payment demand"),
    (r"(?:recharge|invest|deposit)\s+(?:rs\.?|inr|₹|\$|usd)?\s*[\d,]+\s*(?:into|to|in)\s*(?:our|merchant|company|wallet|crypto)", "Recharge or wallet deposit demand"),
    (r"(?:upi|gpay|google\s*pay|phonepe|paytm)\s*(?:id|account|to|transfer)?[:\s]+[a-zA-Z0-9.\-_]+@[a-zA-Z0-9]+", "Direct personal/merchant UPI transfer address"),
    (r"(?:metamask|usdt|crypto|bitcoin|btc|eth|tron)\s+(?:wallet|address|bond|deposit)", "Cryptocurrency deposit / bond demand"),
    (r"(?:cashier['’]?s\s+check|wire\s+the\s+remaining|refund\s+the\s+difference|vendor\s+to\s+ship)", "Fake check / equipment vendor routing scam"),
    (r"refundable\s+security\s+(?:caution\s+)?fee", "Refundable security deposit pretext"),
]

# 2. SENSITIVE PII PATTERNS (Penalty: -30)
PII_PATTERNS = [
    (r"(?:aadhaar|adhaar|aadhar)\s*(?:card|copy|number|photo|front\s*and\s*back|both\s*sides)?", "Aadhaar card document request"),
    (r"(?:pan|pancard|pan\s*card)\s*(?:copy|scan|photo|number)", "PAN card request during preliminary screening"),
    (r"(?:passport\s*(?:copy|scan|photo|front\/back|both\s*sides))", "Passport identity document request"),
    (r"(?:canceled\s+cheque|cancelled\s+cheque|bank\s*passbook|account\s*number\s*and\s*ifsc|bank\s*statement)", "Bank account / passbook / cancelled cheque request"),
    (r"(?:verification|security)\s*otp\s*(?:will\s*be\s*sent|share|forward|provide)", "SMS / Bank OTP request"),
]

# 3. HIGH-RISK OVERSEAS RECRUITMENT PATTERNS
OVERSEAS_PATTERNS = [
    (r"(?:dubai|poland|kuwait|qatar|singapore|canada|malaysia|gulf)\s+.*(?:work\s*permit|visa\s*processing|labor\s*clearance|flight\s*departure)", "Unverified foreign placement with expedited visa"),
    (r"(?:ministry\s+of\s+labor\s+clearance|medical\s+certificate\s+processing)\s+.*(?:transfer|fee|charge)", "Immigration / labor clearance fee demand"),
]

# 4. CHAT MANIPULATION & OFF-PLATFORM LURES
CHAT_LURE_PATTERNS = [
    (r"(?:telegram|whatsapp)\s*(?:channel|group|link|handle|@[\w_]+)", "Pushing conversation to encrypted messaging app (Telegram/WhatsApp)"),
    (r"(?:earn\s*(?:rs\.?|₹|\$)\s*[\d,]+\s*(?:daily|per\s*day|hourly|per\s*hour))\s*(?:by|for)\s*(?:liking|rating|reviewing|subscribing)", "Unrealistic payout for low-skill microtasks (YouTube/Google Maps)"),
    (r"(?:hurry|valid\s*for\s*\d+\s*minutes|urgent\s*opening\s*today|immediate\s*offer\s*without\s*interview)", "High-pressure urgency coercion"),
]

# Heuristic Extraction regexes
EMAIL_REGEX = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
ATS_PATTERNS = [
    re.compile(r"https?://(?:boards\.)?greenhouse\.io/[\w\-]+(?:/jobs/\d+)?", re.IGNORECASE),
    re.compile(r"https?://jobs\.lever\.co/[\w\-]+(?:/[\w\-]+)?", re.IGNORECASE),
    re.compile(r"https?://[\w\-.]+\.myworkdayjobs\.com/[\w\-./]+", re.IGNORECASE),
    re.compile(r"https?://ibegin\.tcs\.com/[\w\-./]+", re.IGNORECASE),
]
DAYS_OPEN_REGEX = re.compile(r"(?:posted|open)\s*(?:for)?\s*(\d+)\s*days?\s*ago", re.IGNORECASE)
APPLICANTS_REGEX = re.compile(r"(\d[\d,]*)\s*applicants?", re.IGNORECASE)
TASK_HOURS_REGEX = re.compile(r"(?:estimated\s*time|takes?|requires?|spend)\s*[:\s]*(\d+)\s*(?:-\s*(\d+))?\s*(?:hours|hrs)", re.IGNORECASE)


def extract_deterministic_fields(raw_text: str) -> ExtractedJobData:
    """Extract emails, domains, ATS links, and metrics from raw text."""
    emails = EMAIL_REGEX.findall(raw_text)
    recruiter_email = emails[0] if emails else None
    
    recruiter_domain = None
    if recruiter_email:
        parts = recruiter_email.split("@")
        if len(parts) > 1:
            recruiter_domain = parts[1].lower()

    # Search for ATS URLs
    ats_url = None
    for pattern in ATS_PATTERNS:
        match = pattern.search(raw_text)
        if match:
            ats_url = match.group(0)
            break

    # Search for Days Open
    days_open = None
    match_days = DAYS_OPEN_REGEX.search(raw_text)
    if match_days:
        try:
            days_open = int(match_days.group(1))
        except ValueError:
            pass

    # Search for Applicant Count
    applicant_count = None
    match_apps = APPLICANTS_REGEX.search(raw_text)
    if match_apps:
        try:
            applicant_count = int(match_apps.group(1).replace(",", ""))
        except ValueError:
            pass

    return ExtractedJobData(
        recruiter_email=recruiter_email,
        recruiter_domain=recruiter_domain,
        ats_url=ats_url,
        days_open=days_open,
        applicant_count=applicant_count,
        extraction_method="deterministic_heuristics"
    )


# Phrases indicating legitimate corporate anti-fraud disclaimers (e.g. "TCS never charges any fee")
NEGATION_DISCLAIMERS = [
    r"(?:never|not|no|without|will\s+not)\s+(?:charge|charges|ask|asks|require|requires|collect|accept|demand)\s+(?:any\s+)?(?:[\w\-]+|\s+or\s+|\s+and\s+)*\s*(?:fees?|charges?|deposits?|money|payment)",
    r"no\s+(?:fees?|charges?|deposits?)\s+(?:of\s+any\s+kind\s+)?(?:are\s+charged|required|collected)",
    r"we\s+do\s+not\s+(?:charge|ask\s+for)\s+(?:any\s+)?(?:fees?|payment|money)",
]

def scan_regex_penalties(text: str, company: Optional[str] = None, domain: Optional[str] = None) -> List[RiskPenalty]:
    """Scan text for deterministic penalty triggers according to JobShield spec."""
    penalties: List[RiskPenalty] = []
    
    # Check if text contains explicit legitimate disclaimer
    has_disclaimer = any(re.search(disclaimer, text, re.IGNORECASE) for disclaimer in NEGATION_DISCLAIMERS)

    # 1. Check Upfront Payment (-60)
    for pattern, description in PAYMENT_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            matched_snippet = match.group(0)
            # If the match is part of an anti-fraud disclaimer, skip it
            if has_disclaimer and any(w in matched_snippet.lower() for w in ["fee", "deposit", "charge"]):
                # Verify if snippet is directly negated in the same sentence
                sentence = ""
                for s in re.split(r"[.\n]", text):
                    if matched_snippet in s:
                        sentence = s
                        break
                if any(re.search(disclaimer, sentence, re.IGNORECASE) for disclaimer in NEGATION_DISCLAIMERS):
                    continue

            penalties.append(RiskPenalty(
                signal_key="UPFRONT_PAYMENT_DEMANDED",
                signal_name="Upfront Payment or Deposit Demanded",
                penalty_points=60,
                trigger_text=matched_snippet,
                evidence_citation=f"Found suspicious payment demand: '{matched_snippet}' ({description})",
                severity="critical"
            ))
            break # Deduct once for upfront payment

    # 2. Check Premature Sensitive PII (-30)
    for pattern, description in PII_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            matched_snippet = match.group(0)
            penalties.append(RiskPenalty(
                signal_key="SENSITIVE_PII_REQUESTED",
                signal_name="Premature Sensitive PII Requested",
                penalty_points=30,
                trigger_text=matched_snippet,
                evidence_citation=f"Found premature identity/banking request: '{matched_snippet}' ({description})",
                severity="high"
            ))
            break

    # 3. Check Free Email for Large Corporate Brand (-25)
    if domain and domain.lower() in FREE_EMAIL_DOMAINS:
        company_lower = (company or "").lower()
        if any(brand in company_lower or brand in text.lower() for brand in TOP_CORPORATE_BRANDS):
            penalties.append(RiskPenalty(
                signal_key="FREE_EMAIL_FOR_CORPORATE",
                signal_name="Free Email Provider Used for Corporate Brand",
                penalty_points=25,
                trigger_text=f"Email domain '{domain}' used for company '{company or 'Enterprise Brand'}'",
                evidence_citation=f"Major corporation recruiter claiming to represent '{company}' used public free mailbox '{domain}' instead of authenticated enterprise domain.",
                severity="high"
            ))

    # 4. Check High-Risk Overseas Placement Fee
    for pattern, description in OVERSEAS_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            matched_snippet = match.group(0)
            penalties.append(RiskPenalty(
                signal_key="HIGH_RISK_OVERSEAS_FEE",
                signal_name="High-Risk Overseas Recruitment Pattern",
                penalty_points=30,
                trigger_text=matched_snippet,
                evidence_citation=f"Unverified foreign work permit or labor clearance dispatch: '{matched_snippet}'",
                severity="high"
            ))
            break

    # 5. Check Chat Manipulation
    for pattern, description in CHAT_LURE_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            matched_snippet = match.group(0)
            penalties.append(RiskPenalty(
                signal_key="CHAT_OFF_PLATFORM_LURE",
                signal_name="Off-Platform Chat Lure / Manipulation Pattern",
                penalty_points=20,
                trigger_text=matched_snippet,
                evidence_citation=f"Recruitment redirection / coercive pattern: '{matched_snippet}'",
                severity="medium"
            ))
            break

    return penalties
