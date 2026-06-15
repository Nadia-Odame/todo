"""
dashboard_view.py — The home dashboard view for the Focus app.

Displays greeting, search bar, horizontally scrollable category cards,
and today's/upcoming tasks. Matches the 'Task Dashboard' layout.
"""

import customtkinter as ctk
from datetime import datetime
from ui.theme import FONTS, PADDING, RADIUS
from ui.components.search_bar import SearchBar
from ui.components.category_card import CategoryCard
from ui.components.task_card import TaskCard
from ui.components.dialogs import EditTaskDialog, ConfirmDialog


class DashboardView(ctk.CTkFrame):
    """The landing dashboard view showing stats summary, categories, and tasks."""

    def __init__(self, master, app, colors, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.app = app
        self.colors = colors
        self.task_ctrl = app.task_ctrl
        self.category_ctrl = app.category_ctrl

        self._build()

    def _build(self):
        colors = self.colors

        # Configure layout: left/right scrollable content
        self.grid_columnconfigure(0, weight=3)  # Main left column
        self.grid_rowconfigure(0, weight=1)

        # Scrollable container for main dashboard elements
        scroll_canvas = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll_canvas.grid(row=0, column=0, sticky="nsew")

        # ── Greeting and Header ────────────────────────────────────
        username = self.app.settings_ctrl.get_username() or "Alex"
        today_str = datetime.now().strftime("%B %d, %Y")

        header_frame = ctk.CTkFrame(scroll_canvas, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, PADDING["md"]))

        # Greeting sub-frame for user name and edit button
        greet_subframe = ctk.CTkFrame(header_frame, fg_color="transparent")
        greet_subframe.pack(side="left")

        greeting_label = ctk.CTkLabel(
            greet_subframe,
            text=f"Hello, {username}!",
            font=FONTS["heading_lg"],
            text_color=colors["text_primary"],
            anchor="w",
        )
        greeting_label.pack(side="left")

        edit_name_btn = ctk.CTkButton(
            greet_subframe,
            text="✏️",
            font=("Segoe UI", 11),
            width=24,
            height=24,
            fg_color="transparent",
            hover_color=colors["bg_hover"],
            corner_radius=RADIUS["sm"],
            text_color=colors["text_secondary"],
            command=self._on_edit_name_click,
        )
        edit_name_btn.pack(side="left", padx=PADDING["xs"])

        # Date sub-frame for date and theme switch
        date_subframe = ctk.CTkFrame(header_frame, fg_color="transparent")
        date_subframe.pack(side="right")

        date_label = ctk.CTkLabel(
            date_subframe,
            text=today_str.upper(),
            font=FONTS["caption_bold"],
            text_color=colors["accent_orange"],
            anchor="e",
        )
        date_label.pack(side="left", padx=(0, PADDING["sm"]))

        theme_icon = "☀️" if self.app.theme_mode == "dark" else "🌙"
        theme_toggle_btn = ctk.CTkButton(
            date_subframe,
            text=theme_icon,
            font=("Segoe UI", 14),
            width=30,
            height=30,
            fg_color=colors["bg_secondary"],
            hover_color=colors["bg_hover"],
            border_width=1,
            border_color=colors["border"],
            corner_radius=RADIUS["round"],
            text_color=colors["text_primary"],
            command=self._on_toggle_theme_click,
        )
        theme_toggle_btn.pack(side="right")

        # Subtitle message
        today_tasks = self.task_ctrl.get_today_tasks()
        pending_today = sum(1 for t in today_tasks if not t.completed)
        subtitle_label = ctk.CTkLabel(
            scroll_canvas,
            text=f"You have {pending_today} tasks to complete today." if pending_today > 0 else "All caught up for today!",
            font=FONTS["body"],
            text_color=colors["text_secondary"],
            anchor="w",
        )
        subtitle_label.pack(fill="x", pady=(0, PADDING["md"]))

        # ── Search Bar ─────────────────────────────────────────────
        search_bar = SearchBar(scroll_canvas, colors, on_search=self._on_search_submit)
        search_bar.pack(fill="x", pady=(0, PADDING["lg"]))

        # ── AI Prioritization Tip / Suggestion ──────────────────────
        self._build_ai_tip(scroll_canvas)

        # ── Categories Section ─────────────────────────────────────
        cat_header_frame = ctk.CTkFrame(scroll_canvas, fg_color="transparent")
        cat_header_frame.pack(fill="x", pady=(PADDING["sm"], PADDING["xs"]))

        ctk.CTkLabel(
            cat_header_frame,
            text="Categories",
            font=FONTS["heading"],
            text_color=colors["text_primary"],
        )  # Left packed
        cat_header_frame.winfo_children()[0].pack(side="left")

        view_all_cat_btn = ctk.CTkButton(
            cat_header_frame,
            text="VIEW ALL",
            font=FONTS["caption_bold"],
            text_color=colors["accent_blue"],
            fg_color="transparent",
            hover_color=colors["bg_secondary"],
            width=60,
            command=lambda: self.app.navigate_to("categories"),
        )
        view_all_cat_btn.pack(side="right")

        # Horizontal scroll container for categories
        # CustomTkinter does not have a horizontal-only scroll widget natively,
        # but we can pack them side-by-side inside a frame in a row grid.
        cat_scroll = ctk.CTkScrollableFrame(scroll_canvas, height=110, orientation="horizontal", fg_color="transparent")
        cat_scroll.pack(fill="x", pady=(0, PADDING["lg"]))

        categories = self.category_ctrl.get_categories_with_counts()
        for idx, cat in enumerate(categories):
            ccard = CategoryCard(
                cat_scroll,
                cat,
                colors,
                on_click=self._on_category_click,
                compact=True,
            )
            ccard.grid(row=0, column=idx, padx=PADDING["xs"])

        # ── Today's Tasks Section ──────────────────────────────────
        ctk.CTkLabel(
            scroll_canvas,
            text="Today's Tasks",
            font=FONTS["heading"],
            text_color=colors["text_primary"],
            anchor="w",
        ).pack(fill="x", pady=(PADDING["sm"], PADDING["xs"]))

        today_list_frame = ctk.CTkFrame(scroll_canvas, fg_color="transparent")
        today_list_frame.pack(fill="x", pady=(0, PADDING["lg"]))

        if not today_tasks:
            ctk.CTkLabel(
                today_list_frame,
                text="No tasks for today. Click '+' to add one!",
                font=FONTS["body"],
                text_color=colors["text_tertiary"],
            ).pack(pady=PADDING["lg"])
        else:
            for task in today_tasks:
                tcard = TaskCard(
                    today_list_frame,
                    task,
                    colors,
                    on_toggle=self._toggle_task,
                    on_edit=self._edit_task,
                    on_delete=self._delete_task,
                )
                tcard.pack(fill="x", pady=4)

        # ── Upcoming Tasks Section ─────────────────────────────────
        ctk.CTkLabel(
            scroll_canvas,
            text="Upcoming Tasks (Next 7 Days)",
            font=FONTS["heading"],
            text_color=colors["text_primary"],
            anchor="w",
        ).pack(fill="x", pady=(PADDING["sm"], PADDING["xs"]))

        upcoming_list_frame = ctk.CTkFrame(scroll_canvas, fg_color="transparent")
        upcoming_list_frame.pack(fill="x", pady=(0, PADDING["lg"]))

        upcoming_tasks = self.task_ctrl.get_upcoming_tasks(days=7)
        if not upcoming_tasks:
            ctk.CTkLabel(
                upcoming_list_frame,
                text="No upcoming tasks this week.",
                font=FONTS["body"],
                text_color=colors["text_tertiary"],
            ).pack(pady=PADDING["lg"])
        else:
            for task in upcoming_tasks:
                tcard = TaskCard(
                    upcoming_list_frame,
                    task,
                    colors,
                    on_toggle=self._toggle_task,
                    on_edit=self._edit_task,
                    on_delete=self._delete_task,
                )
                tcard.pack(fill="x", pady=4)

        # ── Floating Add Task Button ────────────────────────────────
        add_btn = ctk.CTkButton(
            self,
            text="+",
            font=("Segoe UI", 24, "bold"),
            width=56,
            height=56,
            corner_radius=28,
            fg_color=colors["accent_orange"],
            hover_color="#D97706",
            text_color=colors["text_on_accent"],
            command=self._add_task,
        )
        add_btn.place(relx=0.84, rely=0.85, anchor="center")

    def _build_ai_tip(self, master):
        """Generates a contextual AI-based task tip card."""
        colors = self.colors
        all_tasks = self.task_ctrl.get_all_tasks()
        pending_high = [t for t in all_tasks if not t.completed and t.priority == "High"]

        # Simple heuristic rule engine to act as the "AI Productivity Coach"
        if pending_high:
            tip_msg = f"💡 AI Suggestion: Focus on '{pending_high[0].title}' first today. It's marked as HIGH priority."
        elif len(all_tasks) - sum(1 for t in all_tasks if t.completed) > 5:
            tip_msg = "💡 AI Suggestion: You have quite a few pending items. Try the Pomodoro method (25m work, 5m break)!"
        else:
            tip_msg = "💡 AI Suggestion: Clean list! Today is a great day to organize your upcoming 'Side Project' folder."

        tip_card = ctk.CTkFrame(
            master,
            fg_color=colors["purple"],
            border_color=colors["purple"],
            border_width=1,
            corner_radius=RADIUS["md"],
        )
        tip_card.pack(fill="x", pady=(0, PADDING["md"]))

        tip_label = ctk.CTkLabel(
            tip_card,
            text=tip_msg,
            font=FONTS["caption_bold"],
            text_color="#FFFFFF",
            padx=12,
            pady=8,
            anchor="w",
            wraplength=330,
        )
        tip_label.pack(fill="x")

    def _on_search_submit(self, query):
        """Redirects to the Tasks page and fills search query."""
        if query:
            self.app.navigate_to("tasks")
            # Populate search bar in TasksView automatically
            if isinstance(self.app.current_view, TasksView):
                self.app.current_view.search_bar.entry.insert(0, query)
                self.app.current_view._filter_tasks()

    def _on_category_click(self, category):
        """Switch to tasks page filtered by category."""
        self.app.navigate_to("tasks")
        if isinstance(self.app.current_view, TasksView):
            self.app.current_view.category_filter_var.set(category.name)
            self.app.current_view._filter_tasks()

    def _toggle_task(self, task_id):
        self.task_ctrl.toggle_complete(task_id)
        self.app.reload_current_view()

    def _edit_task(self, task):
        categories = self.category_ctrl.get_all_categories()
        EditTaskDialog(
            self.app,
            self.colors,
            task,
            categories,
            on_save=lambda tid, d: [self.task_ctrl.update_task(tid, **d), self.app.reload_current_view()]
        )

    def _delete_task(self, task_id):
        ConfirmDialog(
            self.app,
            self.colors,
            title_text="Delete Task",
            message="Are you sure you want to delete this task permanently?",
            on_confirm=lambda: [self.task_ctrl.delete_task(task_id), self.app.reload_current_view()]
        )

    def _add_task(self):
        # Auto prefill date to today
        today = datetime.now().strftime("%Y-%m-%d")
        self.app.show_add_task_dialog(default_date=today)

    def _on_edit_name_click(self):
        """Prompt to change display name."""
        dialog = ctk.CTkInputDialog(
            title="Edit Name",
            text="Update your display name:",
        )
        dialog.geometry("+450+300")
        new_name = dialog.get_input()
        if new_name and new_name.strip():
            self.app.settings_ctrl.set_username(new_name.strip())
            self.app.reload_current_view()

    def _on_toggle_theme_click(self):
        """Toggle app theme dark/light."""
        new_mode = "light" if self.app.theme_mode == "dark" else "dark"
        self.app.update_theme(new_mode)
