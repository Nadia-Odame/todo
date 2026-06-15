"""
dialogs.py — Modal dialog windows for creating and editing tasks/categories.

All dialogs are CTkToplevel windows styled to match the app's dark theme.
"""

import customtkinter as ctk
from datetime import datetime
from ui.theme import FONTS, PADDING, RADIUS, CATEGORY_ICONS, CATEGORY_COLORS
from utils.validators import validate_task_title, validate_date, validate_time, validate_category_name


class AddTaskDialog(ctk.CTkToplevel):
    """
    Modal dialog for creating a new task.

    Args:
        master:       Parent window.
        colors:       Color dictionary from theme.
        categories:   List of Category objects for the dropdown.
        on_save:      Callback when task is saved — fn(data_dict).
        default_date: Pre-filled date (YYYY-MM-DD), e.g. from calendar click.
    """

    def __init__(self, master, colors, categories, on_save=None, default_date=None, **kwargs):
        super().__init__(master, **kwargs)
        self.colors = colors
        self.categories = categories
        self.on_save = on_save

        self.title("Add New Task")
        self.geometry("480x560")
        self.resizable(False, False)
        self.configure(fg_color=colors["bg_primary"])

        # Make modal
        self.transient(master)
        self.grab_set()

        self._build(default_date)
        self.after(100, self.focus_force)

    def _build(self, default_date=None):
        colors = self.colors

        # ── Header ─────────────────────────────────────────────────
        header = ctk.CTkLabel(
            self, text="Create New Task", font=FONTS["heading"],
            text_color=colors["text_primary"],
        )
        header.pack(pady=(PADDING["xl"], PADDING["lg"]))

        # ── Form container ─────────────────────────────────────────
        form = ctk.CTkFrame(self, fg_color="transparent")
        form.pack(fill="x", padx=PADDING["xl"])

        # Title
        ctk.CTkLabel(form, text="Title *", font=FONTS["caption_bold"],
                      text_color=colors["text_secondary"]).pack(anchor="w", pady=(0, 4))
        self.title_entry = ctk.CTkEntry(
            form, placeholder_text="Enter task title...",
            font=FONTS["body"], height=40, corner_radius=RADIUS["sm"],
            fg_color=colors["bg_tertiary"], border_color=colors["border"],
            text_color=colors["text_primary"],
            placeholder_text_color=colors["text_tertiary"],
        )
        self.title_entry.pack(fill="x", pady=(0, PADDING["md"]))

        # Description
        ctk.CTkLabel(form, text="Description", font=FONTS["caption_bold"],
                      text_color=colors["text_secondary"]).pack(anchor="w", pady=(0, 4))
        self.desc_entry = ctk.CTkTextbox(
            form, height=70, font=FONTS["body"], corner_radius=RADIUS["sm"],
            fg_color=colors["bg_tertiary"], border_color=colors["border"],
            text_color=colors["text_primary"], border_width=1,
        )
        self.desc_entry.pack(fill="x", pady=(0, PADDING["md"]))

        # Priority + Category row
        row1 = ctk.CTkFrame(form, fg_color="transparent")
        row1.pack(fill="x", pady=(0, PADDING["md"]))
        row1.grid_columnconfigure(0, weight=1)
        row1.grid_columnconfigure(1, weight=1)

        # Priority
        pri_frame = ctk.CTkFrame(row1, fg_color="transparent")
        pri_frame.grid(row=0, column=0, sticky="ew", padx=(0, PADDING["sm"]))
        ctk.CTkLabel(pri_frame, text="Priority", font=FONTS["caption_bold"],
                      text_color=colors["text_secondary"]).pack(anchor="w", pady=(0, 4))
        self.priority_var = ctk.StringVar(value="Medium")
        self.priority_menu = ctk.CTkOptionMenu(
            pri_frame, variable=self.priority_var,
            values=["Low", "Medium", "High"],
            font=FONTS["body"], height=40, corner_radius=RADIUS["sm"],
            fg_color=colors["bg_tertiary"], button_color=colors["accent_blue"],
            button_hover_color=colors["accent_blue_hover"],
            text_color=colors["text_primary"],
            dropdown_fg_color=colors["bg_secondary"],
            dropdown_text_color=colors["text_primary"],
            dropdown_hover_color=colors["bg_hover"],
        )
        self.priority_menu.pack(fill="x")

        # Category
        cat_frame = ctk.CTkFrame(row1, fg_color="transparent")
        cat_frame.grid(row=0, column=1, sticky="ew", padx=(PADDING["sm"], 0))
        ctk.CTkLabel(cat_frame, text="Category", font=FONTS["caption_bold"],
                      text_color=colors["text_secondary"]).pack(anchor="w", pady=(0, 4))

        cat_names = ["None"] + [c.name for c in self.categories]
        self.category_var = ctk.StringVar(value="None")
        self.category_menu = ctk.CTkOptionMenu(
            cat_frame, variable=self.category_var,
            values=cat_names,
            font=FONTS["body"], height=40, corner_radius=RADIUS["sm"],
            fg_color=colors["bg_tertiary"], button_color=colors["accent_blue"],
            button_hover_color=colors["accent_blue_hover"],
            text_color=colors["text_primary"],
            dropdown_fg_color=colors["bg_secondary"],
            dropdown_text_color=colors["text_primary"],
            dropdown_hover_color=colors["bg_hover"],
        )
        self.category_menu.pack(fill="x")

        # Date + Time row
        row2 = ctk.CTkFrame(form, fg_color="transparent")
        row2.pack(fill="x", pady=(0, PADDING["md"]))
        row2.grid_columnconfigure(0, weight=1)
        row2.grid_columnconfigure(1, weight=1)

        # Due Date
        date_frame = ctk.CTkFrame(row2, fg_color="transparent")
        date_frame.grid(row=0, column=0, sticky="ew", padx=(0, PADDING["sm"]))
        ctk.CTkLabel(date_frame, text="Due Date", font=FONTS["caption_bold"],
                      text_color=colors["text_secondary"]).pack(anchor="w", pady=(0, 4))
        self.date_entry = ctk.CTkEntry(
            date_frame, placeholder_text="YYYY-MM-DD",
            font=FONTS["body"], height=40, corner_radius=RADIUS["sm"],
            fg_color=colors["bg_tertiary"], border_color=colors["border"],
            text_color=colors["text_primary"],
            placeholder_text_color=colors["text_tertiary"],
        )
        self.date_entry.pack(fill="x")
        if default_date:
            self.date_entry.insert(0, default_date)

        # Due Time
        time_frame = ctk.CTkFrame(row2, fg_color="transparent")
        time_frame.grid(row=0, column=1, sticky="ew", padx=(PADDING["sm"], 0))
        ctk.CTkLabel(time_frame, text="Due Time", font=FONTS["caption_bold"],
                      text_color=colors["text_secondary"]).pack(anchor="w", pady=(0, 4))
        self.time_entry = ctk.CTkEntry(
            time_frame, placeholder_text="HH:MM",
            font=FONTS["body"], height=40, corner_radius=RADIUS["sm"],
            fg_color=colors["bg_tertiary"], border_color=colors["border"],
            text_color=colors["text_primary"],
            placeholder_text_color=colors["text_tertiary"],
        )
        self.time_entry.pack(fill="x")

        # ── Error label ────────────────────────────────────────────
        self.error_label = ctk.CTkLabel(
            self, text="", font=FONTS["caption"],
            text_color=colors["error"],
        )
        self.error_label.pack(pady=(PADDING["sm"], 0))

        # ── Buttons ────────────────────────────────────────────────
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=PADDING["xl"], pady=PADDING["lg"])

        cancel_btn = ctk.CTkButton(
            btn_frame, text="Cancel", font=FONTS["body_bold"],
            fg_color="transparent", border_width=1,
            border_color=colors["border"], text_color=colors["text_secondary"],
            hover_color=colors["bg_hover"], height=42, corner_radius=RADIUS["sm"],
            command=self.destroy,
        )
        cancel_btn.pack(side="left", expand=True, fill="x", padx=(0, PADDING["sm"]))

        save_btn = ctk.CTkButton(
            btn_frame, text="Create Task", font=FONTS["body_bold"],
            fg_color=colors["accent_blue"], hover_color=colors["accent_blue_hover"],
            text_color=colors["text_on_accent"], height=42, corner_radius=RADIUS["sm"],
            command=self._on_save,
        )
        save_btn.pack(side="left", expand=True, fill="x")

    def _on_save(self):
        """Validate and save the task."""
        title = self.title_entry.get().strip()
        valid, msg = validate_task_title(title)
        if not valid:
            self.error_label.configure(text=msg)
            return

        date_str = self.date_entry.get().strip()
        valid, msg = validate_date(date_str)
        if not valid:
            self.error_label.configure(text=msg)
            return

        time_str = self.time_entry.get().strip()
        valid, msg = validate_time(time_str)
        if not valid:
            self.error_label.configure(text=msg)
            return

        # Resolve category ID
        cat_name = self.category_var.get()
        cat_id = None
        for c in self.categories:
            if c.name == cat_name:
                cat_id = c.id
                break

        data = {
            "title": title,
            "description": self.desc_entry.get("1.0", "end-1c").strip(),
            "priority": self.priority_var.get(),
            "category_id": cat_id,
            "due_date": date_str or None,
            "due_time": time_str or None,
        }

        if self.on_save:
            self.on_save(data)
        self.destroy()


class EditTaskDialog(ctk.CTkToplevel):
    """
    Modal dialog for editing an existing task.
    Pre-fills all fields with the task's current data.

    Args:
        master:      Parent window.
        colors:      Color dictionary from theme.
        task:        The Task object to edit.
        categories:  List of Category objects for the dropdown.
        on_save:     Callback when task is saved — fn(task_id, data_dict).
    """

    def __init__(self, master, colors, task, categories, on_save=None, **kwargs):
        super().__init__(master, **kwargs)
        self.colors = colors
        self.task = task
        self.categories = categories
        self.on_save = on_save

        self.title("Edit Task")
        self.geometry("480x560")
        self.resizable(False, False)
        self.configure(fg_color=colors["bg_primary"])

        self.transient(master)
        self.grab_set()

        self._build()
        self.after(100, self.focus_force)

    def _build(self):
        colors = self.colors
        task = self.task

        # ── Header ─────────────────────────────────────────────────
        header = ctk.CTkLabel(
            self, text="Edit Task", font=FONTS["heading"],
            text_color=colors["text_primary"],
        )
        header.pack(pady=(PADDING["xl"], PADDING["lg"]))

        form = ctk.CTkFrame(self, fg_color="transparent")
        form.pack(fill="x", padx=PADDING["xl"])

        # Title
        ctk.CTkLabel(form, text="Title *", font=FONTS["caption_bold"],
                      text_color=colors["text_secondary"]).pack(anchor="w", pady=(0, 4))
        self.title_entry = ctk.CTkEntry(
            form, font=FONTS["body"], height=40, corner_radius=RADIUS["sm"],
            fg_color=colors["bg_tertiary"], border_color=colors["border"],
            text_color=colors["text_primary"],
        )
        self.title_entry.insert(0, task.title)
        self.title_entry.pack(fill="x", pady=(0, PADDING["md"]))

        # Description
        ctk.CTkLabel(form, text="Description", font=FONTS["caption_bold"],
                      text_color=colors["text_secondary"]).pack(anchor="w", pady=(0, 4))
        self.desc_entry = ctk.CTkTextbox(
            form, height=70, font=FONTS["body"], corner_radius=RADIUS["sm"],
            fg_color=colors["bg_tertiary"], border_color=colors["border"],
            text_color=colors["text_primary"], border_width=1,
        )
        if task.description:
            self.desc_entry.insert("1.0", task.description)
        self.desc_entry.pack(fill="x", pady=(0, PADDING["md"]))

        # Priority + Category
        row1 = ctk.CTkFrame(form, fg_color="transparent")
        row1.pack(fill="x", pady=(0, PADDING["md"]))
        row1.grid_columnconfigure(0, weight=1)
        row1.grid_columnconfigure(1, weight=1)

        pri_frame = ctk.CTkFrame(row1, fg_color="transparent")
        pri_frame.grid(row=0, column=0, sticky="ew", padx=(0, PADDING["sm"]))
        ctk.CTkLabel(pri_frame, text="Priority", font=FONTS["caption_bold"],
                      text_color=colors["text_secondary"]).pack(anchor="w", pady=(0, 4))
        self.priority_var = ctk.StringVar(value=task.priority)
        ctk.CTkOptionMenu(
            pri_frame, variable=self.priority_var,
            values=["Low", "Medium", "High"],
            font=FONTS["body"], height=40, corner_radius=RADIUS["sm"],
            fg_color=colors["bg_tertiary"], button_color=colors["accent_blue"],
            button_hover_color=colors["accent_blue_hover"],
            text_color=colors["text_primary"],
            dropdown_fg_color=colors["bg_secondary"],
            dropdown_text_color=colors["text_primary"],
            dropdown_hover_color=colors["bg_hover"],
        ).pack(fill="x")

        cat_frame = ctk.CTkFrame(row1, fg_color="transparent")
        cat_frame.grid(row=0, column=1, sticky="ew", padx=(PADDING["sm"], 0))
        ctk.CTkLabel(cat_frame, text="Category", font=FONTS["caption_bold"],
                      text_color=colors["text_secondary"]).pack(anchor="w", pady=(0, 4))

        cat_names = ["None"] + [c.name for c in self.categories]
        current_cat = "None"
        if task.category_name:
            current_cat = task.category_name
        self.category_var = ctk.StringVar(value=current_cat)
        ctk.CTkOptionMenu(
            cat_frame, variable=self.category_var, values=cat_names,
            font=FONTS["body"], height=40, corner_radius=RADIUS["sm"],
            fg_color=colors["bg_tertiary"], button_color=colors["accent_blue"],
            button_hover_color=colors["accent_blue_hover"],
            text_color=colors["text_primary"],
            dropdown_fg_color=colors["bg_secondary"],
            dropdown_text_color=colors["text_primary"],
            dropdown_hover_color=colors["bg_hover"],
        ).pack(fill="x")

        # Date + Time
        row2 = ctk.CTkFrame(form, fg_color="transparent")
        row2.pack(fill="x", pady=(0, PADDING["md"]))
        row2.grid_columnconfigure(0, weight=1)
        row2.grid_columnconfigure(1, weight=1)

        date_frame = ctk.CTkFrame(row2, fg_color="transparent")
        date_frame.grid(row=0, column=0, sticky="ew", padx=(0, PADDING["sm"]))
        ctk.CTkLabel(date_frame, text="Due Date", font=FONTS["caption_bold"],
                      text_color=colors["text_secondary"]).pack(anchor="w", pady=(0, 4))
        self.date_entry = ctk.CTkEntry(
            date_frame, placeholder_text="YYYY-MM-DD",
            font=FONTS["body"], height=40, corner_radius=RADIUS["sm"],
            fg_color=colors["bg_tertiary"], border_color=colors["border"],
            text_color=colors["text_primary"],
        )
        if task.due_date:
            self.date_entry.insert(0, task.due_date)
        self.date_entry.pack(fill="x")

        time_frame = ctk.CTkFrame(row2, fg_color="transparent")
        time_frame.grid(row=0, column=1, sticky="ew", padx=(PADDING["sm"], 0))
        ctk.CTkLabel(time_frame, text="Due Time", font=FONTS["caption_bold"],
                      text_color=colors["text_secondary"]).pack(anchor="w", pady=(0, 4))
        self.time_entry = ctk.CTkEntry(
            time_frame, placeholder_text="HH:MM",
            font=FONTS["body"], height=40, corner_radius=RADIUS["sm"],
            fg_color=colors["bg_tertiary"], border_color=colors["border"],
            text_color=colors["text_primary"],
        )
        if task.due_time:
            self.time_entry.insert(0, task.due_time)
        self.time_entry.pack(fill="x")

        # Error label
        self.error_label = ctk.CTkLabel(
            self, text="", font=FONTS["caption"], text_color=colors["error"],
        )
        self.error_label.pack(pady=(PADDING["sm"], 0))

        # Buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=PADDING["xl"], pady=PADDING["lg"])

        ctk.CTkButton(
            btn_frame, text="Cancel", font=FONTS["body_bold"],
            fg_color="transparent", border_width=1,
            border_color=colors["border"], text_color=colors["text_secondary"],
            hover_color=colors["bg_hover"], height=42, corner_radius=RADIUS["sm"],
            command=self.destroy,
        ).pack(side="left", expand=True, fill="x", padx=(0, PADDING["sm"]))

        ctk.CTkButton(
            btn_frame, text="Save Changes", font=FONTS["body_bold"],
            fg_color=colors["accent_blue"], hover_color=colors["accent_blue_hover"],
            text_color=colors["text_on_accent"], height=42, corner_radius=RADIUS["sm"],
            command=self._on_save,
        ).pack(side="left", expand=True, fill="x")

    def _on_save(self):
        title = self.title_entry.get().strip()
        valid, msg = validate_task_title(title)
        if not valid:
            self.error_label.configure(text=msg)
            return

        date_str = self.date_entry.get().strip()
        valid, msg = validate_date(date_str)
        if not valid:
            self.error_label.configure(text=msg)
            return

        time_str = self.time_entry.get().strip()
        valid, msg = validate_time(time_str)
        if not valid:
            self.error_label.configure(text=msg)
            return

        cat_name = self.category_var.get()
        cat_id = None
        for c in self.categories:
            if c.name == cat_name:
                cat_id = c.id
                break

        data = {
            "title": title,
            "description": self.desc_entry.get("1.0", "end-1c").strip(),
            "priority": self.priority_var.get(),
            "category_id": cat_id,
            "due_date": date_str or None,
            "due_time": time_str or None,
        }

        if self.on_save:
            self.on_save(self.task.id, data)
        self.destroy()


class AddCategoryDialog(ctk.CTkToplevel):
    """
    Modal dialog for creating a new category.

    Args:
        master:   Parent window.
        colors:   Color dictionary from theme.
        on_save:  Callback — fn(name, icon, color).
    """

    def __init__(self, master, colors, on_save=None, **kwargs):
        super().__init__(master, **kwargs)
        self.colors = colors
        self.on_save = on_save

        self.title("Add Category")
        self.geometry("400x420")
        self.resizable(False, False)
        self.configure(fg_color=colors["bg_primary"])

        self.transient(master)
        self.grab_set()

        self.selected_icon = ctk.StringVar(value="📁")
        self.selected_color = ctk.StringVar(value="#3B82F6")

        self._build()
        self.after(100, self.focus_force)

    def _build(self):
        colors = self.colors

        header = ctk.CTkLabel(
            self, text="New Category", font=FONTS["heading"],
            text_color=colors["text_primary"],
        )
        header.pack(pady=(PADDING["xl"], PADDING["lg"]))

        form = ctk.CTkFrame(self, fg_color="transparent")
        form.pack(fill="x", padx=PADDING["xl"])

        # Name
        ctk.CTkLabel(form, text="Name *", font=FONTS["caption_bold"],
                      text_color=colors["text_secondary"]).pack(anchor="w", pady=(0, 4))
        self.name_entry = ctk.CTkEntry(
            form, placeholder_text="Category name...",
            font=FONTS["body"], height=40, corner_radius=RADIUS["sm"],
            fg_color=colors["bg_tertiary"], border_color=colors["border"],
            text_color=colors["text_primary"],
            placeholder_text_color=colors["text_tertiary"],
        )
        self.name_entry.pack(fill="x", pady=(0, PADDING["md"]))

        # Icon picker
        ctk.CTkLabel(form, text="Icon", font=FONTS["caption_bold"],
                      text_color=colors["text_secondary"]).pack(anchor="w", pady=(0, 4))
        icon_frame = ctk.CTkFrame(form, fg_color=colors["bg_tertiary"], corner_radius=RADIUS["sm"])
        icon_frame.pack(fill="x", pady=(0, PADDING["md"]))

        for i, icon in enumerate(CATEGORY_ICONS):
            btn = ctk.CTkButton(
                icon_frame, text=icon, width=36, height=36,
                fg_color="transparent", hover_color=colors["bg_hover"],
                corner_radius=RADIUS["sm"],
                command=lambda ic=icon: self.selected_icon.set(ic),
            )
            btn.grid(row=i // 9, column=i % 9, padx=2, pady=2)

        # Color picker
        ctk.CTkLabel(form, text="Color", font=FONTS["caption_bold"],
                      text_color=colors["text_secondary"]).pack(anchor="w", pady=(0, 4))
        color_frame = ctk.CTkFrame(form, fg_color=colors["bg_tertiary"], corner_radius=RADIUS["sm"])
        color_frame.pack(fill="x", pady=(0, PADDING["md"]))

        for i, color in enumerate(CATEGORY_COLORS):
            btn = ctk.CTkButton(
                color_frame, text="", width=32, height=32,
                fg_color=color, hover_color=color,
                corner_radius=RADIUS["round"],
                command=lambda c=color: self.selected_color.set(c),
            )
            btn.grid(row=0, column=i, padx=4, pady=6)

        # Error label
        self.error_label = ctk.CTkLabel(
            self, text="", font=FONTS["caption"], text_color=colors["error"],
        )
        self.error_label.pack(pady=(PADDING["sm"], 0))

        # Buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=PADDING["xl"], pady=PADDING["lg"])

        ctk.CTkButton(
            btn_frame, text="Cancel", font=FONTS["body_bold"],
            fg_color="transparent", border_width=1,
            border_color=colors["border"], text_color=colors["text_secondary"],
            hover_color=colors["bg_hover"], height=42, corner_radius=RADIUS["sm"],
            command=self.destroy,
        ).pack(side="left", expand=True, fill="x", padx=(0, PADDING["sm"]))

        ctk.CTkButton(
            btn_frame, text="Create", font=FONTS["body_bold"],
            fg_color=colors["accent_blue"], hover_color=colors["accent_blue_hover"],
            text_color=colors["text_on_accent"], height=42, corner_radius=RADIUS["sm"],
            command=self._on_save,
        ).pack(side="left", expand=True, fill="x")

    def _on_save(self):
        name = self.name_entry.get().strip()
        valid, msg = validate_category_name(name)
        if not valid:
            self.error_label.configure(text=msg)
            return

        if self.on_save:
            self.on_save(name, self.selected_icon.get(), self.selected_color.get())
        self.destroy()


class ConfirmDialog(ctk.CTkToplevel):
    """
    A simple confirmation dialog ('Are you sure?').

    Args:
        master:      Parent window.
        colors:      Color dictionary from theme.
        title_text:  Dialog title.
        message:     The confirmation message.
        on_confirm:  Callback when 'Delete' is clicked.
    """

    def __init__(self, master, colors, title_text="Confirm", message="Are you sure?", on_confirm=None, **kwargs):
        super().__init__(master, **kwargs)
        self.on_confirm = on_confirm

        self.title(title_text)
        self.geometry("360x200")
        self.resizable(False, False)
        self.configure(fg_color=colors["bg_primary"])

        self.transient(master)
        self.grab_set()

        # Icon + message
        ctk.CTkLabel(
            self, text="⚠️", font=("Segoe UI", 36),
        ).pack(pady=(PADDING["xl"], PADDING["sm"]))

        ctk.CTkLabel(
            self, text=message, font=FONTS["body"],
            text_color=colors["text_primary"], wraplength=300,
        ).pack(pady=(0, PADDING["lg"]))

        # Buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=PADDING["xl"], pady=(0, PADDING["lg"]))

        ctk.CTkButton(
            btn_frame, text="Cancel", font=FONTS["body_bold"],
            fg_color="transparent", border_width=1,
            border_color=colors["border"], text_color=colors["text_secondary"],
            hover_color=colors["bg_hover"], height=40, corner_radius=RADIUS["sm"],
            command=self.destroy,
        ).pack(side="left", expand=True, fill="x", padx=(0, PADDING["sm"]))

        ctk.CTkButton(
            btn_frame, text="Delete", font=FONTS["body_bold"],
            fg_color=colors["error"], hover_color="#DC2626",
            text_color=colors["text_on_accent"], height=40, corner_radius=RADIUS["sm"],
            command=self._on_confirm,
        ).pack(side="left", expand=True, fill="x")

        self.after(100, self.focus_force)

    def _on_confirm(self):
        if self.on_confirm:
            self.on_confirm()
        self.destroy()


class WelcomeDialog(ctk.CTkToplevel):
    """
    First-launch dialog asking for the user's name.

    Args:
        master:   Parent window.
        colors:   Color dictionary from theme.
        on_save:  Callback — fn(username).
    """

    def __init__(self, master, colors, on_save=None, **kwargs):
        super().__init__(master, **kwargs)
        self.colors = colors
        self.on_save = on_save

        self.title("Welcome to Focus")
        self.geometry("420x300")
        self.resizable(False, False)
        self.configure(fg_color=colors["bg_primary"])

        self.transient(master)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self._on_save_click)  # Force name entry

        self._build()
        self.after(100, self.focus_force)

    def _build(self):
        colors = self.colors

        # Welcome text
        ctk.CTkLabel(
            self, text="👋", font=("Segoe UI", 48),
        ).pack(pady=(PADDING["xl"], PADDING["sm"]))

        ctk.CTkLabel(
            self, text="Welcome to Focus!", font=FONTS["heading_lg"],
            text_color=colors["text_primary"],
        ).pack(pady=(0, PADDING["xs"]))

        ctk.CTkLabel(
            self, text="Let's personalize your experience.\nWhat should we call you?",
            font=FONTS["body"], text_color=colors["text_secondary"],
        ).pack(pady=(0, PADDING["lg"]))

        # Name input
        self.name_entry = ctk.CTkEntry(
            self, placeholder_text="Enter your name...",
            font=FONTS["body"], height=44, width=280, corner_radius=RADIUS["md"],
            fg_color=colors["bg_tertiary"], border_color=colors["border"],
            text_color=colors["text_primary"],
            placeholder_text_color=colors["text_tertiary"],
            justify="center",
        )
        self.name_entry.pack(pady=(0, PADDING["lg"]))
        self.name_entry.bind("<Return>", lambda e: self._on_save_click())

        # Continue button
        ctk.CTkButton(
            self, text="Get Started →", font=FONTS["body_bold"],
            fg_color=colors["accent_blue"], hover_color=colors["accent_blue_hover"],
            text_color=colors["text_on_accent"], height=44, width=200,
            corner_radius=RADIUS["md"],
            command=self._on_save_click,
        ).pack()

    def _on_save_click(self):
        name = self.name_entry.get().strip()
        if not name:
            name = "User"  # Fallback default
        if self.on_save:
            self.on_save(name)
        self.destroy()
