"""
Module 2: Distance and Depth Estimation
AI-Powered Assistive Navigation System for Visually Impaired People

Integrates Depth Anything V2 (Small) to generate monocular relative depth maps,
computes region-specific disparity scores, and categorizes relative obstacle proximity
into discrete bands (near, medium, far).
Academic Note: Relative depth represents inverse distance/disparity, not physical metric meters.
"""

from typing import Optional, Tuple
import cv2
import numpy as np
import torch
from PIL import Image
from transformers import AutoImageProcessor, AutoModelForDepthEstimation

from config import DEPTH_MODEL_NAME


class DepthEstimator:
    """
    Monocular relative depth estimation using Depth Anything V2.
    Predicts relative scene disparity without requiring dual cameras or LiDAR hardware.
    """

    def __init__(self, model_name: str = DEPTH_MODEL_NAME, device: Optional[str] = None):
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device

        print(f"[DEPTH] Loading Depth Anything V2 ({model_name}) on device: {self.device} ...")
        self.processor = AutoImageProcessor.from_pretrained(model_name)
        self.model = AutoModelForDepthEstimation.from_pretrained(model_name).to(self.device)
        self.model.eval()
        print("[DEPTH] Depth Anything V2 loaded successfully!")

    def estimate_depth_map(self, frame: np.ndarray) -> np.ndarray:
        """
        Infers a normalized 2D relative depth map in range [0.0, 1.0].
        Higher values represent closer proximity (higher disparity).
        """
        if frame is None or frame.size == 0:
            return np.zeros((100, 100), dtype=np.float32)

        orig_h, orig_w = frame.shape[:2]
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(rgb)

        inputs = self.processor(images=pil_img, return_tensors="pt").to(self.device)

        with torch.no_grad():
            outputs = self.model(**inputs)
            predicted_depth = outputs.predicted_depth

        # Extract depth tensor and resize to original frame dimensions
        depth = predicted_depth.squeeze().detach().cpu().numpy()
        depth_resized = cv2.resize(depth, (orig_w, orig_h), interpolation=cv2.INTER_LINEAR)

        # Min-Max Normalization to [0.0, 1.0]
        d_min = float(np.min(depth_resized))
        d_max = float(np.max(depth_resized))

        if d_max - d_min > 1e-6:
            normalized_depth = (depth_resized - d_min) / (d_max - d_min)
        else:
            normalized_depth = np.zeros_like(depth_resized, dtype=np.float32)

        return normalized_depth

    def get_region_depth(
        self,
        depth_map: np.ndarray,
        bbox: Optional[Tuple[int, int, int, int]] = None
    ) -> float:
        """
        Compute mean relative depth score for a given bounding box (x1, y1, x2, y2).
        If bbox is None, evaluates the central navigation corridor (middle 1/3 of frame).
        """
        if depth_map is None or depth_map.size == 0:
            return 0.0

        h, w = depth_map.shape[:2]

        if bbox is not None:
            x1, y1, x2, y2 = bbox
            x1 = max(0, min(x1, w - 1))
            y1 = max(0, min(y1, h - 1))
            x2 = max(x1 + 1, min(x2, w))
            y2 = max(y1 + 1, min(y2, h))
            region = depth_map[y1:y2, x1:x2]
        else:
            # Central walking corridor
            y_start, y_end = h // 3, 2 * h // 3
            x_start, x_end = w // 3, 2 * w // 3
            region = depth_map[y_start:y_end, x_start:x_end]

        if region.size == 0:
            return 0.0

        return float(np.mean(region))

    @staticmethod
    def classify_relative_depth(depth_score: float) -> str:
        """
        Classifies relative depth score into human-understandable qualitative proximity bands:
        - score >= 0.70 : 'near'
        - 0.45 <= score < 0.70 : 'medium'
        - score < 0.45 : 'far'
        """
        if depth_score >= 0.70:
            return "near"
        elif depth_score >= 0.45:
            return "medium"
        else:
            return "far"

    @staticmethod
    def generate_heatmap(depth_map: np.ndarray) -> np.ndarray:
        """
        Converts normalized float depth map [0, 1] to an 8-bit INFERNO colormap for HUD visualization.
        """
        if depth_map is None or depth_map.size == 0:
            return np.zeros((100, 100, 3), dtype=np.uint8)

        depth_uint8 = np.clip(depth_map * 255.0, 0, 255).astype(np.uint8)
        color_heatmap = cv2.applyColorMap(depth_uint8, cv2.COLORMAP_INFERNO)
        return color_heatmap
