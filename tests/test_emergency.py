"""
Phase 8 Verification Script
Tests Emergency Assistance Subsystem, Contact Management, SOS Alert Payloads,
Safety Safeguards, and SQLite Incident Logging.
"""

import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from modules.emergency import EmergencyManager, SOSAlertPayload


def test_contact_management():
    print("=" * 60)
    print("TEST 1: EMERGENCY CONTACT MANAGEMENT (SQLITE)")
    print("=" * 60)

    mgr = EmergencyManager()

    # 1. Read existing contacts
    initial_contacts = mgr.list_contacts()
    print(f"Existing contacts count: {len(initial_contacts)}")
    assert len(initial_contacts) > 0, "Default contact was not found"

    # 2. Add a new contact
    new_id = mgr.register_contact("Dr. Anita Rao", "+91 91234 56789", "Physician")
    print(f"Registered new contact (ID={new_id}): Dr. Anita Rao")

    updated_contacts = mgr.list_contacts()
    contact_names = [c["name"] for c in updated_contacts]
    assert "Dr. Anita Rao" in contact_names, "Newly registered contact not found in database"

    # 3. Clean up test contact
    mgr.unregister_contact(new_id)
    final_contacts = mgr.list_contacts()
    final_names = [c["name"] for c in final_contacts]
    assert "Dr. Anita Rao" not in final_names, "Failed to unregister test contact"
    print("STATUS: PASS (Emergency contact CRUD operational)")


def test_sos_formatting_and_safeguards():
    print("\n" + "=" * 60)
    print("TEST 2: SOS MESSAGE FORMATTING & SAFETY SAFEGUARDS")
    print("=" * 60)

    mgr = EmergencyManager()
    test_lat, test_lon = 17.385044, 78.486671

    # Format verification
    msg = mgr.format_sos_message(test_lat, test_lon, "Obstacle collision reported")
    print(f"Constructed SOS Message:\n'{msg}'")
    assert "EMERGENCY ALERT" in msg
    assert "https://maps.google.com/?q=" in msg
    assert "17.38504" in msg

    # Safety Safeguard Test:
    # Attempting to send a real message without explicit user confirmation MUST be blocked
    blocked_payload = mgr.trigger_sos(
        test_lat, test_lon,
        simulate=False,
        user_confirmed=False
    )
    print(f"\nUnconfirmed Real Dispatch Check:")
    print(f"  Status        : {blocked_payload.status} [Expected: BLOCKED_UNCONFIRMED]")
    print(f"  Is Simulated  : {blocked_payload.is_simulated}")
    assert blocked_payload.status == "BLOCKED_UNCONFIRMED", "Safety violation: Unconfirmed dispatch was not blocked!"

    # Simulated Emergency SOS Test
    sim_payload = mgr.trigger_sos(
        test_lat, test_lon,
        custom_note="Testing SOS audio and caregiver logging",
        simulate=True
    )
    print(f"\nSimulated Dispatch Check:")
    print(f"  Status        : {sim_payload.status} [Expected: DISPATCHED_SIMULATED]")
    print(f"  Logged DB ID  : {sim_payload.log_id}")
    print(f"  Recipients    : {len(sim_payload.recipients)}")
    assert sim_payload.status == "DISPATCHED_SIMULATED"
    assert sim_payload.is_simulated is True
    assert sim_payload.log_id > 0

    print("STATUS: PASS (Formatting, safeguards, and simulated dispatch verified)")


def test_sqlite_incident_logging():
    print("\n" + "=" * 60)
    print("TEST 3: SQLITE SOS INCIDENT LOG RETRIEVAL")
    print("=" * 60)

    mgr = EmergencyManager()
    logs = mgr.get_incident_history(limit=5)
    print(f"Retrieved {len(logs)} recent SOS incident log(s):")
    for log in logs:
        print(f"  [ID {log['id']:<2}] {log['timestamp']} | Status: {log['status']:<22} | Lat: {log['latitude']:.4f}")

    assert len(logs) > 0, "No SOS incident logs retrieved from database"
    print("STATUS: PASS (SQLite incident history verified)")


if __name__ == "__main__":
    test_contact_management()
    test_sos_formatting_and_safeguards()
    test_sqlite_incident_logging()
    print("\n" + "=" * 60)
    print("PHASE 8 COMPLETED SUCCESSFULLY!")
    print("=" * 60)
