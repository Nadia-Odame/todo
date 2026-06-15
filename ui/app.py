"""
app.py — The main application shell for the Focus To-Do application.

Coordinates view switching, top-level layouts, controllers, and dialogs.
"""

import customtkinter as ctk
from ui.theme import get_colors, PADDING, RADIUS, SIDEBAR_WIDTH
from ui.components.nav_bar import NavBar
from ui.components.dialogs import WelcomeDialog, AddTaskDialog

# Import views
from ui.views.dashboard_view import DashboardView
from ui.views.tasks_view import TasksView
from ui.views.categories_view import CategoriesView
from ui.views.calendar_view import CalendarView
from ui.views.stats_view import StatsView
from ui.views.settings_view import SettingsView

import threading
import time
from plyer import notification


class App(ctk.CTk):
    """The root window and navigation hub of the Focus application."""

    def __init__(self, db, task_controller, category_controller, settings_controller):
        super().__init__()

        self.db = db
        self.task_ctrl = task_controller
        self.category_ctrl = category_controller
        self.settings_ctrl = settings_controller

        # Load preferences
        self.theme_mode = self.settings_ctrl.get_theme()
        ctk.set_appearance_mode(self.theme_mode)
        ctk.set_default_color_theme("blue")

        self.colors = get_colors(self.theme_mode)

        # Configure window (Mobile Simulator Dimensions)
        self.title("Focus")
        self.geometry("395x760")
        self.resizable(False, False)
        self.configure(fg_color=self.colors["bg_primary"])

        # State
        self.current_view_id = "dashboard"
        self.current_view = None

        # Build UI Shell
        self._build_layout()

        # Check for first launch name request
        self.after(200, self._check_first_launch)

        # Start background reminder thread
        self.reminder_stop_event = threading.Event()
        self.reminder_thread = threading.Thread(target=self._reminder_loop, daemon=True)
        self.reminder_thread.start()

        # Handle window close
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_layout(self):
        """Construct the main content and mobile bottom navigation layout."""
        # ── Main Content Container ─────────────────────────────────
        self.content_container = ctk.CTkFrame(self, fg_color="transparent")
        self.content_container.pack(fill="both", expand=True, padx=PADDING["md"], pady=(PADDING["md"], PADDING["xs"]))

        # ── Bottom Navigation Bar Container ────────────────────────
        self.nav_container = ctk.CTkFrame(self, fg_color="transparent")
        self.nav_container.pack(side="bottom", fill="x")

        # Docked NavBar (fills bottom edge completely)
        self.nav_bar = NavBar(self.nav_container, self.colors, on_navigate=self.navigate_to)
        self.nav_bar.pack(fill="x", expand=True)

        # Display default view
        self.navigate_to("dashboard")

    def navigate_to(self, view_id: str):
        """
        Switch the main content frame to a different view.

        Args:
            view_id: The ID of the view to switch to (e.g., 'dashboard', 'tasks').
        """
        # Destroy current view if it exists
        if self.current_view:
            self.current_view.destroy()

        self.current_view_id = view_id
        self.nav_bar.set_active(view_id)

        # Instantiate new view
        if view_id == "dashboard":
            self.current_view = DashboardView(self.content_container, self, self.colors)
        elif view_id == "tasks":
            self.current_view = TasksView(self.content_container, self, self.colors)
        elif view_id == "categories":
            self.current_view = CategoriesView(self.content_container, self, self.colors)
        elif view_id == "calendar":
            self.current_view = CalendarView(self.content_container, self, self.colors)
        elif view_id == "stats":
            self.current_view = StatsView(self.content_container, self, self.colors)
        elif view_id == "settings":
            self.current_view = SettingsView(self.content_container, self, self.colors)

        if self.current_view:
            self.current_view.pack(fill="both", expand=True)

    def reload_current_view(self):
        """Redraws the current view to display updated data."""
        self.navigate_to(self.current_view_id)

    def _check_first_launch(self):
        """Checks if this is the first launch and asks for user's name."""
        if self.settings_ctrl.is_first_launch():
            WelcomeDialog(
                self,
                self.colors,
                on_save=self._save_first_launch_name
            )

    def _save_first_launch_name(self, name: str):
        """Saves the user's name and reloads the dashboard greeting."""
        self.settings_ctrl.set_username(name)
        self.reload_current_view()

    def update_theme(self, new_mode: str):
        """
        Updates the theme throughout the application.

        Args:
            new_mode: 'dark' or 'light'.
        """
        self.theme_mode = new_mode
        self.settings_ctrl.set_theme(new_mode)
        ctk.set_appearance_mode(new_mode)
        self.colors = get_colors(new_mode)

        # Update root and navbar colors
        self.configure(fg_color=self.colors["bg_primary"])
        self.nav_bar.update_colors(self.colors)

        # Reload current view with the new theme
        self.reload_current_view()

    def show_add_task_dialog(self, default_date=None, on_task_added=None):
        """Opens the Add Task dialog modal."""
        categories = self.category_ctrl.get_all_categories()

        def handle_save(data):
            self.task_ctrl.create_task(
                title=data["title"],
                priority=data["priority"],
                category_id=data["category_id"],
                due_date=data["due_date"],
                due_time=data["due_time"],
                description=data["description"],
            )
            # Notification trigger / refresh
            self.reload_current_view()
            if on_task_added:
                on_task_added()

        AddTaskDialog(
            self,
            self.colors,
            categories,
            on_save=handle_save,
            default_date=default_date
        )

    def _reminder_loop(self):
        """Background loop that polls database for upcoming task reminders."""
        # Simple task due warning system
        notified_tasks = set()
        while not self.reminder_stop_event.is_set():
            try:
                # Find tasks due in the next 30 minutes
                upcoming = self.task_ctrl.get_tasks_with_reminders(minutes=30)
                for task in upcoming:
                    if task.id not in notified_tasks:
                        # Send OS-level notification
                        notification.notify(
                            title="Task Reminder — Focus",
                            message=f"Task '{task.title}' is due at {task.due_time or 'soon'}!",
                            app_name="Focus",
                            timeout=10,
                        )
                        notified_tasks.add(task.id)
            except Exception as e:
                print(f"Error in reminders background thread: {e}")

            # Sleep 60 seconds
            for _ in range(60):
                if self.reminder_stop_event.is_set():
                    break
                time.sleep(1)

    def _on_close(self):
        """Hook called when window is closed, ensuring background threads stop cleanly."""
        self.reminder_stop_event.set()
        self.destroy()
