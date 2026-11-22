# System Workflow
## AI-Powered Assistive Navigation System for Visually Impaired People

### 1. High-Level Operational Pipeline

```
  +------------------+
  | Application Boot |
  +--------+---------+
           |
           v
  +------------------+
  | Load Weights &   |
  | Initialize Audio |
  +--------+---------+
           |
           v
  +------------------+     Frame Grab      +-------------------+
  | Camera Capture   +-------------------->+ YOLOv8 Inference  |
  +--------+---------+                     +---------+---------+
           |                                         |
           | Depth Map                               | BBoxes, Classes, Centroids
           v                                         v
  +------------------+                     +-------------------+
  | Depth Anything   +-------------------->+ Spatial & Lateral |
  | V2 (Relative)    |                     | Position Analyser |
  +------------------+                     +---------+---------+
           |                                         |
           +--------------------+--------------------+
                                |
                                v
                     +---------------------+
                     | Obstacle Classifier |
                     | (Distance & Hazard) |
                     +----------+----------+
                                |
  [Periodic Events]             |
  - OCR Scan (Every 3s) --------+
  - Turn Navigation Step -------+
                                |
                                v
                     +---------------------+
                     | AI Priority Engine  |
                     | (Decision Matrix)   |
                     +----------+----------+
                                |
                        Highest Priority
                        & De-duplicated
                                |
                                v
                     +---------------------+
                     | Non-blocking Voice  |
                     | Assistant (SAPI/TTS)|
                     +---------------------+
```

### 2. Decision Logic State Flow
1. **Per-frame Detection**: YOLOv8 scans frame for obstacles within user path.
2. **Monocular Relative Disparity**: Center third of frame sampled to compute obstacle proximity score.
3. **Periodic Async Events**:
   - Every 3.0s: EasyOCR scans scene text (signs/rooms/exits).
   - Every 8.0s: Turn navigation checks next waypoint and updates walking instruction.
4. **Priority Matrix Evaluation**:
   - `CRITICAL` (Level 4): Imminent collisions (< 1m ahead) override all speech immediately.
   - `HIGH` (Level 3): Close obstacles (1-2m) voiced with 4s cooldown.
   - `MEDIUM` (Level 2): Turn-by-turn directions voiced with 7s cooldown.
   - `LOW` (Level 1): Scene text voiced with 10s cooldown.
5. **Acoustic Safety**: Audio alerts never speak over each other; the dedicated COM queue handles continuous speech without UI lag.
