"""
models.py — Data models for the Focus To-Do application.

Provides dataclass representations of database entities, making it easy
to pass structured data between controllers and views.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Task:
    """Represents a single to-do task."""

    id: int = 0
    title: str = ""
    description: str = ""
    priority: str = "Medium"  # Low, Medium, High
    category_id: Optional[int] = None
    category_name: Optional[str] = None  # Joined from categories table
    due_date: Optional[str] = None       # YYYY-MM-DD format
    due_time: Optional[str] = None       # HH:MM format
    completed: bool = False
    created_at: str = ""
    updated_at: str = ""

    @classmethod
    def from_row(cls, row) -> "Task":
        """
        Create a Task instance from a database Row object.

        Args:
            row: sqlite3.Row from a query result.

        Returns:
            A populated Task instance.
        """
        keys = row.keys()
        return cls(
            id=row["id"],
            title=row["title"],
            description=row["description"] if "description" in keys else "",
            priority=row["priority"],
            category_id=row["category_id"] if "category_id" in keys else None,
            category_name=row["category_name"] if "category_name" in keys else None,
            due_date=row["due_date"] if "due_date" in keys else None,
            due_time=row["due_time"] if "due_time" in keys else None,
            completed=bool(row["completed"]),
            created_at=row["created_at"] if "created_at" in keys else "",
            updated_at=row["updated_at"] if "updated_at" in keys else "",
        )


@dataclass
class Category:
    """Represents a task category / focus area."""

    id: int = 0
    name: str = ""
    icon: str = "📁"
    color: str = "#3B82F6"
    created_at: str = ""
    pending_count: int = 0  # Computed field — not stored in DB

    @classmethod
    def from_row(cls, row) -> "Category":
        """Create a Category instance from a database Row object."""
        keys = row.keys()
        return cls(
            id=row["id"],
            name=row["name"],
            icon=row["icon"] if "icon" in keys else "📁",
            color=row["color"] if "color" in keys else "#3B82F6",
            created_at=row["created_at"] if "created_at" in keys else "",
            pending_count=row["pending_count"] if "pending_count" in keys else 0,
        )


@dataclass
class UserSettings:
    """Represents application settings as a simple key-value bag."""

    theme: str = "dark"
    username: str = ""

    @classmethod
    def from_rows(cls, rows) -> "UserSettings":
        """
        Build a UserSettings instance from a list of (key, value) rows.

        Args:
            rows: List of sqlite3.Row from the settings table.

        Returns:
            A populated UserSettings instance.
        """
        settings = cls()
        for row in rows:
            key = row["key"]
            value = row["value"]
            if hasattr(settings, key):
                setattr(settings, key, value)
        return settings
