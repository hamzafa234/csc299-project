# Tasks: Task Management System

**Input**: Design documents from `/specs/001-task-management/`
**Prerequisites**: plan.md, spec.md (user stories), research.md, data-model.md, contracts/

**Tests**: Tests are NOT explicitly requested in the feature specification, so test tasks are EXCLUDED per instructions.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `- [ ] [ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- All paths are relative to repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create project directory structure: src/{models,services,cli}/, tests/{unit,integration}/ per plan.md
- [x] T002 Create Python package __init__.py files in src/models/, src/services/, src/cli/
- [x] T003 [P] Create requirements-dev.txt with pytest>=7.4.0, pytest-cov>=4.1.0
- [x] T004 [P] Create .gitignore for Python project (venv/, __pycache__/, *.pyc, .pytest_cache/, tasks.json)
- [x] T005 [P] Create README.md with project description and basic setup instructions

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T006 Create Task entity class in src/models/task.py with validation for description (1-500 chars, non-empty), priority (high/medium/low), completed (boolean), parent_id, subtasks array
- [x] T007 Create TaskStore class in src/models/task_store.py with JSON load/save operations and atomic write pattern (temp file + rename)
- [x] T008 Implement circular dependency validation in src/models/task.py to prevent task from being its own ancestor
- [x] T009 Implement depth limit validation (3 levels max) in src/models/task.py
- [x] T010 Create custom exception classes in src/models/task.py: ValidationError, TaskNotFoundError, with exit_code attributes (1 for validation, 2 for runtime)
- [x] T011 Create argument parser skeleton in src/cli/parser.py with argparse, subparsers for commands, and global flags (--help, --version, --json, --data-file, --verbose, --quiet)
- [x] T012 Create output formatter in src/cli/formatter.py with format_human() and format_json() functions, TTY detection for colors
- [x] T013 Create main entry point in src/main.py with argument parsing, command routing, exception handling, and exit code management
- [x] T014 Create pytest conftest.py in tests/ with temp_task_file fixture that creates temporary JSON file for testing

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Add and View Tasks (Priority: P1) 🎯 MVP

**Goal**: Users can create tasks and view their task list

**Independent Test**: Add a task and verify it appears in the list with correct attributes

### Implementation for User Story 1

- [x] T015 [P] [US1] Implement add_task() method in src/services/task_service.py that validates description, generates UUID, sets defaults (completed=false, priority=medium), validates parent_id if provided, checks depth limit, saves to JSON
- [x] T016 [P] [US1] Implement list_tasks() method in src/services/task_service.py that loads tasks, sorts by priority then creation time (newest first), returns all tasks
- [x] T017 [US1] Add 'add' command handler in src/cli/commands.py that parses description, priority, parent flags, calls task_service.add_task(), formats output
- [x] T018 [US1] Add 'list' command handler in src/cli/commands.py that calls task_service.list_tasks(), formats as human-readable (grouped by priority) or JSON based on --json flag
- [x] T019 [US1] Wire 'add' and 'list' subcommands to parser in src/cli/parser.py with proper arguments (description, --priority, --parent for add; no args for list)
- [x] T020 [US1] Implement human-readable list output in src/cli/formatter.py with priority grouping, completion symbols (✓/○), task counters

**Checkpoint**: User Story 1 complete - users can add and view tasks independently

---

## Phase 4: User Story 2 - Mark Tasks as Complete (Priority: P1) 🎯 MVP

**Goal**: Users can mark tasks complete/incomplete to track progress

**Independent Test**: Create a task, mark it complete, verify status changes, mark incomplete, verify status reverts

### Implementation for User Story 2

- [x] T021 [US2] Implement complete_task(task_id) method in src/services/task_service.py that finds task by ID (full UUID or first 8 chars), sets completed=true, saves to JSON
- [x] T022 [US2] Implement uncomplete_task(task_id) method in src/services/task_service.py that finds task by ID, sets completed=false, saves to JSON
- [x] T023 [US2] Add 'complete' command handler in src/cli/commands.py that parses task_id argument, calls task_service.complete_task(), handles TaskNotFoundError
- [x] T024 [US2] Add 'uncomplete' command handler in src/cli/commands.py that parses task_id argument, calls task_service.uncomplete_task(), handles TaskNotFoundError
- [x] T025 [US2] Wire 'complete' and 'uncomplete' subcommands to parser in src/cli/parser.py with task_id positional argument
- [x] T026 [US2] Update formatter in src/cli/formatter.py to visually distinguish completed tasks (dim/gray color when TTY, ✓ symbol)

**Checkpoint**: User Stories 1 AND 2 complete - full MVP functionality (add, view, complete tasks)

---

## Phase 5: User Story 3 - Remove Tasks (Priority: P2)

**Goal**: Users can delete tasks and their subtasks

**Independent Test**: Create a task with subtasks, remove parent, verify all are deleted

### Implementation for User Story 3

- [x] T027 [US3] Implement remove_task(task_id) method in src/services/task_service.py that recursively collects all subtask IDs, removes from parent's subtasks array, removes all from tasks list, saves to JSON, returns count of deleted tasks
- [x] T028 [US3] Add 'remove' command handler in src/cli/commands.py that parses task_id and --force flag, prompts for confirmation if task has subtasks (unless --force), calls task_service.remove_task(), displays count
- [x] T029 [US3] Wire 'remove' subcommand to parser in src/cli/parser.py with task_id positional argument and --force/-f optional flag
- [x] T030 [US3] Implement confirmation prompt in src/cli/commands.py for remove command when task has subtasks and --force not set (check stdin.isatty() before prompting)

**Checkpoint**: User Stories 1, 2, AND 3 complete - core task management functional

---

## Phase 6: User Story 4 - Assign Priority Levels (Priority: P2)

**Goal**: Users can set and change task priorities

**Independent Test**: Create tasks with different priorities, change a task's priority, verify all display correctly

### Implementation for User Story 4

- [x] T031 [US4] Implement set_priority(task_id, priority) method in src/services/task_service.py that validates priority value (high/medium/low), finds task, updates priority field, saves to JSON
- [x] T032 [US4] Add 'priority' command handler in src/cli/commands.py that parses task_id and priority_level arguments, calls task_service.set_priority(), displays before/after priority
- [x] T033 [US4] Wire 'priority' subcommand to parser in src/cli/parser.py with task_id and priority_level positional arguments, priority_level choices=['high', 'medium', 'low']
- [x] T034 [US4] Update add command in src/cli/commands.py to support --priority flag with default='medium', validation via choices parameter
- [x] T035 [US4] Update list output formatter in src/cli/formatter.py to show priority with color coding (high=red, medium=yellow, low=blue) when TTY

**Checkpoint**: Priority management fully functional across add/list/update operations

---

## Phase 7: User Story 6 - Search Tasks by Keywords (Priority: P2)

**Goal**: Users can search tasks by keywords

**Independent Test**: Create multiple tasks, search with keywords, verify correct results including case-insensitive matching

### Implementation for User Story 6

- [x] T036 [P] [US6] Create SearchService class in src/services/search_service.py with search_tasks(tasks, keywords, case_sensitive=False) method using substring matching with OR logic
- [x] T037 [US6] Add 'search' command handler in src/cli/commands.py that parses keywords (nargs='+'), optional --case-sensitive flag, calls search_service.search_tasks(), formats results
- [x] T038 [US6] Wire 'search' subcommand to parser in src/cli/parser.py with keywords positional argument (nargs='+'), --case-sensitive optional flag
- [x] T039 [US6] Implement keyword validation in src/cli/commands.py for search: not empty, max 100 chars per keyword
- [x] T040 [US6] Update search result formatter in src/cli/formatter.py to show matching tasks with parent context for subtasks, "No tasks found matching: X" message for empty results

**Checkpoint**: Search functionality complete and integrated

---

## Phase 8: User Story 5 - Manage Subtasks (Priority: P3)

**Goal**: Users can create hierarchical task structures

**Independent Test**: Create parent task, add subtasks at multiple levels (up to 3), verify hierarchy display, test depth limit

### Implementation for User Story 5

- [x] T041 [US5] Update add_task() in src/services/task_service.py to support parent_id parameter: validate parent exists, calculate depth, enforce 3-level limit, add child ID to parent's subtasks array
- [x] T042 [US5] Implement get_task_depth(task_id) helper method in src/services/task_service.py that traverses parent chain to calculate nesting level
- [x] T043 [US5] Update list formatter in src/cli/formatter.py to display subtasks indented under parents with tree structure symbols (├─, └─), show subtask completion counts
- [x] T044 [US5] Add 'show' command handler in src/cli/commands.py that displays full task details including all subtasks recursively
- [x] T045 [US5] Wire 'show' subcommand to parser in src/cli/parser.py with task_id positional argument
- [x] T046 [US5] Enhance list command in src/cli/commands.py to support --parent filter flag that shows only subtasks of specified parent_id

**Checkpoint**: Full hierarchical task management complete with 3-level depth support

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T047 [P] Add --version flag handler in src/main.py that displays version 1.0.0 and exits
- [x] T048 [P] Implement --verbose flag support in src/cli/commands.py to show detailed operation info (task IDs, file paths)
- [x] T049 [P] Implement --quiet flag support in src/cli/commands.py to suppress all non-error output
- [x] T050 [P] Add comprehensive error messages for all edge cases per contracts/cli-interface.md (empty description, invalid priority, circular dependencies, depth exceeded, file errors)
- [x] T051 [P] Update README.md with complete usage examples for all 8 commands, installation instructions, and quickstart guide from quickstart.md
- [x] T052 Add short ID support (first 8 chars of UUID) across all commands that accept task_id in src/services/task_service.py
- [x] T053 Implement list filtering in src/services/task_service.py: --priority filter, --status filter (complete/incomplete)
- [x] T054 Wire list filters to parser in src/cli/parser.py: add --priority, --status, --parent optional arguments
- [x] T055 [P] Add TASK_DATA_FILE environment variable support in src/main.py with fallback to --data-file flag then ./tasks.json default
- [x] T056 [P] Add TASK_NO_COLOR environment variable support in src/cli/formatter.py to disable colored output
- [x] T057 Validate quickstart.md workflow: create venv, install pytest, run manual tests per quickstart.md steps
- [x] T058 Create initial empty tasks.json file in project root with {"tasks": []} structure

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-8)**: All depend on Foundational phase completion
  - US1 (Add/View) - Priority P1 - No dependencies on other stories
  - US2 (Complete) - Priority P1 - No dependencies on other stories
  - US3 (Remove) - Priority P2 - Independent
  - US4 (Priority) - Priority P2 - Independent
  - US6 (Search) - Priority P2 - Independent  
  - US5 (Subtasks) - Priority P3 - Enhances all other stories but independent
- **Polish (Phase 9)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Foundation only - can start immediately after Phase 2
- **User Story 2 (P1)**: Foundation only - can start immediately after Phase 2
- **User Story 3 (P2)**: Foundation only - independent
- **User Story 4 (P2)**: Foundation only - independent
- **User Story 6 (P2)**: Foundation only - independent
- **User Story 5 (P3)**: Foundation only - enhances display but independent

All user stories after Phase 2 are independently testable and can be implemented in any order or in parallel.

### Within Each User Story

- Service methods before command handlers
- Command handlers before parser wiring
- Core implementation before formatting enhancements
- Story complete before moving to next priority

### Parallel Opportunities

**Setup Phase**:
- T003 (requirements-dev.txt), T004 (.gitignore), T005 (README.md) can run in parallel

**Foundational Phase** (all sequential - order matters for dependencies):
- T006-T014 must complete in order

**User Story 1**:
- T015 (add_task service), T016 (list_tasks service) can run in parallel
- T017 (add command), T018 (list command) can run after services, in parallel with each other

**User Story 2**:
- All tasks sequential (each depends on previous)

**User Story 3**:
- All tasks sequential

**User Story 4**:
- All tasks sequential

**User Story 6**:
- T036 (SearchService) independent
- T037-T040 sequential after T036

**User Story 5**:
- All tasks sequential (each builds on previous)

**Polish Phase**:
- T047 (version), T048 (verbose), T049 (quiet), T050 (errors), T051 (README), T055 (env vars), T056 (no color) can all run in parallel
- T052-T054 (list filters) sequential
- T057 (quickstart validation), T058 (empty tasks.json) can run in parallel

---

## Parallel Execution Example: Phase 1 (Setup)

```bash
# These can be executed simultaneously:
Task T003: Create requirements-dev.txt
Task T004: Create .gitignore  
Task T005: Create README.md
```

## Parallel Execution Example: User Story 1

```bash
# After Foundation complete, these can run together:
Task T015: Implement add_task() in task_service.py
Task T016: Implement list_tasks() in task_service.py

# Then these can run together:
Task T017: Add 'add' command handler
Task T018: Add 'list' command handler
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 2 Only)

1. Complete Phase 1: Setup (T001-T005)
2. Complete Phase 2: Foundational (T006-T014) - CRITICAL
3. Complete Phase 3: User Story 1 (T015-T020) - Add and view tasks
4. Complete Phase 4: User Story 2 (T021-T026) - Mark complete/incomplete
5. **STOP and VALIDATE**: Test adding, viewing, and completing tasks independently
6. This is a deployable MVP!

### Recommended Full Implementation Order

1. Setup (Phase 1)
2. Foundational (Phase 2) - blocking
3. User Story 1 (P1) - Add/View → Test independently → Checkpoint
4. User Story 2 (P1) - Complete → Test independently → Checkpoint (MVP complete)
5. User Story 4 (P2) - Priority → Test independently → Checkpoint
6. User Story 6 (P2) - Search → Test independently → Checkpoint
7. User Story 3 (P2) - Remove → Test independently → Checkpoint
8. User Story 5 (P3) - Subtasks → Test independently → Checkpoint
9. Polish (Phase 9) - Final enhancements

### Parallel Team Strategy

With 3 developers after Foundation (Phase 2) completes:

- **Developer A**: User Story 1 (T015-T020) + User Story 2 (T021-T026)
- **Developer B**: User Story 4 (T031-T035) + User Story 6 (T036-T040)
- **Developer C**: User Story 3 (T027-T030) + User Story 5 (T041-T046)

All stories integrate cleanly as they're independently testable.

---

## Task Count Summary

- **Phase 1 (Setup)**: 5 tasks
- **Phase 2 (Foundational)**: 9 tasks (BLOCKS everything)
- **Phase 3 (US1 - Add/View)**: 6 tasks
- **Phase 4 (US2 - Complete)**: 6 tasks
- **Phase 5 (US3 - Remove)**: 4 tasks
- **Phase 6 (US4 - Priority)**: 5 tasks
- **Phase 7 (US6 - Search)**: 5 tasks
- **Phase 8 (US5 - Subtasks)**: 6 tasks
- **Phase 9 (Polish)**: 12 tasks

**Total**: 58 tasks

**MVP (Phases 1-4)**: 26 tasks
**Full Feature Set**: 58 tasks

---

## Notes

- **[P]** marker indicates tasks that can run in parallel with other [P] tasks in the same phase
- **[USN]** marker maps each task to its user story for traceability
- Tests are NOT included per feature specification (no explicit test requirement)
- Each user story is independently completable and delivers value
- Stop at any checkpoint to validate story works independently
- All file paths are relative to repository root
- Tasks are atomic and specific with exact file paths
- Commit after completing each user story phase
