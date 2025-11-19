"""Task service for business logic."""

from typing import List, Optional

from src.models.task import Task, ValidationError, TaskNotFoundError
from src.models.task_store import TaskStore


class TaskService:
    """Service layer for task operations."""
    
    def __init__(self, data_file: str):
        """Initialize task service.
        
        Args:
            data_file: Path to task data file
        """
        self.store = TaskStore(data_file)
    
    def add_task(
        self,
        description: str,
        priority: str = 'medium',
        parent_id: Optional[str] = None
    ) -> Task:
        """Add a new task.
        
        Args:
            description: Task description
            priority: Task priority (high/medium/low)
            parent_id: Parent task ID (for subtasks)
            
        Returns:
            Created task
            
        Raises:
            ValidationError: If validation fails
            TaskNotFoundError: If parent task not found
        """
        # Load existing tasks
        tasks = self.store.load()
        
        # Validate parent if provided
        if parent_id:
            parent = self.find_task(parent_id, tasks)
            if not parent:
                raise TaskNotFoundError(f"Parent task not found: {parent_id}")
            
            # Use full parent ID
            parent_id = parent.id
            
            # Validate no circular dependency
            Task.validate_circular_dependency(None, parent_id, tasks)
            
            # Validate depth limit
            Task.validate_depth(parent_id, tasks)
        
        # Create task
        task = Task(
            description=description,
            priority=priority,
            parent_id=parent_id
        )
        
        # Add to parent's subtasks if applicable
        if parent_id:
            for t in tasks:
                if t.id == parent_id:
                    t.subtasks.append(task.id)
                    break
        
        # Add to task list
        tasks.append(task)
        
        # Save
        self.store.save(tasks)
        
        return task
    
    def list_tasks(
        self,
        priority: Optional[str] = None,
        status: Optional[str] = None,
        parent_id: Optional[str] = None
    ) -> List[Task]:
        """List all tasks with optional filtering.
        
        Args:
            priority: Filter by priority (high/medium/low)
            status: Filter by status (complete/incomplete)
            parent_id: Filter by parent (show only subtasks)
            
        Returns:
            List of tasks
        """
        tasks = self.store.load()
        
        # Apply filters
        filtered = tasks
        
        if priority:
            filtered = [t for t in filtered if t.priority == priority]
        
        if status:
            if status == 'complete':
                filtered = [t for t in filtered if t.completed]
            elif status == 'incomplete':
                filtered = [t for t in filtered if not t.completed]
        
        if parent_id:
            # Find parent
            parent = self.find_task(parent_id, tasks)
            if parent:
                parent_id = parent.id
                filtered = [t for t in filtered if t.parent_id == parent_id]
            else:
                filtered = []
        
        # Sort by priority (high > medium > low) then by creation time (newest first)
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        filtered.sort(key=lambda t: (priority_order[t.priority], t.created_at), reverse=True)
        
        return filtered
    
    def find_task(self, task_id: str, tasks: Optional[List[Task]] = None) -> Optional[Task]:
        """Find task by ID (supports short IDs).
        
        Args:
            task_id: Full UUID or first 8 characters
            tasks: Task list (will load if not provided)
            
        Returns:
            Task if found, None otherwise
        """
        if tasks is None:
            tasks = self.store.load()
        
        # Try exact match first
        for task in tasks:
            if task.id == task_id:
                return task
        
        # Try prefix match (first 8 chars)
        if len(task_id) >= 8:
            prefix = task_id[:8]
            matches = [t for t in tasks if t.id.startswith(prefix)]
            if len(matches) == 1:
                return matches[0]
            elif len(matches) > 1:
                raise ValidationError(f"Ambiguous task ID '{task_id}': matches multiple tasks")
        
        return None
    
    def complete_task(self, task_id: str) -> Task:
        """Mark task as complete.
        
        Args:
            task_id: Task ID (full UUID or first 8 chars)
            
        Returns:
            Updated task
            
        Raises:
            TaskNotFoundError: If task not found
        """
        tasks = self.store.load()
        task = self.find_task(task_id, tasks)
        
        if not task:
            raise TaskNotFoundError(f"Task not found: {task_id}")
        
        task.completed = True
        self.store.save(tasks)
        
        return task
    
    def uncomplete_task(self, task_id: str) -> Task:
        """Mark task as incomplete.
        
        Args:
            task_id: Task ID (full UUID or first 8 chars)
            
        Returns:
            Updated task
            
        Raises:
            TaskNotFoundError: If task not found
        """
        tasks = self.store.load()
        task = self.find_task(task_id, tasks)
        
        if not task:
            raise TaskNotFoundError(f"Task not found: {task_id}")
        
        task.completed = False
        self.store.save(tasks)
        
        return task
    
    def remove_task(self, task_id: str) -> int:
        """Remove task and all its subtasks.
        
        Args:
            task_id: Task ID (full UUID or first 8 chars)
            
        Returns:
            Number of tasks removed
            
        Raises:
            TaskNotFoundError: If task not found
        """
        tasks = self.store.load()
        task = self.find_task(task_id, tasks)
        
        if not task:
            raise TaskNotFoundError(f"Task not found: {task_id}")
        
        # Collect all subtask IDs recursively
        def collect_subtasks(t: Task) -> List[str]:
            """Recursively collect all subtask IDs."""
            task_map = {task.id: task for task in tasks}
            ids = [t.id]
            for subtask_id in t.subtasks:
                subtask = task_map.get(subtask_id)
                if subtask:
                    ids.extend(collect_subtasks(subtask))
            return ids
        
        # Get all IDs to remove
        ids_to_remove = set(collect_subtasks(task))
        
        # Remove from parent's subtasks array if applicable
        if task.parent_id:
            for t in tasks:
                if t.id == task.parent_id and task.id in t.subtasks:
                    t.subtasks.remove(task.id)
                    break
        
        # Remove all tasks
        tasks = [t for t in tasks if t.id not in ids_to_remove]
        
        # Save
        self.store.save(tasks)
        
        return len(ids_to_remove)
    
    def set_priority(self, task_id: str, priority: str) -> Task:
        """Set task priority.
        
        Args:
            task_id: Task ID (full UUID or first 8 chars)
            priority: New priority level (high/medium/low)
            
        Returns:
            Updated task
            
        Raises:
            TaskNotFoundError: If task not found
            ValidationError: If priority is invalid
        """
        tasks = self.store.load()
        task = self.find_task(task_id, tasks)
        
        if not task:
            raise TaskNotFoundError(f"Task not found: {task_id}")
        
        # Validate priority
        if priority not in Task.VALID_PRIORITIES:
            raise ValidationError(
                f"Invalid priority '{priority}'. Must be one of: {', '.join(Task.VALID_PRIORITIES)}"
            )
        
        old_priority = task.priority
        task.priority = priority
        self.store.save(tasks)
        
        return task
