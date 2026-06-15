"""
database.py — SQLite database manager for the Focus To-Do application.

Handles database creation, table initialization, and provides generic
query execution methods used by all controllers.
"""

import sqlite3
import os
from datetime import datetime


class Database:
    """Manages the SQLite database connection and schema."""

    DB_NAME = "focus_tasks.db"

    def __init__(self, db_path: str = None):
        """
        Initialize the database connection.

        Args:
            db_path: Optional custom path to the database file.
                     Defaults to 'focus_tasks.db' in the app directory.
        """
        if db_path is None:
            # Store the DB next to the main script
            base_dir = os.path.dirname(os.path.abspath(__file__))
            db_path = os.path.join(base_dir, self.DB_NAME)

        self.db_path = db_path
        self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row  # Enable dict-like row access
        self.connection.execute("PRAGMA foreign_keys = ON")
        self._create_tables()
        self._seed_defaults()

    def _create_tables(self):
        """Create all required tables if they do not exist."""
        cursor = self.connection.cursor()

        # Categories table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                name        TEXT NOT NULL UNIQUE,
                icon        TEXT DEFAULT '📁',
                color       TEXT DEFAULT '#3B82F6',
                created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Tasks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                title       TEXT NOT NULL,
                description TEXT DEFAULT '',
                priority    TEXT CHECK(priority IN ('Low', 'Medium', 'High')) DEFAULT 'Medium',
                category_id INTEGER REFERENCES categories(id) ON DELETE SET NULL,
                due_date    TEXT,
                due_time    TEXT,
                completed   INTEGER DEFAULT 0,
                created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Settings table (key-value store)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key   TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)

        self.connection.commit()

    def _seed_defaults(self):
        """Insert default categories and settings on first run."""
        cursor = self.connection.cursor()

        # Default categories (only if table is empty)
        cursor.execute("SELECT COUNT(*) FROM categories")
        if cursor.fetchone()[0] == 0:
            defaults = [
                ("Work", "💼", "#3B82F6"),
                ("Study", "📚", "#8B5CF6"),
                ("Fitness", "💪", "#22C55E"),
                ("Grocery", "🛒", "#F59E0B"),
                ("Side Project", "🚀", "#EF4444"),
                ("University", "🎓", "#6366F1"),
            ]
            cursor.executemany(
                "INSERT INTO categories (name, icon, color) VALUES (?, ?, ?)",
                defaults,
            )

        # Default settings (only if table is empty)
        cursor.execute("SELECT COUNT(*) FROM settings")
        if cursor.fetchone()[0] == 0:
            default_settings = [
                ("theme", "dark"),
                ("username", ""),  # Empty means first launch
            ]
            cursor.executemany(
                "INSERT INTO settings (key, value) VALUES (?, ?)",
                default_settings,
            )

        self.connection.commit()

    # ── Generic query methods ──────────────────────────────────────────

    def execute(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        """
        Execute a write query (INSERT, UPDATE, DELETE).

        Args:
            query:  SQL query string with ? placeholders.
            params: Tuple of parameter values.

        Returns:
            The cursor after execution.
        """
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        self.connection.commit()
        return cursor

    def fetch_one(self, query: str, params: tuple = ()) -> sqlite3.Row | None:
        """
        Execute a query and return a single row.

        Args:
            query:  SQL query string.
            params: Tuple of parameter values.

        Returns:
            A single Row or None.
        """
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        return cursor.fetchone()

    def fetch_all(self, query: str, params: tuple = ()) -> list[sqlite3.Row]:
        """
        Execute a query and return all matching rows.

        Args:
            query:  SQL query string.
            params: Tuple of parameter values.

        Returns:
            List of Row objects.
        """
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()

    def close(self):
        """Close the database connection."""
        if self.connection:
            self.connection.close()
