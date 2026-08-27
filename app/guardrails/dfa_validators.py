"""Deterministic Finite Automaton (DFA) State Machine & Leave Rule Validators."""
from typing import Dict, Any, Tuple
from datetime import datetime, date

VALID_ITSM_TRANSITIONS = {
    "New": ["In Progress", "Cancelled"],
    "In Progress": ["Resolved", "Pending Customer"],
    "Pending Customer": ["In Progress", "Resolved"],
    "Resolved": ["Closed", "In Progress"],
    "Closed": [] # Terminal
}

class DFAValidator:
    @staticmethod
    def validate_leave_submission(
        leave_type: str,
        start_date_str: str,
        days_requested: float,
        available_balance: float
    ) -> Tuple[bool, str]:
        """Validate leave request against business rules."""
        if leave_type not in ["Vacation", "Sick"]:
            return False, f"Unsupported leave type '{leave_type}'. Automated processing supports only Vacation and Sick leave. Please contact People Ops (people-ops@altostrat.com)."

        if days_requested <= 0:
            return False, "Days requested must be greater than 0."

        if days_requested > available_balance:
            return False, f"Insufficient leave balance. Requested {days_requested} days, but only {available_balance} days available."

        if leave_type == "Vacation":
            try:
                start_dt = datetime.strptime(start_date_str, "%Y-%m-%d").date()
                if start_dt < date.today():
                    return False, "Vacation start date cannot be in the past."
            except ValueError:
                return False, "Invalid start_date format. Must be YYYY-MM-DD."

        return True, "VALID"

    @staticmethod
    def validate_itsm_transition(current_status: str, next_status: str) -> Tuple[bool, str]:
        """Validate ITSM ticket status lifecycle transition."""
        allowed = VALID_ITSM_TRANSITIONS.get(current_status, [])
        if next_status not in allowed:
            return False, f"Invalid ITSM status transition from '{current_status}' to '{next_status}'. Allowed transitions: {allowed}"
        return True, "VALID"
