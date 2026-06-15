"""
stat_card.py — Reusable statistics card widget.

Displays a metric with a large number, label, trend indicator,
and optional progress bar — matching the Productivity Stats screen.
"""

import customtkinter as ctk
from ui.theme import FONTS, PADDING, RADIUS


class StatCard(ctk.CTkFrame):
    """
    A card widget for displaying a single statistic.

    Args:
        master:        Parent widget.
        colors:        Color dictionary from theme.
        label:         Upper label (e.g., "TASKS COMPLETED").
        value:         Main display value (e.g., "142").
        subtitle:      Sub-text below the value (e.g., "+12% from last week").
        accent_color:  Color for the progress bar / icon.
        icon:          Optional emoji icon displayed on the right.
        progress:      Optional float 0–1 to show a progress bar.
    """

    def __init__(
        self,
        master,
        colors: dict,
        label: str = "",
        value: str = "0",
        subtitle: str = "",
        accent_color: str = None,
        icon: str = None,
        progress: float = None,
        **kwargs,
    ):
        super().__init__(
            master,
            fg_color=colors["bg_secondary"],
            corner_radius=RADIUS["lg"],
            border_width=1,
            border_color=colors["border"],
            **kwargs,
        )
        self.colors = colors
        accent = accent_color or colors["accent_orange"]

        self.grid_columnconfigure(0, weight=1)

        # ── Header row: label + icon ──────────────────────────────
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=PADDING["lg"], pady=(PADDING["lg"], PADDING["xs"]))
        header_frame.grid_columnconfigure(0, weight=1)

        label_widget = ctk.CTkLabel(
            header_frame,
            text=label.upper(),
            font=FONTS["caption_bold"],
            text_color=colors["text_secondary"],
            anchor="w",
        )
        label_widget.grid(row=0, column=0, sticky="w")

        if icon:
            icon_label = ctk.CTkLabel(
                header_frame,
                text=icon,
                font=("Segoe UI", 16),
                text_color=accent,
            )
            icon_label.grid(row=0, column=1, sticky="e")

        # ── Value ─────────────────────────────────────────────────
        value_label = ctk.CTkLabel(
            self,
            text=str(value),
            font=FONTS["heading_xl"],
            text_color=colors["text_primary"],
            anchor="w",
        )
        value_label.grid(row=1, column=0, sticky="w", padx=PADDING["lg"], pady=(0, PADDING["xs"]))

        # ── Progress bar (optional) ───────────────────────────────
        if progress is not None:
            progress_bar = ctk.CTkProgressBar(
                self,
                width=200,
                height=6,
                corner_radius=3,
                fg_color=colors["bg_tertiary"],
                progress_color=accent,
            )
            progress_bar.set(max(0, min(1, progress)))
            progress_bar.grid(row=2, column=0, sticky="ew", padx=PADDING["lg"], pady=(0, PADDING["xs"]))

        # ── Subtitle ──────────────────────────────────────────────
        if subtitle:
            sub_label = ctk.CTkLabel(
                self,
                text=subtitle,
                font=FONTS["caption"],
                text_color=colors["text_secondary"] if "+" not in subtitle else colors["success"],
                anchor="w",
            )
            sub_label.grid(row=3, column=0, sticky="w", padx=PADDING["lg"], pady=(0, PADDING["lg"]))
