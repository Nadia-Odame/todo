"""
theme.py — Design tokens and color system for the Focus To-Do application.

Centralizes all colors, fonts, spacing, and style constants so that
every widget in the app draws from a single source of truth.
"""

# ── Dark Theme Colors ──────────────────────────────────────────────────
COLORS_DARK = {
    "bg_primary": "#0D1117",       # Main window background
    "bg_secondary": "#161B22",     # Card / panel backgrounds
    "bg_tertiary": "#1C2333",      # Input fields, hover states
    "bg_hover": "#21262D",         # Hover overlay
    "bg_sidebar": "#0D1117",       # Sidebar background
    "bg_sidebar_active": "#1C2333",# Active nav item background

    "accent_orange": "#E8913A",    # Primary accent (progress bars, highlights)
    "accent_blue": "#3B82F6",      # Selected states, badges, links
    "accent_blue_hover": "#2563EB",

    "priority_high": "#EF4444",    # Red
    "priority_medium": "#F59E0B",  # Amber
    "priority_low": "#22C55E",     # Green

    "text_primary": "#FFFFFF",
    "text_secondary": "#8B949E",
    "text_tertiary": "#484F58",
    "text_on_accent": "#FFFFFF",

    "border": "#21262D",
    "border_light": "#30363D",
    "divider": "#21262D",

    "success": "#22C55E",
    "warning": "#F59E0B",
    "error": "#EF4444",
    "purple": "#8B5CF6",

    "scrollbar": "#30363D",
    "scrollbar_hover": "#484F58",

    "shadow": "rgba(0, 0, 0, 0.3)",
}

# ── Light Theme Colors ─────────────────────────────────────────────────
COLORS_LIGHT = {
    "bg_primary": "#F6F8FA",
    "bg_secondary": "#FFFFFF",
    "bg_tertiary": "#F0F2F5",
    "bg_hover": "#E8EAED",
    "bg_sidebar": "#FFFFFF",
    "bg_sidebar_active": "#EFF6FF",

    "accent_orange": "#D97706",
    "accent_blue": "#2563EB",
    "accent_blue_hover": "#1D4ED8",

    "priority_high": "#DC2626",
    "priority_medium": "#D97706",
    "priority_low": "#16A34A",

    "text_primary": "#1F2937",
    "text_secondary": "#6B7280",
    "text_tertiary": "#9CA3AF",
    "text_on_accent": "#FFFFFF",

    "border": "#E5E7EB",
    "border_light": "#F3F4F6",
    "divider": "#E5E7EB",

    "success": "#16A34A",
    "warning": "#D97706",
    "error": "#DC2626",
    "purple": "#7C3AED",

    "scrollbar": "#D1D5DB",
    "scrollbar_hover": "#9CA3AF",

    "shadow": "rgba(0, 0, 0, 0.08)",
}


def get_colors(mode: str = "dark") -> dict:
    """
    Return the color dictionary for the given mode.

    Args:
        mode: 'dark' or 'light'.

    Returns:
        Dictionary of color tokens.
    """
    return COLORS_DARK if mode == "dark" else COLORS_LIGHT


# ── Font Configuration ─────────────────────────────────────────────────
FONTS = {
    "heading_xl": ("Segoe UI", 28, "bold"),
    "heading_lg": ("Segoe UI", 22, "bold"),
    "heading": ("Segoe UI", 18, "bold"),
    "subheading": ("Segoe UI", 15, "bold"),
    "body": ("Segoe UI", 13),
    "body_bold": ("Segoe UI", 13, "bold"),
    "caption": ("Segoe UI", 11),
    "caption_bold": ("Segoe UI", 11, "bold"),
    "small": ("Segoe UI", 10),
    "badge": ("Segoe UI", 9, "bold"),
}


# ── Spacing & Dimensions ──────────────────────────────────────────────
PADDING = {
    "xs": 4,
    "sm": 8,
    "md": 12,
    "lg": 16,
    "xl": 24,
    "xxl": 32,
}

RADIUS = {
    "sm": 6,
    "md": 10,
    "lg": 14,
    "xl": 20,
    "round": 50,
}

SIDEBAR_WIDTH = 200
SIDEBAR_COLLAPSED_WIDTH = 60

# ── Priority Helpers ───────────────────────────────────────────────────
PRIORITY_COLORS = {
    "High": "priority_high",
    "Medium": "priority_medium",
    "Low": "priority_low",
}

PRIORITY_ORDER = {"High": 0, "Medium": 1, "Low": 2}

# ── Category Default Icons ─────────────────────────────────────────────
CATEGORY_ICONS = [
    "📁", "💼", "📚", "💪", "🛒", "🚀", "🎓", "🎨", "🎵",
    "🏠", "💡", "⭐", "🔧", "📝", "🎯", "❤️", "🌟", "📌",
]

CATEGORY_COLORS = [
    "#3B82F6", "#8B5CF6", "#22C55E", "#F59E0B", "#EF4444",
    "#6366F1", "#EC4899", "#14B8A6", "#F97316", "#06B6D4",
]

# ── Navigation Items ──────────────────────────────────────────────────
NAV_ITEMS = [
    {"id": "dashboard", "label": "Home", "icon": "🏠"},
    {"id": "tasks", "label": "Tasks", "icon": "📋"},
    {"id": "calendar", "label": "Calendar", "icon": "📅"},
    {"id": "stats", "label": "Stats", "icon": "📊"},
    {"id": "categories", "label": "Categories", "icon": "🏷️"},
]
