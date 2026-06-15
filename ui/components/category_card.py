"""
category_card.py — Reusable category card widget.

Displays a category with its icon, name, and pending task count.
"""

import customtkinter as ctk
from ui.theme import FONTS, PADDING, RADIUS


class CategoryCard(ctk.CTkFrame):
    """
    A card widget for displaying a task category.

    Args:
        master:      Parent widget.
        category:    Category model object.
        colors:      Color dictionary from theme.
        on_click:    Callback when card is clicked — fn(category).
        on_edit:     Callback for editing — fn(category).
        on_delete:   Callback for deleting — fn(category_id).
        compact:     If True, uses a smaller compact layout (for dashboard).
    """

    def __init__(
        self,
        master,
        category,
        colors: dict,
        on_click=None,
        on_edit=None,
        on_delete=None,
        compact: bool = False,
        **kwargs,
    ):
        super().__init__(
            master,
            fg_color=colors["bg_secondary"],
            corner_radius=RADIUS["md"],
            border_width=1,
            border_color=colors["border"],
            cursor="hand2",
            **kwargs,
        )
        self.category = category
        self.colors = colors
        self.on_click = on_click
        self.on_edit = on_edit
        self.on_delete = on_delete

        if compact:
            self._build_compact()
        else:
            self._build_full()

        # Bind click and hover to entire card and recursively to children
        self._bind_events_recursively(self)

    def _bind_events_recursively(self, widget):
        """Bind click and hover events to a widget and its children."""
        widget.bind("<Button-1>", self._handle_click)
        widget.bind("<Enter>", lambda e: self._on_hover_enter())
        widget.bind("<Leave>", lambda e: self._on_hover_leave())

        for child in widget.winfo_children():
            if not isinstance(child, ctk.CTkButton):
                self._bind_events_recursively(child)

    def _on_hover_enter(self):
        """Highlight background on hover."""
        self.configure(fg_color=self.colors["bg_hover"])

    def _on_hover_leave(self):
        """Revert background when mouse leaves."""
        self.configure(fg_color=self.colors["bg_secondary"])

    def _build_compact(self):
        """Build a small card for the dashboard categories row."""
        colors = self.colors
        cat = self.category

        self.configure(width=120, height=80)
        self.grid_propagate(False)
        self.grid_columnconfigure(0, weight=1)

        # Icon
        icon_label = ctk.CTkLabel(
            self,
            text=cat.icon,
            font=("Segoe UI", 24),
        )
        icon_label.grid(row=0, column=0, pady=(PADDING["sm"], 2))

        # Name
        name_label = ctk.CTkLabel(
            self,
            text=cat.name,
            font=FONTS["caption_bold"],
            text_color=colors["text_primary"],
        )
        name_label.grid(row=1, column=0)

        # Count
        count_label = ctk.CTkLabel(
            self,
            text=f"{cat.pending_count} Tasks",
            font=FONTS["small"],
            text_color=colors["text_secondary"],
        )
        count_label.grid(row=2, column=0, pady=(0, PADDING["sm"]))

    def _build_full(self):
        """Build the full-size card for the Categories view."""
        colors = self.colors
        cat = self.category

        self.grid_columnconfigure(1, weight=1)

        # ── Icon background ────────────────────────────────────────
        icon_frame = ctk.CTkFrame(
            self,
            width=48,
            height=48,
            fg_color=cat.color,
            corner_radius=RADIUS["md"],
        )
        icon_frame.grid(row=0, column=0, rowspan=2, padx=PADDING["lg"], pady=PADDING["lg"])
        icon_frame.grid_propagate(False)

        icon_label = ctk.CTkLabel(
            icon_frame,
            text=cat.icon,
            font=("Segoe UI", 22),
        )
        icon_label.place(relx=0.5, rely=0.5, anchor="center")

        # ── Name + count ───────────────────────────────────────────
        name_label = ctk.CTkLabel(
            self,
            text=cat.name,
            font=FONTS["body_bold"],
            text_color=colors["text_primary"],
            anchor="w",
        )
        name_label.grid(row=0, column=1, sticky="sw", pady=(PADDING["lg"], 0))

        count_label = ctk.CTkLabel(
            self,
            text=f"{cat.pending_count} PENDING TASKS",
            font=FONTS["caption"],
            text_color=colors["text_secondary"],
            anchor="w",
        )
        count_label.grid(row=1, column=1, sticky="nw", pady=(0, PADDING["lg"]))

        # ── Action buttons ─────────────────────────────────────────
        actions_frame = ctk.CTkFrame(self, fg_color="transparent")
        actions_frame.grid(row=0, column=2, rowspan=2, padx=PADDING["sm"], pady=PADDING["sm"])

        if self.on_edit:
            edit_btn = ctk.CTkButton(
                actions_frame,
                text="✏️",
                width=28,
                height=28,
                fg_color="transparent",
                hover_color=colors["bg_hover"],
                corner_radius=RADIUS["sm"],
                command=lambda: self.on_edit(self.category),
            )
            edit_btn.pack(side="left", padx=2)

        if self.on_delete:
            del_btn = ctk.CTkButton(
                actions_frame,
                text="🗑️",
                width=28,
                height=28,
                fg_color="transparent",
                hover_color=colors["error"],
                corner_radius=RADIUS["sm"],
                command=lambda: self.on_delete(self.category.id),
            )
            del_btn.pack(side="left", padx=2)

    def _handle_click(self, event=None):
        """Handle click on the card body."""
        if self.on_click:
            self.on_click(self.category)
