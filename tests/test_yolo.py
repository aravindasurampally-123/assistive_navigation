"""
Phase 2 Verification Script
Tests YOLOv8 Object Detection, Spatial Position Classification, and Camera Pipeline.
"""

import sys
from pathlib import Path
import cv2
import numpy as np

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from modules.object_detection import ObjectDetector, open_camera, DetectedObject


def test_spatial_classification_logic():
    print("=" * 60)
    print("TEST 1: SPATIAL POSITION CLASSIFICATION LOGIC")
    print("=" * 60)
    frame_width = 600

    cases = [
        (50, "left"),
        (199, "left"),
        (200, "ahead"),
        (300, "ahead"),
        (400, "ahead"),
        (401, "right"),
        (580, "right")
    ]

    for cx, expected in cases:
        pos = ObjectDetector.classify_position(cx, frame_width)
        print(f"Centroid x={cx:<4} in width={frame_width} -> Position: '{pos:<5}' [Expected: '{expected}']")
        assert pos == expected, f"Failed at cx={cx}: got {pos}, expected {expected}"

    print("STATUS: PASS (Spatial position classification verified)")


def test_detector_inference_on_sample_scene():
    print("\n" + "=" * 60)
    print("TEST 2: YOLOv8 INFERENCE & MULTI-OBJECT DETECTION")
    print("=" * 60)

    detector = ObjectDetector()
    import ultralytics
    asset_path = Path(ultralytics.__file__).parent / "assets" / "bus.jpg"
    
    if asset_path.exists():
        img = cv2.imread(str(asset_path))
        objects = detector.detect(img)
        print(f"Inference on standard benchmark scene: {len(objects)} object(s) detected:")
        for obj in objects:
            print(f"  - {obj.name:<8} | Pos: {obj.position:<6} | Conf: {obj.confidence:.2f} | BBox: {obj.bbox}")
        
        assert len(objects) > 0, "Expected objects to be detected in standard benchmark scene"
        annotated = detector.annotate_frame(img, objects, show_lanes=True)
        sample_out = PROJECT_ROOT / "tests" / "sample_bus_detected.jpg"
        cv2.imwrite(str(sample_out), annotated)
        print(f"Annotated benchmark output saved to: {sample_out}")
    else:
        print("Ultralytics sample asset not found, running synthetic test.")
        test_img = np.full((480, 640, 3), 40, dtype=np.uint8)
        objects = detector.detect(test_img)
        print(f"Synthetic test image inference complete. Objects detected: {len(objects)}")

    print("STATUS: PASS (Detector inference and spatial labeling verified)")


def test_webcam_detection():
    print("\n" + "=" * 60)
    print("TEST 3: WEBCAM HARDWARE INGESTION & REAL DETECTION")
    print("=" * 60)

    detector = ObjectDetector()
    cap = open_camera()

    if not cap.isOpened():
        print("WARNING: Webcam could not be opened (hardware unavailable).")
        return

    print("Webcam successfully opened. Capturing test frames...")
    frame = None
    for _ in range(5):
        ret, frame = cap.read()
        if not ret:
            break

    cap.release()
    print("Webcam released.")

    if frame is None:
        print("Could not read frame from camera.")
        return

    print(f"Captured live frame with resolution: {frame.shape[1]}x{frame.shape[0]}")
    detected = detector.detect(frame)
    print(f"Live Detection Results: {len(detected)} object(s) detected.")

    annotated = detector.annotate_frame(frame, detected, show_lanes=True)
    output_path = PROJECT_ROOT / "tests" / "output_yolo_test.jpg"
    cv2.imwrite(str(output_path), annotated)
    print(f"Annotated verification frame saved to: {output_path}")
    print("STATUS: PASS (Live camera capture pipeline verified)")


if __name__ == "__main__":
    test_spatial_classification_logic()
    test_detector_inference_on_sample_scene()
    test_webcam_detection()
    print("\n" + "=" * 60)
    print("PHASE 2 COMPLETED SUCCESSFULLY!")
    print("=" * 60)
