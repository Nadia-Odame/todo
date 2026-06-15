"""
csv_export.py — Export tasks to CSV format.

Provides functionality to save tasks as a CSV file using a file dialog.
"""

import csv
from tkinter import filedialog
from models import Task


def export_tasks_to_csv(tasks: list[Task]) -> str | None:
    """
    Export a list of tasks to a CSV file.

    Opens a file-save dialog for the user to choose a destination,
    then writes all task data to that file.

    Args:
        tasks: List of Task objects to export.

    Returns:
        The file path if saved successfully, or None if cancelled.
    """
    filepath = filedialog.asksaveasfilename(
        title="Export Tasks to CSV",
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        initialfile="focus_tasks_export.csv",
    )

    if not filepath:
        return None  # User cancelled

    try:
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)

            # Header row
            writer.writerow([
                "ID", "Title", "Description", "Priority",
                "Category", "Due Date", "Due Time",
                "Completed", "Created At", "Updated At",
            ])

            # Data rows
            for task in tasks:
                writer.writerow([
                    task.id,
                    task.title,
                    task.description,
                    task.priority,
                    task.category_name or "Uncategorized",
                    task.due_date or "",
                    task.due_time or "",
                    "Yes" if task.completed else "No",
                    task.created_at,
                    task.updated_at,
                ])

        return filepath
    except (IOError, OSError) as e:
        print(f"Error exporting to CSV: {e}")
        return None
