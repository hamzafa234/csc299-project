import json
import os
import sys
from datetime import datetime

TASKS_FILE = "tasks.json"

def load_tasks():
    """Load tasks from JSON file."""
    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, "r") as f:
            return json.load(f)
    return []

def save_tasks(tasks):
    """Save tasks to JSON file."""
    with open(TASKS_FILE, "w") as f:
        json.dump(tasks, f, indent=2)

def add_task(description):
    """Add a new task."""
    tasks = load_tasks()
    # Fix: Find the maximum ID and add 1, or use 1 if no tasks exist
    max_id = max([task["id"] for task in tasks], default=0)
    task = {
        "id": max_id + 1,
        "description": description,
        "completed": False,
        "created_at": datetime.now().isoformat()
    }
    tasks.append(task)
    save_tasks(tasks)
    print(f"✓ Task added: {description}")

def list_tasks():
    """Display all tasks."""
    tasks = load_tasks()
    if not tasks:
        print("No tasks yet!")
        return
    
    print("\n" + "="*50)
    print("TASKS".center(50))
    print("="*50)
    for task in tasks:
        status = "✓" if task["completed"] else "○"
        print(f"{status} [{task['id']}] {task['description']}")
    print("="*50 + "\n")

def search_tasks(keyword):
    """Search for tasks containing the keyword."""
    tasks = load_tasks()
    keyword_lower = keyword.lower()
    
    # Filter tasks that contain the keyword (case-insensitive)
    matching_tasks = [
        task for task in tasks 
        if keyword_lower in task["description"].lower()
    ]
    
    if not matching_tasks:
        print(f"No tasks found matching '{keyword}'")
        return
    
    print("\n" + "="*50)
    print(f"SEARCH RESULTS: '{keyword}'".center(50))
    print("="*50)
    for task in matching_tasks:
        status = "✓" if task["completed"] else "○"
        print(f"{status} [{task['id']}] {task['description']}")
    print("="*50)
    print(f"Found {len(matching_tasks)} task(s)\n")

def complete_task(task_id):
    """Mark a task as completed."""
    tasks = load_tasks()
    for task in tasks:
        if task["id"] == task_id:
            task["completed"] = True
            save_tasks(tasks)
            print(f"✓ Task {task_id} marked as completed")
            return
    print(f"Task {task_id} not found")

def delete_task(task_id):
    """Delete a task."""
    tasks = load_tasks()
    initial_length = len(tasks)
    tasks = [t for t in tasks if t["id"] != task_id]
    
    if len(tasks) == initial_length:
        print(f"Task {task_id} not found")
    else:
        save_tasks(tasks)
        print(f"✓ Task {task_id} deleted")

def show_usage():
    """Display usage information."""
    print("\n" + "="*50)
    print("TASK MANAGER - USAGE".center(50))
    print("="*50)
    print("python script.py add <description>     - Add a new task")
    print("python script.py list                  - List all tasks")
    print("python script.py search <keyword>      - Search for tasks")
    print("python script.py complete <task_id>    - Complete a task")
    print("python script.py delete <task_id>      - Delete a task")
    print("="*50 + "\n")

def main():
    """Main program with command-line arguments."""
    if len(sys.argv) < 2:
        show_usage()
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "add":
        if len(sys.argv) < 3:
            print("Error: Please provide a task description")
            print("Usage: python script.py add <description>")
            sys.exit(1)
        description = " ".join(sys.argv[2:])
        add_task(description)
    
    elif command == "list":
        list_tasks()
    
    elif command == "search":
        if len(sys.argv) < 3:
            print("Error: Please provide a search keyword")
            print("Usage: python script.py search <keyword>")
            sys.exit(1)
        keyword = " ".join(sys.argv[2:])
        search_tasks(keyword)
    
    elif command == "complete":
        if len(sys.argv) < 3:
            print("Error: Please provide a task ID")
            print("Usage: python script.py complete <task_id>")
            sys.exit(1)
        try:
            task_id = int(sys.argv[2])
            complete_task(task_id)
        except ValueError:
            print("Error: Task ID must be a number")
            sys.exit(1)
    
    elif command == "delete":
        if len(sys.argv) < 3:
            print("Error: Please provide a task ID")
            print("Usage: python script.py delete <task_id>")
            sys.exit(1)
        try:
            task_id = int(sys.argv[2])
            delete_task(task_id)
        except ValueError:
            print("Error: Task ID must be a number")
            sys.exit(1)
    
    else:
        print(f"Error: Unknown command '{command}'")
        show_usage()
        sys.exit(1)

if __name__ == "__main__":
    main()
