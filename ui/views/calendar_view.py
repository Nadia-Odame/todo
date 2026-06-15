"""
calendar_view.py — The calendar-based task planner view.

Uses the approved `tkcalendar` library to present a month calendar.
Displays tasks scheduled for the selected calendar date below the calendar.
"""

import customtkinter as ctk
from tkcalendar import Calendar
from datetime import datetime
from ui.theme import FONTS, PADDING, RADIUS
from ui.components.task_card import TaskCard
from ui.components.dialogs import EditTaskDialog, ConfirmDialog


class CalendarView(ctk.CTkFrame):
    """View containing the month calendar and corresponding daily schedules."""

    def __init__(self, master, app, colors, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.app = app
        self.colors = colors
        self.task_ctrl = app.task_ctrl

        self._build()

    def _build(self):
        colors = self.colors

        # Split into left/right side or top/bottom layout.
        # Top/bottom fits best to display the calendar clearly and still have space for list.
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)  # Tasks section expands

        # ── Calendar Widget Container ──────────────────────────────
        cal_container = ctk.CTkFrame(
            self,
            fg_color=colors["bg_secondary"],
            corner_radius=RADIUS["lg"],
            border_width=1,
            border_color=colors["border"],
        )
        cal_container.grid(row=0, column=0, sticky="ew", pady=(0, PADDING["md"]), padx=2)

        # Style options for Calendar
        # tkcalendar Calendar is a tkinter widget, so we theme it using standard styling keywords.
        today = datetime.now()
        self.calendar = Calendar(
            cal_container,
            selectmode="day",
            year=today.year,
            month=today.month,
            day=today.day,
            background=colors["bg_secondary"],
            foreground=colors["text_primary"],
            headersbackground=colors["bg_tertiary"],
            headersforeground=colors["text_primary"],
            selectbackground=colors["accent_blue"],
            selectforeground=colors["text_on_accent"],
            normalbackground=colors["bg_secondary"],
            normalforeground=colors["text_primary"],
            weekendbackground=colors["bg_secondary"],
            weekendforeground=colors["text_secondary"],
            othermonthbackground=colors["bg_primary"],
            othermonthforeground=colors["text_tertiary"],
            othermonthwebackground=colors["bg_primary"],
            othermonthweforeground=colors["text_tertiary"],
            font=("Segoe UI", 11),
            bd=0,
            borderwidth=0,
        )
        self.calendar.pack(fill="x", expand=True, padx=PADDING["md"], pady=PADDING["md"])

        # Listen to selection changes
        self.calendar.bind("<<CalendarSelected>>", self._on_date_changed)

        # ── Row 1: Schedule Header ─────────────────────────────────
        schedule_header = ctk.CTkFrame(self, fg_color="transparent")
        schedule_header.grid(row=1, column=0, sticky="nsew")
        schedule_header.grid_columnconfigure(0, weight=1)
        schedule_header.grid_rowconfigure(1, weight=1)

        header_row = ctk.CTkFrame(schedule_header, fg_color="transparent")
        header_row.grid(row=0, column=0, sticky="ew", pady=(PADDING["sm"], PADDING["xs"]))

        self.schedule_title = ctk.CTkLabel(
            header_row,
            text="Schedule",
            font=FONTS["heading"],
            text_color=colors["text_primary"],
        )
        self.schedule_title.pack(side="left")

        # Add task button for this specific date
        add_btn = ctk.CTkButton(
            header_row,
            text="+ Add Task",
            font=FONTS["body_bold"],
            fg_color=colors["accent_blue"],
            hover_color=colors["accent_blue_hover"],
            text_color=colors["text_on_accent"],
            corner_radius=RADIUS["md"],
            height=30,
            command=self._on_add_task_click,
        )
        add_btn.pack(side="right")

        # Scrollable area for selected date's tasks
        self.tasks_container = ctk.CTkScrollableFrame(schedule_header, fg_color="transparent")
        self.tasks_container.grid(row=1, column=0, sticky="nsew")

        # Initial loading
        self._load_selected_date_tasks()

    def _on_date_changed(self, event=None):
        """Update view when a different date is clicked on calendar."""
        self._load_selected_date_tasks()

    def _get_selected_date_str(self) -> str:
        """Convert Calendar date string (MM/DD/YY or similar depending on locale) to ISO YYYY-MM-DD."""
        # tkcalendar returns datetime.date object from selection using selection_get()
        date_obj = self.calendar.selection_get()
        return date_obj.strftime("%Y-%m-%d")

    def _load_selected_date_tasks(self):
        """Fetch and render tasks for the currently highlighted calendar date."""
        for child in self.tasks_container.winfo_children():
            child.destroy()

        date_str = self._get_selected_date_str()
        readable_date = datetime.strptime(date_str, "%Y-%m-%d").strftime("%A, %b %d")
        self.schedule_title.configure(text=f"Schedule — {readable_date}")

        tasks = self.task_ctrl.get_tasks_by_date(date_str)

        if not tasks:
            ctk.CTkLabel(
                self.tasks_container,
                text="No tasks scheduled for this day.",
                font=FONTS["body"],
                text_color=self.colors["text_tertiary"],
            ).pack(pady=PADDING["lg"])
        else:
            for task in tasks:
                tcard = TaskCard(
                    self.tasks_container,
                    task,
                    self.colors,
                    on_toggle=self._toggle_task,
                    on_edit=self._edit_task,
                    on_delete=self._delete_task,
                )
                tcard.pack(fill="x", pady=4)

    def _on_add_task_click(self):
        """Open task dialog preset to the highlighted calendar date."""
        date_str = self._get_selected_date_str()
        self.app.show_add_task_dialog(default_date=date_str, on_task_added=self._load_selected_date_tasks)

    def _toggle_task(self, task_id):
        self.task_ctrl.toggle_complete(task_id)
        self._load_selected_date_tasks()

    def _edit_task(self, task):
        categories = self.app.category_ctrl.get_all_categories()
        EditTaskDialog(
            self.app,
            self.colors,
            task,
            categories,
            on_save=lambda tid, d: [self.task_ctrl.update_task(tid, **d), self._load_selected_date_tasks()]
        )

    def _delete_task(self, task_id):
        ConfirmDialog(
            self.app,
            self.colors,
            title_text="Delete Task",
            message="Are you sure you want to delete this task permanently?",
            on_confirm=lambda: [self.task_ctrl.delete_task(task_id), self._load_selected_date_tasks()]
        )
