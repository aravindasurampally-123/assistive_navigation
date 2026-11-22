"""
Module 5A: Thread-Safe Voice Assistant (Text-to-Speech)
AI-Powered Assistive Navigation System for Visually Impaired People

Uses Windows SAPI (SpVoice) on a dedicated COM-initialized worker thread with an
asynchronous thread-safe queue. Prevents UI frame drops and enables priority preemption.
"""

import queue
import threading
import time
from typing import Optional
import sys

from config import VOICE_RATE, VOICE_VOLUME

# Platform-specific COM imports
IS_WINDOWS = sys.platform == "win32"
if IS_WINDOWS:
    try:
        import pywin32_bootstrap
    except Exception:
        pass
    import pythoncom
    import win32com.client as win32


class VoiceAssistant:
    """
    Non-blocking speech synthesis engine.
    Ensures that speaking does not freeze the main camera processing loop.
    """

    def __init__(self, rate: int = VOICE_RATE, volume: int = VOICE_VOLUME):
        self.rate = rate
        self.volume = volume
        self.voice_queue: queue.Queue = queue.Queue()
        self.is_ready = threading.Event()
        self.is_running = True
        self.last_spoken_message: str = ""
        self.engine_error: Optional[Exception] = None

        # Start dedicated speech worker thread
        self.worker_thread = threading.Thread(target=self._speech_worker, daemon=True, name="TTSWorker")
        self.worker_thread.start()

        # Wait up to 5 seconds for COM initialization
        if not self.is_ready.wait(timeout=5.0):
            print("[VOICE] WARNING: Voice engine initialization timed out.")

    def _speech_worker(self):
        """Worker loop running in a dedicated thread with its own COM apartment."""
        if IS_WINDOWS:
            pythoncom.CoInitialize()

        voice_engine = None
        try:
            if IS_WINDOWS:
                voice_engine = win32.Dispatch("SAPI.SpVoice")
                # SAPI rate: -10 to +10 (0 is normal)
                voice_engine.Rate = int(self.rate)
                voice_engine.Volume = int(self.volume)
                print("[VOICE] Windows SAPI (SpVoice) initialized successfully.")
            else:
                import pyttsx3
                voice_engine = pyttsx3.init()
                print("[VOICE] pyttsx3 fallback initialized.")

            self.is_ready.set()

            while self.is_running:
                item = self.voice_queue.get()
                if item is None:
                    self.voice_queue.task_done()
                    break

                message, is_critical = item
                try:
                    self.last_spoken_message = message
                    if IS_WINDOWS and voice_engine is not None:
                        # SAPI Speak flags: 0 = Synchronous on this worker thread
                        voice_engine.Speak(str(message), 0)
                    elif voice_engine is not None:
                        voice_engine.say(str(message))
                        voice_engine.runAndWait()
                    else:
                        print(f"[VOICE SIMULATED]: {message}")
                except Exception as exc:
                    print(f"[VOICE ERROR]: Speech execution failed: {exc}")
                finally:
                    self.voice_queue.task_done()

        except Exception as exc:
            self.engine_error = exc
            self.is_ready.set()
            print(f"[VOICE CRITICAL]: Worker initialization failed: {exc}")
        finally:
            if IS_WINDOWS:
                pythoncom.CoUninitialize()

    def speak(self, message: str, clear_pending: bool = False):
        """
        Enqueues a message for speech synthesis.
        If clear_pending=True (for CRITICAL hazards), purges queued non-critical speech
        so the safety alert speaks with minimum latency.
        """
        if not message or not self.is_running:
            return

        if clear_pending:
            # Drain lower priority messages currently waiting in queue
            try:
                while not self.voice_queue.empty():
                    self.voice_queue.get_nowait()
                    self.voice_queue.task_done()
            except (queue.Empty, ValueError):
                pass

        self.voice_queue.put((message, clear_pending))

    def wait_until_done(self, timeout: float = 10.0):
        """Blocks until all queued speech items have finished speaking."""
        self.voice_queue.join()

    def stop(self):
        """Stops the worker thread and releases resources."""
        self.is_running = False
        self.voice_queue.put(None)
        if self.worker_thread.is_alive():
            self.worker_thread.join(timeout=3.0)
        print("[VOICE] Voice engine stopped cleanly.")
