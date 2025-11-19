# CLI Interface Contract: Task Management System

**Phase**: 1 - Design & Contracts  
**Date**: 2025-11-18  
**Purpose**: Define command-line interface contracts for all operations

## Global Options

Available for all commands:

| Flag | Description | Default |
|------|-------------|---------|
| `--help`, `-h` | Show help message and exit | N/A |
| `--version`, `-v` | Show version and exit | N/A |
| `--json` | Output in JSON format | false (human-readable) |
| `--data-file PATH` | Path to tasks JSON file | `./tasks.json` |
| `--verbose` | Enable verbose output | false |
| `--quiet` | Suppress non-error output | false |

## Commands

### 1. Add Task

**Command**: `task add DESCRIPTION [OPTIONS]`

**Purpose**: Create a new task with description and optional properties

**Arguments**:
- `DESCRIPTION` (required): Task description text (1-500 characters)

**Options**:
| Flag | Description | Default | Validation |
|------|-------------|---------|------------|
| `--priority LEVEL`, `-p LEVEL` | Priority level | `medium` | Must be: high, medium, or low |
| `--parent ID` | Parent task ID for subtask | null | Must be valid existing task ID |

**Examples**:
```bash
# Add simple task with default priority
task add "Buy groceries"

# Add high priority task
task add "Fix critical bug" --priority high

# Add subtask to existing task
task add "Research options" --parent a3f2b1c4

# Shorter version with flags
task add "Call client" -p high
```

**Success Output** (human-readable):
```
✓ Task added successfully
  ID: a3f2b1c4
  Description: Buy groceries
  Priority: medium
  Created: 2025-11-18 10:30
```

**Success Output** (--json):
```json
{
  "status": "success",
  "task": {
    "id": "a3f2b1c4-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "description": "Buy groceries",
    "completed": false,
    "priority": "medium",
    "created_at": "2025-11-18T10:30:00.000Z",
    "parent_id": null,
    "subtasks": []
  }
}
```

**Error Conditions**:
| Error | Exit Code | Message |
|-------|-----------|---------|
| Empty description | 1 | "Error: Task description cannot be empty" |
| Description too long | 1 | "Error: Task description must be 500 characters or less (got: N)" |
| Invalid priority | 1 | "Error: Priority must be 'high', 'medium', or 'low' (got: 'X')" |
| Parent not found | 1 | "Error: Parent task 'X' not found" |
| Max depth exceeded | 1 | "Error: Cannot add subtask - maximum nesting depth (3 levels) reached" |
| File write error | 2 | "Error: Failed to save tasks: [reason]" |

---

### 2. List Tasks

**Command**: `task list [OPTIONS]`

**Purpose**: Display all tasks or filter by criteria

**Options**:
| Flag | Description | Default |
|------|-------------|---------|
| `--priority LEVEL`, `-p LEVEL` | Filter by priority | all |
| `--status STATUS`, `-s STATUS` | Filter by status (complete/incomplete) | all |
| `--parent ID` | Show only subtasks of parent | all tasks |

**Examples**:
```bash
# List all tasks
task list

# List only high priority tasks
task list --priority high

# List completed tasks
task list --status complete

# List incomplete tasks
task list -s incomplete

# List subtasks of specific task
task list --parent a3f2b1c4
```

**Success Output** (human-readable):
```
HIGH PRIORITY (2 tasks)
  [1] ✓ Fix critical bug
      ID: a3f2b1c4 | Created: 2025-11-18 10:30
      
  [2] ○ Complete report
      ID: b4e3c2d5 | Created: 2025-11-18 11:00
      Subtasks: 2 (1 completed)

MEDIUM PRIORITY (1 task)
  [3] ○ Buy groceries
      ID: c5d4e3f6 | Created: 2025-11-18 12:00

Total: 3 tasks (1 completed, 2 pending)
```

**Success Output** (--json):
```json
{
  "status": "success",
  "tasks": [
    {
      "id": "a3f2b1c4-xxxx",
      "description": "Fix critical bug",
      "completed": true,
      "priority": "high",
      "created_at": "2025-11-18T10:30:00.000Z",
      "parent_id": null,
      "subtasks": []
    }
  ],
  "summary": {
    "total": 3,
    "completed": 1,
    "pending": 2
  }
}
```

**Error Conditions**:
| Error | Exit Code | Message |
|-------|-----------|---------|
| Invalid priority filter | 1 | "Error: Priority must be 'high', 'medium', or 'low' (got: 'X')" |
| Invalid status filter | 1 | "Error: Status must be 'complete' or 'incomplete' (got: 'X')" |
| Parent not found | 1 | "Error: Parent task 'X' not found" |
| File read error | 2 | "Error: Failed to load tasks: [reason]" |

**Note**: Empty list is not an error (exit code 0)

---

### 3. Complete Task

**Command**: `task complete TASK_ID`

**Purpose**: Mark a task as completed

**Arguments**:
- `TASK_ID` (required): ID of task to mark complete (full UUID or first 8 chars)

**Examples**:
```bash
# Complete task by full ID
task complete a3f2b1c4-5678-90ab-cdef-1234567890ab

# Complete task by short ID
task complete a3f2b1c4
```

**Success Output** (human-readable):
```
✓ Task completed
  ID: a3f2b1c4
  Description: Buy groceries
```

**Success Output** (--json):
```json
{
  "status": "success",
  "task": {
    "id": "a3f2b1c4-xxxx",
    "description": "Buy groceries",
    "completed": true,
    "priority": "medium",
    "created_at": "2025-11-18T10:30:00.000Z",
    "parent_id": null,
    "subtasks": []
  }
}
```

**Error Conditions**:
| Error | Exit Code | Message |
|-------|-----------|---------|
| Task not found | 1 | "Error: Task 'X' not found" |
| Already completed | 0 | "Task 'X' is already completed" (warning, not error) |
| File write error | 2 | "Error: Failed to save tasks: [reason]" |

---

### 4. Uncomplete Task

**Command**: `task uncomplete TASK_ID`

**Purpose**: Mark a completed task as incomplete

**Arguments**:
- `TASK_ID` (required): ID of task to mark incomplete (full UUID or first 8 chars)

**Examples**:
```bash
# Mark task as incomplete
task uncomplete a3f2b1c4
```

**Success Output** (human-readable):
```
✓ Task marked as incomplete
  ID: a3f2b1c4
  Description: Buy groceries
```

**Error Conditions**: Same as `complete` command

---

### 5. Remove Task

**Command**: `task remove TASK_ID [OPTIONS]`

**Purpose**: Delete a task and optionally its subtasks

**Arguments**:
- `TASK_ID` (required): ID of task to remove (full UUID or first 8 chars)

**Options**:
| Flag | Description | Default |
|------|-------------|---------|
| `--force`, `-f` | Skip confirmation prompt | false (prompt if has subtasks) |

**Examples**:
```bash
# Remove task (prompts if has subtasks)
task remove a3f2b1c4

# Force remove without confirmation
task remove a3f2b1c4 --force
```

**Success Output** (human-readable):
```
✓ Task removed successfully
  Removed 1 task (plus 2 subtasks)
```

**Success Output** (--json):
```json
{
  "status": "success",
  "removed": {
    "count": 3,
    "ids": ["a3f2b1c4-xxxx", "b4e3c2d5-xxxx", "c5d4e3f6-xxxx"]
  }
}
```

**Confirmation Prompt** (when task has subtasks and --force not used):
```
Warning: Task has 2 subtasks. All will be deleted.
Continue? [y/N]:
```

**Error Conditions**:
| Error | Exit Code | Message |
|-------|-----------|---------|
| Task not found | 1 | "Error: Task 'X' not found" |
| User cancelled | 1 | "Operation cancelled" |
| File write error | 2 | "Error: Failed to save tasks: [reason]" |

---

### 6. Set Priority

**Command**: `task priority TASK_ID LEVEL`

**Purpose**: Change the priority level of a task

**Arguments**:
- `TASK_ID` (required): ID of task (full UUID or first 8 chars)
- `LEVEL` (required): New priority level (high/medium/low)

**Examples**:
```bash
# Set task to high priority
task priority a3f2b1c4 high

# Set task to low priority
task priority b4e3c2d5 low
```

**Success Output** (human-readable):
```
✓ Task priority updated
  ID: a3f2b1c4
  Description: Buy groceries
  Priority: medium → high
```

**Success Output** (--json):
```json
{
  "status": "success",
  "task": {
    "id": "a3f2b1c4-xxxx",
    "description": "Buy groceries",
    "completed": false,
    "priority": "high",
    "created_at": "2025-11-18T10:30:00.000Z",
    "parent_id": null,
    "subtasks": []
  },
  "previous_priority": "medium"
}
```

**Error Conditions**:
| Error | Exit Code | Message |
|-------|-----------|---------|
| Task not found | 1 | "Error: Task 'X' not found" |
| Invalid priority | 1 | "Error: Priority must be 'high', 'medium', or 'low' (got: 'X')" |
| File write error | 2 | "Error: Failed to save tasks: [reason]" |

---

### 7. Search Tasks

**Command**: `task search KEYWORDS... [OPTIONS]`

**Purpose**: Search for tasks by keywords in description

**Arguments**:
- `KEYWORDS` (required): One or more keywords to search for

**Options**:
| Flag | Description | Default |
|------|-------------|---------|
| `--case-sensitive` | Enable case-sensitive search | false |

**Examples**:
```bash
# Search for single keyword
task search meeting

# Search for multiple keywords (OR logic)
task search report presentation slides

# Case-sensitive search
task search "Important" --case-sensitive
```

**Success Output** (human-readable):
```
Found 2 matching tasks:

[1] ○ Prepare meeting agenda (high)
    ID: a3f2b1c4 | Created: 2025-11-18 10:30
    
[2] ✓ Attend team meeting (medium)
    ID: b4e3c2d5 | Created: 2025-11-18 11:00
    Parent: Project planning
```

**Success Output** (--json):
```json
{
  "status": "success",
  "query": ["meeting"],
  "results": [
    {
      "id": "a3f2b1c4-xxxx",
      "description": "Prepare meeting agenda",
      "completed": false,
      "priority": "high",
      "created_at": "2025-11-18T10:30:00.000Z",
      "parent_id": null,
      "subtasks": []
    }
  ],
  "count": 2
}
```

**Error Conditions**:
| Error | Exit Code | Message |
|-------|-----------|---------|
| Empty keywords | 1 | "Error: Search keywords cannot be empty" |
| Keywords too long | 1 | "Error: Search keyword exceeds maximum length (100 characters)" |
| File read error | 2 | "Error: Failed to load tasks: [reason]" |

**Note**: No matches is not an error (exit code 0, shows "No tasks found matching: X")

---

### 8. Show Task Details

**Command**: `task show TASK_ID`

**Purpose**: Display detailed information about a specific task

**Arguments**:
- `TASK_ID` (required): ID of task (full UUID or first 8 chars)

**Examples**:
```bash
# Show task details
task show a3f2b1c4
```

**Success Output** (human-readable):
```
Task Details:
  ID: a3f2b1c4-5678-90ab-cdef-1234567890ab
  Description: Complete project proposal
  Status: Incomplete
  Priority: High
  Created: 2025-11-18 10:30:00
  
  Subtasks (2):
    [1] ✓ Research background (b4e3c2d5)
    [2] ○ Write executive summary (c5d4e3f6)
```

**Success Output** (--json):
```json
{
  "status": "success",
  "task": {
    "id": "a3f2b1c4-xxxx",
    "description": "Complete project proposal",
    "completed": false,
    "priority": "high",
    "created_at": "2025-11-18T10:30:00.000Z",
    "parent_id": null,
    "subtasks": ["b4e3c2d5-xxxx", "c5d4e3f6-xxxx"]
  },
  "subtask_details": [
    {
      "id": "b4e3c2d5-xxxx",
      "description": "Research background",
      "completed": true
    }
  ]
}
```

**Error Conditions**:
| Error | Exit Code | Message |
|-------|-----------|---------|
| Task not found | 1 | "Error: Task 'X' not found" |
| File read error | 2 | "Error: Failed to load tasks: [reason]" |

---

## Exit Codes

| Code | Meaning | Usage |
|------|---------|-------|
| 0 | Success | Operation completed successfully |
| 1 | Usage Error | Invalid arguments, validation failure, task not found |
| 2 | Runtime Error | File I/O error, data corruption, system error |

## Output Formats

### Human-Readable Format
- Default format for terminal use
- Uses symbols: ✓ (complete), ○ (incomplete)
- Color-coded when stdout is a TTY:
  - High priority: Red
  - Medium priority: Yellow
  - Low priority: Blue
  - Completed: Gray/dim

### JSON Format (--json flag)
- Machine-readable structured output
- Always valid JSON on success
- Error format:
```json
{
  "status": "error",
  "error": {
    "code": 1,
    "message": "Error description"
  }
}
```

## Environment Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `TASK_DATA_FILE` | Default path to tasks.json | `./tasks.json` |
| `TASK_NO_COLOR` | Disable colored output | not set |

**Note**: Command-line flags override environment variables

---

CLI interface contract complete. Ready for implementation.
