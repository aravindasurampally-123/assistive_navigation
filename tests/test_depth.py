"""
Phase 3 Verification Script
Tests Depth Anything V2 Monocular Depth Estimation, Depth Heatmap Generation,
and Multimodal Obstacle Hazard Prioritization.
"""

import sys
from pathlib import Path
import cv2
import numpy as np

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from modules.depth_estimation import DepthEstimator
from modules.obstacle_detection import ObstacleClassifier, EvaluatedObstacle
from modules.object_detection import ObjectDetector, DetectedObject, open_camera


def test_depth_estimation_and_heatmap():
    print("=" * 60)
    print("TEST 1: DEPTH ANYTHING V2 MODEL INFERENCE & HEATMAP")
    print("=" * 60)

    estimator = DepthEstimator()

    # Create synthetic gradient test image simulating near ground and distant sky
    test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    for y in range(480):
        test_frame[y, :] = int(y / 480.0 * 255)

    print("Running depth inference on test frame...")
    depth_map = estimator.estimate_depth_map(test_frame)

    assert depth_map.shape == (480, 640), f"Unexpected depth map shape: {depth_map.shape}"
    assert 0.0 <= np.min(depth_map) <= np.max(depth_map) <= 1.0, "Depth map values not normalized [0, 1]"
    print(f"Depth map generated successfully. Min: {np.min(depth_map):.3f}, Max: {np.max(depth_map):.3f}")

    # Central corridor depth
    center_depth = estimator.get_region_depth(depth_map)
    proximity_band = estimator.classify_relative_depth(center_depth)
    print(f"Center corridor depth score: {center_depth:.3f} -> Proximity: '{proximity_band}'")

    # Heatmap generation
    heatmap = estimator.generate_heatmap(depth_map)
    assert heatmap.shape == (480, 640, 3), "Heatmap shape mismatch"
    heatmap_out = PROJECT_ROOT / "tests" / "output_depth_heatmap.jpg"
    cv2.imwrite(str(heatmap_out), heatmap)
    print(f"Heatmap visualization saved to: {heatmap_out}")
    print("STATUS: PASS (Depth model and heatmap generation verified)")
    return estimator


def test_multimodal_obstacle_fusion(estimator: DepthEstimator):
    print("\n" + "=" * 60)
    print("TEST 2: MULTIMODAL SENSOR FUSION & HAZARD PRIORITIZATION")
    print("=" * 60)

    classifier = ObstacleClassifier()

    # Create a simulated synthetic depth map
    synthetic_depth = np.full((480, 640), 0.5, dtype=np.float32)

    # Simulate 3 detected objects with varying positions and scales:
    # 1. Very close person directly ahead
    obj_critical = DetectedObject(
        class_id=0, name="person", confidence=0.88,
        bbox=(200, 100, 440, 460), centroid=(320, 280),
        position="ahead", width=240, height=360,
        area_ratio=0.38, is_navigational_hazard=True
    )

    # 2. Near chair on the left
    obj_high = DetectedObject(
        class_id=56, name="chair", confidence=0.82,
        bbox=(20, 200, 180, 420), centroid=(100, 310),
        position="left", width=160, height=220,
        area_ratio=0.12, is_navigational_hazard=True
    )

    # 3. Medium distance bicycle on the right
    obj_medium = DetectedObject(
        class_id=1, name="bicycle", confidence=0.75,
        bbox=(480, 220, 620, 380), centroid=(550, 300),
        position="right", width=140, height=160,
        area_ratio=0.07, is_navigational_hazard=True
    )

    evaluated = classifier.prioritize_obstacles([obj_critical, obj_high, obj_medium], synthetic_depth, estimator)

    print(f"Evaluated {len(evaluated)} obstacle(s):")
    for i, obs in enumerate(evaluated, start=1):
        print(f"  [{i}] Level: {obs.hazard_level:<8} (Pri {obs.priority}) | {obs.name:<8} | "
              f"Pos: {obs.position:<6} | Prox: {obs.fused_proximity:<10} | Message: '{obs.warning_message}'")

    # Assert priority hierarchy: Critical should be ranked #1
    assert evaluated[0].hazard_level == "CRITICAL", "Critical collision hazard was not ranked #1"
    assert "Stop" in evaluated[0].warning_message, "Critical warning message missing 'Stop'"
    assert evaluated[1].hazard_level in ["HIGH", "MEDIUM"], "Secondary obstacle misranked"

    # Test de-duplication logic
    should_1 = classifier.should_announce(evaluated[0])
    should_2_repeat = classifier.should_announce(evaluated[0])  # immediate repeat should be suppressed by cooldown
    print(f"\nDe-duplication Test:")
    print(f"  First announcement trigger   : {should_1} [Expected: True]")
    print(f"  Immediate repeated trigger   : {should_2_repeat} [Expected: False]")
    assert should_1 is True, "First alert should trigger"
    assert should_2_repeat is False, "Repeated alert should be suppressed by cooldown"

    print("STATUS: PASS (Sensor fusion and alert de-duplication verified)")


def test_live_webcam_depth_and_fusion(estimator: DepthEstimator):
    print("\n" + "=" * 60)
    print("TEST 3: LIVE WEBCAM INGESTION WITH DEPTH ESTIMATION")
    print("=" * 60)

    cap = open_camera()
    if not cap.isOpened():
        print("Webcam unavailable, skipping live camera frame.")
        return

    frame = None
    for _ in range(5):
        ret, frame = cap.read()
        if not ret:
            break
    cap.release()

    if frame is None:
        print("Failed to capture live frame.")
        return

    print("Live frame captured. Running depth estimation...")
    depth_map = estimator.estimate_depth_map(frame)
    center_score = estimator.get_region_depth(depth_map)
    proximity = estimator.classify_relative_depth(center_score)
    print(f"Live central depth score: {center_score:.3f} ({proximity})")

    heatmap = estimator.generate_heatmap(depth_map)
    live_heatmap_path = PROJECT_ROOT / "tests" / "output_live_depth.jpg"
    cv2.imwrite(str(live_heatmap_path), heatmap)
    print(f"Live depth heatmap saved to: {live_heatmap_path}")
    print("STATUS: PASS (Live depth estimation pipeline verified)")


if __name__ == "__main__":
    depth_est = test_depth_estimation_and_heatmap()
    test_multimodal_obstacle_fusion(depth_est)
    test_live_webcam_depth_and_fusion(depth_est)
    print("\n" + "=" * 60)
    print("PHASE 3 COMPLETED SUCCESSFULLY!")
    print("=" * 60)
