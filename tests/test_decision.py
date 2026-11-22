"""
Phase 6 Verification Script
Tests AI Decision and Priority Engine Arbitration, Preemption, and De-duplication.
"""

import sys
import time
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from modules.ai_decision import AIDecisionEngine, DecisionResult
from modules.obstacle_detection import EvaluatedObstacle
from config import (
    PRIORITY_CRITICAL,
    PRIORITY_HIGH,
    PRIORITY_MEDIUM,
    PRIORITY_LOW,
    PRIORITY_NONE
)


def test_priority_arbitration_scenarios():
    print("=" * 60)
    print("TEST 1: MULTI-MODAL PRIORITY ARBITRATION MATRIX")
    print("=" * 60)

    engine = AIDecisionEngine()

    # Scenario A: Collision obstacle + Navigation instruction + OCR signboard simultaneously
    obs_critical = EvaluatedObstacle(
        name="person", position="ahead", fused_proximity="very close",
        depth_score=0.85, area_ratio=0.40, priority=PRIORITY_CRITICAL,
        hazard_level="CRITICAL", warning_message="Warning! person ahead. Stop!"
    )
    nav_msg = "Turn right in 30 meters onto Main Street"
    ocr_msg = "Signboard: EMERGENCY EXIT"

    decision_a = engine.arbitrate(
        obstacles=[obs_critical],
        navigation_instruction=nav_msg,
        ocr_announcement=ocr_msg
    )

    print("Scenario A (Simultaneous Critical Obstacle + Nav + OCR):")
    print(f"  Selected Level    : {decision_a.level} (Priority {decision_a.priority}) [Expected: CRITICAL]")
    print(f"  Selected Source   : {decision_a.source} [Expected: OBSTACLE]")
    print(f"  Selected Message  : '{decision_a.message}'")
    print(f"  Clear Audio Queue : {decision_a.clear_audio_queue} [Expected: True]")
    print(f"  Should Speak      : {decision_a.should_speak} [Expected: True]")

    assert decision_a.level == "CRITICAL", "Failed to prioritize CRITICAL obstacle"
    assert decision_a.clear_audio_queue is True, "CRITICAL priority must request audio queue clearing"
    assert decision_a.should_speak is True, "CRITICAL alert must be spoken"

    # Scenario B: High-priority near obstacle vs Navigation instruction
    engine.reset()
    obs_high = EvaluatedObstacle(
        name="chair", position="ahead", fused_proximity="near",
        depth_score=0.65, area_ratio=0.20, priority=PRIORITY_HIGH,
        hazard_level="HIGH", warning_message="Caution! chair nearby ahead."
    )
    decision_b = engine.arbitrate(
        obstacles=[obs_high],
        navigation_instruction=nav_msg,
        ocr_announcement=ocr_msg
    )

    print("\nScenario B (High Obstacle vs Nav vs OCR):")
    print(f"  Selected Level    : {decision_b.level} [Expected: HIGH]")
    print(f"  Selected Source   : {decision_b.source} [Expected: OBSTACLE]")
    assert decision_b.level == "HIGH", "Failed to prioritize HIGH obstacle over navigation"

    # Scenario C: Navigation instruction vs Scene OCR (No obstacles)
    engine.reset()
    decision_c = engine.arbitrate(
        obstacles=[],
        navigation_instruction=nav_msg,
        ocr_announcement=ocr_msg
    )

    print("\nScenario C (Navigation Instruction vs Scene OCR):")
    print(f"  Selected Level    : {decision_c.level} [Expected: MEDIUM]")
    print(f"  Selected Source   : {decision_c.source} [Expected: NAVIGATION]")
    print(f"  Selected Message  : '{decision_c.message}'")
    assert decision_c.level == "MEDIUM", "Failed to prioritize Navigation over OCR"
    assert decision_c.source == "NAVIGATION", "Source mismatch"

    print("STATUS: PASS (Priority arbitration hierarchy verified)")
    return engine


def test_preemption_and_cooldown_suppression():
    print("\n" + "=" * 60)
    print("TEST 2: PREEMPTION & LOWER-PRIORITY SUPPRESSION LOGIC")
    print("=" * 60)

    engine = AIDecisionEngine()

    # Step 1: Trigger CRITICAL obstacle
    obs_crit = EvaluatedObstacle(
        name="person", position="ahead", fused_proximity="very close",
        depth_score=0.90, area_ratio=0.42, priority=PRIORITY_CRITICAL,
        hazard_level="CRITICAL", warning_message="Warning! person ahead. Stop!"
    )
    dec_1 = engine.arbitrate(obstacles=[obs_crit])
    print(f"Step 1: Spoke CRITICAL alert -> should_speak={dec_1.should_speak} [Expected: True]")
    assert dec_1.should_speak is True

    # Step 2: Immediately attempt to announce LOW priority OCR text (0.1 seconds later)
    time.sleep(0.1)
    dec_2 = engine.arbitrate(ocr_announcement="Text detected: Room 101")
    print(f"Step 2: Low-priority OCR while Critical hazard is active -> should_speak={dec_2.should_speak} [Expected: False]")
    assert dec_2.should_speak is False, "Low priority alert must be suppressed during critical hazard"

    # Step 3: Immediate repeat of the exact same CRITICAL alert (within 2s cooldown)
    dec_3 = engine.arbitrate(obstacles=[obs_crit])
    print(f"Step 3: Immediate identical Critical repeat within cooldown -> should_speak={dec_3.should_speak} [Expected: False]")
    assert dec_3.should_speak is False, "Repeated critical alert within cooldown must be debounced"

    # Step 4: After cooldown elapsed (2.1s), same critical alert should be allowed to remind user
    print("Waiting 2.1s for cooldown expiry...")
    time.sleep(2.1)
    dec_4 = engine.arbitrate(obstacles=[obs_crit])
    print(f"Step 4: Critical alert after cooldown elapsed -> should_speak={dec_4.should_speak} [Expected: True]")
    assert dec_4.should_speak is True, "Critical reminder must speak after cooldown expires"

    print("STATUS: PASS (Preemption and cooldown suppression verified)")


def test_idle_state():
    print("\n" + "=" * 60)
    print("TEST 3: IDLE STATE VERIFICATION")
    print("=" * 60)

    engine = AIDecisionEngine()
    idle_dec = engine.arbitrate(obstacles=[], navigation_instruction=None, ocr_announcement=None)

    print(f"Idle Level  : {idle_dec.level} [Expected: NONE]")
    print(f"Idle Source : {idle_dec.source} [Expected: NONE]")
    print(f"Should Speak: {idle_dec.should_speak} [Expected: False]")

    assert idle_dec.level == "NONE"
    assert idle_dec.should_speak is False
    print("STATUS: PASS (Idle state verified)")


if __name__ == "__main__":
    test_priority_arbitration_scenarios()
    test_preemption_and_cooldown_suppression()
    test_idle_state()
    print("\n" + "=" * 60)
    print("PHASE 6 COMPLETED SUCCESSFULLY!")
    print("=" * 60)
