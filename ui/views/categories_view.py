"""
categories_view.py — The category management view.

Displays all categories in a grid. Allows editing, creating, and deleting categories,
with pending task counts shown on each category card.
"""

import customtkinter as ctk
from ui.theme import FONTS, PADDING, RADIUS
from ui.components.category_card import CategoryCard
from ui.components.dialogs import AddCategoryDialog, ConfirmDialog


class CategoriesView(ctk.CTkFrame):
    """View showing all categories, with options to create and modify them."""

    def __init__(self, master, app, colors, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.app = app
        self.colors = colors
        self.category_ctrl = app.category_ctrl

        self._build()

    def _build(self):
        colors = self.colors

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # ── Header ─────────────────────────────────────────────────
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, PADDING["lg"]))

        ctk.CTkLabel(
            header_frame,
            text="Task Categories",
            font=FONTS["heading_lg"],
            text_color=colors["text_primary"],
        ).pack(side="left")

        add_cat_btn = ctk.CTkButton(
            header_frame,
            text="+ Add New",
            font=FONTS["body_bold"],
            fg_color=colors["accent_blue"],
            hover_color=colors["accent_blue_hover"],
            text_color=colors["text_on_accent"],
            corner_radius=RADIUS["md"],
            height=36,
            command=self._on_add_category,
        )
        add_cat_btn.pack(side="right")

        # ── Scrollable list of categories ──────────────────────────
        self.list_container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.list_container.grid(row=1, column=0, sticky="nsew")

        self._load_categories()

    def _load_categories(self):
        """Redraw all categories into the container."""
        for child in self.list_container.winfo_children():
            child.destroy()

        categories = self.category_ctrl.get_categories_with_counts()

        if not categories:
            ctk.CTkLabel(
                self.list_container,
                text="No categories created yet.",
                font=FONTS["body"],
                text_color=self.colors["text_tertiary"],
            ).pack(pady=PADDING["xxl"])
            return

        # Display as full-width cards inside the list
        for cat in categories:
            # We don't delete system default categories to avoid breaking standard operations,
            # but allow delete on others. Or we can allow deleting all categories since DB
            # has ON DELETE SET NULL on the foreign keys.
            card = CategoryCard(
                self.list_container,
                cat,
                self.colors,
                on_click=self._on_category_click,
                on_edit=self._on_edit_category,
                on_delete=self._on_delete_category,
                compact=False,
            )
            card.pack(fill="x", pady=6)

    def _on_category_click(self, category):
        """Navigate to TasksView filtered by this category."""
        self.app.navigate_to("tasks")
        from ui.views.tasks_view import TasksView
        if isinstance(self.app.current_view, TasksView):
            self.app.current_view.category_filter_var.set(category.name)
            self.app.current_view._filter_tasks()

    def _on_add_category(self):
        """Open AddCategory dialog."""
        AddCategoryDialog(
            self.app,
            self.colors,
            on_save=self._save_new_category,
        )

    def _save_new_category(self, name, icon, color):
        """Create category and reload."""
        try:
            self.category_ctrl.create_category(name, icon, color)
            self._load_categories()
        except Exception as e:
            # Duplicate category name error
            print(f"Error saving category: {e}")

    def _on_edit_category(self, category):
        """Edit category logic."""
        # Simple prompt for name update (keep it simple for now, or just reuse Add dialog logic)
        dialog = ctk.CTkInputDialog(
            title="Edit Category",
            text=f"Change category name for '{category.name}':",
        )
        # Center dialog roughly
        dialog.geometry("+450+300")
        new_name = dialog.get_input()
        if new_name and new_name.strip():
            self.category_ctrl.update_category(category.id, name=new_name.strip())
            self._load_categories()

    def _on_delete_category(self, cat_id):
        """Open deletion confirm dialog."""
        ConfirmDialog(
            self.app,
            self.colors,
            title_text="Delete Category",
            message="Are you sure you want to delete this category? Linked tasks will not be deleted.",
            on_confirm=lambda: [self.category_ctrl.delete_category(cat_id), self._load_categories()]
        )
