"""Command handlers for CLI operations."""

import sys
from typing import Any

from src.models.task import Task, ValidationError, TaskNotFoundError
from src.models.task_store import TaskStore
from src.cli.formatter import Formatter
from src.services.task_service import TaskService


def handle_add(args: Any, data_file: str) -> None:
    """Handle add command.
    
    Args:
        args: Parsed arguments
        data_file: Path to data file
    """
    service = TaskService(data_file)
    formatter = Formatter()
    
    try:
        # Add task
        task = service.add_task(
            description=args.description,
            priority=args.priority,
            parent_id=args.parent
        )
        
        # Output
        if not args.quiet:
            if args.json:
                print(formatter.format_json({
                    'success': True,
                    'task': task.to_dict()
                }))
            else:
                print(f"✓ Task added: {task.id[:8]}")
                if args.verbose:
                    print(f"  Description: {task.description}")
                    print(f"  Priority: {task.priority}")
                    if task.parent_id:
                        print(f"  Parent: {task.parent_id[:8]}")
    
    except (ValidationError, TaskNotFoundError) as e:
        if not args.quiet:
            if args.json:
                print(formatter.format_json({
                    'success': False,
                    'error': str(e)
                }))
            else:
                print(f"Error: {e}", file=sys.stderr)
        raise


def handle_list(args: Any, data_file: str) -> None:
    """Handle list command.
    
    Args:
        args: Parsed arguments
        data_file: Path to data file
    """
    service = TaskService(data_file)
    formatter = Formatter()
    
    # Get tasks
    tasks = service.list_tasks(
        priority=args.priority,
        status=args.status,
        parent_id=args.parent
    )
    
    # Output
    if not args.quiet:
        if args.json:
            print(formatter.format_json({
                'count': len(tasks),
                'tasks': [t.to_dict() for t in tasks]
            }))
        else:
            # Show task count header
            print(f"\nTotal tasks: {len(tasks)}\n")
            print(formatter.format_human(tasks))


def handle_complete(args: Any, data_file: str) -> None:
    """Handle complete command.
    
    Args:
        args: Parsed arguments
        data_file: Path to data file
    """
    service = TaskService(data_file)
    formatter = Formatter()
    
    try:
        task = service.complete_task(args.task_id)
        
        if not args.quiet:
            if args.json:
                print(formatter.format_json({
                    'success': True,
                    'task': task.to_dict()
                }))
            else:
                print(f"✓ Task marked as complete: {task.id[:8]}")
                if args.verbose:
                    print(f"  Description: {task.description}")
    
    except (ValidationError, TaskNotFoundError) as e:
        if not args.quiet:
            if args.json:
                print(formatter.format_json({
                    'success': False,
                    'error': str(e)
                }))
            else:
                print(f"Error: {e}", file=sys.stderr)
        raise


def handle_uncomplete(args: Any, data_file: str) -> None:
    """Handle uncomplete command.
    
    Args:
        args: Parsed arguments
        data_file: Path to data file
    """
    service = TaskService(data_file)
    formatter = Formatter()
    
    try:
        task = service.uncomplete_task(args.task_id)
        
        if not args.quiet:
            if args.json:
                print(formatter.format_json({
                    'success': True,
                    'task': task.to_dict()
                }))
            else:
                print(f"○ Task marked as incomplete: {task.id[:8]}")
                if args.verbose:
                    print(f"  Description: {task.description}")
    
    except (ValidationError, TaskNotFoundError) as e:
        if not args.quiet:
            if args.json:
                print(formatter.format_json({
                    'success': False,
                    'error': str(e)
                }))
            else:
                print(f"Error: {e}", file=sys.stderr)
        raise


def handle_remove(args: Any, data_file: str) -> None:
    """Handle remove command.
    
    Args:
        args: Parsed arguments
        data_file: Path to data file
    """
    service = TaskService(data_file)
    formatter = Formatter()
    
    try:
        # Check if task has subtasks and needs confirmation
        tasks = service.store.load()
        task = service.find_task(args.task_id, tasks)
        
        if not task:
            raise TaskNotFoundError(f"Task not found: {args.task_id}")
        
        # Prompt for confirmation if task has subtasks and --force not set
        if task.subtasks and not args.force:
            if sys.stdin.isatty():
                print(f"Warning: Task '{task.description}' has {len(task.subtasks)} subtask(s).")
                print("All subtasks will also be removed.")
                response = input("Continue? (y/N): ").strip().lower()
                if response not in ('y', 'yes'):
                    print("Cancelled.")
                    return
            else:
                # Non-interactive mode without --force
                raise ValidationError("Task has subtasks. Use --force to remove without confirmation.")
        
        # Remove task
        count = service.remove_task(args.task_id)
        
        if not args.quiet:
            if args.json:
                print(formatter.format_json({
                    'success': True,
                    'removed_count': count
                }))
            else:
                if count == 1:
                    print(f"✓ Task removed: {task.id[:8]}")
                else:
                    print(f"✓ Removed {count} tasks (including subtasks)")
                if args.verbose:
                    print(f"  Task: {task.description}")
    
    except (ValidationError, TaskNotFoundError) as e:
        if not args.quiet:
            if args.json:
                print(formatter.format_json({
                    'success': False,
                    'error': str(e)
                }))
            else:
                print(f"Error: {e}", file=sys.stderr)
        raise


def handle_priority(args: Any, data_file: str) -> None:
    """Handle priority command.
    
    Args:
        args: Parsed arguments
        data_file: Path to data file
    """
    service = TaskService(data_file)
    formatter = Formatter()
    
    try:
        # Get old priority before update
        tasks = service.store.load()
        task = service.find_task(args.task_id, tasks)
        if task:
            old_priority = task.priority
        else:
            raise TaskNotFoundError(f"Task not found: {args.task_id}")
        
        # Update priority
        task = service.set_priority(args.task_id, args.priority_level)
        
        if not args.quiet:
            if args.json:
                print(formatter.format_json({
                    'success': True,
                    'task': task.to_dict(),
                    'old_priority': old_priority
                }))
            else:
                print(f"✓ Task priority updated: {task.id[:8]}")
                print(f"  {old_priority} → {task.priority}")
                if args.verbose:
                    print(f"  Description: {task.description}")
    
    except (ValidationError, TaskNotFoundError) as e:
        if not args.quiet:
            if args.json:
                print(formatter.format_json({
                    'success': False,
                    'error': str(e)
                }))
            else:
                print(f"Error: {e}", file=sys.stderr)
        raise


def handle_search(args: Any, data_file: str) -> None:
    """Handle search command.
    
    Args:
        args: Parsed arguments
        data_file: Path to data file
    """
    from src.services.search_service import SearchService
    
    service = TaskService(data_file)
    formatter = Formatter()
    
    try:
        # Load all tasks
        all_tasks = service.store.load()
        
        # Search
        matching_tasks = SearchService.search_tasks(
            all_tasks,
            args.keywords,
            case_sensitive=args.case_sensitive
        )
        
        # Output
        if not args.quiet:
            if args.json:
                print(formatter.format_json({
                    'count': len(matching_tasks),
                    'keywords': args.keywords,
                    'case_sensitive': args.case_sensitive,
                    'tasks': [t.to_dict() for t in matching_tasks]
                }))
            else:
                keywords_str = ', '.join(args.keywords)
                if matching_tasks:
                    print(f"\nFound {len(matching_tasks)} task(s) matching: {keywords_str}\n")
                    print(formatter.format_human(matching_tasks))
                else:
                    print(f"\nNo tasks found matching: {keywords_str}")
    
    except ValidationError as e:
        if not args.quiet:
            if args.json:
                print(formatter.format_json({
                    'success': False,
                    'error': str(e)
                }))
            else:
                print(f"Error: {e}", file=sys.stderr)
        raise


def handle_show(args: Any, data_file: str) -> None:
    """Handle show command.
    
    Args:
        args: Parsed arguments
        data_file: Path to data file
    """
    service = TaskService(data_file)
    formatter = Formatter()
    
    try:
        tasks = service.store.load()
        task = service.find_task(args.task_id, tasks)
        
        if not task:
            raise TaskNotFoundError(f"Task not found: {args.task_id}")
        
        if not args.quiet:
            if args.json:
                # Include full task tree
                task_map = {t.id: t for t in tasks}
                task_dict = task.to_dict()
                
                # Add subtask details
                def add_subtask_details(t_dict):
                    subtasks_detailed = []
                    for subtask_id in t_dict.get('subtasks', []):
                        subtask = task_map.get(subtask_id)
                        if subtask:
                            sub_dict = subtask.to_dict()
                            add_subtask_details(sub_dict)
                            subtasks_detailed.append(sub_dict)
                    t_dict['subtasks_detailed'] = subtasks_detailed
                
                add_subtask_details(task_dict)
                
                print(formatter.format_json(task_dict))
            else:
                print(formatter.format_task_detail(task, tasks))
    
    except (ValidationError, TaskNotFoundError) as e:
        if not args.quiet:
            if args.json:
                print(formatter.format_json({
                    'success': False,
                    'error': str(e)
                }))
            else:
                print(f"Error: {e}", file=sys.stderr)
        raise
