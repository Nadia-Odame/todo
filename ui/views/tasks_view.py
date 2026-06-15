"""
tasks_view.py — The task list and filter panel view.

Provides comprehensive task browsing with live title search,
category dropdown filters, priority tags, and completion state toggles.
"""

import customtkinter as ctk
from ui.theme import FONTS, PADDING, RADIUS
from ui.components.search_bar import SearchBar
from ui.components.task_card import TaskCard
from ui.components.dialogs import EditTaskDialog, ConfirmDialog


class TasksView(ctk.CTkFrame):
    """The central task management board view with search/filters."""

    def __init__(self, master, app, colors, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.app = app
        self.colors = colors
        self.task_ctrl = app.task_ctrl
        self.category_ctrl = app.category_ctrl

        self._build()

    def _build(self):
        colors = self.colors

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)  # Tasks list row expands

        # ── Row 0: Header + Search (Stacked for mobile layout) ─────
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, PADDING["md"]))
        header_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header_frame,
            text="All Tasks",
            font=FONTS["heading_lg"],
            text_color=colors["text_primary"],
            anchor="w",
        ).grid(row=0, column=0, sticky="w", pady=(0, PADDING["xs"]))

        self.search_bar = SearchBar(
            header_frame,
            colors,
            placeholder="Search tasks by title...",
            on_search=self._on_search_change,
        )
        self.search_bar.grid(row=1, column=0, sticky="ew")

        # ── Row 1: Filter bar (Grid/stacked layout) ───────────────
        filters_frame = ctk.CTkFrame(self, fg_color="transparent")
        filters_frame.grid(row=1, column=0, sticky="ew", pady=(0, PADDING["md"]))
        filters_frame.grid_columnconfigure(0, weight=1)
        filters_frame.grid_columnconfigure(1, weight=1)

        # Category dropdown (occupies full top row)
        categories = self.category_ctrl.get_all_categories()
        cat_names = ["All Categories"] + [c.name for c in categories]
        self.category_filter_var = ctk.StringVar(value="All Categories")
        self.cat_filter_menu = ctk.CTkOptionMenu(
            filters_frame,
            variable=self.category_filter_var,
            values=cat_names,
            font=FONTS["body"],
            height=34,
            corner_radius=RADIUS["sm"],
            fg_color=colors["bg_secondary"],
            button_color=colors["accent_blue"],
            button_hover_color=colors["accent_blue_hover"],
            text_color=colors["text_primary"],
            dropdown_fg_color=colors["bg_secondary"],
            dropdown_text_color=colors["text_primary"],
            dropdown_hover_color=colors["bg_hover"],
            command=lambda v: self._filter_tasks(),
        )
        self.cat_filter_menu.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, PADDING["xs"]))

        # Priority filter (bottom-left)
        self.priority_filter_var = ctk.StringVar(value="All Priorities")
        self.pri_filter_menu = ctk.CTkOptionMenu(
            filters_frame,
            variable=self.priority_filter_var,
            values=["All Priorities", "Low", "Medium", "High"],
            font=FONTS["body"],
            height=34,
            corner_radius=RADIUS["sm"],
            fg_color=colors["bg_secondary"],
            button_color=colors["accent_blue"],
            button_hover_color=colors["accent_blue_hover"],
            text_color=colors["text_primary"],
            dropdown_fg_color=colors["bg_secondary"],
            dropdown_text_color=colors["text_primary"],
            dropdown_hover_color=colors["bg_hover"],
            command=lambda v: self._filter_tasks(),
        )
        self.pri_filter_menu.grid(row=1, column=0, sticky="ew", padx=(0, PADDING["xs"]))

        # Status filter (bottom-center)
        self.status_filter_var = ctk.StringVar(value="All Statuses")
        self.status_filter_menu = ctk.CTkOptionMenu(
            filters_frame,
            variable=self.status_filter_var,
            values=["All Statuses", "Pending", "Completed"],
            font=FONTS["body"],
            height=34,
            corner_radius=RADIUS["sm"],
            fg_color=colors["bg_secondary"],
            button_color=colors["accent_blue"],
            button_hover_color=colors["accent_blue_hover"],
            text_color=colors["text_primary"],
            dropdown_fg_color=colors["bg_secondary"],
            dropdown_text_color=colors["text_primary"],
            dropdown_hover_color=colors["bg_hover"],
            command=lambda v: self._filter_tasks(),
        )
        self.status_filter_menu.grid(row=1, column=1, sticky="ew", padx=(PADDING["xs"], 0))

        # Clear button (placed cleanly below)
        self.reset_btn = ctk.CTkButton(
            filters_frame,
            text="Clear Filters",
            font=FONTS["caption_bold"],
            text_color=colors["text_secondary"],
            fg_color="transparent",
            hover_color=colors["bg_hover"],
            height=28,
            corner_radius=RADIUS["sm"],
            command=self._clear_filters,
        )
        self.reset_btn.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(PADDING["xs"], 0))

        # ── Row 2: Scrollable task list ──────────────────────────
        self.list_container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.list_container.grid(row=2, column=0, sticky="nsew")

        # Populate tasks list initially
        self._filter_tasks()

        # ── Floating Add Button ────────────────────────────────────
        self.add_btn = ctk.CTkButton(
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
        self.add_btn.place(relx=0.84, rely=0.85, anchor="center")

    def _filter_tasks(self):
        """Perform search/filter from inputs and redraw the task list."""
        # Clear existing card widgets
        for child in self.list_container.winfo_children():
            child.destroy()

        # Gather inputs
        query = self.search_bar.get_query().strip()

        cat_val = self.category_filter_var.get()
        cat_id = None
        if cat_val != "All Categories":
            for c in self.category_ctrl.get_all_categories():
                if c.name == cat_val:
                    cat_id = c.id
                    break

        pri_val = self.priority_filter_var.get()
        priority = None if pri_val == "All Priorities" else pri_val

        stat_val = self.status_filter_var.get()
        status = None
        if stat_val == "Completed":
            status = "completed"
        elif stat_val == "Pending":
            status = "pending"

        # Query database
        tasks = self.task_ctrl.search_tasks(
            query=query, category_id=cat_id, priority=priority, status=status
        )

        # Draw list
        if not tasks:
            ctk.CTkLabel(
                self.list_container,
                text="No tasks match your filters.",
                font=FONTS["body"],
                text_color=self.colors["text_tertiary"],
            ).pack(pady=PADDING["xxl"])
        else:
            for task in tasks:
                tcard = TaskCard(
                    self.list_container,
                    task,
                    self.colors,
                    on_toggle=self._toggle_task,
                    on_edit=self._edit_task,
                    on_delete=self._delete_task,
                )
                tcard.pack(fill="x", pady=4)

    def _on_search_change(self, query):
        """Live search text change trigger."""
        self._filter_tasks()

    def _clear_filters(self):
        """Reset all filtering states."""
        self.search_bar.clear()
        self.category_filter_var.set("All Categories")
        self.priority_filter_var.set("All Priorities")
        self.status_filter_var.set("All Statuses")
        self._filter_tasks()

    def _toggle_task(self, task_id):
        self.task_ctrl.toggle_complete(task_id)
        self._filter_tasks()

    def _edit_task(self, task):
        categories = self.category_ctrl.get_all_categories()
        EditTaskDialog(
            self.app,
            self.colors,
            task,
            categories,
            on_save=lambda tid, d: [self.task_ctrl.update_task(tid, **d), self._filter_tasks()]
        )

    def _delete_task(self, task_id):
        ConfirmDialog(
            self.app,
            self.colors,
            title_text="Delete Task",
            message="Are you sure you want to delete this task permanently?",
            on_confirm=lambda: [self.task_ctrl.delete_task(task_id), self._filter_tasks()]
        )

    def _add_task(self):
        self.app.show_add_task_dialog(on_task_added=self._filter_tasks)
