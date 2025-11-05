import json
from datetime import datetime
from tasks3.tasks import add_task, load_tasks, save_tasks, TASKS_FILE
import os

def test_add_task(tmp_path, monkeypatch):
    # Point the TASKS_FILE to a temporary file for testing
    test_file = tmp_path / "tasks.json"
    monkeypatch.setattr("tasks3.tasks.TASKS_FILE", str(test_file))

    # Initially, no tasks exist
    assert not os.path.exists(test_file)

    # Add a new task
    add_task("Buy groceries")

    # Verify the file was created
    assert test_file.exists()

    # Load tasks from file
    with open(test_file, "r") as f:
        tasks = json.load(f)

    # Check that the task was added correctly
    assert len(tasks) == 1
    task = tasks[0]
    assert task["description"] == "Buy groceries"
    assert task["priority"] == "low"
    assert task["completed"] is False
    assert "created_at" in task
    assert isinstance(task["id"], int)

def test_add_multiple_tasks(tmp_path, monkeypatch):
    # Point the TASKS_FILE to a temporary file for testing
    test_file = tmp_path / "tasks.json"
    monkeypatch.setattr("tasks3.tasks.TASKS_FILE", str(test_file))

    # Add the first task
    add_task("Buy groceries")

    # Add a second task
    add_task("Walk the dog")

    # Verify the file was created and tasks were added
    assert test_file.exists()

    # Load tasks from file
    with open(test_file, "r") as f:
        tasks = json.load(f)

    # Check that both tasks were added correctly
    assert len(tasks) == 2

    task1, task2 = tasks

    assert task1["description"] == "Buy groceries"
    assert task2["description"] == "Walk the dog"

    assert task1["priority"] == "low"
    assert task2["priority"] == "low"

    assert task1["completed"] is False
    assert task2["completed"] is False

    assert "created_at" in task1 and "created_at" in task2

    # Ensure the tasks have unique IDs
    assert task1["id"] != task2["id"]

