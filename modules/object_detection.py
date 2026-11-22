"""
Module 1: Real-Time Object Detection
AI-Powered Assistive Navigation System for Visually Impaired People

Uses YOLOv8 to detect surrounding obstacles, calculate their bounding box coordinates,
and classify their lateral spatial position (left, ahead, right) relative to the user.
"""

from dataclasses import dataclass
from typing import List, Tuple, Optional
from pathlib import Path
import shutil
import cv2
import numpy as np
from ultralytics import YOLO

from config import (
    YOLO_MODEL_PATH,
    YOLO_CONFIDENCE_THRESHOLD,
    NAVIGATIONAL_OBSTACLES,
    CAMERA_INDEX,
    CAMERA_WIDTH,
    CAMERA_HEIGHT
)


@dataclass
class DetectedObject:
    """Structured representation of a detected obstacle in the scene."""
    class_id: int
    name: str
    confidence: float
    bbox: Tuple[int, int, int, int]  # (x1, y1, x2, y2)
    centroid: Tuple[int, int]         # (cx, cy)
    position: str                     # "left", "ahead", "right"
    width: int
    height: int
    area_ratio: float                 # bbox area relative to full frame
    is_navigational_hazard: bool


class ObjectDetector:
    """
    Encapsulates YOLOv8 model loading, inference, lateral position estimation,
    and visual HUD annotation.
    """

    def __init__(self, model_path: str = YOLO_MODEL_PATH, conf_threshold: float = YOLO_CONFIDENCE_THRESHOLD):
        """Initialize the YOLOv8 model with automatic weight download fallback."""
        self.conf_threshold = conf_threshold
        target_path = Path(model_path)

        if target_path.is_file():
            print(f"[YOLO] Loading model from: {target_path} ...")
            self.model = YOLO(str(target_path))
        else:
            print(f"[YOLO] Model weights not found at {target_path}. Auto-downloading yolov8n.pt...")
            self.model = YOLO("yolov8n.pt")
            # If target directory exists, copy weights there for future runs
            try:
                target_path.parent.mkdir(parents=True, exist_ok=True)
                downloaded = Path("yolov8n.pt")
                if downloaded.is_file() and not target_path.is_file():
                    shutil.copy(str(downloaded), str(target_path))
            except Exception as e:
                print(f"[YOLO] Note: Could not cache to target dir ({e})")

        self.class_names = self.model.names
        print(f"[YOLO] Successfully loaded model with {len(self.class_names)} classes.")

    @staticmethod
    def classify_position(cx: int, frame_width: int) -> str:
        """
        Divide the horizontal field-of-view into three spatial zones:
        - Left   : 0% to 33.3% of frame width
        - Ahead  : 33.3% to 66.6% of frame width (directly in path)
        - Right  : 66.6% to 100% of frame width
        """
        one_third = frame_width / 3.0
        two_thirds = 2.0 * one_third

        if cx < one_third:
            return "left"
        elif cx > two_thirds:
            return "right"
        else:
            return "ahead"

    def detect(self, frame: np.ndarray, filter_obstacles_only: bool = False) -> List[DetectedObject]:
        """
        Run inference on an input BGR OpenCV frame.
        Returns a list of DetectedObject instances sorted by area (largest/closest first).
        """
        if frame is None or frame.size == 0:
            return []

        frame_height, frame_width = frame.shape[:2]
        total_frame_area = float(frame_width * frame_height)

        # Run inference in verbose=False mode for clean output
        results = self.model(frame, conf=self.conf_threshold, verbose=False)

        detected_objects: List[DetectedObject] = []

        for r in results:
            boxes = r.boxes
            if boxes is None:
                continue

            for box in boxes:
                xyxy = box.xyxy[0].cpu().numpy().astype(int)
                x1, y1, x2, y2 = int(xyxy[0]), int(xyxy[1]), int(xyxy[2]), int(xyxy[3])

                conf = float(box.conf[0].cpu().numpy())
                class_id = int(box.cls[0].cpu().numpy())
                name = self.class_names.get(class_id, f"obj_{class_id}")

                is_hazard = name.lower() in NAVIGATIONAL_OBSTACLES

                if filter_obstacles_only and not is_hazard:
                    continue

                w = max(0, x2 - x1)
                h = max(0, y2 - y1)
                cx = x1 + (w // 2)
                cy = y1 + (h // 2)

                area_ratio = (w * h) / total_frame_area
                position = self.classify_position(cx, frame_width)

                detected_objects.append(DetectedObject(
                    class_id=class_id,
                    name=name,
                    confidence=conf,
                    bbox=(x1, y1, x2, y2),
                    centroid=(cx, cy),
                    position=position,
                    width=w,
                    height=h,
                    area_ratio=area_ratio,
                    is_navigational_hazard=is_hazard
                ))

        # Sort detected objects by area ratio descending (larger objects are typically closer)
        detected_objects.sort(key=lambda obj: obj.area_ratio, reverse=True)
        return detected_objects

    def annotate_frame(self, frame: np.ndarray, objects: List[DetectedObject], show_lanes: bool = True) -> np.ndarray:
        """
        Draw bounding boxes, class labels, spatial centroids, and navigational lane boundaries.
        """
        annotated = frame.copy()
        h, w = annotated.shape[:2]

        # Draw subtle vertical boundary lines dividing the 3 spatial zones
        if show_lanes:
            x_left = int(w / 3.0)
            x_right = int(2.0 * w / 3.0)
            cv2.line(annotated, (x_left, 0), (x_left, h), (180, 180, 180), 1, cv2.LINE_AA)
            cv2.line(annotated, (x_right, 0), (x_right, h), (180, 180, 180), 1, cv2.LINE_AA)
            cv2.putText(annotated, "LEFT", (20, h - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
            cv2.putText(annotated, "AHEAD", (x_left + 20, h - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
            cv2.putText(annotated, "RIGHT", (x_right + 20, h - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

        for obj in objects:
            x1, y1, x2, y2 = obj.bbox
            
            # Select color based on lateral position
            # Ahead = Red/Orange warning; Left/Right = Cyan/Green guidance
            if obj.position == "ahead":
                color = (0, 70, 255)  # Orange-Red in BGR
            elif obj.position == "left":
                color = (255, 170, 0)  # Cyan-Blue
            else:
                color = (0, 200, 100)  # Green

            # Draw bounding box
            cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)

            # Draw centroid dot
            cv2.circle(annotated, obj.centroid, 4, color, -1)

            # Formulate label
            label = f"{obj.name} ({obj.position}) {obj.confidence:.2f}"
            (text_w, text_h), baseline = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)

            # Draw label background
            cv2.rectangle(
                annotated,
                (x1, max(y1 - text_h - 6, 0)),
                (x1 + text_w + 4, max(y1, text_h + 6)),
                color,
                -1
            )
            cv2.putText(
                annotated,
                label,
                (x1 + 2, max(y1 - 4, text_h)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                1,
                cv2.LINE_AA
            )

        return annotated


def open_camera(camera_index: int = CAMERA_INDEX, width: int = CAMERA_WIDTH, height: int = CAMERA_HEIGHT) -> cv2.VideoCapture:
    """Helper to open camera using CAP_DSHOW on Windows for fast initialization."""
    cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
    if not cap.isOpened():
        cap = cv2.VideoCapture(camera_index)  # fallback to default backend
    if cap.isOpened():
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    return cap
