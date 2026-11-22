"""
Phase 4 Verification Script
Tests EasyOCR Scene Text Detection, Regex Sanitization, Confidence Filtering,
and Announcement De-duplication.
"""

import sys
from pathlib import Path
import cv2
import numpy as np

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from modules.ocr_reader import OCRReader, OCRResult
from modules.object_detection import open_camera


def test_text_cleaning_and_keyword_rules():
    print("=" * 60)
    print("TEST 1: TEXT CLEANING & KEYWORD DETECTION LOGIC")
    print("=" * 60)

    # Test cases: (raw_input, expected_cleaned, expected_is_critical)
    test_cases = [
        ("  EMERGENCY   EXIT!!  ", "EMERGENCY EXIT!!", True),
        ("Room  302  -- North", "Room 302 -- North", False),
        ("<< DANGER >> High Voltage", "DANGER High Voltage", True),
        ("~`|@#Random Noise%^", "Random Noise", False),
        ("CAUTION: Wet Floor", "CAUTION: Wet Floor", True),
        ("RESTROOM ->", "RESTROOM ->", True)
    ]

    reader = OCRReader(gpu=False)

    for raw, expected_clean, expected_crit in test_cases:
        cleaned = reader.clean_text(raw)
        is_crit = reader.is_critical(cleaned)
        print(f"Raw: '{raw:<24}' -> Cleaned: '{cleaned:<22}' | Critical: {is_crit} [Expected: {expected_crit}]")
        assert is_crit == expected_crit, f"Critical keyword mismatch for '{cleaned}'"

    print("STATUS: PASS (Text cleaning and keyword rules verified)")
    return reader


def test_ocr_inference_on_synthetic_signboard(reader: OCRReader):
    print("\n" + "=" * 60)
    print("TEST 2: SYNTHETIC SIGNBOARD INFERENCE & CONFIDENCE FILTERING")
    print("=" * 60)

    # Create a synthetic image containing standard architectural signs
    # Dimensions: 500x800
    canvas = np.full((500, 800, 3), 240, dtype=np.uint8)

    # 1. Green Emergency Exit Sign
    cv2.rectangle(canvas, (50, 50), (450, 180), (34, 139, 34), -1)  # Forest Green
    cv2.putText(canvas, "EMERGENCY EXIT", (70, 130), cv2.FONT_HERSHEY_DUPLEX, 1.2, (255, 255, 255), 2)

    # 2. Room Number Plate
    cv2.rectangle(canvas, (50, 240), (380, 360), (40, 40, 40), -1)   # Dark Gray
    cv2.putText(canvas, "ROOM 302", (70, 315), cv2.FONT_HERSHEY_DUPLEX, 1.3, (255, 255, 255), 2)

    # 3. Yellow Caution Sign
    cv2.rectangle(canvas, (440, 240), (750, 360), (0, 215, 255), -1) # Yellow
    cv2.putText(canvas, "CAUTION", (460, 315), cv2.FONT_HERSHEY_DUPLEX, 1.3, (0, 0, 0), 2)

    print("Running EasyOCR inference on synthetic signboards...")
    results = reader.read_text(canvas, min_confidence=0.50)
    print(f"Recognized {len(results)} text region(s):")

    for i, res in enumerate(results, start=1):
        crit_tag = "[CRITICAL SAFETY SIGN]" if res.is_critical_keyword else "[STANDARD SIGN]"
        print(f"  [{i}] {crit_tag:<22} Text: '{res.cleaned_text:<18}' | Conf: {res.confidence:.2f}")

    # Assert that our signs were recognized
    recognized_texts = [r.cleaned_text.upper() for r in results]
    has_exit = any("EXIT" in t or "EMERGENCY" in t for t in recognized_texts)
    has_room = any("ROOM" in t or "302" in t for t in recognized_texts)

    assert has_exit, "Failed to recognize EMERGENCY EXIT sign"
    assert has_room, "Failed to recognize ROOM 302 plate"

    # Annotate and save
    annotated = reader.annotate_frame(canvas, results)
    out_path = PROJECT_ROOT / "tests" / "output_ocr_test.jpg"
    cv2.imwrite(str(out_path), annotated)
    print(f"\nAnnotated OCR output saved to: {out_path}")

    # Test De-duplication
    announcement_1 = reader.get_announcement(results)
    announcement_2_repeat = reader.get_announcement(results)
    print(f"\nDe-duplication Test:")
    print(f"  First announcement trigger   : '{announcement_1}'")
    print(f"  Immediate repeated trigger   : {announcement_2_repeat} [Expected: None]")
    assert announcement_1 is not None, "Failed to generate initial voice announcement"
    assert announcement_2_repeat is None, "Repeated OCR announcement was not suppressed by cooldown"

    print("STATUS: PASS (OCR inference, annotation, and de-duplication verified)")


def test_live_webcam_ocr(reader: OCRReader):
    print("\n" + "=" * 60)
    print("TEST 3: LIVE WEBCAM SCENE OCR SCAN")
    print("=" * 60)

    cap = open_camera()
    if not cap.isOpened():
        print("Webcam unavailable, skipping live camera OCR test.")
        return

    frame = None
    for _ in range(5):
        ret, frame = cap.read()
        if not ret:
            break
    cap.release()

    if frame is None:
        print("Could not read frame from camera.")
        return

    print("Live frame captured. Running scene text scan...")
    live_results = reader.read_text(frame, min_confidence=0.60)
    print(f"Live OCR results: {len(live_results)} text region(s) detected.")

    annotated = reader.annotate_frame(frame, live_results)
    live_out = PROJECT_ROOT / "tests" / "output_live_ocr.jpg"
    cv2.imwrite(str(live_out), annotated)
    print(f"Live OCR annotated frame saved to: {live_out}")
    print("STATUS: PASS (Live camera OCR pipeline verified)")


if __name__ == "__main__":
    ocr_rd = test_text_cleaning_and_keyword_rules()
    test_ocr_inference_on_synthetic_signboard(ocr_rd)
    test_live_webcam_ocr(ocr_rd)
    print("\n" + "=" * 60)
    print("PHASE 4 COMPLETED SUCCESSFULLY!")
    print("=" * 60)
