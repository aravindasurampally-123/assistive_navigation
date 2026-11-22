# Database package
from .database import (
    init_db,
    get_setting,
    set_setting,
    get_all_settings,
    get_emergency_contacts,
    add_emergency_contact,
    delete_emergency_contact,
    log_sos_event,
    get_sos_logs,
)
