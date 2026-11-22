"""
Database Management Module (SQLite)
AI-Powered Assistive Navigation System
Manages application configuration, emergency contacts, and SOS alert logs.
"""

import sqlite3
from typing import List, Dict, Any, Optional
from config import DATABASE_PATH


def get_connection() -> sqlite3.Connection:
    """Create a thread-safe connection to the SQLite database."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize database tables with appropriate schemas and default values."""
    with get_connection() as conn:
        cursor = conn.cursor()

        # 1. Settings Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                description TEXT
            )
        """)

        # 2. Emergency Contacts Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS emergency_contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                relationship TEXT,
                notify_sms INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 3. SOS Alert Logs Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sos_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                latitude REAL,
                longitude REAL,
                status TEXT,
                message TEXT
            )
        """)

        # Seed default settings if not already present
        default_settings = [
            ("voice_rate", "0", "Windows SAPI speech rate (-10 to 10)"),
            ("voice_volume", "100", "Windows SAPI speech volume (0 to 100)"),
            ("yolo_confidence", "0.45", "Confidence threshold for YOLOv8 object detection"),
            ("ocr_interval", "3.0", "Interval between background OCR text scans (seconds)"),
            ("default_destination_name", "City Center", "Default destination preset name"),
            ("default_destination_lat", "17.3880", "Default destination latitude"),
            ("default_destination_lon", "78.4600", "Default destination longitude")
        ]

        cursor.executemany("""
            INSERT OR IGNORE INTO settings (key, value, description)
            VALUES (?, ?, ?)
        """, default_settings)

        # Seed an example emergency contact if table is empty
        cursor.execute("SELECT COUNT(*) FROM emergency_contacts")
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO emergency_contacts (name, phone, relationship, notify_sms)
                VALUES ('Primary Caregiver', '+91 98765 43210', 'Family', 1)
            """)

        conn.commit()


# ============================================================
# SETTINGS CRUD OPERATIONS
# ============================================================

def get_setting(key: str, default: Optional[str] = None) -> Optional[str]:
    """Retrieve a setting value by key."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
        row = cursor.fetchone()
        return row["value"] if row else default


def set_setting(key: str, value: str, description: Optional[str] = None):
    """Set or update a configuration setting."""
    with get_connection() as conn:
        cursor = conn.cursor()
        if description:
            cursor.execute("""
                INSERT INTO settings (key, value, description)
                VALUES (?, ?, ?)
                ON CONFLICT(key) DO UPDATE SET value = excluded.value, description = excluded.description
            """, (key, str(value), description))
        else:
            cursor.execute("""
                INSERT INTO settings (key, value)
                VALUES (?, ?)
                ON CONFLICT(key) DO UPDATE SET value = excluded.value
            """, (key, str(value)))
        conn.commit()


def get_all_settings() -> Dict[str, str]:
    """Retrieve all system settings as a dictionary."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT key, value FROM settings")
        return {row["key"]: row["value"] for row in cursor.fetchall()}


# ============================================================
# EMERGENCY CONTACTS CRUD OPERATIONS
# ============================================================

def get_emergency_contacts() -> List[Dict[str, Any]]:
    """Retrieve all registered emergency contacts."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, phone, relationship, notify_sms, created_at FROM emergency_contacts ORDER BY id ASC")
        return [dict(row) for row in cursor.fetchall()]


def add_emergency_contact(name: str, phone: str, relationship: str = "Family", notify_sms: int = 1) -> int:
    """Add a new emergency contact."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO emergency_contacts (name, phone, relationship, notify_sms)
            VALUES (?, ?, ?, ?)
        """, (name, phone, relationship, notify_sms))
        conn.commit()
        return cursor.lastrowid


def delete_emergency_contact(contact_id: int):
    """Delete an emergency contact by ID."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM emergency_contacts WHERE id = ?", (contact_id,))
        conn.commit()


# ============================================================
# SOS LOGGING
# ============================================================

def log_sos_event(latitude: float, longitude: float, status: str, message: str) -> int:
    """Log an SOS trigger event into the database."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO sos_logs (latitude, longitude, status, message)
            VALUES (?, ?, ?, ?)
        """, (latitude, longitude, status, message))
        conn.commit()
        return cursor.lastrowid


def get_sos_logs(limit: int = 10) -> List[Dict[str, Any]]:
    """Retrieve the most recent SOS trigger events."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, timestamp, latitude, longitude, status, message FROM sos_logs ORDER BY id DESC LIMIT ?", (limit,))
        return [dict(row) for row in cursor.fetchall()]


if __name__ == "__main__":
    print("Testing database initialization...")
    init_db()
    print("Settings:", get_all_settings())
    print("Contacts:", get_emergency_contacts())
    print("Database test passed.")
