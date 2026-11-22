"""
Module 4: OCR and Scene Text Recognition
AI-Powered Assistive Navigation System for Visually Impaired People

Uses EasyOCR (CRAFT + CRNN) to detect and recognize signboards, room numbers,
and navigational text. Includes text cleaning, confidence filtering, and de-duplication.
"""

from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict
import re
import time
import cv2
import numpy as np
import easyocr
import torch

from config import (
    OCR_LANGUAGES,
    OCR_CONFIDENCE_THRESHOLD,
    MIN_OCR_TEXT_LENGTH,
    ALERT_COOLDOWNS
)


@dataclass
class OCRResult:
    """Structured representation of recognized scene text."""
    raw_text: str
    cleaned_text: str
    confidence: float
    bbox: List[List[int]]  # 4 corner points [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
    is_critical_keyword: bool


class OCRReader:
    """
    Encapsulates EasyOCR reader loading, image preprocessing, scene text recognition,
    regex text cleaning, keyword prioritization, and audio alert de-duplication.
    """

    CRITICAL_KEYWORDS = {
        "exit", "emergency", "danger", "caution", "warning", "stop",
        "stairs", "elevator", "lift", "restroom", "washroom", "toilet",
        "push", "pull", "entrance", "entry", "way out", "keep clear"
    }

    def __init__(self, languages: List[str] = OCR_LANGUAGES, gpu: Optional[bool] = None):
        if gpu is None:
            self.gpu = torch.cuda.is_available()
        else:
            self.gpu = gpu

        print(f"[OCR] Loading EasyOCR models (languages={languages}, GPU={self.gpu}) ...")
        self.reader = easyocr.Reader(languages, gpu=self.gpu)
        print("[OCR] EasyOCR models loaded successfully!")

        # De-duplication tracking
        self.last_spoken_text: str = ""
        self.last_spoken_time: float = 0.0

    @staticmethod
    def clean_text(text: str) -> str:
        """
        Sanitize raw OCR output:
        - Strip whitespace.
        - Collapse consecutive spaces.
        - Filter non-printable ASCII or random glyph artifacts.
        """
        if not text:
            return ""
        # Remove non-alphanumeric noise except standard punctuation
        cleaned = re.sub(r"[^A-Za-z0-9\s.,!?:/-]", "", text)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        return cleaned

    def is_critical(self, text: str) -> bool:
        """Check if recognized text contains navigational or safety keywords."""
        lower = text.lower()
        return any(keyword in lower for keyword in self.CRITICAL_KEYWORDS)

    def read_text(
        self,
        frame: np.ndarray,
        min_confidence: float = OCR_CONFIDENCE_THRESHOLD
    ) -> List[OCRResult]:
        """
        Runs scene text detection and recognition on an input BGR OpenCV frame.
        Applies grayscale contrast preprocessing and confidence thresholding.
        """
        if frame is None or frame.size == 0:
            return []

        # Convert to grayscale for cleaner text edge contrast
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # EasyOCR readtext returns: (bbox, text, prob)
        raw_results = self.reader.readtext(gray)
        results: List[OCRResult] = []

        for bbox, text, prob in raw_results:
            confidence = float(prob)
            if confidence < min_confidence:
                continue

            cleaned = self.clean_text(text)
            if len(cleaned) < MIN_OCR_TEXT_LENGTH:
                continue

            # Check if text is just standalone punctuation
            if not any(c.isalnum() for c in cleaned):
                continue

            critical = self.is_critical(cleaned)

            results.append(OCRResult(
                raw_text=text,
                cleaned_text=cleaned,
                confidence=confidence,
                bbox=bbox,
                is_critical_keyword=critical
            ))

        # Sort: safety-critical keywords first, then highest confidence
        results.sort(key=lambda x: (x.is_critical_keyword, x.confidence), reverse=True)
        return results

    def get_announcement(
        self,
        ocr_results: List[OCRResult],
        cooldown: Optional[float] = None
    ) -> Optional[str]:
        """
        Selects the top recognized text for voice announcement, enforcing de-duplication
        and cooldown timers to avoid audio chatter.
        """
        if not ocr_results:
            return None

        if cooldown is None:
            cooldown = ALERT_COOLDOWNS.get("LOW", 10.0)

        # Select the highest-priority text
        top_result = ocr_results[0]
        text_to_speak = top_result.cleaned_text
        now = time.time()

        # If identical text was recently spoken, respect cooldown
        if text_to_speak.lower() == self.last_spoken_text.lower():
            if now - self.last_spoken_time < cooldown:
                return None

        # If new text arrives, enforce at least a brief 2-second gap
        if now - self.last_spoken_time < 2.0:
            return None

        self.last_spoken_text = text_to_speak
        self.last_spoken_time = now

        if top_result.is_critical_keyword:
            return f"Signboard: {text_to_speak}"
        else:
            return f"Text detected: {text_to_speak}"

    @staticmethod
    def annotate_frame(frame: np.ndarray, ocr_results: List[OCRResult]) -> np.ndarray:
        """
        Draws OCR bounding polygons and text labels on the frame for visual HUD.
        """
        annotated = frame.copy()

        for res in ocr_results:
            pts = np.array(res.bbox, dtype=np.int32).reshape((-1, 1, 2))
            color = (0, 0, 255) if res.is_critical_keyword else (0, 255, 255)

            # Draw polygon around text
            cv2.polylines(annotated, [pts], isClosed=True, color=color, thickness=2)

            # Draw text label at top-left corner
            x1, y1 = int(res.bbox[0][0]), int(res.bbox[0][1])
            label = f"{res.cleaned_text} ({res.confidence:.2f})"
            cv2.putText(
                annotated,
                label,
                (x1, max(y1 - 6, 15)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                color,
                1,
                cv2.LINE_AA
            )

        return annotated
