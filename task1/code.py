import json
import os
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
    task = {
        "id": len(tasks) + 1,
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
    tasks = [t for t in tasks if t["id"] != task_id]
    save_tasks(tasks)
    print(f"✓ Task {task_id} deleted")

def show_menu():
    """Display the menu."""
    print("\n" + "="*50)
    print("TASK MANAGER".center(50))
    print("="*50)
    print("1. Add task")
    print("2. List tasks")
    print("3. Complete task")
    print("4. Delete task")
    print("5. Exit")
    print("="*50)

def main():
    """Main program loop."""
    while True:
        show_menu()
        choice = input("Choose an option (1-5): ").strip()
        
        if choice == "1":
            description = input("Enter task description: ").strip()
            if description:
                add_task(description)
            else:
                print("Task description cannot be empty!")
        
        elif choice == "2":
            list_tasks()
        
        elif choice == "3":
            list_tasks()
            try:
                task_id = int(input("Enter task ID to complete: "))
                complete_task(task_id)
            except ValueError:
                print("Invalid ID!")
        
        elif choice == "4":
            list_tasks()
            try:
                task_id = int(input("Enter task ID to delete: "))
                delete_task(task_id)
            except ValueError:
                print("Invalid ID!")
        
        elif choice == "5":
            print("Goodbye!")
            break
        
        else:
            print("Invalid option! Please choose 1-5.")

if __name__ == "__main__":
    main()
