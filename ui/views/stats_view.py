"""
stats_view.py — The productivity analytics view.

Displays task metrics (Total, Completed, Pending, Completion Rate) using StatCards.
Uses a Tkinter Canvas to draw a dark-themed week-completion bar chart.
"""

import customtkinter as ctk
from ui.theme import FONTS, PADDING, RADIUS
from ui.components.stat_card import StatCard


class StatsView(ctk.CTkFrame):
    """Analytics view displaying completion trends and statistics cards."""

    def __init__(self, master, app, colors, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.app = app
        self.colors = colors
        self.task_ctrl = app.task_ctrl

        self._build()

    def _build(self):
        colors = self.colors
        stats = self.task_ctrl.get_stats()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)  # Chart section expands

        # ── Scrollable Frame for Stats Content ─────────────────────
        scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll_frame.grid(row=0, column=0, rowspan=2, sticky="nsew")
        scroll_frame.grid_columnconfigure(0, weight=1)

        # Title
        ctk.CTkLabel(
            scroll_frame,
            text="Productivity Stats",
            font=FONTS["heading_lg"],
            text_color=colors["text_primary"],
            anchor="w",
        ).pack(fill="x", pady=(0, PADDING["md"]))

        # ── Grid of Stat Cards ──────────────────────────────────────
        cards_grid = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        cards_grid.pack(fill="x", pady=(0, PADDING["lg"]))

        # Configure columns (2x2 grid)
        cards_grid.grid_columnconfigure(0, weight=1)
        cards_grid.grid_columnconfigure(1, weight=1)

        # Card 1: Completed count
        # Calculate weekly difference percentage
        this_w = stats["completed_this_week"]
        last_w = stats["completed_last_week"]
        if last_w > 0:
            diff = round(((this_w - last_w) / last_w) * 100)
            trend = f"+{diff}% from last week" if diff >= 0 else f"{diff}% from last week"
        else:
            trend = f"+{this_w} tasks this week"

        card_completed = StatCard(
            cards_grid,
            colors,
            label="Tasks Completed",
            value=str(stats["completed"]),
            subtitle=trend,
            icon="🏆",
        )
        card_completed.grid(row=0, column=0, padx=PADDING["xs"], pady=PADDING["xs"], sticky="nsew")

        # Card 2: Efficiency Score (Completion Rate)
        card_rate = StatCard(
            cards_grid,
            colors,
            label="Efficiency Score",
            value=f"{stats['completion_rate']}%",
            subtitle="Overall task completion rate",
            accent_color=colors["accent_orange"],
            progress=stats["completion_rate"] / 100,
            icon="⚡",
        )
        card_rate.grid(row=0, column=1, padx=PADDING["xs"], pady=PADDING["xs"], sticky="nsew")

        # Card 3: Pending count
        card_pending = StatCard(
            cards_grid,
            colors,
            label="Pending Tasks",
            value=str(stats["pending"]),
            subtitle="Tasks waiting to be done",
            accent_color=colors["priority_high"],
            icon="⏳",
        )
        card_pending.grid(row=1, column=0, padx=PADDING["xs"], pady=PADDING["xs"], sticky="nsew")

        # Card 4: Focus Time (Estimation based on tasks completed)
        # Assume 45 minutes of focus time per completed task
        estimated_hours = round((stats["completed"] * 45) / 60, 1)
        card_focus = StatCard(
            cards_grid,
            colors,
            label="Focus Time",
            value=f"{estimated_hours}h",
            subtitle="Estimated deep work sessions",
            accent_color=colors["purple"],
            icon="⏱️",
        )
        card_focus.grid(row=1, column=1, padx=PADDING["xs"], pady=PADDING["xs"], sticky="nsew")

        # ── Weekly Completion Chart Card ───────────────────────────
        chart_card = ctk.CTkFrame(
            scroll_frame,
            fg_color=colors["bg_secondary"],
            corner_radius=RADIUS["lg"],
            border_width=1,
            border_color=colors["border"],
        )
        chart_card.pack(fill="x", pady=PADDING["sm"])

        chart_header = ctk.CTkFrame(chart_card, fg_color="transparent")
        chart_header.pack(fill="x", padx=PADDING["lg"], pady=(PADDING["lg"], PADDING["sm"]))

        ctk.CTkLabel(
            chart_header,
            text="Weekly Completion",
            font=FONTS["subheading"],
            text_color=colors["text_primary"],
        ).pack(side="left")

        # Canvas drawing for weekly stats bars
        self.canvas_width = 320
        self.canvas_height = 200

        self.canvas = ctk.CTkCanvas(
            chart_card,
            width=self.canvas_width,
            height=self.canvas_height,
            bg=colors["bg_secondary"],
            highlightthickness=0,
        )
        self.canvas.pack(fill="x", padx=PADDING["lg"], pady=(0, PADDING["lg"]))

        self._draw_chart(this_w, last_w)

    def _draw_chart(self, this_week_val, last_week_val):
        """Draw a sleek bar chart on the canvas matching the theme colors."""
        colors = self.colors
        canvas = self.canvas

        # Clear canvas
        canvas.delete("all")

        # Draw grid lines
        for i in range(1, 5):
            y = self.canvas_height - (i * 40) - 20
            canvas.create_line(30, y, self.canvas_width - 20, y, fill=colors["border_light"], dash=(4, 4))

        # Values
        max_val = max(10, this_week_val, last_week_val)

        # Bar dimensions
        bar_width = 50
        bar_y_bottom = self.canvas_height - 30

        # Bar 1: Last Week
        h1 = (last_week_val / max_val) * (self.canvas_height - 70)
        x1 = 60
        y1 = bar_y_bottom - h1
        canvas.create_rectangle(
            x1, y1, x1 + bar_width, bar_y_bottom,
            fill=colors["text_tertiary"], outline="", width=0
        )
        canvas.create_text(
            x1 + (bar_width // 2), bar_y_bottom + 15,
            text="Last Week", fill=colors["text_secondary"], font=("Segoe UI", 10)
        )
        canvas.create_text(
            x1 + (bar_width // 2), y1 - 12,
            text=str(last_week_val), fill=colors["text_secondary"], font=("Segoe UI", 10, "bold")
        )

        # Bar 2: This Week
        h2 = (this_week_val / max_val) * (self.canvas_height - 70)
        x2 = 180
        y2 = bar_y_bottom - h2
        canvas.create_rectangle(
            x2, y2, x2 + bar_width, bar_y_bottom,
            fill=colors["accent_orange"], outline="", width=0
        )
        canvas.create_text(
            x2 + (bar_width // 2), bar_y_bottom + 15,
            text="This Week", fill=colors["text_primary"], font=("Segoe UI", 10, "bold")
        )
        canvas.create_text(
            x2 + (bar_width // 2), y2 - 12,
            text=str(this_week_val), fill=colors["accent_orange"], font=("Segoe UI", 10, "bold")
        )
