"""
search_bar.py — Styled search input component.

A rounded dark input field with a search icon, matching the UI reference.
"""

import customtkinter as ctk
from ui.theme import FONTS, PADDING, RADIUS


class SearchBar(ctk.CTkFrame):
    """
    A search input bar with a magnifying glass icon.

    Args:
        master:       Parent widget.
        colors:       Color dictionary from theme.
        placeholder:  Placeholder text shown when input is empty.
        on_search:    Callback when user types or presses Enter — fn(query).
    """

    def __init__(
        self,
        master,
        colors: dict,
        placeholder: str = "Search tasks...",
        on_search=None,
        **kwargs,
    ):
        super().__init__(
            master,
            fg_color=colors["bg_tertiary"],
            corner_radius=RADIUS["lg"],
            **kwargs,
        )
        self.colors = colors
        self.on_search = on_search

        # Search icon
        icon_label = ctk.CTkLabel(
            self,
            text="🔍",
            font=("Segoe UI", 14),
            width=30,
        )
        icon_label.pack(side="left", padx=(PADDING["sm"], 0))

        # Text input
        self.entry = ctk.CTkEntry(
            self,
            placeholder_text=placeholder,
            font=FONTS["body"],
            fg_color="transparent",
            border_width=0,
            text_color=colors["text_primary"],
            placeholder_text_color=colors["text_tertiary"],
            height=36,
        )
        self.entry.pack(side="left", fill="x", expand=True, padx=PADDING["xs"], pady=PADDING["xs"])

        # Bind events
        self.entry.bind("<Return>", self._on_submit)
        self.entry.bind("<KeyRelease>", self._on_key_release)

    def _on_submit(self, event=None):
        """Handle Enter key press."""
        if self.on_search:
            self.on_search(self.entry.get())

    def _on_key_release(self, event=None):
        """Handle key release for live search."""
        if self.on_search:
            self.on_search(self.entry.get())

    def get_query(self) -> str:
        """Return the current search text."""
        return self.entry.get()

    def clear(self):
        """Clear the search input."""
        self.entry.delete(0, "end")
