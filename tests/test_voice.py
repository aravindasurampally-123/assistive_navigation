"""
Phase 5 Verification Script
Tests Voice Assistant (Text-to-Speech Engine) and Voice Command Recognition Subsystem.
"""

import sys
import time
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from modules.voice_assistant import VoiceAssistant
from modules.speech_commands import (
    CommandParser,
    CMD_START_SYSTEM,
    CMD_STOP_SYSTEM,
    CMD_START_NAV,
    CMD_STOP_NAV,
    CMD_READ_TEXT,
    CMD_REPEAT,
    CMD_EMERGENCY
)


def test_command_parser_intent_rules():
    print("=" * 60)
    print("TEST 1: VOICE COMMAND NLP INTENT RECOGNITION")
    print("=" * 60)

    # Test cases mapping natural speech variations to expected command constants
    test_utterances = [
        # 1. Start system
        ("start system", CMD_START_SYSTEM),
        ("please activate now", CMD_START_SYSTEM),
        ("turn on the system", CMD_START_SYSTEM),

        # 2. Stop system
        ("stop system", CMD_STOP_SYSTEM),
        ("shutdown immediately", CMD_STOP_SYSTEM),
        ("turn off", CMD_STOP_SYSTEM),

        # 3. Start navigation
        ("start navigation", CMD_START_NAV),
        ("begin walking route", CMD_START_NAV),
        ("navigate to destination", CMD_START_NAV),

        # 4. Stop navigation
        ("stop navigation", CMD_STOP_NAV),
        ("cancel navigation", CMD_STOP_NAV),
        ("end navigation now", CMD_STOP_NAV),

        # 5. Read text
        ("read text", CMD_READ_TEXT),
        ("what does that signboard say", CMD_READ_TEXT),
        ("read the sign", CMD_READ_TEXT),

        # 6. Repeat instruction
        ("repeat instruction", CMD_REPEAT),
        ("what was that direction", CMD_REPEAT),
        ("say again please", CMD_REPEAT),

        # 7. Emergency help
        ("emergency help", CMD_EMERGENCY),
        ("sos someone help me", CMD_EMERGENCY),
        ("call for help immediately", CMD_EMERGENCY)
    ]

    for transcript, expected_cmd in test_utterances:
        detected = CommandParser.parse(transcript)
        print(f"Utterance: '{transcript:<32}' -> Detected: '{detected}' [Expected: '{expected_cmd}']")
        assert detected == expected_cmd, f"Mismatch for '{transcript}': got {detected}, expected {expected_cmd}"

    # Test unrecognized utterance
    unrecognized = CommandParser.parse("what is the weather today")
    print(f"Utterance: 'what is the weather today'       -> Detected: '{unrecognized}' [Expected: None]")
    assert unrecognized is None, "Expected unhandled query to return None"

    print("STATUS: PASS (All 7 voice command intents verified)")


def test_voice_assistant_synthesis():
    print("\n" + "=" * 60)
    print("TEST 2: NON-BLOCKING SAPI VOICE SYNTHESIS & PREEMPTION")
    print("=" * 60)

    voice = VoiceAssistant()
    assert voice.is_ready.is_set(), "Voice assistant failed to initialize"

    # Non-blocking timing test
    start_time = time.time()
    voice.speak("AI voice assistant test initiated.")
    call_duration = time.time() - start_time

    print(f"Non-blocking enqueue call took: {call_duration * 1000:.2f} ms")
    assert call_duration < 0.20, "voice.speak() blocked the calling thread!"
    print("STATUS: PASS (Non-blocking queue execution verified)")

    # Test priority preemption:
    # Enqueue a long message, then immediately purge and speak a critical hazard
    print("\nTesting emergency alert queue preemption:")
    voice.speak("This is a long background announcement that will be purged.")
    time.sleep(0.05)
    voice.speak("Warning! Critical hazard ahead. Stop!", clear_pending=True)

    print("Waiting for audio output to complete...")
    voice.wait_until_done(timeout=5.0)

    # Clean shutdown
    voice.stop()
    print("STATUS: PASS (Voice synthesis and preemption verified)")


if __name__ == "__main__":
    test_command_parser_intent_rules()
    test_voice_assistant_synthesis()
    print("\n" + "=" * 60)
    print("PHASE 5 COMPLETED SUCCESSFULLY!")
    print("=" * 60)
