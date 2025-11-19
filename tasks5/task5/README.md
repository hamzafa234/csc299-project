# Task Management System

A command-line task management application built with Python that helps you organize and track your tasks efficiently.

## Features

- ✅ Add and view tasks
- ✅ Mark tasks as complete/incomplete
- ✅ Remove tasks
- ✅ Assign priority levels (high, medium, low)
- ✅ Create hierarchical subtasks (up to 3 levels)
- ✅ Search tasks by keywords
- 📊 JSON-based storage
- 🎨 Color-coded output for better readability

## Requirements

- Python 3.11 or higher
- macOS (POSIX-compliant)

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd task5
```

2. Create a virtual environment (optional but recommended):
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install development dependencies (for testing):
```bash
pip install -r requirements-dev.txt
```

## Usage

### Basic Commands

**Add a task:**
```bash
python -m src.main add "Complete project documentation"
python -m src.main add "Review code" --priority high
```

**List all tasks:**
```bash
python -m src.main list
```

**Mark task as complete:**
```bash
python -m src.main complete <task-id>
```

**Mark task as incomplete:**
```bash
python -m src.main uncomplete <task-id>
```

**Remove a task:**
```bash
python -m src.main remove <task-id>
python -m src.main remove <task-id> --force  # Skip confirmation
```

**Set task priority:**
```bash
python -m src.main priority <task-id> high
```

**Search tasks:**
```bash
python -m src.main search keyword1 keyword2
python -m src.main search "exact phrase" --case-sensitive
```

**Show task details:**
```bash
python -m src.main show <task-id>
```

### Global Options

- `--help` - Show help message
- `--version` - Display version information
- `--json` - Output in JSON format
- `--data-file PATH` - Specify custom data file location
- `--verbose` - Show detailed operation information
- `--quiet` - Suppress all non-error output

### Environment Variables

- `TASK_DATA_FILE` - Default data file location
- `TASK_NO_COLOR` - Disable colored output

## Development

### Running Tests

```bash
pytest
pytest --cov=src --cov-report=html
```

### Project Structure

```
task5/
├── src/
│   ├── models/          # Task entity and data storage
│   ├── services/        # Business logic
│   ├── cli/             # Command-line interface
│   └── main.py          # Entry point
├── tests/
│   ├── unit/            # Unit tests
│   └── integration/     # Integration tests
├── tasks.json           # Task data (created automatically)
└── README.md
```

## License

MIT License
