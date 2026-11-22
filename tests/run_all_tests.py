"""
Master Automated Test Runner & Verification Suite
AI-Powered Assistive Navigation System for Visually Impaired People

Executes all 8 phase verification test suites sequentially in isolated processes,
measures execution duration, and generates a unified academic evaluation report.
"""

import sys
import subprocess
import time
from pathlib import Path
from typing import List, Dict, Any

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent

TEST_SUITES = [
    {
        "id": "PHASE_1",
        "name": "Architecture, SQLite Database & Config",
        "script": PROJECT_ROOT / "tests" / "test_phase1.py"
    },
    {
        "id": "PHASE_2",
        "name": "YOLOv8 Detection & Spatial Position Classification",
        "script": PROJECT_ROOT / "tests" / "test_yolo.py"
    },
    {
        "id": "PHASE_3",
        "name": "Depth Anything V2 & Multimodal Hazard Fusion",
        "script": PROJECT_ROOT / "tests" / "test_depth.py"
    },
    {
        "id": "PHASE_4",
        "name": "EasyOCR Text Recognition & Signboard Filtering",
        "script": PROJECT_ROOT / "tests" / "test_ocr.py"
    },
    {
        "id": "PHASE_5",
        "name": "Thread-Safe SAPI Voice & Voice Command NLP",
        "script": PROJECT_ROOT / "tests" / "test_voice.py"
    },
    {
        "id": "PHASE_6",
        "name": "AI Decision & 4-Tier Priority Arbitration Engine",
        "script": PROJECT_ROOT / "tests" / "test_decision.py"
    },
    {
        "id": "PHASE_7",
        "name": "Walking Navigation & Resilient OSRM Fallback",
        "script": PROJECT_ROOT / "tests" / "test_navigation.py"
    },
    {
        "id": "PHASE_8",
        "name": "Emergency Assistance, Safeguards & SOS Logging",
        "script": PROJECT_ROOT / "tests" / "test_emergency.py"
    }
]


def run_master_test_suite():
    print("\n" + "=" * 78)
    print("AI ASSISTIVE NAVIGATION - MASTER AUTOMATED TEST SUITE")
    print("Major Academic B.Tech AIML Evaluation")
    print("=" * 78)

    results: List[Dict[str, Any]] = []
    total_start = time.time()

    for idx, suite in enumerate(TEST_SUITES, start=1):
        print(f"\n[{idx}/{len(TEST_SUITES)}] Running {suite['id']}: {suite['name']} ...")
        script_path = str(suite["script"])

        start_t = time.time()
        try:
            res = subprocess.run(
                [sys.executable, script_path],
                cwd=str(PROJECT_ROOT),
                capture_output=True,
                text=True,
                timeout=180
            )
            elapsed = time.time() - start_t
            passed = (res.returncode == 0)

            if passed:
                status_str = "PASS"
                print(f"      STATUS: [PASS] ({elapsed:.2f}s)")
            else:
                status_str = "FAIL"
                print(f"      STATUS: [FAIL] ({elapsed:.2f}s)")
                print(f"      ERROR OUTPUT:\n{res.stderr[-400:]}")

            results.append({
                "suite": suite["id"],
                "name": suite["name"],
                "status": status_str,
                "duration": elapsed,
                "error": res.stderr if not passed else None
            })

        except subprocess.TimeoutExpired:
            elapsed = time.time() - start_t
            print(f"      STATUS: [TIMEOUT] ({elapsed:.2f}s)")
            results.append({
                "suite": suite["id"],
                "name": suite["name"],
                "status": "TIMEOUT",
                "duration": elapsed,
                "error": "Execution exceeded 180s timeout"
            })

    total_elapsed = time.time() - total_start

    # Print Summary Table
    print("\n" + "=" * 78)
    print(f"{'TEST SUITE':<10} | {'MODULE EVALUATED':<46} | {'STATUS':<6} | {'TIME'}")
    print("-" * 78)

    pass_count = 0
    for r in results:
        status_disp = f"[{r['status']}]"
        print(f"{r['suite']:<10} | {r['name'][:46]:<46} | {status_disp:<8} | {r['duration']:>5.2f}s")
        if r["status"] == "PASS":
            pass_count += 1

    print("=" * 78)
    print(f"OVERALL SUMMARY: {pass_count}/{len(TEST_SUITES)} Suites Passed ({pass_count/len(TEST_SUITES):.0%}) | Total Duration: {total_elapsed:.2f}s")
    print("=" * 78)

    if pass_count == len(TEST_SUITES):
        print("\nALL VERIFICATION CRITERIA SATISFIED! Project is ready for demonstration.")
        return 0
    else:
        print(f"\n{len(TEST_SUITES) - pass_count} SUITE(S) FAILED. Review errors above.")
        return 1


if __name__ == "__main__":
    exit_code = run_master_test_suite()
    sys.exit(exit_code)
