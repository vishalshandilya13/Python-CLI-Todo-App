"""
To-Do List Application (Command-Line Interface)
--------------------------------------------------
A simple, persistent to-do list manager that runs in the terminal.

Features:
    - Add tasks (with optional priority and due date)
    - View all tasks (pending and completed)
    - Update a task's text, priority, or due date
    - Mark a task as complete / incomplete
    - Delete a task
    - Tasks are saved to a local JSON file so they persist between runs

Run with:
    python todo_cli.py
"""

import json
import os
from datetime import datetime

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tasks.json")


class TodoList:
    """Handles loading, saving, and manipulating the list of tasks."""

    def __init__(self, data_file=DATA_FILE):
        self.data_file = data_file
        self.tasks = []
        self.load()

    # ---------- Persistence ----------

    def load(self):
        """Load tasks from the JSON file, if it exists."""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    self.tasks = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.tasks = []
        else:
            self.tasks = []

    def save(self):
        """Persist the current tasks to the JSON file."""
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(self.tasks, f, indent=2)

    # ---------- Core operations ----------

    def add_task(self, title, priority="Medium", due_date=""):
        task = {
            "id": self._next_id(),
            "title": title,
            "priority": priority,
            "due_date": due_date,
            "completed": False,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
        self.tasks.append(task)
        self.save()
        return task

    def _next_id(self):
        return max((t["id"] for t in self.tasks), default=0) + 1

    def find_task(self, task_id):
        for task in self.tasks:
            if task["id"] == task_id:
                return task
        return None

    def update_task(self, task_id, title=None, priority=None, due_date=None):
        task = self.find_task(task_id)
        if not task:
            return False
        if title:
            task["title"] = title
        if priority:
            task["priority"] = priority
        if due_date is not None:
            task["due_date"] = due_date
        self.save()
        return True

    def toggle_complete(self, task_id):
        task = self.find_task(task_id)
        if not task:
            return False
        task["completed"] = not task["completed"]
        self.save()
        return True

    def delete_task(self, task_id):
        task = self.find_task(task_id)
        if not task:
            return False
        self.tasks.remove(task)
        self.save()
        return True

    def list_tasks(self, show_completed=True):
        if show_completed:
            return sorted(self.tasks, key=lambda t: t["completed"])
        return [t for t in self.tasks if not t["completed"]]


# ---------------------------------------------------------------------
# Command-line interface
# ---------------------------------------------------------------------

PRIORITY_CHOICES = ("Low", "Medium", "High")


def print_menu():
    print("\n===== TO-DO LIST =====")
    print("1. View all tasks")
    print("2. Add a task")
    print("3. Update a task")
    print("4. Mark task complete/incomplete")
    print("5. Delete a task")
    print("6. View pending tasks only")
    print("7. Exit")
    print("=======================")


def print_tasks(tasks):
    if not tasks:
        print("  (no tasks to show)")
        return
    for t in tasks:
        status = "✔" if t["completed"] else "✗"
        due = f" | due: {t['due_date']}" if t["due_date"] else ""
        print(f"  [{status}] #{t['id']} ({t['priority']}) {t['title']}{due}")


def prompt_priority(default="Medium"):
    choice = input(f"Priority [Low/Medium/High] (default {default}): ").strip().title()
    return choice if choice in PRIORITY_CHOICES else default


def main():
    todo = TodoList()
    print("Welcome to your To-Do List!")

    while True:
        print_menu()
        choice = input("Choose an option (1-7): ").strip()

        if choice == "1":
            print("\nAll tasks:")
            print_tasks(todo.list_tasks(show_completed=True))

        elif choice == "2":
            title = input("Task description: ").strip()
            if not title:
                print("Task description cannot be empty.")
                continue
            priority = prompt_priority()
            due_date = input("Due date (YYYY-MM-DD, optional): ").strip()
            task = todo.add_task(title, priority, due_date)
            print(f"Added task #{task['id']}.")

        elif choice == "3":
            try:
                task_id = int(input("Task ID to update: ").strip())
            except ValueError:
                print("Please enter a valid numeric ID.")
                continue
            if not todo.find_task(task_id):
                print("Task not found.")
                continue
            new_title = input("New description (leave blank to keep current): ").strip()
            new_priority = prompt_priority(default="")
            new_due = input("New due date (leave blank to keep current): ").strip()
            todo.update_task(
                task_id,
                title=new_title or None,
                priority=new_priority or None,
                due_date=new_due if new_due else None,
            )
            print(f"Task #{task_id} updated.")

        elif choice == "4":
            try:
                task_id = int(input("Task ID to toggle complete: ").strip())
            except ValueError:
                print("Please enter a valid numeric ID.")
                continue
            if todo.toggle_complete(task_id):
                print(f"Task #{task_id} status toggled.")
            else:
                print("Task not found.")

        elif choice == "5":
            try:
                task_id = int(input("Task ID to delete: ").strip())
            except ValueError:
                print("Please enter a valid numeric ID.")
                continue
            if todo.delete_task(task_id):
                print(f"Task #{task_id} deleted.")
            else:
                print("Task not found.")

        elif choice == "6":
            print("\nPending tasks:")
            print_tasks(todo.list_tasks(show_completed=False))

        elif choice == "7":
            print("Goodbye!")
            break

        else:
            print("Invalid option. Please choose a number from 1 to 7.")


if __name__ == "__main__":
    main()
