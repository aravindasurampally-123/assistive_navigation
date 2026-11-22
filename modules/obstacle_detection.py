"""
Module 3: Intelligent Obstacle Detection & Sensor Fusion
AI-Powered Assistive Navigation System for Visually Impaired People

Combines 2D YOLOv8 object detections with Depth Anything V2 monocular disparity
to perform sensor fusion, compute hazard priority, and generate understandable warnings.
"""

from dataclasses import dataclass
from typing import List, Optional, Dict
import time
import numpy as np

from modules.object_detection import DetectedObject
from modules.depth_estimation import DepthEstimator
from config import (
    PRIORITY_CRITICAL,
    PRIORITY_HIGH,
    PRIORITY_MEDIUM,
    PRIORITY_LOW,
    ALERT_COOLDOWNS
)


@dataclass
class EvaluatedObstacle:
    """An obstacle evaluated with fused 2D bounding box and depth perception."""
    name: str
    position: str             # "left", "ahead", "right"
    fused_proximity: str      # "very close", "near", "medium", "far"
    depth_score: float        # Relative depth score [0, 1]
    area_ratio: float         # Bounding box area relative to frame
    priority: int             # 1 (LOW) to 4 (CRITICAL)
    hazard_level: str         # "CRITICAL", "HIGH", "MEDIUM", "LOW"
    warning_message: str


class ObstacleClassifier:
    """
    Fuses object bounding box scale with relative depth maps to prioritize navigational obstacles.
    """

    def __init__(self):
        # Dictionary to track last announcement timestamp for de-duplication
        self.last_alert_time: Dict[str, float] = {}
        self.last_spoken_message: Optional[str] = None
        self.last_spoken_priority: int = 0

    @staticmethod
    def fuse_proximity(area_ratio: float, depth_score: float) -> str:
        """
        Multimodal fusion:
        - Bounding box area ratio reflects geometric projection scale.
        - Depth score reflects monocular disparity from Depth Anything V2.
        Combines both cues to prevent false positives from tiny distant objects or flat background patterns.
        """
        if area_ratio > 0.35 or (area_ratio > 0.18 and depth_score >= 0.70):
            return "very close"
        elif area_ratio > 0.18 or depth_score >= 0.60:
            return "near"
        elif area_ratio > 0.08 or depth_score >= 0.40:
            return "medium"
        else:
            return "far"

    @classmethod
    def evaluate_obstacle(
        cls,
        obj: DetectedObject,
        depth_map: np.ndarray,
        depth_estimator: DepthEstimator
    ) -> EvaluatedObstacle:
        """
        Calculates region depth for an obstacle and determines its hazard priority.
        """
        region_depth = depth_estimator.get_region_depth(depth_map, obj.bbox)
        proximity = cls.fuse_proximity(obj.area_ratio, region_depth)

        # Priority determination based on proximity and lateral direction
        if proximity == "very close":
            if obj.position == "ahead":
                priority = PRIORITY_CRITICAL
                level = "CRITICAL"
                message = f"Warning! {obj.name} ahead. Stop!"
            else:
                priority = PRIORITY_HIGH
                level = "HIGH"
                message = f"Caution! {obj.name} very close on your {obj.position}."
        elif proximity == "near":
            if obj.position == "ahead":
                priority = PRIORITY_HIGH
                level = "HIGH"
                message = f"Caution! {obj.name} nearby ahead."
            else:
                priority = PRIORITY_MEDIUM
                level = "MEDIUM"
                message = f"{obj.name} nearby on your {obj.position}."
        elif proximity == "medium":
            priority = PRIORITY_MEDIUM
            level = "MEDIUM"
            if obj.position == "ahead":
                message = f"{obj.name} detected ahead."
            else:
                message = f"{obj.name} on your {obj.position}."
        else:
            priority = PRIORITY_LOW
            level = "LOW"
            message = f"{obj.name} in distance."

        return EvaluatedObstacle(
            name=obj.name,
            position=obj.position,
            fused_proximity=proximity,
            depth_score=region_depth,
            area_ratio=obj.area_ratio,
            priority=priority,
            hazard_level=level,
            warning_message=message
        )

    def prioritize_obstacles(
        self,
        detected_objects: List[DetectedObject],
        depth_map: np.ndarray,
        depth_estimator: DepthEstimator
    ) -> List[EvaluatedObstacle]:
        """
        Evaluates and ranks all detected navigational obstacles by hazard priority descending.
        """
        evaluated: List[EvaluatedObstacle] = []

        for obj in detected_objects:
            if not obj.is_navigational_hazard and obj.area_ratio < 0.05:
                continue
            item = self.evaluate_obstacle(obj, depth_map, depth_estimator)
            evaluated.append(item)

        # Sort primarily by priority tier descending, secondarily by depth score descending
        evaluated.sort(key=lambda x: (x.priority, x.depth_score), reverse=True)
        return evaluated

    def should_announce(self, obstacle: EvaluatedObstacle) -> bool:
        """
        Determines whether an alert message should be voiced, adhering to de-duplication
        and cooldown rules to prevent cognitive overload.
        """
        now = time.time()
        cooldown = ALERT_COOLDOWNS.get(obstacle.hazard_level, 5.0)

        # Immediate preemption if higher priority than previous
        if obstacle.priority > self.last_spoken_priority:
            self.last_spoken_message = obstacle.warning_message
            self.last_spoken_priority = obstacle.priority
            self.last_alert_time[obstacle.warning_message] = now
            return True

        last_time = self.last_alert_time.get(obstacle.warning_message, 0.0)
        if now - last_time >= cooldown:
            self.last_spoken_message = obstacle.warning_message
            self.last_spoken_priority = obstacle.priority
            self.last_alert_time[obstacle.warning_message] = now
            return True

        return False
