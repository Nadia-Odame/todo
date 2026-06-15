"""
validators.py — Input validation helpers.

Provides reusable validation functions for task and category inputs.
"""

from datetime import datetime


def validate_task_title(title: str) -> tuple[bool, str]:
    """
    Validate a task title.

    Args:
        title: The task title string.

    Returns:
        Tuple of (is_valid, error_message).
    """
    if not title or not title.strip():
        return False, "Task title cannot be empty."
    if len(title.strip()) > 200:
        return False, "Task title must be 200 characters or fewer."
    return True, ""


def validate_date(date_str: str) -> tuple[bool, str]:
    """
    Validate a date string in YYYY-MM-DD format.

    Args:
        date_str: The date string to validate.

    Returns:
        Tuple of (is_valid, error_message).
    """
    if not date_str or not date_str.strip():
        return True, ""  # Date is optional

    try:
        datetime.strptime(date_str.strip(), "%Y-%m-%d")
        return True, ""
    except ValueError:
        return False, "Invalid date format. Use YYYY-MM-DD."


def validate_time(time_str: str) -> tuple[bool, str]:
    """
    Validate a time string in HH:MM format.

    Args:
        time_str: The time string to validate.

    Returns:
        Tuple of (is_valid, error_message).
    """
    if not time_str or not time_str.strip():
        return True, ""  # Time is optional

    try:
        datetime.strptime(time_str.strip(), "%H:%M")
        return True, ""
    except ValueError:
        return False, "Invalid time format. Use HH:MM (24-hour)."


def validate_category_name(name: str) -> tuple[bool, str]:
    """
    Validate a category name.

    Args:
        name: The category name string.

    Returns:
        Tuple of (is_valid, error_message).
    """
    if not name or not name.strip():
        return False, "Category name cannot be empty."
    if len(name.strip()) > 50:
        return False, "Category name must be 50 characters or fewer."
    return True, ""
