# Research: Task Management System

**Phase**: 0 - Outline & Research  
**Date**: 2025-11-18  
**Purpose**: Resolve technical unknowns and document best practices for implementation

## Research Tasks Completed

### 1. Python CLI Best Practices

**Decision**: Use `argparse` (standard library) with subcommands pattern

**Rationale**:
- Part of Python standard library (no external dependencies)
- Native support for subcommands (add, list, complete, remove, etc.)
- Built-in help generation with --help
- Type validation and error handling
- Wide adoption in production CLI tools

**Alternatives Considered**:
- **Click**: More features but external dependency; adds complexity for simple use case
- **Typer**: Modern with type hints but requires external dependency
- **docopt**: Interesting but less common, harder to maintain

**Implementation Pattern**:
```python
parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(dest='command')

# Add command
add_parser = subparsers.add_parser('add', help='Add a new task')
add_parser.add_argument('description', help='Task description')
add_parser.add_argument('--priority', choices=['high', 'medium', 'low'], default='medium')
```

### 2. JSON Data Storage Pattern

**Decision**: Single JSON file with atomic writes and backup strategy

**Rationale**:
- User requirement: JSON file in same directory
- Simple, human-readable format for debugging
- Python's json module handles serialization/deserialization efficiently
- Atomic writes prevent corruption (write to temp, then rename)
- Small data size (<1MB for 1000 tasks) fits well in memory

**Alternatives Considered**:
- **SQLite**: Overkill for hierarchical task data; adds query complexity
- **Pickle**: Not human-readable; security concerns
- **YAML**: Requires external library; no significant benefit over JSON

**Implementation Pattern**:
```python
import json
import tempfile
from pathlib import Path

def save_tasks(tasks, filepath):
    # Atomic write: write to temp file, then rename
    temp = tempfile.NamedTemporaryFile(mode='w', delete=False, dir=filepath.parent)
    json.dump(tasks, temp, indent=2)
    temp.close()
    Path(temp.name).replace(filepath)
```

### 3. Task ID Generation Strategy

**Decision**: UUID4 for task identifiers

**Rationale**:
- Globally unique without coordination
- No collision risk even with concurrent access (future-proof)
- Standard library support (uuid module)
- Human-readable in shortened form (first 8 chars)
- No sequential ID management complexity

**Alternatives Considered**:
- **Sequential integers**: Simple but requires locking; collision risk with manual edits
- **Timestamp-based**: Not unique for simultaneous operations
- **Hash of content**: Changes if task edited

**Implementation Pattern**:
```python
import uuid

task_id = str(uuid.uuid4())
short_id = task_id[:8]  # For display: "a3f2b1c4"
```

### 4. Hierarchical Task Data Structure

**Decision**: Nested dictionary with parent_id references

**Rationale**:
- Efficient for 3-level depth limit
- Easy to serialize to JSON
- Simple traversal algorithms
- Supports both parent→child and child→parent queries
- Memory efficient for expected scale (1000 tasks)

**Data Structure**:
```python
{
  "tasks": [
    {
      "id": "uuid",
      "description": "Parent task",
      "completed": false,
      "priority": "high",
      "created_at": "2025-11-18T10:30:00",
      "parent_id": null,
      "subtasks": ["child-uuid-1", "child-uuid-2"]
    },
    {
      "id": "child-uuid-1",
      "description": "Subtask 1",
      "completed": false,
      "priority": "medium",
      "created_at": "2025-11-18T10:31:00",
      "parent_id": "uuid",
      "subtasks": []
    }
  ]
}
```

**Alternatives Considered**:
- **Nested objects**: Hard to search flat; complex updates
- **Adjacency list**: More complex for small depth
- **Path enumeration**: Overkill for 3 levels

### 5. Search Implementation

**Decision**: In-memory linear search with case-insensitive substring matching

**Rationale**:
- Performance target: <2s for 1000 tasks easily met with linear scan
- Simple implementation, no indexing complexity
- Supports multiple keywords (OR logic)
- Case-insensitive via .lower()
- Python's string operations are fast for small datasets

**Performance Analysis**:
- 1000 tasks × 500 chars avg = 500KB text
- Modern Python: ~1-5ms per 1000 string comparisons
- Well under 2s target, no optimization needed for MVP

**Implementation Pattern**:
```python
def search_tasks(tasks, keywords):
    keywords_lower = [k.lower() for k in keywords]
    results = []
    for task in tasks:
        desc_lower = task['description'].lower()
        if any(kw in desc_lower for kw in keywords_lower):
            results.append(task)
    return results
```

**Alternatives Considered**:
- **Full-text search library**: Overkill for small dataset
- **Regex**: More complex, not needed for simple substring matching
- **Inverted index**: Unnecessary complexity for MVP scale

### 6. Testing Strategy

**Decision**: pytest with fixtures for test data isolation

**Rationale**:
- Industry standard for Python testing
- Excellent fixture system for test data management
- pytest-cov integration for coverage reporting
- Clear assertion messages
- Supports both unit and integration tests

**Test Categories**:
1. **Unit Tests**: Models, services, search logic (80%+ coverage target)
2. **Integration Tests**: End-to-end command execution with temp data files
3. **Edge Case Tests**: Validation, error handling, boundary conditions

**Implementation Pattern**:
```python
# conftest.py
@pytest.fixture
def temp_task_file(tmp_path):
    task_file = tmp_path / "test_tasks.json"
    task_file.write_text('{"tasks": []}')
    return task_file

# test_task_service.py
def test_add_task(temp_task_file):
    service = TaskService(temp_task_file)
    task = service.add_task("Test task", priority="high")
    assert task['description'] == "Test task"
    assert task['priority'] == "high"
```

### 7. Error Handling Strategy

**Decision**: Custom exception hierarchy with exit code mapping

**Rationale**:
- Separates business errors from system errors
- Clean error messages without stack traces
- Standard exit codes for shell scripting
- Easy to test error conditions

**Exit Codes**:
- 0: Success
- 1: Usage error (invalid arguments, validation failure)
- 2: Runtime error (file access, data corruption)

**Implementation Pattern**:
```python
class TaskError(Exception):
    """Base exception for task operations"""
    exit_code = 2

class ValidationError(TaskError):
    """Invalid user input"""
    exit_code = 1

class TaskNotFoundError(TaskError):
    """Task ID not found"""
    exit_code = 1
```

### 8. Output Formatting

**Decision**: Template-based formatting with --json flag for machine output

**Rationale**:
- Human-readable default for terminal use
- --json flag for scripting/automation
- Colored output only when stdout is TTY
- Consistent formatting across commands

**Human-Readable Format**:
```
[1] ✓ Buy groceries (high)
    Created: 2025-11-18 10:30
    
[2] ○ Complete report (medium)
    Created: 2025-11-18 11:00
    Subtasks: 2 (1 completed)
```

**JSON Format** (--json flag):
```json
[
  {
    "id": "a3f2b1c4",
    "description": "Buy groceries",
    "completed": true,
    "priority": "high",
    "created_at": "2025-11-18T10:30:00"
  }
]
```

## Key Technical Decisions Summary

| Area | Decision | Primary Reason |
|------|----------|----------------|
| CLI Framework | argparse (stdlib) | Zero dependencies, built-in subcommands |
| Data Storage | JSON file with atomic writes | User requirement, human-readable |
| Task IDs | UUID4 | Collision-free, no coordination needed |
| Data Structure | Nested dict with parent refs | Efficient for 3-level depth limit |
| Search | Linear scan, case-insensitive | Simple, meets <2s target for 1000 tasks |
| Testing | pytest with fixtures | Industry standard, excellent tooling |
| Error Handling | Custom exceptions + exit codes | Clean errors, shell script friendly |
| Output | Template + --json flag | Human and machine readable |

## Dependencies

### Runtime
- Python 3.11+ (standard library only)
  - argparse: CLI parsing
  - json: Data serialization
  - uuid: Task ID generation
  - pathlib: File operations
  - datetime: Timestamps

### Development
- pytest: Testing framework
- pytest-cov: Coverage reporting
- black: Code formatting (optional)
- mypy: Type checking (optional)

## Performance Considerations

- **Memory**: ~1MB for 1000 tasks (500 chars avg) - negligible
- **Load time**: JSON parsing ~10-50ms for 1000 tasks
- **Search time**: <100ms for 1000 tasks with substring matching
- **Write time**: <50ms for atomic JSON write
- All operations well within constitutional requirements

## Security Considerations

- No credential storage needed
- File permissions: 644 for data file (user read/write)
- Input validation prevents injection (no shell execution)
- JSON parsing is safe (no eval/exec)
- No network operations, no external attack surface

## Future Optimization Paths

*Not needed for MVP, documented for Phase 2+*

1. **Incremental JSON**: Only load/save changed tasks
2. **Search index**: Build inverted index if >10,000 tasks
3. **SQLite migration**: If relational queries become common
4. **Batch operations**: If users need bulk updates

All research items resolved. Ready for Phase 1: Design & Contracts.
