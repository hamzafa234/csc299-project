# Quick Start Guide: Task Management System

**Phase**: 1 - Design & Contracts  
**Date**: 2025-11-18  
**Purpose**: Guide developers through setup and basic implementation workflow

## Prerequisites

- Python 3.11 or higher
- Git (for version control)
- Basic command-line knowledge
- Text editor or IDE

## Project Setup

### 1. Clone/Navigate to Repository

```bash
cd /path/to/project
```

### 2. Create Project Structure

```bash
# Create source directories
mkdir -p src/{models,services,cli}
mkdir -p tests/{unit,integration}

# Create entry point files
touch src/main.py
touch src/{models,services,cli}/__init__.py

# Create test files
touch tests/conftest.py
```

### 3. Set Up Python Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # macOS/Linux

# Install development dependencies
pip install pytest pytest-cov
```

### 4. Create Requirements Files

**requirements.txt** (runtime dependencies):
```
# Python 3.11+ standard library only
# No external dependencies
```

**requirements-dev.txt** (development dependencies):
```
pytest>=7.4.0
pytest-cov>=4.1.0
black>=23.0.0
mypy>=1.5.0
```

Install dev dependencies:
```bash
pip install -r requirements-dev.txt
```

## Development Workflow

### Phase 1: Implement Data Layer

**Order**: Models → Storage → Tests

1. **Create Task Model** (`src/models/task.py`):
   - Task class with validation
   - Priority enum
   - Helper methods for hierarchy
   
2. **Create Task Store** (`src/models/task_store.py`):
   - JSON file operations
   - Atomic writes
   - Load/save methods

3. **Write Unit Tests** (`tests/unit/test_task.py`, `tests/unit/test_task_store.py`):
   - Test validation rules
   - Test CRUD operations
   - Test edge cases

```bash
# Run tests
pytest tests/unit/ -v
```

### Phase 2: Implement Business Logic

**Order**: Service Layer → Tests

1. **Create Task Service** (`src/services/task_service.py`):
   - Add task
   - List tasks
   - Complete/uncomplete task
   - Remove task
   - Update priority

2. **Create Search Service** (`src/services/search_service.py`):
   - Keyword search
   - Case-insensitive matching
   - Result filtering

3. **Write Unit Tests** (`tests/unit/test_task_service.py`, `tests/unit/test_search_service.py`):
   - Test all service methods
   - Test error conditions
   - Test business rules (depth limits, circular dependencies)

```bash
# Run tests with coverage
pytest tests/unit/ --cov=src --cov-report=html
```

### Phase 3: Implement CLI Interface

**Order**: Parser → Formatter → Commands → Integration Tests

1. **Create Argument Parser** (`src/cli/parser.py`):
   - Set up argparse with subcommands
   - Define all command arguments and options
   - Global flags (--help, --version, --json)

2. **Create Output Formatter** (`src/cli/formatter.py`):
   - Human-readable format
   - JSON format
   - Color support detection

3. **Create Command Handlers** (`src/cli/commands.py`):
   - Implement each command (add, list, complete, etc.)
   - Error handling
   - Exit code management

4. **Create Main Entry Point** (`src/main.py`):
   - Parse arguments
   - Route to command handlers
   - Handle exceptions

5. **Write Integration Tests** (`tests/integration/test_commands.py`):
   - Test end-to-end workflows
   - Test with actual file operations (use temp files)
   - Test error scenarios

```bash
# Run all tests
pytest tests/ -v

# Run integration tests only
pytest tests/integration/ -v
```

### Phase 4: Testing & Refinement

1. **Run Full Test Suite**:
```bash
# All tests with coverage
pytest tests/ --cov=src --cov-report=term --cov-report=html

# Check coverage threshold (80%+)
pytest tests/ --cov=src --cov-fail-under=80
```

2. **Manual Testing**:
```bash
# Make entry point executable
chmod +x src/main.py

# Test basic operations
python src/main.py add "Test task"
python src/main.py list
python src/main.py complete <task-id>
python src/main.py search test
```

3. **Code Quality**:
```bash
# Format code
black src/ tests/

# Type checking (optional)
mypy src/
```

## Quick Reference

### Common Commands During Development

```bash
# Activate virtual environment
source venv/bin/activate

# Run specific test file
pytest tests/unit/test_task.py -v

# Run tests matching pattern
pytest -k "test_add" -v

# Run tests with output
pytest -v -s

# Generate coverage report
pytest --cov=src --cov-report=html
open htmlcov/index.html

# Run type checker
mypy src/

# Format code
black src/ tests/
```

### File Organization Checklist

- [ ] `src/models/task.py` - Task entity
- [ ] `src/models/task_store.py` - JSON persistence
- [ ] `src/services/task_service.py` - Business logic
- [ ] `src/services/search_service.py` - Search functionality
- [ ] `src/cli/parser.py` - Argument parsing
- [ ] `src/cli/formatter.py` - Output formatting
- [ ] `src/cli/commands.py` - Command handlers
- [ ] `src/main.py` - Entry point
- [ ] `tests/unit/` - Unit tests (80%+ coverage)
- [ ] `tests/integration/` - Integration tests
- [ ] `tests/conftest.py` - Pytest fixtures
- [ ] `requirements-dev.txt` - Dev dependencies
- [ ] `README.md` - User documentation

## Testing Strategy

### Unit Tests (tests/unit/)

Test individual components in isolation:

- **Models**: Validation, state transitions
- **Storage**: File operations, atomic writes
- **Services**: Business logic, CRUD operations
- **Search**: Keyword matching, filtering

**Example**:
```python
def test_add_task(temp_task_file):
    service = TaskService(temp_task_file)
    task = service.add_task("Buy groceries", priority="high")
    
    assert task['description'] == "Buy groceries"
    assert task['priority'] == "high"
    assert task['completed'] is False
```

### Integration Tests (tests/integration/)

Test complete workflows:

- **Add and list**: Create task, verify it appears in list
- **Complete workflow**: Add task, mark complete, verify status
- **Subtask workflow**: Add parent, add subtask, verify hierarchy
- **Search workflow**: Add multiple tasks, search, verify results
- **Error handling**: Invalid operations, file errors

**Example**:
```python
def test_add_and_list_workflow(temp_task_file):
    # Add task
    result = run_command(["add", "Test task", "--data-file", str(temp_task_file)])
    assert result.exit_code == 0
    
    # List tasks
    result = run_command(["list", "--data-file", str(temp_task_file)])
    assert "Test task" in result.output
    assert result.exit_code == 0
```

## Troubleshooting

### Common Issues

**Import Errors**:
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements-dev.txt
```

**Test Failures**:
```bash
# Run specific failing test with verbose output
pytest tests/unit/test_task.py::test_name -v -s

# Check test isolation (each test should use fresh fixtures)
pytest tests/unit/test_task.py -v --setup-show
```

**Coverage Issues**:
```bash
# Generate detailed coverage report
pytest --cov=src --cov-report=term-missing

# Focus on uncovered lines
pytest --cov=src --cov-report=html
open htmlcov/index.html
```

## Next Steps

After completing Phase 1:

1. **Review**: Check all tests pass, coverage meets 80%+
2. **Documentation**: Update README with installation and usage instructions
3. **Constitution Check**: Verify compliance with all constitutional requirements
4. **Phase 2**: Ready for `/speckit.tasks` command to generate implementation tasks

## Resources

- **Specification**: `specs/001-task-management/spec.md`
- **Implementation Plan**: `specs/001-task-management/plan.md`
- **Research**: `specs/001-task-management/research.md`
- **Data Model**: `specs/001-task-management/data-model.md`
- **CLI Contract**: `specs/001-task-management/contracts/cli-interface.md`
- **Python argparse docs**: https://docs.python.org/3/library/argparse.html
- **pytest docs**: https://docs.pytest.org/

---

Quick start guide complete. Ready for implementation!
