"""
settings_controller.py — Manages user preferences persistence.

Stores and retrieves key-value settings from the SQLite settings table.
"""

from database import Database
from models import UserSettings


class SettingsController:
    """Handles reading and writing user preferences."""

    def __init__(self, db: Database):
        self.db = db

    def get(self, key: str, default: str = "") -> str:
        """
        Get a single setting value.

        Args:
            key:     The setting key name.
            default: Value returned if key not found.

        Returns:
            The setting value as a string.
        """
        row = self.db.fetch_one("SELECT value FROM settings WHERE key = ?", (key,))
        return row["value"] if row else default

    def set(self, key: str, value: str) -> None:
        """
        Set a single setting value (upsert).

        Args:
            key:   The setting key name.
            value: The value to store.
        """
        self.db.execute(
            "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
            (key, value),
        )

    def get_theme(self) -> str:
        """Return the current theme ('dark' or 'light')."""
        return self.get("theme", "dark")

    def set_theme(self, mode: str) -> None:
        """
        Save the theme preference.

        Args:
            mode: 'dark' or 'light'.
        """
        if mode in ("dark", "light"):
            self.set("theme", mode)

    def get_username(self) -> str:
        """Return the saved username."""
        return self.get("username", "")

    def set_username(self, name: str) -> None:
        """Save the username."""
        self.set("username", name)

    def get_all_settings(self) -> UserSettings:
        """Load all settings into a UserSettings object."""
        rows = self.db.fetch_all("SELECT * FROM settings")
        return UserSettings.from_rows(rows)

    def is_first_launch(self) -> bool:
        """Check if this is the first time the app is launched (no username set)."""
        username = self.get_username()
        return username == "" or username is None
