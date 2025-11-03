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

def get_priority_input():
    """Prompt user to select a priority level."""
    print("\nSelect priority level:")
    print("  1 - High")
    print("  2 - Medium")
    print("  3 - Low")
    
    while True:
        try:
            choice = input("Enter priority (1-3): ").strip()
            if choice == "1":
                return "high"
            elif choice == "2":
                return "medium"
            elif choice == "3":
                return "low"
            else:
                print("Invalid choice. Please enter 1, 2, or 3.")
        except (EOFError, KeyboardInterrupt):
            print("\nOperation cancelled.")
            sys.exit(0)

def add_task(description):
    """Add a new task."""
    tasks = load_tasks()
    
    # Get priority from user
    priority = get_priority_input()
    
    # Find the maximum ID and add 1, or use 1 if no tasks exist
    max_id = max([task["id"] for task in tasks], default=0)
    task = {
        "id": max_id + 1,
        "description": description,
        "priority": priority,
        "completed": False,
        "created_at": datetime.now().isoformat()
    }
    tasks.append(task)
    save_tasks(tasks)
    print(f"✓ Task added: {description} (Priority: {priority})")

def get_priority_symbol(priority):
    """Return a symbol representing the priority level."""
    symbols = {
        "high": "!!!",
        "medium": "!!",
        "low": "!"
    }
    return symbols.get(priority, "!")

def list_tasks():
    """Display all tasks."""
    tasks = load_tasks()
    if not tasks:
        print("No tasks yet!")
        return
    
    print("\n" + "="*60)
    print("TASKS".center(60))
    print("="*60)
    for task in tasks:
        status = "✓" if task["completed"] else "○"
        priority = task.get("priority", "medium")  # Default to medium for old tasks
        priority_symbol = get_priority_symbol(priority)
        print(f"{status} [{task['id']}] {priority_symbol} {task['description']} ({priority})")
    print("="*60 + "\n")

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
    
    print("\n" + "="*60)
    print(f"SEARCH RESULTS: '{keyword}'".center(60))
    print("="*60)
    for task in matching_tasks:
        status = "✓" if task["completed"] else "○"
        priority = task.get("priority", "medium")
        priority_symbol = get_priority_symbol(priority)
        print(f"{status} [{task['id']}] {priority_symbol} {task['description']} ({priority})")
    print("="*60)
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

def change_priority(task_id):
    """Change the priority of a task."""
    tasks = load_tasks()
    for task in tasks:
        if task["id"] == task_id:
            old_priority = task.get("priority", "medium")
            print(f"\nCurrent task: {task['description']}")
            print(f"Current priority: {old_priority}")
            
            new_priority = get_priority_input()
            task["priority"] = new_priority
            save_tasks(tasks)
            print(f"✓ Task {task_id} priority changed from {old_priority} to {new_priority}")
            return
    print(f"Task {task_id} not found")

def show_usage():
    """Display usage information."""
    print("\n" + "="*60)
    print("TASK MANAGER - USAGE".center(60))
    print("="*60)
    print("python script.py add <description>     - Add a new task")
    print("python script.py list                  - List all tasks")
    print("python script.py search <keyword>      - Search for tasks")
    print("python script.py complete <task_id>    - Complete a task")
    print("python script.py delete <task_id>      - Delete a task")
    print("python script.py change <task_id>      - Change task priority")
    print("="*60 + "\n") 


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
    
    elif command == "change":
        if len(sys.argv) < 3:
            print("Error: Please provide a task ID")
            print("Usage: python script.py change <task_id>")
            sys.exit(1)
        try:
            task_id = int(sys.argv[2])
            change_priority(task_id)
        except ValueError:
            print("Error: Task ID must be a number")
            sys.exit(1)

    elif command == "help":
        show_usage()
    
    else:
        print(f"Error: Unknown command '{command}'")
        show_usage()
        sys.exit(1)

if __name__ == "__main__":
    main()