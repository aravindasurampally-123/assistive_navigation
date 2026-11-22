"""
Module 6: AI Decision and Priority Engine
AI-Powered Assistive Navigation System for Visually Impaired People

Arbitrates between multimodal inputs (obstacle hazards, turn-by-turn directions,
signboard OCR text, and system notices) across four strict priority tiers:
  - CRITICAL (4): Immediate danger (collision risk ahead)
  - HIGH (3)    : Nearby obstacles requiring caution
  - MEDIUM (2)  : Navigation walking instructions
  - LOW (1)     : Environmental scene text & ambient information
"""

from dataclasses import dataclass
from typing import Optional, List, Dict
import time

from config import (
    PRIORITY_CRITICAL,
    PRIORITY_HIGH,
    PRIORITY_MEDIUM,
    PRIORITY_LOW,
    PRIORITY_NONE,
    ALERT_COOLDOWNS
)
from modules.obstacle_detection import EvaluatedObstacle


@dataclass
class DecisionResult:
    """The unified decision outcome produced by the AI Decision Engine."""
    priority: int
    level: str             # "CRITICAL", "HIGH", "MEDIUM", "LOW", "NONE"
    message: Optional[str]
    source: str            # "OBSTACLE", "NAVIGATION", "OCR", "NONE"
    clear_audio_queue: bool
    should_speak: bool


class AIDecisionEngine:
    """
    State-machine priority arbitrator enforcing safety-critical preemption,
    alert de-duplication, and cognitive load reduction for the visually impaired user.
    """

    def __init__(self):
        self.last_spoken_message: Optional[str] = None
        self.last_spoken_time: float = 0.0
        self.last_priority: int = PRIORITY_NONE

    def arbitrate(
        self,
        obstacles: Optional[List[EvaluatedObstacle]] = None,
        navigation_instruction: Optional[str] = None,
        ocr_announcement: Optional[str] = None
    ) -> DecisionResult:
        """
        Evaluate candidate events across all sensory modalities and select
        the single most critical alert that should be presented to the user.
        """
        candidates = []

        # 1. Evaluate Obstacle Candidates (Levels: CRITICAL, HIGH, MEDIUM, LOW)
        if obstacles and len(obstacles) > 0:
            top_obstacle = obstacles[0]
            clear_queue = (top_obstacle.priority == PRIORITY_CRITICAL)
            candidates.append({
                "priority": top_obstacle.priority,
                "level": top_obstacle.hazard_level,
                "message": top_obstacle.warning_message,
                "source": "OBSTACLE",
                "clear_queue": clear_queue
            })

        # 2. Evaluate Navigation Instruction (Level: MEDIUM)
        if navigation_instruction:
            candidates.append({
                "priority": PRIORITY_MEDIUM,
                "level": "MEDIUM",
                "message": navigation_instruction,
                "source": "NAVIGATION",
                "clear_queue": False
            })

        # 3. Evaluate Scene OCR Announcement (Level: LOW)
        if ocr_announcement:
            candidates.append({
                "priority": PRIORITY_LOW,
                "level": "LOW",
                "message": ocr_announcement,
                "source": "OCR",
                "clear_queue": False
            })

        # If no sensory candidate is active, return idle state
        if not candidates:
            return DecisionResult(
                priority=PRIORITY_NONE,
                level="NONE",
                message=None,
                source="NONE",
                clear_audio_queue=False,
                should_speak=False
            )

        # Sort candidates strictly by priority descending
        candidates.sort(key=lambda x: x["priority"], reverse=True)
        top_choice = candidates[0]

        priority = top_choice["priority"]
        level = top_choice["level"]
        message = top_choice["message"]
        source = top_choice["source"]
        clear_queue = top_choice["clear_queue"]

        now = time.time()
        cooldown = ALERT_COOLDOWNS.get(level, 5.0)

        should_speak = False

        # --- Arbitration Rule 1: Higher Priority Preemption ---
        if priority > self.last_priority:
            should_speak = True
            self.last_spoken_message = message
            self.last_spoken_time = now
            self.last_priority = priority

        # --- Arbitration Rule 2: Lower Priority Suppression ---
        # Suppress lower priority message if a higher priority alert occurred recently
        elif priority < self.last_priority:
            higher_cooldown = ALERT_COOLDOWNS.get(
                self._priority_to_level(self.last_priority), 5.0
            )
            if now - self.last_spoken_time < higher_cooldown:
                should_speak = False
            else:
                # Higher priority hazard has cleared; allow lower priority
                should_speak = True
                self.last_spoken_message = message
                self.last_spoken_time = now
                self.last_priority = priority

        # --- Arbitration Rule 3: Equal Priority Cooldown & De-duplication ---
        else:
            if message == self.last_spoken_message:
                # Same message: enforce cooldown window
                if now - self.last_spoken_time >= cooldown:
                    should_speak = True
                    self.last_spoken_time = now
            else:
                # New message of same priority: require brief 1.5s separation
                if now - self.last_spoken_time >= 1.5:
                    should_speak = True
                    self.last_spoken_message = message
                    self.last_spoken_time = now

        return DecisionResult(
            priority=priority,
            level=level,
            message=message,
            source=source,
            clear_audio_queue=clear_queue,
            should_speak=should_speak
        )

    @staticmethod
    def _priority_to_level(priority: int) -> str:
        mapping = {
            PRIORITY_CRITICAL: "CRITICAL",
            PRIORITY_HIGH: "HIGH",
            PRIORITY_MEDIUM: "MEDIUM",
            PRIORITY_LOW: "LOW"
        }
        return mapping.get(priority, "NONE")

    def reset(self):
        """Reset internal arbitration state."""
        self.last_spoken_message = None
        self.last_spoken_time = 0.0
        self.last_priority = PRIORITY_NONE
