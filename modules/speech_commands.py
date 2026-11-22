"""
Module 5B: Voice Command Recognition
AI-Powered Assistive Navigation System for Visually Impaired People

Listens for spoken voice commands from the user and maps them to application actions:
- Start system
- Stop system
- Start navigation
- Stop navigation
- Read text
- Repeat instruction
- Emergency help
"""

import re
from typing import Optional, Dict, List
import threading
import time

try:
    import speech_recognition as sr
    HAS_SR = True
except ImportError:
    HAS_SR = False

from config import SPEECH_RECOGNITION_TIMEOUT, SPEECH_PHRASE_TIME_LIMIT


# Canonical Command Constants
CMD_START_SYSTEM = "START_SYSTEM"
CMD_STOP_SYSTEM = "STOP_SYSTEM"
CMD_START_NAV = "START_NAVIGATION"
CMD_STOP_NAV = "STOP_NAVIGATION"
CMD_READ_TEXT = "READ_TEXT"
CMD_REPEAT = "REPEAT_INSTRUCTION"
CMD_EMERGENCY = "EMERGENCY_HELP"


class CommandParser:
    """
    Regex and keyword-based NLP parser to map natural speech transcripts
    to discrete application commands.
    """

    PATTERNS: Dict[str, List[str]] = {
        CMD_EMERGENCY: [
            r"\bemergency\b", r"\bsos\b", r"\bhelp me\b", r"\bcall for help\b",
            r"\bemergency help\b", r"\bneed help\b"
        ],
        CMD_START_NAV: [
            r"\bstart navigation\b", r"\bbegin navigation\b", r"\bnavigate\b",
            r"\bstart route\b", r"\bstart walking\b", r"\bwalking route\b"
        ],
        CMD_STOP_NAV: [
            r"\bstop navigation\b", r"\bcancel navigation\b", r"\bend navigation\b",
            r"\bstop route\b"
        ],
        CMD_START_SYSTEM: [
            r"\bstart system\b", r"\bturn on\b", r"\bactivate\b", r"\bbegin system\b", r"^begin$"
        ],
        CMD_STOP_SYSTEM: [
            r"\bstop system\b", r"\bturn off\b", r"\bshutdown\b", r"\bexit system\b", r"\bquit\b"
        ],
        CMD_READ_TEXT: [
            r"\bread text\b", r"\bread signboard\b", r"\bread sign\b",
            r"\bwhat does .* say\b", r"\bread\b", r"\bscan text\b", r"\bsignboard\b"
        ],
        CMD_REPEAT: [
            r"\brepeat instruction\b", r"\brepeat\b", r"\bsay again\b",
            r"\bwhat was that\b", r"\brepeat direction\b"
        ]
    }

    @classmethod
    def parse(cls, transcript: str) -> Optional[str]:
        """
        Matches recognized text against known command intent regex patterns.
        Order of evaluation: Emergency -> Navigation -> System -> OCR -> Repeat.
        """
        if not transcript:
            return None

        clean = transcript.strip().lower()

        # Check emergency triggers first
        for pattern in cls.PATTERNS[CMD_EMERGENCY]:
            if re.search(pattern, clean):
                return CMD_EMERGENCY

        # Check remaining command patterns in priority order
        order = [
            CMD_START_NAV,
            CMD_STOP_NAV,
            CMD_START_SYSTEM,
            CMD_STOP_SYSTEM,
            CMD_READ_TEXT,
            CMD_REPEAT
        ]

        for cmd_type in order:
            patterns = cls.PATTERNS[cmd_type]
            for pattern in patterns:
                if re.search(pattern, clean):
                    return cmd_type

        return None


class SpeechCommandListener:
    """
    Manages microphone input and SpeechRecognition processing.
    """

    def __init__(self):
        self.recognizer = sr.Recognizer() if HAS_SR else None
        self.microphone = None
        self.is_mic_available = False

        if HAS_SR:
            try:
                self.microphone = sr.Microphone()
                self.is_mic_available = True
                print("[SPEECH-REC] Microphone found and initialized.")
            except Exception as e:
                print(f"[SPEECH-REC] Hardware microphone unavailable: {e}")
                self.is_mic_available = False
        else:
            print("[SPEECH-REC] SpeechRecognition library not found. Command simulation enabled.")

    def listen_once(
        self,
        timeout: float = SPEECH_RECOGNITION_TIMEOUT,
        phrase_time_limit: float = SPEECH_PHRASE_TIME_LIMIT
    ) -> Optional[str]:
        """
        Listens for a single speech utterance and returns the canonical command ID.
        Returns None if silence or unrecognized speech occurs.
        """
        if not self.is_mic_available or not self.recognizer or not self.microphone:
            return None

        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                print("[SPEECH-REC] Listening for voice command...")
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)

            transcript = self.recognizer.recognize_google(audio)
            print(f"[SPEECH-REC] Heard: '{transcript}'")
            return CommandParser.parse(transcript)

        except sr.WaitTimeoutError:
            return None
        except sr.UnknownValueError:
            return None
        except Exception as exc:
            print(f"[SPEECH-REC] Recognition error: {exc}")
            return None

    @staticmethod
    def simulate_speech(transcript: str) -> Optional[str]:
        """
        Simulate speech input without needing a physical microphone (useful for tests and automation).
        """
        return CommandParser.parse(transcript)
