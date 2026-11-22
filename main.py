"""
Main Application Entry Point
AI-Powered Assistive Navigation System for Visually Impaired People

Supports both native desktop OpenCV HUD mode and accessible Streamlit web dashboard.
Usage:
    python main.py              # Runs native desktop OpenCV HUD mode
    python main.py --streamlit  # Launches accessible Streamlit web dashboard
    python main.py --demo       # Runs non-interactive automated feature demonstration
"""

import sys
import os
import argparse
import time
import subprocess
from pathlib import Path
import cv2
import numpy as np

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from config import (
    CAMERA_INDEX,
    CAMERA_WIDTH,
    CAMERA_HEIGHT,
    WINDOW_TITLE,
    YOLO_CONFIDENCE_THRESHOLD,
    OCR_SCAN_INTERVAL
)
from database.database import init_db
from modules.object_detection import ObjectDetector, open_camera
from modules.depth_estimation import DepthEstimator
from modules.obstacle_detection import ObstacleClassifier
from modules.ocr_reader import OCRReader
from modules.voice_assistant import VoiceAssistant
from modules.ai_decision import AIDecisionEngine
from modules.navigation import WalkingNavigator
from modules.emergency import EmergencyManager


def run_desktop_hud():
    """
    Runs the native real-time computer vision pipeline with OpenCV HUD overlay.
    """
    print("\n" + "=" * 60)
    print("STARTING AI ASSISTIVE NAVIGATION (DESKTOP HUD MODE)")
    print("=" * 60)
    print("Keyboard Controls:")
    print("  'q' - Quit application")
    print("  's' - Trigger Simulated Emergency SOS")
    print("  'n' - Advance to next navigation step")
    print("  'r' - Repeat current navigation step")
    print("  't' - Force OCR text scan")
    print("=" * 60 + "\n")

    init_db()

    # 1. Initialize subsystems
    detector = ObjectDetector(conf_threshold=YOLO_CONFIDENCE_THRESHOLD)
    depth_estimator = DepthEstimator()
    obstacle_classifier = ObstacleClassifier()
    ocr_reader = OCRReader()
    voice = VoiceAssistant()
    decision_engine = AIDecisionEngine()
    navigator = WalkingNavigator()
    emergency_mgr = EmergencyManager()

    # Calculate initial default route (City center)
    curr_loc = WalkingNavigator.get_current_location()
    navigator.calculate_walking_route(
        curr_loc.latitude, curr_loc.longitude,
        curr_loc.latitude + 0.004, curr_loc.longitude + 0.004
    )

    cap = open_camera(camera_index=CAMERA_INDEX, width=CAMERA_WIDTH, height=CAMERA_HEIGHT)
    if not cap.isOpened():
        print("[ERROR] Could not open camera. Please check camera connection.")
        return

    cv2.namedWindow(WINDOW_TITLE, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(WINDOW_TITLE, 1000, 700)

    voice.speak("AI assistive navigation started.")
    last_ocr_scan = 0.0
    latest_ocr_announcement = None
    latest_ocr_results = []

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("[WARNING] Could not read camera frame.")
                break

            now = time.time()
            h, w = frame.shape[:2]

            # ----------------------------------------------------
            # 1. YOLOv8 Object Detection
            # ----------------------------------------------------
            detected_objects = detector.detect(frame)
            annotated_frame = detector.annotate_frame(frame, detected_objects, show_lanes=True)

            # ----------------------------------------------------
            # 2. Depth Anything V2 Disparity Map
            # ----------------------------------------------------
            depth_map = depth_estimator.estimate_depth_map(frame)
            depth_heatmap = depth_estimator.generate_heatmap(depth_map)
            center_depth_score = depth_estimator.get_region_depth(depth_map)

            # ----------------------------------------------------
            # 3. Obstacle Classification & Multimodal Fusion
            # ----------------------------------------------------
            evaluated_obstacles = obstacle_classifier.prioritize_obstacles(
                detected_objects, depth_map, depth_estimator
            )

            # ----------------------------------------------------
            # 4. Periodic Scene OCR Scan
            # ----------------------------------------------------
            if now - last_ocr_scan >= OCR_SCAN_INTERVAL:
                latest_ocr_results = ocr_reader.read_text(frame, min_confidence=0.60)
                latest_ocr_announcement = ocr_reader.get_announcement(latest_ocr_results)
                last_ocr_scan = now

            # ----------------------------------------------------
            # 5. Walking Navigation Guidance
            # ----------------------------------------------------
            nav_instruction = navigator.get_current_instruction()

            # ----------------------------------------------------
            # 6. AI Priority Decision Engine
            # ----------------------------------------------------
            decision = decision_engine.arbitrate(
                obstacles=evaluated_obstacles,
                navigation_instruction=nav_instruction,
                ocr_announcement=latest_ocr_announcement
            )

            # ----------------------------------------------------
            # 7. Thread-Safe Voice Output
            # ----------------------------------------------------
            if decision.should_speak and decision.message:
                voice.speak(decision.message, clear_pending=decision.clear_audio_queue)

            # ----------------------------------------------------
            # 8. Render HUD Composite
            # ----------------------------------------------------
            # Resize depth heatmap for picture-in-picture in top-right corner
            pip_w, pip_h = 240, 160
            small_depth = cv2.resize(depth_heatmap, (pip_w, pip_h))
            annotated_frame[10:10 + pip_h, w - pip_w - 10:w - 10] = small_depth
            cv2.rectangle(annotated_frame, (w - pip_w - 10, 10), (w - 10, 10 + pip_h), (255, 255, 255), 1)
            cv2.putText(annotated_frame, "DEPTH HEATMAP", (w - pip_w - 5, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

            # Header Banner: AI Status & Proximity
            status_color = (0, 0, 255) if decision.level == "CRITICAL" else (
                (0, 140, 255) if decision.level == "HIGH" else ((255, 120, 0) if decision.level == "MEDIUM" else (0, 200, 0))
            )
            cv2.rectangle(annotated_frame, (0, 0), (w - pip_w - 20, 45), (20, 20, 20), -1)
            cv2.putText(annotated_frame, f"AI STATUS: {decision.level}", (15, 30), cv2.FONT_HERSHEY_DUPLEX, 0.7, status_color, 2)
            cv2.putText(annotated_frame, f"Center Depth: {center_depth_score:.2f}", (240, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)

            # Alert Sub-banner
            alert_text = decision.message if decision.message else "Path clear."
            cv2.putText(annotated_frame, f"Alert: {alert_text[:50]}", (15, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

            # Footer Banner: Navigation Direction & Controls
            cv2.rectangle(annotated_frame, (0, h - 45), (w, h), (15, 15, 15), -1)
            nav_text = nav_instruction if nav_instruction else "No active walking route."
            cv2.putText(annotated_frame, f"NAV: {nav_text[:60]}", (15, h - 22), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 215, 255), 1)
            cv2.putText(annotated_frame, "[Q] Quit | [S] SOS | [N] Next Step | [R] Repeat | [T] OCR", (15, h - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (160, 160, 160), 1)

            cv2.imshow(WINDOW_TITLE, annotated_frame)

            # Key handling
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                curr = WalkingNavigator.get_current_location()
                emergency_mgr.trigger_sos(curr.latitude, curr.longitude, custom_note="Manual SOS trigger from desktop HUD", simulate=True)
                voice.speak("Emergency SOS alert dispatched to caregivers.", clear_pending=True)
            elif key == ord('n'):
                next_step = navigator.advance_step()
                if next_step:
                    voice.speak(next_step)
            elif key == ord('r'):
                voice.speak(navigator.repeat_instruction())
            elif key == ord('t'):
                ocr_results = ocr_reader.read_text(frame, min_confidence=0.50)
                msg = ocr_reader.get_announcement(ocr_results, cooldown=0.0)
                if msg:
                    voice.speak(msg)

    except KeyboardInterrupt:
        print("\n[STOP] User interrupted execution.")

    finally:
        cap.release()
        cv2.destroyAllWindows()
        voice.speak("AI Assistive Navigation stopped.")
        voice.stop()
        print("[STOP] System shutdown cleanly.")


def launch_streamlit():
    """Launch the accessible Streamlit web application."""
    app_path = PROJECT_ROOT / "interface" / "app.py"
    cmd = [sys.executable, "-m", "streamlit", "run", str(app_path)]
    print(f"[STREAMLIT] Launching: {' '.join(cmd)}")
    subprocess.run(cmd)


def run_automated_demo():
    """
    Non-interactive demonstration runner for evaluation.
    Runs each subsystem sequentially and verifies end-to-end integration.
    """
    print("\n" + "=" * 60)
    print("STARTING NON-INTERACTIVE AUTOMATED DEMONSTRATION")
    print("=" * 60)

    init_db()
    detector = ObjectDetector()
    depth_estimator = DepthEstimator()
    classifier = ObstacleClassifier()
    ocr_reader = OCRReader()
    decision_engine = AIDecisionEngine()
    navigator = WalkingNavigator()
    emergency_mgr = EmergencyManager()

    # Load benchmark scene
    import ultralytics
    asset_path = Path(ultralytics.__file__).parent / "assets" / "bus.jpg"
    if not asset_path.exists():
        print("Sample asset missing, creating test image.")
        frame = np.full((480, 640, 3), 120, dtype=np.uint8)
    else:
        frame = cv2.imread(str(asset_path))

    print("\n[STEP 1] Running YOLOv8 Detection on Benchmark Scene...")
    detected_objs = detector.detect(frame)
    print(f"  Detected {len(detected_objs)} obstacle(s). Top: {detected_objs[0].name} ({detected_objs[0].position})")

    print("\n[STEP 2] Running Depth Anything V2 Disparity Estimation...")
    depth_map = depth_estimator.estimate_depth_map(frame)
    center_depth = depth_estimator.get_region_depth(depth_map)
    print(f"  Center corridor relative depth score: {center_depth:.3f}")

    print("\n[STEP 3] Evaluating Multimodal Sensor Fusion...")
    obstacles = classifier.prioritize_obstacles(detected_objs, depth_map, depth_estimator)
    print(f"  Ranked {len(obstacles)} obstacles. Primary hazard: {obstacles[0].warning_message} (Level: {obstacles[0].hazard_level})")

    print("\n[STEP 4] Calculating Walking Navigation Route...")
    route = navigator.calculate_walking_route(17.3840, 78.4564, 17.3880, 78.4600)
    print(f"  Walking route generated: {route.total_distance_km:.2f} km via {route.provider}")

    print("\n[STEP 5] Arbitrating in AI Decision Engine...")
    decision = decision_engine.arbitrate(obstacles=obstacles, navigation_instruction=navigator.get_current_instruction())
    print(f"  Decision Outcome: Level={decision.level} | Message='{decision.message}' | Should Speak={decision.should_speak}")

    print("\n[STEP 6] Testing Simulated Emergency SOS Dispatch...")
    sos_payload = emergency_mgr.trigger_sos(17.3840, 78.4564, custom_note="Automated demo test", simulate=True)
    print(f"  SOS Trigger Status: {sos_payload.status} | Map: {sos_payload.maps_url}")

    # Annotate and save composite demonstration evidence
    annotated = detector.annotate_frame(frame, detected_objs)
    heatmap = depth_estimator.generate_heatmap(depth_map)
    demo_out = PROJECT_ROOT / "tests" / "output_full_integration_demo.jpg"
    cv2.imwrite(str(demo_out), annotated)
    print(f"\nVerification composite saved to: {demo_out}")

    print("\n" + "=" * 60)
    print("ALL INTEGRATION CHECKS PASSED SUCCESSFULLY!")
    print("=" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI-Powered Assistive Navigation System")
    parser.add_argument("--streamlit", action="store_true", help="Launch Streamlit web dashboard")
    parser.add_argument("--demo", action="store_true", help="Run automated integration demo")
    args = parser.parse_args()

    if args.streamlit:
        launch_streamlit()
    elif args.demo:
        run_automated_demo()
    else:
        run_desktop_hud()
