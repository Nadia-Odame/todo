"""
task_card.py — Reusable task card widget.

Displays a single task as a styled card with checkbox, priority badge,
category tag, due time, and action buttons.
"""

import customtkinter as ctk
from ui.theme import get_colors, FONTS, PADDING, RADIUS, PRIORITY_COLORS


class TaskCard(ctk.CTkFrame):
    """
    A card widget representing a single task.

    Args:
        master:        Parent widget.
        task:          Task model object.
        colors:        Color dictionary from theme.
        on_toggle:     Callback when checkbox is clicked — fn(task_id).
        on_edit:       Callback when edit button is clicked — fn(task).
        on_delete:     Callback when delete button is clicked — fn(task_id).
    """

    def __init__(
        self,
        master,
        task,
        colors: dict,
        on_toggle=None,
        on_edit=None,
        on_delete=None,
        **kwargs,
    ):
        super().__init__(
            master,
            fg_color=colors["bg_secondary"],
            corner_radius=RADIUS["md"],
            border_width=1,
            border_color=colors["border"],
            **kwargs,
        )
        self.task = task
        self.colors = colors
        self.on_toggle = on_toggle
        self.on_edit = on_edit
        self.on_delete = on_delete

        self._build()
        self._bind_hover_recursively(self)

    def _bind_hover_recursively(self, widget):
        """Recursively binds mouse hover to the widget and all its children."""
        widget.bind("<Enter>", lambda e: self._on_hover_enter())
        widget.bind("<Leave>", lambda e: self._on_hover_leave())
        for child in widget.winfo_children():
            # Don't bind hover on checkboxes and action buttons because they have their own hover states
            if not isinstance(child, (ctk.CTkCheckBox, ctk.CTkButton)):
                self._bind_hover_recursively(child)

    def _on_hover_enter(self):
        """Highlight background on hover."""
        self.configure(fg_color=self.colors["bg_hover"])

    def _on_hover_leave(self):
        """Revert background when mouse leaves."""
        self.configure(fg_color=self.colors["bg_secondary"])

    def _build(self):
        """Construct the card layout."""
        colors = self.colors
        task = self.task

        # Configure grid: checkbox | content | actions
        self.grid_columnconfigure(1, weight=1)

        # ── Priority accent bar (left edge) ────────────────────────
        priority_color_key = PRIORITY_COLORS.get(task.priority, "priority_medium")
        priority_color = colors[priority_color_key]

        accent_bar = ctk.CTkFrame(
            self,
            width=4,
            height=50,
            fg_color=priority_color,
            corner_radius=2,
        )
        accent_bar.grid(row=0, column=0, rowspan=2, sticky="ns", padx=(PADDING["sm"], 0), pady=PADDING["sm"])

        # ── Checkbox ───────────────────────────────────────────────
        self.check_var = ctk.BooleanVar(value=task.completed)
        checkbox = ctk.CTkCheckBox(
            self,
            text="",
            variable=self.check_var,
            command=self._on_toggle_click,
            width=24,
            height=24,
            checkbox_width=22,
            checkbox_height=22,
            corner_radius=6,
            border_width=2,
            fg_color=colors["accent_blue"],
            hover_color=colors["accent_blue_hover"],
            border_color=colors["border_light"],
            checkmark_color=colors["text_on_accent"],
        )
        checkbox.grid(row=0, column=1, rowspan=2, sticky="w", padx=(PADDING["sm"], PADDING["sm"]), pady=PADDING["sm"])

        # ── Content area ───────────────────────────────────────────
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.grid(row=0, column=2, sticky="ew", padx=0, pady=(PADDING["sm"], 0))
        content_frame.grid_columnconfigure(0, weight=1)

        # Title (with strikethrough effect for completed tasks)
        title_color = colors["text_tertiary"] if task.completed else colors["text_primary"]
        title_text = task.title
        title_label = ctk.CTkLabel(
            content_frame,
            text=title_text,
            font=FONTS["body_bold"],
            text_color=title_color,
            anchor="w",
        )
        title_label.grid(row=0, column=0, sticky="w")

        # ── Tags row (priority + category + time) ─────────────────
        tags_frame = ctk.CTkFrame(self, fg_color="transparent")
        tags_frame.grid(row=1, column=2, sticky="ew", padx=0, pady=(0, PADDING["sm"]))

        # Priority badge
        priority_badge = ctk.CTkLabel(
            tags_frame,
            text=f" {task.priority.upper()} ",
            font=FONTS["badge"],
            text_color=colors["text_on_accent"],
            fg_color=priority_color,
            corner_radius=4,
            padx=6,
            pady=1,
        )
        priority_badge.pack(side="left", padx=(0, PADDING["xs"]))

        # Due time
        if task.due_time:
            time_label = ctk.CTkLabel(
                tags_frame,
                text=f"• {task.due_time}",
                font=FONTS["caption"],
                text_color=colors["text_secondary"],
            )
            time_label.pack(side="left", padx=(PADDING["xs"], 0))

        # Category name
        if task.category_name:
            cat_label = ctk.CTkLabel(
                tags_frame,
                text=f"• {task.category_name}",
                font=FONTS["caption"],
                text_color=colors["text_secondary"],
            )
            cat_label.pack(side="left", padx=(PADDING["xs"], 0))

        # Due date (if present)
        if task.due_date:
            date_label = ctk.CTkLabel(
                tags_frame,
                text=f"• {task.due_date}",
                font=FONTS["small"],
                text_color=colors["text_tertiary"],
            )
            date_label.pack(side="left", padx=(PADDING["xs"], 0))

        # ── Action buttons ─────────────────────────────────────────
        actions_frame = ctk.CTkFrame(self, fg_color="transparent")
        actions_frame.grid(row=0, column=3, rowspan=2, sticky="e", padx=PADDING["sm"], pady=PADDING["sm"])

        edit_btn = ctk.CTkButton(
            actions_frame,
            text="✏️",
            width=30,
            height=30,
            fg_color="transparent",
            hover_color=colors["bg_hover"],
            corner_radius=RADIUS["sm"],
            command=self._on_edit_click,
        )
        edit_btn.pack(side="left", padx=2)

        delete_btn = ctk.CTkButton(
            actions_frame,
            text="🗑️",
            width=30,
            height=30,
            fg_color="transparent",
            hover_color=colors["error"],
            corner_radius=RADIUS["sm"],
            command=self._on_delete_click,
        )
        delete_btn.pack(side="left", padx=2)

    def _on_toggle_click(self):
        """Handle checkbox toggle."""
        if self.on_toggle:
            self.on_toggle(self.task.id)

    def _on_edit_click(self):
        """Handle edit button click."""
        if self.on_edit:
            self.on_edit(self.task)

    def _on_delete_click(self):
        """Handle delete button click."""
        if self.on_delete:
            self.on_delete(self.task.id)
