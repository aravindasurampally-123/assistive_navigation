"""
Central Configuration Module
AI-Powered Assistive Navigation System for Visually Impaired People
"""

import os
from pathlib import Path

# ============================================================
# BASE DIRECTORIES
# ============================================================
PROJECT_ROOT = Path(__file__).resolve().parent
MODELS_DIR = PROJECT_ROOT / "models"
DATABASE_DIR = PROJECT_ROOT / "database"
DOCS_DIR = PROJECT_ROOT / "docs"

# Ensure directories exist
MODELS_DIR.mkdir(parents=True, exist_ok=True)
DATABASE_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# CAMERA & DISPLAY
# ============================================================
CAMERA_INDEX = 0
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
CAMERA_FPS = 30
WINDOW_TITLE = "AI Assistive Navigation"

# ============================================================
# OBJECT DETECTION (YOLOv8)
# ============================================================
YOLO_MODEL_PATH = str(MODELS_DIR / "yolov8n.pt")
YOLO_CONFIDENCE_THRESHOLD = 0.45

# COCO classes considered navigational obstacles of high interest
NAVIGATIONAL_OBSTACLES = {
    "person", "chair", "table", "couch", "bed", "door", "bench",
    "car", "bus", "truck", "motorcycle", "bicycle", "traffic light",
    "stop sign", "fire hydrant", "dog", "cat", "backpack", "suitcase",
    "bottle", "potted plant"
}

# ============================================================
# DEPTH ESTIMATION (Depth Anything V2)
# ============================================================
DEPTH_MODEL_NAME = "depth-anything/Depth-Anything-V2-Small-hf"
# Monocular relative depth: Depth Anything outputs relative disparity/depth
# Higher values generally represent closer objects after normalization
DEPTH_INVERTED = False  # When True, lower score means closer; when False, higher means closer
DEPTH_VERY_CLOSE_THRESHOLD = 0.70  # Normalized 0-1
DEPTH_NEAR_THRESHOLD = 0.45

# ============================================================
# OCR & TEXT RECOGNITION (EasyOCR)
# ============================================================
OCR_LANGUAGES = ["en"]
OCR_CONFIDENCE_THRESHOLD = 0.60
OCR_SCAN_INTERVAL = 3.0  # seconds between background scans
MIN_OCR_TEXT_LENGTH = 2

# ============================================================
# VOICE ASSISTANT (TTS & STT)
# ============================================================
VOICE_RATE = 0       # SAPI rate: -10 to +10 (0 is normal)
VOICE_VOLUME = 100   # SAPI volume: 0 to 100
SPEECH_RECOGNITION_TIMEOUT = 5.0
SPEECH_PHRASE_TIME_LIMIT = 4.0

# Alert cooldowns per priority tier (seconds)
ALERT_COOLDOWNS = {
    "CRITICAL": 2.0,   # Immediate danger
    "HIGH": 4.0,       # Nearby obstacle
    "MEDIUM": 7.0,     # Turn instructions / notices
    "LOW": 10.0        # Ambient OCR text / non-urgent
}

# Priority ranks (higher number = higher priority)
PRIORITY_CRITICAL = 4
PRIORITY_HIGH = 3
PRIORITY_MEDIUM = 2
PRIORITY_LOW = 1
PRIORITY_NONE = 0

# ============================================================
# WALKING NAVIGATION
# ============================================================
DEFAULT_LATITUDE = 17.3850
DEFAULT_LONGITUDE = 78.4867
ORS_API_KEY = os.getenv("ORS_API_KEY", "")
OSRM_FALLBACK_URL = "https://router.project-osrm.org/route/v1/foot"
NAVIGATION_STEP_INTERVAL = 8.0  # seconds between step guidance updates

# ============================================================
# DATABASE & EMERGENCY
# ============================================================
DATABASE_PATH = str(DATABASE_DIR / "assistive_navigation.db")
DEFAULT_SOS_MESSAGE = "EMERGENCY: User requires immediate navigation assistance at coordinates:"
