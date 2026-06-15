"""
task_controller.py — Business logic for task management.

Provides CRUD operations, search/filter, and statistics for tasks.
"""

from datetime import datetime, timedelta
from database import Database
from models import Task


class TaskController:
    """Handles all task-related operations."""

    def __init__(self, db: Database):
        self.db = db

    def create_task(
        self,
        title: str,
        priority: str = "Medium",
        category_id: int = None,
        due_date: str = None,
        due_time: str = None,
        description: str = "",
    ) -> int:
        """
        Create a new task.

        Args:
            title:       Task title (required).
            priority:    'Low', 'Medium', or 'High'.
            category_id: FK to categories table (optional).
            due_date:    Date string in YYYY-MM-DD format.
            due_time:    Time string in HH:MM format.
            description: Optional longer description.

        Returns:
            The ID of the newly created task.
        """
        now = datetime.now().isoformat()
        cursor = self.db.execute(
            """INSERT INTO tasks
               (title, description, priority, category_id, due_date, due_time, completed, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, 0, ?, ?)""",
            (title, description, priority, category_id, due_date, due_time, now, now),
        )
        return cursor.lastrowid

    def update_task(self, task_id: int, **fields) -> None:
        """
        Update one or more fields on an existing task.

        Args:
            task_id: The task to update.
            **fields: Keyword arguments for columns to update
                      (title, description, priority, category_id, due_date, due_time).
        """
        allowed = {"title", "description", "priority", "category_id", "due_date", "due_time"}
        updates = {k: v for k, v in fields.items() if k in allowed}
        if not updates:
            return

        updates["updated_at"] = datetime.now().isoformat()
        set_clause = ", ".join(f"{col} = ?" for col in updates)
        values = list(updates.values()) + [task_id]

        self.db.execute(
            f"UPDATE tasks SET {set_clause} WHERE id = ?",
            tuple(values),
        )

    def delete_task(self, task_id: int) -> None:
        """Delete a task by ID."""
        self.db.execute("DELETE FROM tasks WHERE id = ?", (task_id,))

    def toggle_complete(self, task_id: int) -> bool:
        """
        Toggle the completed status of a task.

        Returns:
            The new completed state (True/False).
        """
        row = self.db.fetch_one("SELECT completed FROM tasks WHERE id = ?", (task_id,))
        if row is None:
            return False
        new_state = 0 if row["completed"] else 1
        self.db.execute(
            "UPDATE tasks SET completed = ?, updated_at = ? WHERE id = ?",
            (new_state, datetime.now().isoformat(), task_id),
        )
        return bool(new_state)

    def get_all_tasks(self) -> list[Task]:
        """Return all tasks, joined with category names, ordered by due date."""
        rows = self.db.fetch_all(
            """SELECT t.*, c.name AS category_name
               FROM tasks t
               LEFT JOIN categories c ON t.category_id = c.id
               ORDER BY t.completed ASC, t.due_date ASC, t.due_time ASC"""
        )
        return [Task.from_row(r) for r in rows]

    def get_tasks_by_date(self, date_str: str) -> list[Task]:
        """
        Return tasks for a specific date.

        Args:
            date_str: Date in YYYY-MM-DD format.
        """
        rows = self.db.fetch_all(
            """SELECT t.*, c.name AS category_name
               FROM tasks t
               LEFT JOIN categories c ON t.category_id = c.id
               WHERE t.due_date = ?
               ORDER BY t.due_time ASC""",
            (date_str,),
        )
        return [Task.from_row(r) for r in rows]

    def get_today_tasks(self) -> list[Task]:
        """Return tasks due today."""
        today = datetime.now().strftime("%Y-%m-%d")
        return self.get_tasks_by_date(today)

    def get_upcoming_tasks(self, days: int = 7) -> list[Task]:
        """
        Return tasks due in the next N days (excluding today).

        Args:
            days: Number of days to look ahead.
        """
        today = datetime.now().strftime("%Y-%m-%d")
        end = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
        rows = self.db.fetch_all(
            """SELECT t.*, c.name AS category_name
               FROM tasks t
               LEFT JOIN categories c ON t.category_id = c.id
               WHERE t.due_date > ? AND t.due_date <= ?
               ORDER BY t.due_date ASC, t.due_time ASC""",
            (today, end),
        )
        return [Task.from_row(r) for r in rows]

    def search_tasks(
        self,
        query: str = "",
        category_id: int = None,
        priority: str = None,
        status: str = None,
    ) -> list[Task]:
        """
        Search and filter tasks.

        Args:
            query:       Search string matched against title.
            category_id: Filter by category ID.
            priority:    Filter by priority level.
            status:      'completed', 'pending', or None for all.

        Returns:
            Filtered list of Task objects.
        """
        sql = """SELECT t.*, c.name AS category_name
                 FROM tasks t
                 LEFT JOIN categories c ON t.category_id = c.id
                 WHERE 1=1"""
        params = []

        if query:
            sql += " AND t.title LIKE ?"
            params.append(f"%{query}%")
        if category_id is not None:
            sql += " AND t.category_id = ?"
            params.append(category_id)
        if priority:
            sql += " AND t.priority = ?"
            params.append(priority)
        if status == "completed":
            sql += " AND t.completed = 1"
        elif status == "pending":
            sql += " AND t.completed = 0"

        sql += " ORDER BY t.completed ASC, t.due_date ASC, t.due_time ASC"
        rows = self.db.fetch_all(sql, tuple(params))
        return [Task.from_row(r) for r in rows]

    def get_stats(self) -> dict:
        """
        Compute task statistics.

        Returns:
            Dict with keys: total, completed, pending, completion_rate,
            completed_this_week, completed_last_week.
        """
        total_row = self.db.fetch_one("SELECT COUNT(*) AS cnt FROM tasks")
        total = total_row["cnt"] if total_row else 0

        completed_row = self.db.fetch_one(
            "SELECT COUNT(*) AS cnt FROM tasks WHERE completed = 1"
        )
        completed = completed_row["cnt"] if completed_row else 0

        pending = total - completed
        rate = round((completed / total * 100), 1) if total > 0 else 0.0

        # Tasks completed this week (Mon–Sun)
        today = datetime.now()
        start_of_week = (today - timedelta(days=today.weekday())).strftime("%Y-%m-%d")
        week_row = self.db.fetch_one(
            "SELECT COUNT(*) AS cnt FROM tasks WHERE completed = 1 AND updated_at >= ?",
            (start_of_week,),
        )
        completed_this_week = week_row["cnt"] if week_row else 0

        # Tasks completed last week
        start_last_week = (
            today - timedelta(days=today.weekday() + 7)
        ).strftime("%Y-%m-%d")
        last_week_row = self.db.fetch_one(
            "SELECT COUNT(*) AS cnt FROM tasks WHERE completed = 1 AND updated_at >= ? AND updated_at < ?",
            (start_last_week, start_of_week),
        )
        completed_last_week = last_week_row["cnt"] if last_week_row else 0

        return {
            "total": total,
            "completed": completed,
            "pending": pending,
            "completion_rate": rate,
            "completed_this_week": completed_this_week,
            "completed_last_week": completed_last_week,
        }

    def get_tasks_with_reminders(self, minutes: int = 30) -> list[Task]:
        """
        Return incomplete tasks due within the next N minutes.
        Used for the reminder notification system.

        Args:
            minutes: Look-ahead window in minutes.
        """
        now = datetime.now()
        today = now.strftime("%Y-%m-%d")
        current_time = now.strftime("%H:%M")
        future_time = (now + timedelta(minutes=minutes)).strftime("%H:%M")

        rows = self.db.fetch_all(
            """SELECT t.*, c.name AS category_name
               FROM tasks t
               LEFT JOIN categories c ON t.category_id = c.id
               WHERE t.completed = 0
                 AND t.due_date = ?
                 AND t.due_time >= ?
                 AND t.due_time <= ?""",
            (today, current_time, future_time),
        )
        return [Task.from_row(r) for r in rows]
