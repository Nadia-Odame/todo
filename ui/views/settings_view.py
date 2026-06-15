"""
settings_view.py — The user preferences and configurations view.

Allows updating the username, toggling between Dark/Light modes,
and triggering CSV task exports.
"""

import customtkinter as ctk
from ui.theme import FONTS, PADDING, RADIUS
from utils.csv_export import export_tasks_to_csv


class SettingsView(ctk.CTkFrame):
    """View managing preferences, theme settings, and task export features."""

    def __init__(self, master, app, colors, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.app = app
        self.colors = colors
        self.settings_ctrl = app.settings_ctrl

        self._build()

    def _build(self):
        colors = self.colors

        # Header Title
        ctk.CTkLabel(
            self,
            text="Settings",
            font=FONTS["heading_lg"],
            text_color=colors["text_primary"],
            anchor="w",
        ).pack(fill="x", pady=(0, PADDING["lg"]))

        # ── Scrollable settings list ──────────────────────────────
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        # ── Section 1: Profile ─────────────────────────────────────
        profile_card = ctk.CTkFrame(
            scroll,
            fg_color=colors["bg_secondary"],
            corner_radius=RADIUS["lg"],
            border_width=1,
            border_color=colors["border"],
        )
        profile_card.pack(fill="x", pady=(0, PADDING["md"]))

        ctk.CTkLabel(
            profile_card,
            text="PROFILE SETTINGS",
            font=FONTS["caption_bold"],
            text_color=colors["text_secondary"],
        ).pack(anchor="w", padx=PADDING["lg"], pady=(PADDING["lg"], PADDING["sm"]))

        username_frame = ctk.CTkFrame(profile_card, fg_color="transparent")
        username_frame.pack(fill="x", padx=PADDING["lg"], pady=(0, PADDING["lg"]))

        ctk.CTkLabel(
            username_frame,
            text="Display Name",
            font=FONTS["body_bold"],
            text_color=colors["text_primary"],
        ).pack(side="left")

        # Edit box for display name
        self.name_entry = ctk.CTkEntry(
            username_frame,
            width=200,
            font=FONTS["body"],
            fg_color=colors["bg_tertiary"],
            border_color=colors["border"],
            text_color=colors["text_primary"],
        )
        self.name_entry.insert(0, self.settings_ctrl.get_username() or "Alex")
        self.name_entry.pack(side="right", padx=(PADDING["sm"], 0))

        # Save username button
        save_name_btn = ctk.CTkButton(
            username_frame,
            text="Save",
            font=FONTS["caption_bold"],
            fg_color=colors["accent_blue"],
            hover_color=colors["accent_blue_hover"],
            text_color=colors["text_on_accent"],
            width=60,
            height=28,
            corner_radius=RADIUS["sm"],
            command=self._on_save_name,
        )
        save_name_btn.pack(side="right", padx=PADDING["sm"])

        # ── Section 2: Personalization (Theme) ─────────────────────
        theme_card = ctk.CTkFrame(
            scroll,
            fg_color=colors["bg_secondary"],
            corner_radius=RADIUS["lg"],
            border_width=1,
            border_color=colors["border"],
        )
        theme_card.pack(fill="x", pady=(0, PADDING["md"]))

        ctk.CTkLabel(
            theme_card,
            text="PERSONALIZATION",
            font=FONTS["caption_bold"],
            text_color=colors["text_secondary"],
        ).pack(anchor="w", padx=PADDING["lg"], pady=(PADDING["lg"], PADDING["sm"]))

        theme_row = ctk.CTkFrame(theme_card, fg_color="transparent")
        theme_row.pack(fill="x", padx=PADDING["lg"], pady=(0, PADDING["lg"]))

        ctk.CTkLabel(
            theme_row,
            text="Theme Mode",
            font=FONTS["body_bold"],
            text_color=colors["text_primary"],
        ).pack(side="left")

        # Segmented button for theme selection
        theme_options = ["Dark", "Light"]
        initial_value = "Dark" if self.app.theme_mode == "dark" else "Light"

        self.theme_segment = ctk.CTkSegmentedButton(
            theme_row,
            values=theme_options,
            command=self._on_theme_changed,
            font=FONTS["caption_bold"],
            fg_color=colors["bg_tertiary"],
            selected_color=colors["accent_blue"],
            selected_text_color=colors["text_on_accent"],
            unselected_color=colors["bg_secondary"],
            unselected_text_color=colors["text_secondary"],
        )
        self.theme_segment.set(initial_value)
        self.theme_segment.pack(side="right")

        # ── Section 3: Data & Export ──────────────────────────────
        data_card = ctk.CTkFrame(
            scroll,
            fg_color=colors["bg_secondary"],
            corner_radius=RADIUS["lg"],
            border_width=1,
            border_color=colors["border"],
        )
        data_card.pack(fill="x", pady=(0, PADDING["md"]))

        ctk.CTkLabel(
            data_card,
            text="DATA AND BACKUP",
            font=FONTS["caption_bold"],
            text_color=colors["text_secondary"],
        ).pack(anchor="w", padx=PADDING["lg"], pady=(PADDING["lg"], PADDING["sm"]))

        export_row = ctk.CTkFrame(data_card, fg_color="transparent")
        export_row.pack(fill="x", padx=PADDING["lg"], pady=(0, PADDING["lg"]))

        ctk.CTkLabel(
            export_row,
            text="Backup Tasks",
            font=FONTS["body_bold"],
            text_color=colors["text_primary"],
        ).pack(side="left")

        export_btn = ctk.CTkButton(
            export_row,
            text="Export to CSV",
            font=FONTS["caption_bold"],
            fg_color=colors["accent_orange"],
            hover_color="#D97706",
            text_color=colors["text_on_accent"],
            corner_radius=RADIUS["md"],
            height=32,
            command=self._on_export_csv,
        )
        export_btn.pack(side="right")

        # Status output line
        self.status_label = ctk.CTkLabel(
            scroll,
            text="",
            font=FONTS["caption"],
            text_color=colors["success"],
        )
        self.status_label.pack(pady=PADDING["sm"])

        # ── App Info ───────────────────────────────────────────────
        ctk.CTkLabel(
            scroll,
            text="Focus Planner v1.0.0\nMade with CustomTkinter & SQLite",
            font=FONTS["small"],
            text_color=colors["text_tertiary"],
            justify="center",
        ).pack(pady=PADDING["xl"])

    def _on_save_name(self):
        """Save username to DB."""
        new_name = self.name_entry.get().strip()
        if new_name:
            self.settings_ctrl.set_username(new_name)
            self.status_label.configure(
                text="Username updated successfully!",
                text_color=self.colors["success"]
            )
        else:
            self.status_label.configure(
                text="Username cannot be empty.",
                text_color=self.colors["error"]
            )

    def _on_theme_changed(self, value):
        """Handle toggle of dark/light theme."""
        new_mode = "dark" if value == "Dark" else "light"
        self.app.update_theme(new_mode)

    def _on_export_csv(self):
        """Export tasks list to CSV."""
        tasks = self.app.task_ctrl.get_all_tasks()
        filepath = export_tasks_to_csv(tasks)
        if filepath:
            self.status_label.configure(
                text=f"Tasks exported to CSV successfully!",
                text_color=self.colors["success"]
            )
        else:
            self.status_label.configure(
                text="CSV export cancelled.",
                text_color=self.colors["text_secondary"]
            )
