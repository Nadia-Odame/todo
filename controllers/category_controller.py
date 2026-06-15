"""
category_controller.py — Business logic for category management.

Handles CRUD operations for task categories / focus areas.
"""

from database import Database
from models import Category


class CategoryController:
    """Handles all category-related operations."""

    def __init__(self, db: Database):
        self.db = db

    def create_category(
        self, name: str, icon: str = "📁", color: str = "#3B82F6"
    ) -> int:
        """
        Create a new category.

        Args:
            name:  Category name (must be unique).
            icon:  Emoji icon for display.
            color: Hex color string.

        Returns:
            The ID of the newly created category.
        """
        cursor = self.db.execute(
            "INSERT INTO categories (name, icon, color) VALUES (?, ?, ?)",
            (name, icon, color),
        )
        return cursor.lastrowid

    def update_category(self, cat_id: int, **fields) -> None:
        """
        Update one or more fields on an existing category.

        Args:
            cat_id:  Category ID to update.
            **fields: Keyword arguments (name, icon, color).
        """
        allowed = {"name", "icon", "color"}
        updates = {k: v for k, v in fields.items() if k in allowed}
        if not updates:
            return

        set_clause = ", ".join(f"{col} = ?" for col in updates)
        values = list(updates.values()) + [cat_id]
        self.db.execute(
            f"UPDATE categories SET {set_clause} WHERE id = ?",
            tuple(values),
        )

    def delete_category(self, cat_id: int) -> None:
        """
        Delete a category by ID.
        Tasks referencing this category will have their category_id set to NULL
        (enforced by ON DELETE SET NULL in the schema).
        """
        self.db.execute("DELETE FROM categories WHERE id = ?", (cat_id,))

    def get_all_categories(self) -> list[Category]:
        """Return all categories ordered by name."""
        rows = self.db.fetch_all(
            "SELECT * FROM categories ORDER BY name ASC"
        )
        return [Category.from_row(r) for r in rows]

    def get_category_by_id(self, cat_id: int) -> Category | None:
        """Return a single category by ID, or None."""
        row = self.db.fetch_one("SELECT * FROM categories WHERE id = ?", (cat_id,))
        return Category.from_row(row) if row else None

    def get_categories_with_counts(self) -> list[Category]:
        """
        Return all categories with the count of pending (incomplete) tasks.

        Returns:
            List of Category objects with pending_count populated.
        """
        rows = self.db.fetch_all(
            """SELECT c.*,
                      COALESCE(SUM(CASE WHEN t.completed = 0 THEN 1 ELSE 0 END), 0) AS pending_count
               FROM categories c
               LEFT JOIN tasks t ON t.category_id = c.id
               GROUP BY c.id
               ORDER BY c.name ASC"""
        )
        return [Category.from_row(r) for r in rows]
