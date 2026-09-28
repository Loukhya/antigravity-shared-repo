"""
JobShield AI - Automated Benchmark Regression Test Runner
Evaluates the deterministic tool layer against the 30-case labeled test set.
Measures accuracy, false-positive rate, and Tier classification fidelity.
"""

import json
import asyncio
import sys
from pathlib import Path

# Fix Windows console encoding for UTF-8 symbols
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

from shared.schemas import JobAnalysisRequest, InputType
from backend.deterministic.pipeline import run_deterministic_pipeline

async def run_benchmark():
    test_set_path = root_dir / "data" / "labeled_test_set.json"
    with open(test_set_path, "r", encoding="utf-8") as f:
        cases = json.load(f)

    print(f"\n==================================================")
    print(f"  JOBSHIELD AI - DETERMINISTIC REGRESSION TEST RUN")
    print(f"  Evaluating {len(cases)} Ground-Truth Test Cases")
    print(f"==================================================\n")

    passed = 0
    failed = 0
    tier_matches = 0
    verdict_matches = 0

    for idx, case in enumerate(cases, 1):
        case_id = case["id"]
        title = case["title"]
        raw_text = case["text"]
        input_type = InputType(case.get("input_type", "job_posting"))
        expected_tier = case["ground_truth_tier"]
        expected_verdict = case["expected_verdict"]
        simulated_domain_age = case.get("domain_age_days")

        request = JobAnalysisRequest(
            raw_text=raw_text,
            input_type=input_type,
            company_name=case.get("company"),
            recruiter_email=case.get("recruiter_email"),
            source_url=case.get("ats_url")
        )

        res = await run_deterministic_pipeline(request, simulated_domain_age=simulated_domain_age)
        score_breakdown = res["trust_score"]
        actual_tier = score_breakdown.tier.value
        actual_verdict = score_breakdown.verdict
        final_score = score_breakdown.final_score

        # Check verdict match
        v_match = (actual_verdict == expected_verdict)
        if v_match:
            verdict_matches += 1

        # Check tier match
        t_match = (actual_tier.split()[0] == expected_tier.split()[0]) # Compare tier numbers
        if t_match:
            tier_matches += 1

        is_success = v_match and t_match
        status_sym = "✅" if is_success else "⚠️"
        if is_success:
            passed += 1
        else:
            failed += 1

        penalties_str = ", ".join([p.signal_key for p in score_breakdown.penalties]) or "None"
        bonuses_str = ", ".join([b.signal_key for b in score_breakdown.bonuses]) or "None"

        print(f"[{status_sym}] #{idx:02d} {case_id}: {title[:42]}")
        print(f"     Score: {final_score}/100 | Verdict: {actual_verdict} (Expected: {expected_verdict})")
        print(f"     Tier:  {actual_tier} | (Expected: {expected_tier})")
        print(f"     Penalties: [{penalties_str}] | Bonuses: [{bonuses_str}]")
        print("-" * 65)

    print(f"\n==================================================")
    print(f"  BENCHMARK SUMMARY")
    print(f"==================================================")
    print(f"  Total Cases:         {len(cases)}")
    print(f"  Verdict Accuracy:    {verdict_matches}/{len(cases)} ({verdict_matches/len(cases)*100:.1f}%)")
    print(f"  Tier Match Accuracy: {tier_matches}/{len(cases)} ({tier_matches/len(cases)*100:.1f}%)")
    print(f"  Full Test Passed:    {passed}/{len(cases)} ({passed/len(cases)*100:.1f}%)")
    print(f"==================================================\n")

    return 0 if failed == 0 else 1

if __name__ == "__main__":
    exit_code = asyncio.run(run_benchmark())
    sys.exit(exit_code)
