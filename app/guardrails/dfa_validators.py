"""Deterministic Finite Automaton (DFA) State Machine & Business Rule Validators."""
from typing import Dict, Any, Tuple
from datetime import datetime, date, timedelta
import logging

logger = logging.getLogger(__name__)

VALID_ITSM_TRANSITIONS = {
    "New": ["In Progress", "Cancelled"],
    "In Progress": ["Resolved", "Pending Customer"],
    "Pending Customer": ["In Progress", "Resolved"],
    "Resolved": ["Closed", "In Progress"],
    "Closed": []
}

class DFAValidator:
    @staticmethod
    def validate_leave_submission(
        leave_type: str,
        start_date_str: str,
        days_requested: float,
        available_balance: float
    ) -> Tuple[bool, str]:
        """Validate leave request against business rules including -14d retroactivity."""
        if leave_type not in ["Vacation", "Sick"]:
            return False, f"Unsupported leave type '{leave_type}'. Automated processing supports only Vacation and Sick leave. Please contact People Operations (people-ops@altostrat.com)."

        if days_requested <= 0:
            return False, "Days requested must be greater than 0."

        if days_requested > available_balance:
            return False, f"Insufficient leave balance. Requested {days_requested} days, but your current available {leave_type} balance is {available_balance} days. Please adjust your request to not exceed {available_balance} days or contact People Operations."

        try:
            start_dt = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        except ValueError:
            return False, "Invalid start_date format. Must be YYYY-MM-DD."

        today = date.today()

        # Rule 1: Vacation leave cannot be retroactive (future dates only per FR-3.3)
        if leave_type == "Vacation" and start_dt < today:
            return False, "Vacation start date cannot be in the past."

        # Rule 2: Sick leave retroactivity check (max -14 calendar days per SDD D-008)
        if leave_type == "Sick":
            min_allowed_date = today - timedelta(days=14)
            if start_dt < min_allowed_date:
                return False, f"Sick leave cannot be applied retroactively beyond 14 calendar days (earliest allowed: {min_allowed_date.isoformat()})."

        return True, "VALID"

    @staticmethod
    def validate_itsm_transition(current_status: str, next_status: str) -> Tuple[bool, str]:
        """Validate ITSM ticket status lifecycle transition."""
        allowed = VALID_ITSM_TRANSITIONS.get(current_status, [])
        if next_status not in allowed:
            return False, f"Invalid ITSM status transition from '{current_status}' to '{next_status}'. Allowed transitions: {allowed}"
        return True, "VALID"
