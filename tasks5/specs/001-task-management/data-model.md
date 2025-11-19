# Data Model: Task Management System

**Phase**: 1 - Design & Contracts  
**Date**: 2025-11-18  
**Purpose**: Define data entities, relationships, and validation rules

## Entities

### Task

Represents a work item that needs to be tracked.

**Attributes**:

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| id | string (UUID) | Yes | Unique, generated on creation | Unique identifier for the task |
| description | string | Yes | 1-500 characters, non-empty | Text description of the task |
| completed | boolean | Yes | Default: false | Whether the task is completed |
| priority | enum | Yes | One of: "high", "medium", "low"; Default: "medium" | Priority level of the task |
| created_at | string (ISO 8601) | Yes | Valid datetime | Timestamp when task was created |
| parent_id | string (UUID) or null | No | Must reference existing task if not null | ID of parent task (null for top-level tasks) |
| subtasks | array of strings (UUIDs) | Yes | Default: empty array | List of child task IDs |

**Validation Rules**:

1. **Description Validation**:
   - Must not be empty or whitespace-only
   - Must be ≤ 500 characters
   - Special characters allowed

2. **Priority Validation**:
   - Must be one of: "high", "medium", "low"
   - Case-sensitive
   - Defaults to "medium" if not specified

3. **Hierarchy Validation**:
   - Maximum nesting depth: 3 levels
   - Cannot have self as parent (circular dependency check)
   - Cannot have circular dependencies in ancestor chain
   - parent_id must reference an existing task or be null
   - Subtasks array must contain only valid task IDs

4. **Completion Status**:
   - Boolean value only
   - No automatic propagation to/from subtasks (user controls this)

**State Transitions**:

```
[Created] → (completed=false, priority=medium by default)
    ↓
[Active] → User can: mark complete, change priority, add subtasks, update description
    ↓
[Completed] → (completed=true) → Can be marked incomplete again
    ↓
[Deleted] → Removed from system (cascades to subtasks)
```

### Task Hierarchy

Represents the parent-child relationships between tasks.

**Relationships**:

- A task can have **zero or many** subtasks
- A subtask has **exactly one** parent task
- Top-level tasks have `parent_id = null`
- Maximum depth: 3 levels (task → subtask → sub-subtask)

**Hierarchy Rules**:

1. **Depth Calculation**:
   ```
   Level 0: parent_id = null (top-level)
   Level 1: parent is Level 0
   Level 2: parent is Level 1
   Level 3: parent is Level 2 (maximum depth)
   ```

2. **Cascade Deletion**:
   - When a parent task is deleted, all subtasks are also deleted
   - Deletion recursively removes entire subtree

3. **Circular Dependency Prevention**:
   - Task A cannot be a subtask of itself
   - Task A cannot be a subtask of its own descendant
   - Validation checks entire ancestor chain

## JSON Schema

The data file (`tasks.json`) structure:

```json
{
  "tasks": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "description": "Complete project proposal",
      "completed": false,
      "priority": "high",
      "created_at": "2025-11-18T10:30:00.000Z",
      "parent_id": null,
      "subtasks": [
        "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
        "6ba7b811-9dad-11d1-80b4-00c04fd430c8"
      ]
    },
    {
      "id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
      "description": "Research background information",
      "completed": true,
      "priority": "medium",
      "created_at": "2025-11-18T10:31:00.000Z",
      "parent_id": "550e8400-e29b-41d4-a716-446655440000",
      "subtasks": []
    },
    {
      "id": "6ba7b811-9dad-11d1-80b4-00c04fd430c8",
      "description": "Write executive summary",
      "completed": false,
      "priority": "high",
      "created_at": "2025-11-18T10:32:00.000Z",
      "parent_id": "550e8400-e29b-41d4-a716-446655440000",
      "subtasks": []
    }
  ]
}
```

**Root Structure**:
- Single key `"tasks"` containing array of task objects
- Empty file initializes as `{"tasks": []}`

## Data Operations

### Create (Add Task)

**Inputs**:
- description (required, 1-500 chars)
- priority (optional, defaults to "medium")
- parent_id (optional, defaults to null)

**Process**:
1. Validate description is non-empty and ≤ 500 chars
2. Validate priority is valid enum value
3. Generate unique UUID for task ID
4. Set created_at to current ISO 8601 timestamp
5. Set completed to false
6. If parent_id provided:
   - Validate parent exists
   - Validate depth limit not exceeded
   - Add new task ID to parent's subtasks array
7. Add task to tasks array
8. Save data file atomically

**Outputs**:
- Complete task object
- Exit code 0 on success, 1 on validation error

### Read (List/Search Tasks)

**List All**:
- Return all tasks in creation order (newest first) within priority groups
- Include subtasks with indentation markers

**Search by Keywords**:
- Case-insensitive substring matching
- Multiple keywords use OR logic (match any keyword)
- Search entire task description
- Include subtasks in results with parent context

**Outputs**:
- Array of task objects
- Empty array if no matches
- Exit code 0 always (empty results not an error)

### Update

**Mark Complete/Incomplete**:
- Toggle completed boolean
- No cascade to parent or children
- Validation: task must exist

**Change Priority**:
- Update priority field to new value
- Validation: must be valid enum value
- Validation: task must exist

**Outputs**:
- Updated task object
- Exit code 0 on success, 1 if task not found

### Delete (Remove Task)

**Process**:
1. Validate task exists
2. Recursively collect all subtask IDs
3. Remove task and all subtasks from tasks array
4. Remove task ID from parent's subtasks array (if applicable)
5. Save data file atomically

**Cascade Behavior**:
- All subtasks deleted recursively
- No orphaned subtasks remain

**Outputs**:
- Count of tasks deleted (parent + all subtasks)
- Exit code 0 on success, 1 if task not found

## Data Integrity

**Atomic Operations**:
- All writes use atomic file replacement (write to temp, then rename)
- No partial updates possible
- Read-modify-write cycle protected by single-process assumption

**Validation on Load**:
- Validate JSON structure on file read
- Check all task references are valid
- Detect and report circular dependencies
- Validate all required fields present
- Reject malformed data with clear error message

**Backup Strategy** (Future Enhancement):
- Before writes, optionally copy current file to .backup
- Not implemented in MVP but structure supports it

## Index Strategy

**Current (MVP)**:
- No indexes, linear scan for all operations
- Performance adequate for 1000 tasks (<100ms)

**Future Optimization**:
- If >10,000 tasks: build in-memory index on load
  - id → task object (O(1) lookup)
  - parent_id → array of children (O(1) subtask access)
  - Priority groups (O(1) priority filtering)

## Example Data Scenarios

### Scenario 1: Simple Flat List
```json
{
  "tasks": [
    {
      "id": "a1",
      "description": "Buy groceries",
      "completed": false,
      "priority": "medium",
      "created_at": "2025-11-18T10:00:00Z",
      "parent_id": null,
      "subtasks": []
    },
    {
      "id": "a2",
      "description": "Call dentist",
      "completed": true,
      "priority": "high",
      "created_at": "2025-11-18T11:00:00Z",
      "parent_id": null,
      "subtasks": []
    }
  ]
}
```

### Scenario 2: Multi-Level Hierarchy (3 levels)
```json
{
  "tasks": [
    {
      "id": "t1",
      "description": "Plan vacation",
      "completed": false,
      "priority": "low",
      "created_at": "2025-11-18T09:00:00Z",
      "parent_id": null,
      "subtasks": ["t2", "t3"]
    },
    {
      "id": "t2",
      "description": "Book flights",
      "completed": false,
      "priority": "high",
      "created_at": "2025-11-18T09:01:00Z",
      "parent_id": "t1",
      "subtasks": ["t4"]
    },
    {
      "id": "t4",
      "description": "Compare prices",
      "completed": true,
      "priority": "medium",
      "created_at": "2025-11-18T09:02:00Z",
      "parent_id": "t2",
      "subtasks": []
    },
    {
      "id": "t3",
      "description": "Reserve hotel",
      "completed": false,
      "priority": "medium",
      "created_at": "2025-11-18T09:03:00Z",
      "parent_id": "t1",
      "subtasks": []
    }
  ]
}
```

## Migration Strategy

**Version 1.0** (Current):
- Schema as documented above
- No migration needed

**Future Versions**:
- Add "version" field to root object
- Implement migration functions for schema changes
- Backup original before migration
- Document breaking changes in changelog

---

Data model complete and ready for contract definition.
