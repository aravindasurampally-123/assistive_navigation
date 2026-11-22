"""
Accessible Streamlit Web Dashboard
AI-Powered Assistive Navigation System for Visually Impaired People

Provides real-time camera HUD, depth heatmap visualization, OCR readout,
turn-by-turn navigation panel, emergency SOS triggers, and system configuration.
"""

import sys
from pathlib import Path
import time
import cv2
import numpy as np
import streamlit as st

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config import (
    CAMERA_INDEX,
    YOLO_CONFIDENCE_THRESHOLD,
    DEFAULT_LATITUDE,
    DEFAULT_LONGITUDE
)
from modules.object_detection import ObjectDetector, open_camera
from modules.depth_estimation import DepthEstimator
from modules.obstacle_detection import ObstacleClassifier
from modules.ocr_reader import OCRReader
from modules.voice_assistant import VoiceAssistant
from modules.ai_decision import AIDecisionEngine
from modules.navigation import WalkingNavigator
from modules.emergency import EmergencyManager
from database.database import (
    init_db,
    get_all_settings,
    set_setting,
    get_emergency_contacts,
    add_emergency_contact,
    delete_emergency_contact
)
from interface.components import (
    apply_custom_styles,
    render_priority_badge,
    render_obstacle_summary,
    render_ocr_summary
)

# Streamlit Page Config
st.set_page_config(
    page_title="AI Assistive Navigation",
    page_icon="🦯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Database
init_db()


@st.cache_resource
def load_ai_models():
    """Cache models in memory across Streamlit reruns."""
    detector = ObjectDetector(conf_threshold=YOLO_CONFIDENCE_THRESHOLD)
    depth_estimator = DepthEstimator()
    ocr_reader = OCRReader()
    voice = VoiceAssistant()
    decision_engine = AIDecisionEngine()
    navigator = WalkingNavigator()
    emergency_mgr = EmergencyManager()
    return detector, depth_estimator, ocr_reader, voice, decision_engine, navigator, emergency_mgr


# Load subsystems
detector, depth_est, ocr_reader, voice, decision_engine, navigator, emergency_mgr = load_ai_models()

# Inject accessible styles
apply_custom_styles()


# ============================================================
# SIDEBAR CONTROLS & NAVIGATION
# ============================================================
st.sidebar.title("🦯 AI Assistive System")
st.sidebar.markdown("**B.Tech AIML Major Project**")

active_tab = st.sidebar.radio(
    "Navigation Mode",
    ["🏠 Live Navigation HUD", "🗺️ Route Planner", "🆘 Emergency & SOS", "⚙️ System Settings", "📖 About Project"],
    index=0
)

st.sidebar.divider()
st.sidebar.subheader("Quick Voice Commands")
st.sidebar.info("""
- **Start / Stop Navigation**
- **Read Text**
- **Repeat Instruction**
- **Emergency Help (SOS)**
""")


# ============================================================
# TAB 1: LIVE NAVIGATION HUD
# ============================================================
if active_tab == "🏠 Live Navigation HUD":
    st.title("Live Multimodal Assistive HUD")
    st.caption("Real-time YOLOv8 obstacle detection, Depth Anything V2 relative disparity, and AI priority arbitration.")

    col1, col2 = st.columns([2, 1])

    with col2:
        st.subheader("System Controls")
        run_camera = st.toggle("Activate Live Camera Stream", value=False)
        voice_enabled = st.checkbox("Enable Spoken Voice Alerts", value=True)

        st.divider()
        st.subheader("AI Decision Status")
        status_placeholder = st.empty()
        status_placeholder.markdown(render_priority_badge("NONE"), unsafe_allow_html=True)

        message_placeholder = st.empty()
        message_placeholder.info("System Standby. Activate camera to start.")

        st.divider()
        st.subheader("Detected Obstacles")
        obstacles_placeholder = st.empty()

        st.subheader("Recognized Signage")
        ocr_placeholder = st.empty()

    with col1:
        st.subheader("Camera View & Monocular Depth")
        feed_col1, feed_col2 = st.columns(2)
        camera_placeholder = feed_col1.empty()
        depth_placeholder = feed_col2.empty()

        # Display static sample if camera is stopped
        if not run_camera:
            sample_path = PROJECT_ROOT / "tests" / "sample_bus_detected.jpg"
            sample_depth = PROJECT_ROOT / "tests" / "output_depth_heatmap.jpg"

            if sample_path.exists():
                camera_placeholder.image(str(sample_path), caption="Reference Scene View", use_container_width=True)
            if sample_depth.exists():
                depth_placeholder.image(str(sample_depth), caption="Monocular Relative Disparity Heatmap", use_container_width=True)

    if run_camera:
        cap = open_camera(camera_index=CAMERA_INDEX)
        classifier = ObstacleClassifier()
        last_ocr_time = 0.0

        if not cap.isOpened():
            st.error("Failed to open webcam. Check camera connection or privacy settings.")
        else:
            voice.speak("AI Assistive Navigation live monitoring activated.")
            stop_btn = st.sidebar.button("⏹️ Emergency Stop")

            while cap.isOpened() and not stop_btn:
                ret, frame = cap.read()
                if not ret:
                    st.warning("Frame read error.")
                    break

                now = time.time()

                # 1. YOLOv8 Detection
                detected_objs = detector.detect(frame)
                annotated_frame = detector.annotate_frame(frame, detected_objs, show_lanes=True)

                # 2. Depth Anything V2 Disparity
                depth_map = depth_est.estimate_depth_map(frame)
                depth_heatmap = depth_est.generate_heatmap(depth_map)

                # 3. Obstacle Classification & Sensor Fusion
                evaluated_obstacles = classifier.prioritize_obstacles(detected_objs, depth_map, depth_est)

                # 4. Periodic OCR (every 3 seconds)
                ocr_results = []
                ocr_announcement = None
                if now - last_ocr_time >= 3.0:
                    ocr_results = ocr_reader.read_text(frame, min_confidence=0.60)
                    ocr_announcement = ocr_reader.get_announcement(ocr_results)
                    last_ocr_time = now

                # 5. Turn Navigation Guidance
                nav_instruction = navigator.get_current_instruction()

                # 6. AI Priority Decision Engine
                decision = decision_engine.arbitrate(
                    obstacles=evaluated_obstacles,
                    navigation_instruction=nav_instruction,
                    ocr_announcement=ocr_announcement
                )

                # 7. Voice Output Execution
                if voice_enabled and decision.should_speak and decision.message:
                    voice.speak(decision.message, clear_pending=decision.clear_audio_queue)

                # Update Streamlit UI
                rgb_annotated = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
                rgb_depth = cv2.cvtColor(depth_heatmap, cv2.COLOR_BGR2RGB)

                camera_placeholder.image(rgb_annotated, caption="Real-Time Detection & Lane HUD", use_container_width=True)
                depth_placeholder.image(rgb_depth, caption="Depth Anything V2 Heatmap", use_container_width=True)

                status_placeholder.markdown(render_priority_badge(decision.level), unsafe_allow_html=True)
                if decision.message:
                    message_placeholder.warning(f"🔊 Alert: **{decision.message}**")
                else:
                    message_placeholder.success("Path is clear.")

                with obstacles_placeholder.container():
                    render_obstacle_summary(evaluated_obstacles)

                with ocr_placeholder.container():
                    render_ocr_summary(ocr_results)

                time.sleep(0.03)

            cap.release()
            voice.speak("AI Assistive Navigation stopped.")


# ============================================================
# TAB 2: ROUTE PLANNER & WALKING NAVIGATION
# ============================================================
elif active_tab == "🗺️ Route Planner":
    st.title("Walking Navigation & Turn-by-Turn Guidance")
    st.caption("Dual-Engine pedestrian routing (OpenRouteService + OSRM Public Fallback).")

    loc_col, dest_col = st.columns(2)

    with loc_col:
        st.subheader("Starting Location")
        loc_mode = st.radio("Acquisition Mode", ["Automatic Network Geolocation", "Manual Coordinates"], index=0)

        if loc_mode == "Automatic Network Geolocation":
            current_loc = WalkingNavigator.get_current_location(allow_ip_lookup=True)
            st.success(f"Location: `{current_loc.latitude:.5f}, {current_loc.longitude:.5f}`")
            st.caption(f"ℹ️ {current_loc.accuracy_note}")
            start_lat, start_lon = current_loc.latitude, current_loc.longitude
        else:
            start_lat = st.number_input("Start Latitude", value=DEFAULT_LATITUDE, format="%.5f")
            start_lon = st.number_input("Start Longitude", value=DEFAULT_LONGITUDE, format="%.5f")

    with dest_col:
        st.subheader("Destination Selection")
        presets = {
            "Hyderabad City Center": (17.3880, 78.4600),
            "Campus Library": (17.3865, 78.4890),
            "Metro Station": (17.3895, 78.4820),
            "Custom Coordinates": (0.0, 0.0)
        }
        dest_choice = st.selectbox("Destination Preset", list(presets.keys()))

        if dest_choice == "Custom Coordinates":
            dest_lat = st.number_input("Destination Latitude", value=17.3900, format="%.5f")
            dest_lon = st.number_input("Destination Longitude", value=78.4900, format="%.5f")
        else:
            dest_lat, dest_lon = presets[dest_choice]
            st.info(f"Target: `{dest_lat:.5f}, {dest_lon:.5f}`")

    if st.button("🚶 Calculate Walking Route", type="primary"):
        with st.spinner("Calculating walking route..."):
            route = navigator.calculate_walking_route(start_lat, start_lon, dest_lat, dest_lon)
            if route:
                st.session_state["active_route"] = route
                voice.speak(f"Walking route calculated. Total distance is {route.total_distance_km:.2f} kilometers.")

    if "active_route" in st.session_state:
        route = st.session_state["active_route"]
        st.divider()
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Walking Distance", f"{route.total_distance_km:.2f} km")
        m2.metric("Estimated Walking Time", f"{route.total_duration_minutes:.0f} mins")
        m3.metric("Routing Provider", route.provider)

        st.subheader("Turn-by-Turn Guidance")
        step_cols = st.columns([3, 1])
        with step_cols[0]:
            st.markdown(f"### Current Instruction: **{navigator.get_current_instruction()}**")
        with step_cols[1]:
            if st.button("⏭️ Next Step"):
                next_inst = navigator.advance_step()
                if next_inst:
                    voice.speak(next_inst)
                    st.rerun()

        st.write("#### Detailed Maneuvers")
        for s in route.steps:
            st.write(f"**Step {s.step_number}:** {s.instruction} *(Distance: {s.distance_meters:.0f} m)*")


# ============================================================
# TAB 3: EMERGENCY & SOS
# ============================================================
elif active_tab == "🆘 Emergency & SOS":
    st.title("Caregiver Emergency & SOS Assistance")
    st.caption("Manage trusted caregiver emergency contacts and simulate emergency SOS dispatches.")

    sos_col, contact_col = st.columns([1, 1])

    with sos_col:
        st.subheader("Emergency SOS Trigger")
        st.error("🚨 ONE-TOUCH EMERGENCY TRIGGER")
        custom_sos_note = st.text_input("Incident Note", value="Visually impaired user requested immediate help")
        
        sim_mode = st.checkbox("Simulate Dispatch (Recommended for academic demo)", value=True)
        confirmed = st.checkbox("I authorize emergency dispatch transmission", value=False)

        if st.button("🚨 TRIGGER EMERGENCY SOS ALERT", type="primary"):
            curr_loc = WalkingNavigator.get_current_location()
            payload = emergency_mgr.trigger_sos(
                latitude=curr_loc.latitude,
                longitude=curr_loc.longitude,
                custom_note=custom_sos_note,
                simulate=sim_mode,
                user_confirmed=confirmed
            )

            if payload.status == "DISPATCHED_SIMULATED":
                st.success("✅ SIMULATED SOS ALERT DISPATCHED TO CAREGIVERS")
                voice.speak("Emergency SOS alert dispatched to caregivers.", clear_pending=True)
                st.json({
                    "Timestamp": payload.timestamp,
                    "Coordinates": f"{payload.latitude}, {payload.longitude}",
                    "Live Map": payload.maps_url,
                    "Recipients": len(payload.recipients),
                    "Payload": payload.message
                })
            elif payload.status == "BLOCKED_UNCONFIRMED":
                st.warning("⚠️ Real emergency transmission blocked: Explicit user authorization checkbox was not checked.")
            else:
                st.success("🚨 REAL EMERGENCY ALERT DISPATCHED")

    with contact_col:
        st.subheader("Emergency Contact Registry")
        contacts = emergency_mgr.list_contacts()

        for c in contacts:
            c_col1, c_col2 = st.columns([3, 1])
            c_col1.markdown(f"**{c['name']}** ({c['relationship']})<br/>`{c['phone']}`", unsafe_allow_html=True)
            if c_col2.button("🗑️ Delete", key=f"del_{c['id']}"):
                emergency_mgr.unregister_contact(c['id'])
                st.rerun()

        st.divider()
        st.write("#### Add Caregiver Contact")
        new_name = st.text_input("Full Name")
        new_phone = st.text_input("Phone Number (with country code)")
        new_rel = st.selectbox("Relationship", ["Family", "Friend", "Doctor", "Caregiver"])

        if st.button("➕ Register Contact"):
            if new_name and new_phone:
                emergency_mgr.register_contact(new_name, new_phone, new_rel)
                st.success(f"Added {new_name}")
                st.rerun()

    st.divider()
    st.subheader("Recent SOS Incident Log")
    logs = emergency_mgr.get_incident_history(limit=5)
    st.table(logs)


# ============================================================
# TAB 4: SYSTEM SETTINGS
# ============================================================
elif active_tab == "⚙️ System Settings":
    st.title("System Preferences & Hardware Settings")
    st.caption("Settings are persisted locally in the SQLite database (`database/assistive_navigation.db`).")

    settings = get_all_settings()

    st.subheader("Voice Assistant Settings")
    v_rate = st.slider("Speech Rate (-10 to +10)", -10, 10, int(settings.get("voice_rate", "0")))
    v_vol = st.slider("Speech Volume (0 to 100%)", 0, 100, int(settings.get("voice_volume", "100")))

    st.subheader("Computer Vision & Detection")
    conf_thresh = st.slider("YOLOv8 Confidence Threshold", 0.10, 0.90, float(settings.get("yolo_confidence", "0.45")), 0.05)
    ocr_int = st.slider("OCR Background Scan Interval (seconds)", 1.0, 10.0, float(settings.get("ocr_interval", "3.0")), 0.5)

    if st.button("💾 Save Settings", type="primary"):
        set_setting("voice_rate", str(v_rate))
        set_setting("voice_volume", str(v_vol))
        set_setting("yolo_confidence", str(conf_thresh))
        set_setting("ocr_interval", str(ocr_int))
        st.success("Settings saved successfully to SQLite database.")
        voice.rate = v_rate
        voice.volume = v_vol


# ============================================================
# TAB 5: ABOUT PROJECT
# ============================================================
elif active_tab == "📖 About Project":
    st.title("About AI Assistive Navigation System")
    st.markdown("""
    ### 3rd-Year B.Tech AIML Major Project
    **Project Title**: AI-Powered Assistive Navigation System for Visually Impaired People
    
    #### Key AIML Concepts Implemented:
    1. **Real-Time Object Detection**: Single-stage YOLOv8 Nano architecture performing anchor-free edge inference.
    2. **Monocular Relative Depth Estimation**: Vision Transformer (Depth Anything V2) extracting qualitative proximity without stereo/LiDAR hardware.
    3. **Scene Text Understanding**: End-to-end optical character recognition with EasyOCR (CRAFT + CRNN).
    4. **AI Priority Arbitration Engine**: 4-tier state-machine decision model preventing auditory overload.
    5. **Resilient Graph Pathfinding**: Pedestrian walking directions with automatic fallback to OSRM.
    6. **Asynchronous Non-Blocking Voice Architecture**: Thread-safe Windows SAPI engine with emergency queue preemption.
    7. **Ethical HCI Safeguards**: Distinguishing approximate IP derivation from GPS; blocking unconfirmed real SOS dispatches.
    """)
