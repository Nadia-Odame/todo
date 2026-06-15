"""
main.py — The entry point for the Focus To-Do List desktop application.

Initializes the database, loads preferences, starts the controllers,
and runs the CustomTkinter UI loop.
"""

from database import Database
from controllers.task_controller import TaskController
from controllers.category_controller import CategoryController
from controllers.settings_controller import SettingsController
from ui.app import App


def main():
    """Main launch sequence for the application."""
    # ── Database Initialization ────────────────────────────────────
    # SQLite connection is created and database tables are auto-seeded
    db = Database()

    # ── Controllers Setup ──────────────────────────────────────────
    settings_ctrl = SettingsController(db)
    task_ctrl = TaskController(db)
    category_ctrl = CategoryController(db)

    # ── Application Boot ───────────────────────────────────────────
    app = App(
        db=db,
        task_controller=task_ctrl,
        category_controller=category_ctrl,
        settings_controller=settings_ctrl,
    )

    try:
        # Start UI event loop
        app.mainloop()
    finally:
        # Guarantee database connection closes safely when the app is shut down
        db.close()


if __name__ == "__main__":
    main()
