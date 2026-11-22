"""
Module 8: Emergency Assistance & SOS Subsystem
AI-Powered Assistive Navigation System for Visually Impaired People

Manages emergency caregiver contacts, constructs location-aware SOS alerts,
logs all emergency incidents to SQLite, and implements safety safeguards to
distinguish simulated academic testing from real message dispatch.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from datetime import datetime

from config import DEFAULT_SOS_MESSAGE
from database.database import (
    get_emergency_contacts,
    add_emergency_contact,
    delete_emergency_contact,
    log_sos_event,
    get_sos_logs
)


@dataclass
class SOSAlertPayload:
    """The structured emergency alert package."""
    timestamp: str
    latitude: float
    longitude: float
    maps_url: str
    message: str
    recipients: List[Dict[str, Any]]
    is_simulated: bool
    status: str
    log_id: int


class EmergencyManager:
    """
    Handles emergency contact management, alert formatting, and SOS incident logging.
    """

    def __init__(self):
        pass

    @staticmethod
    def list_contacts() -> List[Dict[str, Any]]:
        """Retrieve registered emergency contacts from SQLite."""
        return get_emergency_contacts()

    @staticmethod
    def register_contact(name: str, phone: str, relationship: str = "Family", notify_sms: int = 1) -> int:
        """Register a new emergency contact in the database."""
        if not name or not phone:
            raise ValueError("Contact name and phone number are required.")
        return add_emergency_contact(name.strip(), phone.strip(), relationship.strip(), notify_sms)

    @staticmethod
    def unregister_contact(contact_id: int):
        """Remove an emergency contact by ID."""
        delete_emergency_contact(contact_id)

    @staticmethod
    def format_sos_message(latitude: float, longitude: float, custom_note: Optional[str] = None) -> str:
        """
        Constructs a concise, standardized emergency SMS/notification payload
        with coordinates and a clickable Google Maps web link.
        """
        maps_link = f"https://maps.google.com/?q={latitude:.6f},{longitude:.6f}"
        note = f" Note: {custom_note}." if custom_note else ""
        return (
            f"EMERGENCY ALERT: Visually Impaired User has triggered SOS assistance.{note} "
            f"Coordinates: {latitude:.5f}, {longitude:.5f}. Live Map: {maps_link}"
        )

    def trigger_sos(
        self,
        latitude: float,
        longitude: float,
        custom_note: Optional[str] = None,
        simulate: bool = True,
        user_confirmed: bool = False
    ) -> SOSAlertPayload:
        """
        Activates an emergency SOS event.
        Safety Safeguard: Real telecommunication dispatch (e.g. Twilio/SMS) is strictly blocked
        unless explicit user confirmation (user_confirmed=True) is provided.
        """
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        maps_link = f"https://maps.google.com/?q={latitude:.6f},{longitude:.6f}"
        message_body = self.format_sos_message(latitude, longitude, custom_note)
        contacts = self.list_contacts()

        if not simulate and not user_confirmed:
            status = "BLOCKED_UNCONFIRMED"
            log_id = log_sos_event(latitude, longitude, status, "Real dispatch blocked: explicit confirmation required.")
            return SOSAlertPayload(
                timestamp=now_str,
                latitude=latitude,
                longitude=longitude,
                maps_url=maps_link,
                message=message_body,
                recipients=contacts,
                is_simulated=False,
                status=status,
                log_id=log_id
            )

        if simulate:
            status = "DISPATCHED_SIMULATED"
            print(f"[SOS SIMULATED] Emergency Alert Dispatched at {now_str}:")
            print(f"  Recipients : {len(contacts)} contact(s)")
            for c in contacts:
                print(f"    - {c['name']} ({c['relationship']}): {c['phone']}")
            print(f"  Payload    : {message_body}")
        else:
            status = "DISPATCHED_AUTHORIZED"
            print(f"[SOS AUTHORIZED REAL DISPATCH] Sent to {len(contacts)} contacts.")

        # Log event to database
        log_id = log_sos_event(latitude, longitude, status, message_body)

        return SOSAlertPayload(
            timestamp=now_str,
            latitude=latitude,
            longitude=longitude,
            maps_url=maps_link,
            message=message_body,
            recipients=contacts,
            is_simulated=simulate,
            status=status,
            log_id=log_id
        )

    @staticmethod
    def get_incident_history(limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve historical SOS logs from SQLite."""
        return get_sos_logs(limit)
