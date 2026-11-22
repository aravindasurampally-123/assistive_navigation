"""
Phase 1 Verification Script
AI-Powered Assistive Navigation System
Verifies project environment, directories, configuration, and database subsystem.
"""

import os
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

def test_environment_and_directories():
    print("=" * 60)
    print("PHASE 1: ENVIRONMENT & ARCHITECTURE VERIFICATION")
    print("=" * 60)

    # 1. Python version
    print(f"\n[1/6] Python Version: {sys.version.split()[0]}")
    assert sys.version_info >= (3, 10), "Python 3.10+ required"
    print("      STATUS: OK (Python version meets requirements)")

    # 2. Directory structure
    required_dirs = ["modules", "interface", "database", "tests", "docs", "models"]
    print("\n[2/6] Checking Directory Structure:")
    for d in required_dirs:
        dir_path = PROJECT_ROOT / d
        exists = dir_path.is_dir()
        print(f"      - {d:<12}: {'[FOUND]' if exists else '[MISSING]'}")
        assert exists, f"Directory {d} is missing"
    print("      STATUS: OK (All project folders present)")

    # 3. Model weights presence or auto-download
    yolo_model = PROJECT_ROOT / "models" / "yolov8n.pt"
    print(f"\n[3/6] Checking YOLOv8 Model Weights:")
    if not yolo_model.is_file():
        print(f"      Weights not found locally. Auto-downloading yolov8n.pt...")
        from ultralytics import YOLO
        import shutil
        m = YOLO("yolov8n.pt")
        downloaded = Path("yolov8n.pt")
        if downloaded.is_file():
            shutil.copy(str(downloaded), str(yolo_model))

    assert yolo_model.is_file(), "yolov8n.pt model file not found in models/"
    size_mb = yolo_model.stat().st_size / (1024 * 1024)
    print(f"      Path: {yolo_model}")
    print(f"      Size: {size_mb:.2f} MB")
    print("      STATUS: OK (Model weights verified)")

    # 4. Config module
    print("\n[4/6] Loading Configuration (config.py):")
    import config
    print(f"      - Camera Index     : {config.CAMERA_INDEX}")
    print(f"      - YOLO Threshold   : {config.YOLO_CONFIDENCE_THRESHOLD}")
    print(f"      - Depth Model      : {config.DEPTH_MODEL_NAME}")
    print(f"      - OCR Languages    : {config.OCR_LANGUAGES}")
    print(f"      - Database Path    : {config.DATABASE_PATH}")
    print("      STATUS: OK (Configuration module loaded successfully)")

    # 5. SQLite Database CRUD Verification
    print("\n[5/6] Testing SQLite Database Initialization & CRUD:")
    from database.database import (
        init_db,
        get_setting,
        set_setting,
        get_emergency_contacts,
        add_emergency_contact,
        log_sos_event,
        get_sos_logs
    )
    init_db()
    test_val = get_setting("voice_rate")
    print(f"      - Default Setting 'voice_rate': {test_val}")

    set_setting("test_key", "test_value_123")
    read_back = get_setting("test_key")
    assert read_back == "test_value_123", "Database setting read-write mismatch"
    print(f"      - Setting Write/Read Verified : '{read_back}'")

    contacts = get_emergency_contacts()
    print(f"      - Emergency Contacts Count    : {len(contacts)}")
    assert len(contacts) > 0, "Default emergency contact not seeded"

    sos_id = log_sos_event(17.3850, 78.4867, "TEST_SIMULATED", "Phase 1 verification test alert")
    print(f"      - Logged Test SOS Event ID    : {sos_id}")
    sos_logs = get_sos_logs(limit=1)
    assert len(sos_logs) > 0, "Failed to retrieve SOS log"
    print(f"      - Retrieved SOS Status        : {sos_logs[0]['status']}")
    print("      STATUS: OK (SQLite database operational)")

    # 6. Core Deep Learning & CV Library Imports
    print("\n[6/6] Checking Core Library Bindings:")
    import cv2
    print(f"      - OpenCV Version      : {cv2.__version__}")

    import torch
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"      - PyTorch Version     : {torch.__version__} (Device: {device})")

    from ultralytics import YOLO
    print("      - Ultralytics YOLO    : Ready")

    import transformers
    print(f"      - Transformers Version: {transformers.__version__}")

    import easyocr
    print("      - EasyOCR             : Ready")

    print("      STATUS: OK (All deep learning dependencies verified)")

    print("\n" + "=" * 60)
    print("PHASE 1 VERIFICATION COMPLETED SUCCESSFULLY!")
    print("All architectural foundations and environments are verified.")
    print("=" * 60)

if __name__ == "__main__":
    test_environment_and_directories()
