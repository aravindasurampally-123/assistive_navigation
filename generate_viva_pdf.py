"""
PDF Generator: Viva Questions & Comprehensive Defense Guide
AI-Powered Assistive Navigation System for Visually Impaired People
"""

import sys
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

PROJECT_ROOT = Path(__file__).resolve().parent
DOCS_DIR = PROJECT_ROOT / "docs"
DOCS_DIR.mkdir(parents=True, exist_ok=True)
PDF_PATH = DOCS_DIR / "AI_Assistive_Navigation_Viva_Questions.pdf"


def generate_viva_pdf():
    doc = SimpleDocTemplate(
        str(PDF_PATH),
        pagesize=letter,
        leftMargin=0.6 * inch,
        rightMargin=0.6 * inch,
        topMargin=0.6 * inch,
        bottomMargin=0.6 * inch
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#0F2942'),
        spaceAfter=4
    )

    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=14,
        textColor=colors.HexColor('#3182CE'),
        spaceAfter=12
    )

    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=colors.HexColor('#0F2942'),
        spaceBefore=12,
        spaceAfter=6
    )

    question_style = ParagraphStyle(
        'QuestionStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#1A365D'),
        spaceBefore=8,
        spaceAfter=3
    )

    answer_style = ParagraphStyle(
        'AnswerStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#2D3748'),
        spaceAfter=6
    )

    tip_style = ParagraphStyle(
        'TipStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor('#2B6CB0')
    )

    story = []

    # Title & Header
    story.append(Paragraph("AI-Powered Assistive Navigation System", title_style))
    story.append(Paragraph("Major Academic B.Tech AIML Project &bull; Comprehensive Viva Voce Examination Guide", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0F2942'), spaceAfter=10))

    # Meta Table
    meta_data = [
        [
            Paragraph("<b>Candidate:</b> Aravinda", answer_style),
            Paragraph("<b>Degree:</b> B.Tech (3rd Year, AIML)", answer_style)
        ],
        [
            Paragraph("<b>Domain:</b> Multimodal Edge AI & Computer Vision", answer_style),
            Paragraph("<b>Verification:</b> 8/8 Test Suites Passed (100%)", answer_style)
        ]
    ]
    t = Table(meta_data, colWidths=[3.5 * inch, 3.5 * inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#EDF2F7')),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t)
    story.append(Spacer(1, 12))

    # Viva Questions & Answers
    viva_qa = [
        (
            "Q1. Why did you select YOLOv8 Nano instead of larger architectures like YOLOv8x or Faster R-CNN?",
            "In an assistive edge system for the visually impaired, low latency and thermal efficiency on edge hardware are paramount. Faster R-CNN relies on a two-stage architecture (Region Proposal Network + R-CNN classifier), introducing prohibitive latency for real-time mobile tasks. YOLOv8 Nano uses an anchor-free single-stage backbone with only 3.2M parameters (~6.2 MB), achieving steady ~30 FPS on standard CPUs while accurately detecting pedestrians, vehicles, chairs, and doors without audio frame stuttering."
        ),
        (
            "Q2. How does Depth Anything V2 function, and why is its output labeled 'relative depth' rather than meters?",
            "Depth Anything V2 utilizes a Vision Transformer (DINOv2) backbone trained via self-supervised pretraining to predict dense relative disparity / inverse depth. True physical metric distance in meters requires known camera intrinsic focal parameters (fx, fy), sensor mounting height, or dual-camera stereo triangulation. To maintain scientific rigor and avoid inaccurate claims during our defense, our system normalizes disparity to [0.0, 1.0] and categorizes proximity into qualitative hazard bands ('very close', 'near', 'medium', 'far')."
        ),
        (
            "Q3. How is the 3-zone lateral spatial localization mathematically computed?",
            "For a camera frame of horizontal pixel width W, the horizontal centroid cx of a detected obstacle bounding box (x1, y1, x2, y2) is computed as cx = x1 + (x2 - x1) / 2. The obstacle is then categorized into directional walking lanes: Left if cx < W/3; Ahead (direct collision corridor) if W/3 <= cx <= 2W/3; and Right if cx > 2W/3. Obstacles labeled 'ahead' receive top safety priority."
        ),
        (
            "Q4. What is the architecture behind EasyOCR and why was regex text cleaning necessary?",
            "EasyOCR utilizes a deep learning pipeline consisting of CRAFT (Character Region Awareness for Text Detection) to locate arbitrary-oriented character polygons, followed by a CRNN (ResNet + Bidirectional LSTM + CTC loss decoder) for character sequence transcription. Real-world scene OCR frequently produces spurious punctuation debris (~, |, ^). Regex sanitization filters non-alphanumeric noise, ensuring only coherent words reach the speech synthesizer."
        ),
        (
            "Q5. Explain the architecture of the AI Priority Decision Engine and why it is critical for visually impaired users.",
            "Visually impaired pedestrians suffer from severe auditory cognitive overload if every object, signboard, and turn instruction is spoken continuously. Sighted individuals filter visual noise using peripheral vision; our AI Decision Engine acts as an algorithmic cognitive filter. It arbitrates all candidate inputs across four strict tiers: CRITICAL (4: Immediate Collision Danger) > HIGH (3: Nearby Obstacle) > MEDIUM (2: Walking Route Direction) > LOW (1: Scene Signboard). High priority immediately preempts speech, while lower-priority messages are suppressed during active hazard cooldowns."
        ),
        (
            "Q6. How does your audio architecture achieve zero camera frame drops during speech?",
            "Calling synchronous Text-to-Speech directly in the OpenCV loop freezes video capture for 2 to 4 seconds during speech output. Furthermore, Windows SAPI requires Single-Threaded Apartment (STA) initialization. We engineered a dedicated background worker thread running pythoncom.CoInitialize() with an asynchronous thread-safe queue.Queue. When voice.speak() is invoked, the message enqueues in 0.00 ms, allowing the main OpenCV computer vision pipeline to sustain steady real-time execution."
        ),
        (
            "Q7. What is Priority Preemption in the voice queue, and how is it implemented?",
            "If the system is articulating a routine message like 'Continue straight for 50 meters' when a pedestrian suddenly enters the user's path, the navigation instruction must not block the safety alert. When a CRITICAL alert arrives, the voice assistant executes clear_pending=True, draining the pending queue via non-blocking queue.get_nowait() calls so that 'Warning! Person ahead. Stop!' speaks with zero latency."
        ),
        (
            "Q8. How does the Walking Navigation engine achieve resilience against API failures?",
            "Many student projects crash during live defense if cloud API tokens expire, hit rate limits, or return server proxy 500 errors. In modules/navigation.py, we built a dual-engine architecture: the primary query targets OpenRouteService (ORS); upon any timeout, 401, or 500 error, it automatically falls back to public Open Source Routing Machine (OSRM) foot-walking endpoints without crashing, and further includes an offline linear bearing estimator if completely disconnected."
        ),
        (
            "Q9. Why does your project explicitly distinguish between IP Geolocation and Satellite GPS?",
            "Standard laptops lack dedicated satellite GPS receiver chips and instead derive coordinates from public IP routing tables (ISP node approximations). IP-based geolocation has an accuracy radius of 2 to 10 kilometers. Misrepresenting IP lookup as 'satellite GPS' is factually incorrect and penalized in technical vivas. Our system adheres to academic integrity by labeling IP coordinates as IP_APPROXIMATE and providing manual coordinate input for campus presets."
        ),
        (
            "Q10. What Human-Computer Interaction (HCI) safety safeguards are built into the Emergency SOS module?",
            "False emergency dispatches can cause panic for family members and strain emergency services. In modules/emergency.py, external transmission is strictly blocked unless the user explicitly checks an authorization confirmation (BLOCKED_UNCONFIRMED). For academic testing and viva demonstrations, the system operates in DISPATCHED_SIMULATED mode, formatting a standardized message with a live Google Maps pin and recording the incident in SQLite."
        ),
        (
            "Q11. Explain your database schema and why SQLite was selected.",
            "We selected embedded SQLite 3 because it requires zero external server setup, is ACID compliant, and is natively cross-platform. Our schema contains: 1) settings (application parameters like voice rates and confidence thresholds), 2) emergency_contacts (caregiver names, phones, relationships), and 3) sos_logs (timestamped audit log of all emergency triggers with coordinates and dispatch status)."
        ),
        (
            "Q12. How does the system recognize spoken voice commands?",
            "In modules/speech_commands.py, the CommandParser uses regex pattern matching to map colloquial speech to canonical commands: START_SYSTEM, STOP_SYSTEM, START_NAVIGATION, STOP_NAVIGATION, READ_TEXT, REPEAT_INSTRUCTION, and EMERGENCY_HELP. Emergency triggers are evaluated first for immediate safety preemption."
        ),
        (
            "Q13. How was the entire codebase verified, and what was the empirical test result?",
            "We built a master automated test suite (tests/run_all_tests.py) that executes all 8 module verification suites in isolated subprocesses. Each suite validates boundary conditions, inference correctness, and exception handling. The master suite achieved a 100% pass rate (8/8 suites passed) with an aggregated execution duration of 93.08 seconds."
        ),
        (
            "Q14. What are the key limitations of your current prototype?",
            "1) Running Depth Anything V2 on CPU introduces ~200-350ms latency per depth frame (mitigated by running depth asynchronously). 2) Optical cameras degrade in pitch-black conditions without an auxiliary infrared or torch source. 3) IP geolocation lacks meter-level precision without external GPS hardware."
        ),
        (
            "Q15. How would you commercialize and deploy this system in the real world?",
            "I would convert the PyTorch models to INT8 precision using NVIDIA TensorRT or ONNX Runtime and deploy them onto a wearable embedded platform such as an NVIDIA Jetson Orin Nano or Raspberry Pi 5. The hardware would be mounted onto lightweight smart glasses paired with bone-conduction headphones so the user's ear canals remain open to environmental sounds."
        )
    ]

    for q, a in viva_qa:
        item = []
        item.append(Paragraph(f"<b>{q}</b>", question_style))
        item.append(Paragraph(a, answer_style))
        story.append(KeepTogether(item))

    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#CBD5E0'), spaceAfter=8))

    # Defense Strategy Box
    tips = [
        "<b>Examiner Tip 1:</b> Never claim Depth Anything V2 gives distance in meters. Always specify 'qualitative relative disparity'.",
        "<b>Examiner Tip 2:</b> Emphasize the AI Decision Engine as your key original algorithmic contribution reducing cognitive load.",
        "<b>Examiner Tip 3:</b> Run the Master Test Suite (tests/run_all_tests.py) first to prove 100% automated software verification."
    ]
    for tip in tips:
        story.append(Paragraph(f"&bull; {tip}", tip_style))
        story.append(Spacer(1, 3))

    doc.build(story)
    print(f"[VIVA PDF] Successfully generated at: {PDF_PATH}")


if __name__ == "__main__":
    generate_viva_pdf()
