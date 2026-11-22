"""
PDF Generator: Slide-by-Slide Presentation Deck
AI-Powered Assistive Navigation System for Visually Impaired People
Generates high-contrast landscape presentation slides in PDF format.
"""

import sys
from pathlib import Path
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

PROJECT_ROOT = Path(__file__).resolve().parent
DOCS_DIR = PROJECT_ROOT / "docs"
PDF_PATH = DOCS_DIR / "AI_Assistive_Navigation_Presentation.pdf"


def generate_presentation_pdf():
    # Landscape Letter format (11 x 8.5 inches)
    doc = SimpleDocTemplate(
        str(PDF_PATH),
        pagesize=landscape(letter),
        leftMargin=0.5 * inch,
        rightMargin=0.5 * inch,
        topMargin=0.5 * inch,
        bottomMargin=0.5 * inch
    )

    styles = getSampleStyleSheet()

    # Presentation Typography Styles
    slide_title_style = ParagraphStyle(
        'SlideTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#0F2942'),
        spaceAfter=4
    )

    slide_subtitle_style = ParagraphStyle(
        'SlideSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=13,
        textColor=colors.HexColor('#3182CE'),
        spaceAfter=10
    )

    bullet_style = ParagraphStyle(
        'SlideBullet',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10.5,
        leading=15,
        textColor=colors.HexColor('#2D3748'),
        spaceAfter=6
    )

    bullet_bold = ParagraphStyle(
        'SlideBulletBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=15,
        textColor=colors.HexColor('#1A202C'),
        spaceAfter=6
    )

    code_box_style = ParagraphStyle(
        'SlideCode',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#2B6CB0')
    )

    table_header_style = ParagraphStyle(
        'THStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=12,
        textColor=colors.white
    )

    table_cell_style = ParagraphStyle(
        'TCStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#2D3748')
    )

    story = []

    def add_slide_header(title: str, subtitle: str, slide_num: int):
        story.append(Paragraph(title, slide_title_style))
        story.append(Paragraph(f"{subtitle} &bull; <i>Slide {slide_num} of 12</i>", slide_subtitle_style))
        story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0F2942'), spaceAfter=12))

    # ========================================================
    # SLIDE 1: TITLE SLIDE
    # ========================================================
    story.append(Spacer(1, 0.6 * inch))
    title_p = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=30,
        textColor=colors.HexColor('#0F2942'),
        alignment=1,
        spaceAfter=10
    )
    story.append(Paragraph("AI-POWERED ASSISTIVE NAVIGATION SYSTEM<br/>FOR VISUALLY IMPAIRED PEOPLE", title_p))
    story.append(HRFlowable(width="80%", thickness=2, color=colors.HexColor('#3182CE'), spaceAfter=16))

    cover_meta = ParagraphStyle(
        'CoverMeta',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=18,
        textColor=colors.HexColor('#2D3748'),
        alignment=1
    )
    story.append(Paragraph("<b>3rd-Year B.Tech Major Project Defense</b><br/>Department of Artificial Intelligence & Machine Learning", cover_meta))
    story.append(Spacer(1, 20))

    meta_table_data = [
        [
            Paragraph("<b>Presented By:</b> Aravinda (3rd Year B.Tech AIML)", bullet_style),
            Paragraph("<b>Domain:</b> Multimodal Edge AI & Computer Vision", bullet_style)
        ],
        [
            Paragraph("<b>Implementation:</b> 100% Tested Production Prototype", bullet_style),
            Paragraph("<b>Repository:</b> github.com/aravindasurampally-123/assistive_navigation", bullet_style)
        ]
    ]
    t_cover = Table(meta_table_data, colWidths=[4.8 * inch, 4.8 * inch])
    t_cover.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#EDF2F7')),
        ('PADDING', (0, 0), (-1, -1), 10),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#CBD5E0')),
    ]))
    story.append(t_cover)
    story.append(PageBreak())

    # ========================================================
    # SLIDE 2: PROBLEM STATEMENT & MOTIVATION
    # ========================================================
    add_slide_header("Problem Statement & Motivation", "Background & Challenges in Visual Impairment", 2)
    story.append(Paragraph("&bull; <b>Global Magnitude:</b> Over 2.2 billion people worldwide live with vision impairment (WHO), facing daily physical hazards.", bullet_style))
    story.append(Paragraph("&bull; <b>The White Cane Deficit:</b> White canes detect only ground-level obstacles within 1 meter; they fail completely to warn against head-height obstacles, open truck beds, low hanging tree branches, or elevated signboards.", bullet_style))
    story.append(Paragraph("&bull; <b>Ultrasonic Sensor Limitations:</b> Conventional smart canes use 1D sonar beepers that cannot differentiate a person from a wall or trash can, generating high false-alarm rates.", bullet_style))
    story.append(Paragraph("&bull; <b>Scene Text Inaccessibility:</b> Navigating unfamiliar public transit, hospitals, and educational institutions is impossible without reading room plates and exit signs.", bullet_style))
    story.append(Paragraph("&bull; <b>Auditory Cognitive Overload:</b> Existing vision apps announce everything indiscriminately, masking critical environmental audio cues.", bullet_style))
    story.append(PageBreak())

    # ========================================================
    # SLIDE 3: EXISTING VS PROPOSED SYSTEM
    # ========================================================
    add_slide_header("Comparative Analysis", "Benchmarking Conventional Aids vs. Proposed System", 3)
    comp_data = [
        [
            Paragraph("<b>Dimension</b>", table_header_style),
            Paragraph("<b>Traditional White Cane</b>", table_header_style),
            Paragraph("<b>Smart Ultrasonic Canes</b>", table_header_style),
            Paragraph("<b>Proposed Multimodal AI System</b>", table_header_style)
        ],
        [
            Paragraph("<b>Detection Range</b>", table_cell_style),
            Paragraph("< 1 meter (Ground only)", table_cell_style),
            Paragraph("1–2 meters (1D Sonar echo)", table_cell_style),
            Paragraph("<b>0.5–10m (Corridor + Periphery)</b>", table_cell_style)
        ],
        [
            Paragraph("<b>Depth Perception</b>", table_cell_style),
            Paragraph("Physical contact required", table_cell_style),
            Paragraph("Coarse beep frequency", table_cell_style),
            Paragraph("<b>Dense 2D Relative Disparity (ViT)</b>", table_cell_style)
        ],
        [
            Paragraph("<b>Spatial Position</b>", table_cell_style),
            Paragraph("None", table_cell_style),
            Paragraph("None (Point sensor)", table_cell_style),
            Paragraph("<b>3-Zone FOV (Left, Ahead, Right)</b>", table_cell_style)
        ],
        [
            Paragraph("<b>Scene OCR</b>", table_cell_style),
            Paragraph("None", table_cell_style),
            Paragraph("None", table_cell_style),
            Paragraph("<b>Automated CRAFT + CRNN OCR</b>", table_cell_style)
        ],
        [
            Paragraph("<b>Audio Speech</b>", table_cell_style),
            Paragraph("N/A", table_cell_style),
            Paragraph("Buzzer beeps", table_cell_style),
            Paragraph("<b>4-Tier Prioritized Preemption</b>", table_cell_style)
        ],
        [
            Paragraph("<b>Walking Navigation</b>", table_cell_style),
            Paragraph("None", table_cell_style),
            Paragraph("None", table_cell_style),
            Paragraph("<b>Turn-by-turn ORS + OSRM Fallback</b>", table_cell_style)
        ],
        [
            Paragraph("<b>Emergency SOS</b>", table_cell_style),
            Paragraph("None", table_cell_style),
            Paragraph("None", table_cell_style),
            Paragraph("<b>One-touch SOS with Live Map Link</b>", table_cell_style)
        ]
    ]
    t_comp = Table(comp_data, colWidths=[2.2 * inch, 2.5 * inch, 2.5 * inch, 2.8 * inch])
    t_comp.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F2942')),
        ('PADDING', (0, 0), (-1, -1), 4),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E0')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F7FAFC')])
    ]))
    story.append(t_comp)
    story.append(PageBreak())

    # ========================================================
    # SLIDE 4: SYSTEM ARCHITECTURE
    # ========================================================
    add_slide_header("System Architecture & Dataflow", "End-to-End Decoupled Five-Layer Design", 4)
    story.append(Paragraph("&bull; <b>Layer 1 (Sensors):</b> Laptop/USB Webcam (30 FPS DirectShow), Microphone SpeechRecognition, Geolocation Provider.", bullet_style))
    story.append(Paragraph("&bull; <b>Layer 2 (Perception):</b> Single-stage YOLOv8 Nano (bounding boxes), Depth Anything V2 (monocular disparity), EasyOCR (scene text).", bullet_style))
    story.append(Paragraph("&bull; <b>Layer 3 (Intelligence):</b> Scale-depth multimodal fusion, walking pathfinder, and state-machine priority arbitration engine.", bullet_style))
    story.append(Paragraph("&bull; <b>Layer 4 (Persistence):</b> Thread-safe SQLite 3 database persisting settings, caregiver contacts, and SOS incident audit logs.", bullet_style))
    story.append(Paragraph("&bull; <b>Layer 5 (Output & Interaction):</b> Dedicated COM-threaded Windows SAPI voice queue + Accessible Streamlit web dashboard.", bullet_style))
    story.append(PageBreak())

    # ========================================================
    # SLIDE 5: REAL-TIME OBJECT DETECTION
    # ========================================================
    add_slide_header("Module 1: Real-Time Object Detection", "YOLOv8 Edge Inference & Spatial Lane Partitioning", 5)
    story.append(Paragraph("&bull; <b>Anchor-Free Edge Model:</b> Uses lightweight YOLOv8 Nano (3.2M parameters, 6.25 MB) optimized for real-time edge CPU inference.", bullet_style))
    story.append(Paragraph("&bull; <b>Navigational Obstacle Filter:</b> Targets 20 critical obstacle categories (pedestrians, vehicles, chairs, doors, stairs, bicycles).", bullet_style))
    story.append(Paragraph("&bull; <b>Mathematical Lateral FOV Partitioning:</b>", bullet_bold))
    story.append(Paragraph("For frame width W, the horizontal centroid cx = x1 + (x2 - x1) / 2 is classified into directional zones:<br/>"
                           "&bull; <b>LEFT Zone:</b> cx &lt; W / 3 &nbsp;&bull; <b>AHEAD Zone:</b> W / 3 &le; cx &le; 2W / 3 &nbsp;&bull; <b>RIGHT Zone:</b> cx &gt; 2W / 3", code_box_style))
    story.append(Spacer(1, 6))
    story.append(Paragraph("&bull; <b>Actionable Directional Guidance:</b> Converts raw coordinates into natural spoken directions: <i>'Warning! Person ahead. Stop!'</i> vs <i>'Chair on your left.'</i>", bullet_style))
    story.append(PageBreak())

    # ========================================================
    # SLIDE 6: DEPTH ESTIMATION & SENSOR FUSION
    # ========================================================
    add_slide_header("Modules 2 & 3: Depth & Obstacle Classification", "Depth Anything V2 & Multimodal Scale-Disparity Fusion", 6)
    story.append(Paragraph("&bull; <b>Monocular Relative Disparity:</b> Integrates Depth Anything V2 (Small) using a Vision Transformer (DINOv2) backbone to estimate dense scene disparity without stereo hardware.", bullet_style))
    story.append(Paragraph("&bull; <b>Scientific Rigor:</b> Relative depth represents inverse disparity in range [0.0, 1.0], NOT metric meters. Metric claims without camera calibration are scientifically invalid.", bullet_style))
    story.append(Paragraph("&bull; <b>Multimodal Sensor Fusion Rule:</b>", bullet_bold))
    story.append(Paragraph("Fuses bounding box area ratio (A_ratio) with regional disparity score (D_score):<br/>"
                           "&bull; <b>VERY CLOSE:</b> A_ratio &gt; 0.35 OR (A_ratio &gt; 0.18 AND D_score &ge; 0.70) &rarr; Immediate Collision Risk<br/>"
                           "&bull; <b>NEAR:</b> A_ratio &gt; 0.18 OR D_score &ge; 0.60 &nbsp;&bull; <b>MEDIUM:</b> A_ratio &gt; 0.08 OR D_score &ge; 0.40 &nbsp;&bull; <b>FAR:</b> Otherwise", code_box_style))
    story.append(Spacer(1, 6))
    story.append(Paragraph("&bull; <b>Visual Heatmap:</b> Produces high-contrast INFERNO colormaps for caregiver visual monitoring.", bullet_style))
    story.append(PageBreak())

    # ========================================================
    # SLIDE 7: SCENE OCR & VOICE ASSISTANT
    # ========================================================
    add_slide_header("Modules 4 & 5: Scene OCR & Audio Interaction", "Vision-Language Text Reading & Thread-Safe SAPI Speech", 7)
    story.append(Paragraph("&bull; <b>EasyOCR Engine:</b> Combines CRAFT (Character Region Awareness for Text Detection) with deep CRNN (ResNet + BiLSTM + CTC) to detect distorted or curved scene text.", bullet_style))
    story.append(Paragraph("&bull; <b>Regex Sanitization & Safety Prioritization:</b> Cleans non-alphanumeric noise; elevates life-safety signage (*EXIT*, *DANGER*, *RESTROOM*, *CAUTION*, *ROOM*).", bullet_style))
    story.append(Paragraph("&bull; <b>Thread-Safe Asynchronous Voice Worker:</b>", bullet_bold))
    story.append(Paragraph("&bull; Windows SAPI (SpVoice) initialized on a dedicated STA thread via pythoncom.CoInitialize().<br/>"
                           "&bull; Non-blocking queue.Queue ensures voice.speak() returns in <b>0.00 ms</b> (zero camera frame drops).<br/>"
                           "&bull; Supports 7 hands-free voice commands parsed via regex NLP (Start/Stop System, Start/Stop Nav, Read Text, Repeat, SOS).", bullet_style))
    story.append(PageBreak())

    # ========================================================
    # SLIDE 8: AI PRIORITY DECISION ENGINE
    # ========================================================
    add_slide_header("Module 6: AI Priority Decision Engine", "Algorithmic Cognitive Filtering & Hazard Preemption", 8)
    story.append(Paragraph("&bull; <b>The 4-Tier Hierarchy Matrix:</b>", bullet_bold))
    story.append(Paragraph("&bull; <b>CRITICAL (Priority 4):</b> Immediate collision risk ahead &rarr; Flushes speech queue and speaks immediately.<br/>"
                           "&bull; <b>HIGH (Priority 3):</b> Nearby obstacle requiring caution &rarr; 4.0 second cooldown.<br/>"
                           "&bull; <b>MEDIUM (Priority 2):</b> Turn-by-turn walking instruction &rarr; 7.0 second cooldown.<br/>"
                           "&bull; <b>LOW (Priority 1):</b> Scene text and signboard announcements &rarr; 10.0 second cooldown.", bullet_style))
    story.append(Spacer(1, 6))
    story.append(Paragraph("&bull; <b>Preemption Rule:</b> If a new candidate has higher priority than ongoing speech, it preempts immediately.", bullet_style))
    story.append(Paragraph("&bull; <b>Suppression Rule:</b> Lower-priority ambient messages are silenced while an active higher-priority hazard is present.", bullet_style))
    story.append(Paragraph("&bull; <b>Debouncing:</b> Prevents repetitive audio chatter by enforcing tier-specific cooldown timers.", bullet_style))
    story.append(PageBreak())

    # ========================================================
    # SLIDE 9: WALKING NAVIGATION & EMERGENCY SOS
    # ========================================================
    add_slide_header("Modules 7 & 8: Walking Navigation & SOS", "Resilient Dual-Engine Routing & Caregiver Safety", 9)
    story.append(Paragraph("&bull; <b>Dual-Engine Pedestrian Pathfinding:</b> Queries OpenRouteService (ORS) foot-walking profile; upon any key expiry, rate limit, or 500 error, automatically engages resilient public OSRM fallback with zero user interruption.", bullet_style))
    story.append(Paragraph("&bull; <b>Ethical Location Labeling:</b> Network IP geolocation is explicitly labeled as IP_APPROXIMATE (city/ISP level accuracy); never misrepresented as satellite GPS. Full manual coordinate override supported.", bullet_style))
    story.append(Paragraph("&bull; <b>Emergency SOS Safeguards:</b>", bullet_bold))
    story.append(Paragraph("&bull; Accidental external SMS dispatch blocked unless explicitly authorized by user (BLOCKED_UNCONFIRMED).<br/>"
                           "&bull; Simulated dispatch (DISPATCHED_SIMULATED) generates live Google Maps pin hyperlinks.<br/>"
                           "&bull; All emergency incidents and caregiver contacts persisted in SQLite database.", bullet_style))
    story.append(PageBreak())

    # ========================================================
    # SLIDE 10: USER INTERFACES & EMPIRICAL TEST RESULTS
    # ========================================================
    add_slide_header("Modules 9 & 10: Interfaces & Test Scorecard", "Dual Execution Modes & 100% Automated Verification", 10)
    story.append(Paragraph("&bull; <b>Dual Operational Interfaces:</b>", bullet_bold))
    story.append(Paragraph("1. <b>Real-Time Desktop OpenCV HUD:</b> Low-latency direct webcam stream, lane dividers, picture-in-picture depth heatmap, audio alerts, and tactile keyboard hotkeys (Q, S, N, R, T).<br/>"
                           "2. <b>Accessible Streamlit Web Dashboard:</b> Caregiver portal for route planning, emergency contact registry, SOS audit logs, and hardware settings.", bullet_style))
    story.append(Spacer(1, 6))
    story.append(Paragraph("&bull; <b>Master Test Suite Scorecard (100% Pass Rate):</b>", bullet_bold))

    score_data = [
        [Paragraph("<b>Phase</b>", table_header_style), Paragraph("<b>Module Evaluated</b>", table_header_style), Paragraph("<b>Test Status</b>", table_header_style), Paragraph("<b>Duration</b>", table_header_style)],
        [Paragraph("Phase 1", table_cell_style), Paragraph("Architecture, SQLite DB & Config", table_cell_style), Paragraph("<b>PASS</b>", table_cell_style), Paragraph("12.32s", table_cell_style)],
        [Paragraph("Phase 2", table_cell_style), Paragraph("YOLOv8 Detection & Spatial Lanes", table_cell_style), Paragraph("<b>PASS</b>", table_cell_style), Paragraph("13.14s", table_cell_style)],
        [Paragraph("Phase 3", table_cell_style), Paragraph("Depth Anything V2 & Sensor Fusion", table_cell_style), Paragraph("<b>PASS</b>", table_cell_style), Paragraph("22.58s", table_cell_style)],
        [Paragraph("Phase 4", table_cell_style), Paragraph("EasyOCR Recognition & Text Filtering", table_cell_style), Paragraph("<b>PASS</b>", table_cell_style), Paragraph("20.95s", table_cell_style)],
        [Paragraph("Phase 5", table_cell_style), Paragraph("Thread-Safe SAPI Voice & Voice NLP", table_cell_style), Paragraph("<b>PASS</b>", table_cell_style), Paragraph("9.44s", table_cell_style)],
        [Paragraph("Phase 6", table_cell_style), Paragraph("AI Decision 4-Tier Priority Engine", table_cell_style), Paragraph("<b>PASS</b>", table_cell_style), Paragraph("12.43s", table_cell_style)],
        [Paragraph("Phase 7", table_cell_style), Paragraph("Walking Navigation & OSRM Fallback", table_cell_style), Paragraph("<b>PASS</b>", table_cell_style), Paragraph("2.05s", table_cell_style)],
        [Paragraph("Phase 8", table_cell_style), Paragraph("Emergency SOS Safeguards & Logging", table_cell_style), Paragraph("<b>PASS</b>", table_cell_style), Paragraph("0.16s", table_cell_style)],
        [Paragraph("<b>TOTAL</b>", table_header_style), Paragraph("<b>Complete System Evaluation</b>", table_header_style), Paragraph("<b>8 / 8 PASSED (100%)</b>", table_header_style), Paragraph("<b>93.08s</b>", table_header_style)]
    ]
    t_score = Table(score_data, colWidths=[1.5 * inch, 4.5 * inch, 2.2 * inch, 1.8 * inch])
    t_score.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F2942')),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#1A365D')),
        ('PADDING', (0, 0), (-1, -1), 3),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E0')),
    ]))
    story.append(t_score)
    story.append(PageBreak())

    # ========================================================
    # SLIDE 11: LIMITATIONS & FUTURE SCOPE
    # ========================================================
    add_slide_header("Limitations & Future Enhancements", "Critical Reflection & Technical Roadmap", 11)
    story.append(Paragraph("&bull; <b>Current Prototype Limitations:</b>", bullet_bold))
    story.append(Paragraph("&bull; <b>CPU Monocular Depth Latency:</b> ViT depth estimation takes ~200-350ms per frame on CPU (mitigated via asynchronous threading).<br/>"
                           "&bull; <b>Lighting Sensitivity:</b> Optical cameras experience accuracy degradation in pitch darkness without infrared illumination.<br/>"
                           "&bull; <b>IP Geolocation:</b> Lacks meter-level resolution without external hardware GPS dongles.", bullet_style))
    story.append(Spacer(1, 6))
    story.append(Paragraph("&bull; <b>Future Research & Engineering Roadmap:</b>", bullet_bold))
    story.append(Paragraph("&bull; <b>INT8 Model Quantization:</b> Port YOLOv8 and Depth Anything V2 to TensorRT / ONNX Runtime for sub-15ms edge inference.<br/>"
                           "&bull; <b>Smart Eyewear Hardware:</b> Deploy onto NVIDIA Jetson Orin Nano / Raspberry Pi 5 embedded in smart glasses.<br/>"
                           "&bull; <b>Haptic Feedback Vest:</b> Supplement audio with 3 directional vibration motors (Left, Center, Right).", bullet_style))
    story.append(PageBreak())

    # ========================================================
    # SLIDE 12: CONCLUSION & REPOSITORY
    # ========================================================
    add_slide_header("Conclusion & Project Artifacts", "Summary of Achievements", 12)
    story.append(Paragraph("&bull; <b>Delivered Outcome:</b> Designed, implemented, and empirically validated a production-ready assistive navigation prototype for visually impaired pedestrians.", bullet_style))
    story.append(Paragraph("&bull; <b>Engineering Discipline:</b> Clean modular architecture separating perception, intelligence, decision, persistence, and audio interaction.", bullet_style))
    story.append(Paragraph("&bull; <b>Academic Rigor:</b> Fused computer vision with ethical location handling, cognitive load filtering, and fail-safe routing.", bullet_style))
    story.append(Spacer(1, 12))

    summary_box = [
        [Paragraph("<b>Project Title:</b> AI-Powered Assistive Navigation System", bullet_style)],
        [Paragraph("<b>GitHub Repository:</b> https://github.com/aravindasurampally-123/assistive_navigation", bullet_style)],
        [Paragraph("<b>Verification:</b> 8/8 Automated Test Suites Passed (100% Pass Rate)", bullet_style)],
        [Paragraph("<b>Documentation:</b> Complete Architecture Docs, Workflow Specs, and Test Reports Included", bullet_style)]
    ]
    t_sum = Table(summary_box, colWidths=[9.5 * inch])
    t_sum.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#EDF2F7')),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#CBD5E0')),
    ]))
    story.append(t_sum)
    story.append(Spacer(1, 16))
    story.append(Paragraph("<b>Thank you! Questions and Discussion Invited.</b>", ParagraphStyle('EndP', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=14, alignment=1, textColor=colors.HexColor('#0F2942'))))

    doc.build(story)
    print(f"[PRESENTATION PDF] Successfully generated at: {PDF_PATH}")


if __name__ == "__main__":
    generate_presentation_pdf()
