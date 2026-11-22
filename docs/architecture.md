# System Architecture
## AI-Powered Assistive Navigation System for Visually Impaired People

### 1. Abstract
The AI-Powered Assistive Navigation System is a multimodal edge-computing assistive platform designed for visually impaired and blind individuals. By combining real-time computer vision (YOLOv8), monocular relative depth estimation (Depth Anything V2), vision-language optical character recognition (EasyOCR), turn-by-turn walking navigation (OpenRouteService with OSRM fallback), and an intelligent four-tier priority decision engine, the system delivers timely, non-conflicting, and prioritized acoustic guidance.

### 2. Architectural Layers

```
+-------------------------------------------------------------------------+
|                         USER INTERFACE & TTS                           |
|       Streamlit Accessible Dashboard  |  Windows SAPI SpVoice Queue     |
+-------------------------------------------------------------------------+
                                    ^
                                    | (Prioritized Auditory Alerts)
+-------------------------------------------------------------------------+
|                     INTELLIGENCE & ARBITRATION                          |
|             AI Priority Decision Engine (CRITICAL -> LOW)              |
|        Dynamic Cooldowns | Alert Preemption | Audio De-duplication      |
+-------------------------------------------------------------------------+
          ^                         ^                         ^
          |                         |                         |
+-------------------+     +-------------------+     +-------------------+
| OBJECT DETECTION  |     | DEPTH ESTIMATION  |     | SCENE OCR & NAV   |
| YOLOv8 Nano       |     | Depth Anything V2 |     | EasyOCR + OSRM    |
| (BBox & Position) |     | (Monocular Dispar)|     | (Sign & Turn API) |
+-------------------+     +-------------------+     +-------------------+
          ^                         ^                         ^
          +-------------------------+-------------------------+
                                    |
+-------------------------------------------------------------------------+
|                            HARDWARE SENSORS                             |
|          Webcam Video Stream  |  Microphone STT  |  GPS / IP Geo        |
+-------------------------------------------------------------------------+
```

### 3. Layer Breakdown

#### Layer 1: Hardware & Sensor Ingestion
- **Webcam Sensor**: Captures live 640x480 RGB frames at 30 FPS.
- **Audio Input**: Microphone ingestion via SpeechRecognition library for speech command triggers.
- **Location Provider**: Lat/Long coordinate derivation via geocoder or manual override.

#### Layer 2: Multimodal Perception
- **Object Detection (YOLOv8n)**: Detects 80 COCO categories with specific emphasis on navigational obstacles (pedestrians, vehicles, chairs, doors, stairs). Categorizes lateral location into `left`, `ahead`, and `right`.
- **Depth Anything V2 (Small)**: Monocular relative depth estimation using a Vision Transformer (ViT-Small) backbone. Extracts central hazard region disparity.
- **EasyOCR (CRAFT + CRNN)**: Detects and recognizes text on indoor/outdoor signs and room numbers.

#### Layer 3: Intelligence & Decision Arbitration
- **Priority Tiering**:
  1. `CRITICAL` (Priority 4): Immediate hazards (e.g., obstacle within < 1m ahead).
  2. `HIGH` (Priority 3): Approaching obstacles (e.g., obstacle within 1-2m).
  3. `MEDIUM` (Priority 2): Walking directions and navigation maneuvers.
  4. `LOW` (Priority 1): Environmental text and ambient scene information.
- **Debounce & Cooldown Engine**: Enforces adaptive silence intervals to prevent cognitive fatigue.

#### Layer 4: Output & Interaction
- **Thread-Safe SAPI Voice Worker**: Dedicated COM-initialized thread consuming from an asynchronous thread-safe queue.
- **Streamlit Interface**: Visual verification HUD for caregivers and demonstrations.
