# JobShield AI — Recruitment Integrity & Opportunity Trust Engine

[![JobShield CI](https://github.com/Loukhya/antigravity-shared-repo/actions/workflows/ci.yml/badge.svg)](https://github.com/Loukhya/antigravity-shared-repo/actions/workflows/ci.yml)
[![Accuracy](https://img.shields.io/badge/Benchmark%20Accuracy-100%25%20(30%2F30)-emerald)](data/labeled_test_set.json)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

Job scam and employment exploitation detection engine. Instead of a binary "real/fake" black box, JobShield AI gathers independently verifiable evidence (IETF RDAP domain age, DNS MX/SPF/DMARC, official enterprise ATS confirmation, upfront payment demands, PII harvesting, and unpaid labor scopes) and presents a transparent, evidence-linked trust audit.

---

## 🏛️ System Architecture

JobShield uses a **hybrid deterministic + narrow LLM** architecture:

```
                      User Input
(Job Posting / Recruiter Email / Chat Transcript / Offer Letter)
                          │
                          ▼
            FastAPI Backend Orchestrator
                          │
       ┌──────────────────┴──────────────────┐
       ▼                                     ▼
Deterministic Tool Layer            Narrow LLM Judgment Calls
(Pure Code — Zero LLM)              (Hard Decisions Only)
• IETF RDAP domain age lookup       • Free-text metadata extraction fallback
• DNS MX / SPF / DMARC verification • Take-home task fairness judgment
• Levenshtein typosquat distance    • WhatsApp / Telegram manipulation tone
• Regex rule engine (UPI, PII, fee) • Grounded audit report narration
• ATS API validation (Greenhouse,
  Lever, Workday, iBegin)
• 100-pt weighted scoring formula
       │                                     │
       └──────────────────┬──────────────────┘
                          ▼
             Evidence-Linked Trust Report
       (0–100 Score, 8-Tier Taxonomy, Cited Evidence)
                          │
                          ▼
               React + Vite Dashboard
```

---

## 🎯 8-Tier Risk Taxonomy

| Tier | Category | Definition |
| :--- | :--- | :--- |
| **1 🟢** | **Verified Legitimate** | Company registered, official ATS vacancy confirmed, recruiter domain matches |
| **2 🟡** | **Unverified SMB/Startup** | Cannot be confirmed on an ATS, but zero malicious indicators |
| **3 🟠** | **Suspicious Inconsistency** | Domain registered days ago, address mismatches, free corporate email, typosquatting |
| **4 🔴** | **Direct Scam / Fraud** | Upfront fees, security deposits, UPI/crypto transfers, fake checks |
| **5 🟣** | **Data & PII Harvesting** | Posting asks for Aadhaar, PAN, passport, or bank details upfront |
| **6 🔵** | **Unpaid Labor / Task Harvesting** | 15–40+ hour unpaid assignments building real production features |
| **7 📉** | **Ghost Job / Resume Farming** | Open >90 days, >2,500 applicants, continuous reposting with no hiring closure |
| **8 🌍** | **High-Risk Overseas Recruitment** | Unlicensed overseas placement asking for advance visa/labor clearance fee |

---

## ⚖️ Scoring Formula (Strictly Deterministic)

$$\text{Trust Score} = 100 - \sum \text{Risk Penalties} + \sum \text{Verification Bonuses}$$

*Clamped strictly to $[0, 100]$.*

* **Automatic DO NOT PROCEED**: Upfront payment/deposit ($-60$), Typosquatted domain ($-45$), Premature PII ($-30$), Overseas placement fee ($-30$).
* **Channel & Inactivity Warnings**: Domain $<14$ days old ($-35$), Free email for corporate brand ($-25$), Unpaid task $>15$ hrs ($-20$), Ghost job ($-15$).
* **Verification Bonuses**: Official ATS confirmed ($+30$), Corporate domain verified ($+20$).

---

## 👥 2-Person Team Collaboration Split

To prevent merge conflicts and maintain high velocity, responsibilities are cleanly split by layer:

### 👤 Person A: Deterministic Core & Infrastructure
* `backend/deterministic/rdap_verifier.py`: IETF RDAP domain age & registrar lookups.
* `backend/deterministic/dns_verifier.py`: DNS MX, SPF, DMARC validation.
* `backend/deterministic/typosquat.py`: Levenshtein distance & homoglyph protection.
* `backend/deterministic/regex_rules.py`: Payment, PII, and disclaimer negation rules.
* `backend/deterministic/ats_verifier.py`: Greenhouse, Lever, Workday API verification.
* `backend/deterministic/scoring_engine.py`: 100-point deterministic scoring formula.
* `backend/test_regression.py`: Benchmark suite maintenance against `data/labeled_test_set.json`.

### 👤 Person B: LLM Orchestration & Frontend Dashboard
* `shared/schemas.py`: Shared Pydantic contracts & types.
* `backend/llm/llm_client.py`: Groq (Llama 3.3 70B) & Google Gemini 2.5 Flash adapters.
* `backend/llm/fallback_extractor.py`: Unstructured free-text extraction fallback.
* `backend/llm/task_judge.py`: Unpaid task fairness & proprietary IP analysis.
* `backend/llm/chat_analyzer.py`: WhatsApp/Telegram chat manipulation & urgency detector.
* `backend/llm/report_narrator.py`: Evidence-grounded narrative summary generator.
* `frontend/`: React + Vite + Tailwind interactive candidate inspection dashboard.

---

## 🚀 Quickstart Guide

### 1. Clone the Shared Repository
```bash
git clone https://github.com/Loukhya/antigravity-shared-repo.git
cd antigravity-shared-repo
```

### 2. Backend Setup
```bash
# Create and activate virtual environment
python -m venv .venv

# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the 30-case benchmark regression test (100% ground-truth pass required)
python backend/test_regression.py

# Start FastAPI backend server
uvicorn backend.main:app --reload --port 8000
```
Backend API docs available at: `http://localhost:8000/docs`

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:5173` in your browser.

---

## 🧪 Benchmark Test Suite

JobShield enforces an automated regression test suite on every commit:
```bash
python backend/test_regression.py
```
* Current benchmark: **30 diverse real-world ground-truth test cases** across all 8 tiers.
* Current pass rate: **100.0% (30/30)**.

---

## 🛡️ Legal & Compliance
* **No LinkedIn DOM Scraping**: Built as a paste-based web form, complying with platform terms of service.
* **DPDP Act & Privacy**: Candidate text and resumes are analyzed in-memory and not stored or sold.
* **Defamation Safeguard**: Every finding is framed as an objective, independently cited evidence risk signal rather than an unsubstantiated accusation.
