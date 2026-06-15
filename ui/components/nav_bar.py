"""
nav_bar.py — Floating bottom navigation bar component.

Provides a modern, glassmorphic-inspired floating bottom navigation bar,
replacing the traditional sidebar with a dynamic horizontal layout.
"""

import customtkinter as ctk
from ui.theme import FONTS, PADDING, RADIUS, NAV_ITEMS


class NavBar(ctk.CTkFrame):
    """
    A horizontal bottom navigation bar that floats at the bottom of the screen.

    Args:
        master:       Parent widget.
        colors:       Color dictionary from theme.
        on_navigate:  Callback when a nav item is clicked — fn(view_id).
    """

    def __init__(self, master, colors: dict, on_navigate=None, **kwargs):
        super().__init__(
            master,
            fg_color=colors["bg_secondary"],
            corner_radius=0,
            border_width=1,
            border_color=colors["border"],
            height=64,
            **kwargs,
        )
        self.colors = colors
        self.on_navigate = on_navigate
        self.active_id = "dashboard"
        self.nav_buttons: dict[str, ctk.CTkFrame] = {}
        self.nav_labels: dict[str, ctk.CTkLabel] = {}
        self.nav_icons: dict[str, ctk.CTkLabel] = {}

        # Fix size to look floating and centered
        self.pack_propagate(False)

        self._build()

    def _build(self):
        """Construct the horizontal tab buttons."""
        colors = self.colors

        # Center the buttons inside the bar by adding horizontal spacer columns
        self.grid_rowconfigure(0, weight=1)
        
        # Configure grid columns for each item to distribute space evenly
        num_items = len(NAV_ITEMS)
        for i in range(num_items):
            self.grid_columnconfigure(i, weight=1)

        # ── Navigation Items ──────────────────────────────────────
        for idx, item in enumerate(NAV_ITEMS):
            # We use a CTkFrame as a container for each button to handle hover highlights dynamically
            item_frame = ctk.CTkFrame(
                self,
                fg_color="transparent",
                corner_radius=RADIUS["lg"],
                cursor="hand2",
            )
            item_frame.grid(row=0, column=idx, padx=PADDING["xs"], pady=6, sticky="nsew")
            
            # Pack details vertically
            icon_lbl = ctk.CTkLabel(
                item_frame,
                text=item["icon"],
                font=("Segoe UI", 20),
                text_color=colors["text_secondary"],
            )
            icon_lbl.pack(pady=(PADDING["sm"], 0))

            label_lbl = ctk.CTkLabel(
                item_frame,
                text=item["label"],
                font=FONTS["badge"],
                text_color=colors["text_secondary"],
            )
            label_lbl.pack(pady=(2, PADDING["sm"]))

            # Save references to animate state
            self.nav_buttons[item["id"]] = item_frame
            self.nav_icons[item["id"]] = icon_lbl
            self.nav_labels[item["id"]] = label_lbl

            # Bind events for hover and click simulation
            self._bind_events(item_frame, item["id"])

        # Set initial active state styling
        self._update_active_style()

    def _bind_events(self, widget, view_id):
        """Bind hover animations and mouse clicks to a tab."""
        widget.bind("<Button-1>", lambda e: self._handle_navigate(view_id))
        widget.bind("<Enter>", lambda e: self._on_hover_enter(view_id))
        widget.bind("<Leave>", lambda e: self._on_hover_leave(view_id))

        # Apply bindings recursively to children labels
        for child in widget.winfo_children():
            child.bind("<Button-1>", lambda e: self._handle_navigate(view_id))
            child.bind("<Enter>", lambda e: self._on_hover_enter(view_id))
            child.bind("<Leave>", lambda e: self._on_hover_leave(view_id))

    def _handle_navigate(self, view_id: str):
        """Navigate to selected view and trigger callback."""
        self.active_id = view_id
        self._update_active_style()
        if self.on_navigate:
            self.on_navigate(view_id)

    def _on_hover_enter(self, view_id: str):
        """Animate visual scaling/highlighting on mouse hover."""
        colors = self.colors
        if view_id != self.active_id:
            # Highlight hovered item subtly
            self.nav_buttons[view_id].configure(fg_color=colors["bg_hover"])
            self.nav_icons[view_id].configure(text_color=colors["text_primary"])
            self.nav_labels[view_id].configure(text_color=colors["text_primary"])

    def _on_hover_leave(self, view_id: str):
        """Revert animation state when mouse leaves."""
        colors = self.colors
        if view_id != self.active_id:
            self.nav_buttons[view_id].configure(fg_color="transparent")
            self.nav_icons[view_id].configure(text_color=colors["text_secondary"])
            self.nav_labels[view_id].configure(text_color=colors["text_secondary"])

    def _update_active_style(self):
        """Apply the active pill highlight and accent coloring to the selected tab."""
        colors = self.colors
        for vid, frame in self.nav_buttons.items():
            if vid == self.active_id:
                # Active pill highlight
                frame.configure(fg_color=colors["bg_sidebar_active"])
                self.nav_icons[vid].configure(text_color=colors["accent_blue"])
                self.nav_labels[vid].configure(text_color=colors["accent_blue"])
            else:
                # Idle transparent state
                frame.configure(fg_color="transparent")
                self.nav_icons[vid].configure(text_color=colors["text_secondary"])
                self.nav_labels[vid].configure(text_color=colors["text_secondary"])

    def set_active(self, view_id: str):
        """Programmatically select and highlight a view tab."""
        self.active_id = view_id
        self._update_active_style()

    def update_colors(self, colors: dict):
        """Re-style widget components when theme changes."""
        self.colors = colors
        self.configure(
            fg_color=colors["bg_secondary"],
            border_color=colors["border"],
        )
        self._update_active_style()
