"""
Accessible UI Components
AI-Powered Assistive Navigation System
Custom CSS, high-contrast badges, cards, and accessibility helpers for Streamlit.
"""

from typing import List, Dict, Any, Optional
import streamlit as st


ACCESSIBILITY_CSS = """
<style>
    /* High-contrast and accessible typography */
    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    .status-badge {
        display: inline-block;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.95rem;
        letter-spacing: 0.5px;
        margin-bottom: 8px;
    }
    
    .badge-critical {
        background-color: #ff2b2b;
        color: #ffffff;
        animation: pulse 1.5s infinite;
    }
    
    .badge-high {
        background-color: #ff8c00;
        color: #ffffff;
    }
    
    .badge-medium {
        background-color: #0084ff;
        color: #ffffff;
    }
    
    .badge-low {
        background-color: #2e7d32;
        color: #ffffff;
    }
    
    .badge-none {
        background-color: #424242;
        color: #e0e0e0;
    }

    .obstacle-card {
        padding: 12px;
        border-radius: 8px;
        background-color: #1e1e1e;
        border-left: 5px solid #0084ff;
        margin-bottom: 10px;
    }

    .obstacle-critical {
        border-left-color: #ff2b2b;
        background-color: #2a1515;
    }

    .obstacle-high {
        border-left-color: #ff8c00;
        background-color: #2a2015;
    }

    .metric-box {
        text-align: center;
        padding: 10px;
        background-color: #1a1a1a;
        border-radius: 6px;
        border: 1px solid #333333;
    }

    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.03); }
        100% { transform: scale(1); }
    }
</style>
"""


def apply_custom_styles():
    """Inject accessible high-contrast CSS styling into Streamlit app."""
    st.markdown(ACCESSIBILITY_CSS, unsafe_allow_html=True)


def render_priority_badge(level: str) -> str:
    """Returns HTML for color-coded status badge."""
    level_lower = level.lower()
    return f'<span class="status-badge badge-{level_lower}">AI STATUS: {level.upper()}</span>'


def render_obstacle_summary(obstacles: List[Any]):
    """Renders accessible cards for detected obstacles."""
    if not obstacles:
        st.info("No immediate navigational obstacles detected.")
        return

    for obs in obstacles[:4]:
        card_class = "obstacle-card"
        if obs.hazard_level == "CRITICAL":
            card_class += " obstacle-critical"
        elif obs.hazard_level == "HIGH":
            card_class += " obstacle-high"

        html = f"""
        <div class="{card_class}">
            <strong style="font-size: 1.1rem; text-transform: uppercase;">{obs.name}</strong> 
            <span style="float: right; font-weight: bold; color: #ff8c00;">{obs.hazard_level}</span>
            <br/>
            <span style="color: #cccccc;">Position: <strong>{obs.position.upper()}</strong> | Proximity: <strong>{obs.fused_proximity}</strong></span>
            <br/>
            <span style="font-size: 0.9rem; color: #aaaaaa;">Alert: <em>"{obs.warning_message}"</em></span>
        </div>
        """
        st.markdown(html, unsafe_allow_html=True)


def render_ocr_summary(ocr_results: List[Any]):
    """Renders detected scene text and signage."""
    if not ocr_results:
        st.caption("No scene text detected in current frame.")
        return

    for item in ocr_results[:3]:
        tag = "🚨 CRITICAL SIGNBOARD" if item.is_critical_keyword else "ℹ️ SCENE TEXT"
        st.markdown(f"**{tag}**: `{item.cleaned_text}` *(Conf: {item.confidence:.0%})*")
