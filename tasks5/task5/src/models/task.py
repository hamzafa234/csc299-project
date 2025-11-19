"""Task entity and validation."""

import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any


class ValidationError(Exception):
    """Validation error exception."""
    
    def __init__(self, message: str):
        super().__init__(message)
        self.exit_code = 1


class TaskNotFoundError(Exception):
    """Task not found exception."""
    
    def __init__(self, message: str):
        super().__init__(message)
        self.exit_code = 2


class Task:
    """Task entity with validation."""
    
    VALID_PRIORITIES = ['high', 'medium', 'low']
    MAX_DESCRIPTION_LENGTH = 500
    MAX_DEPTH = 3
    
    def __init__(
        self,
        description: str,
        task_id: Optional[str] = None,
        completed: bool = False,
        priority: str = 'medium',
        created_at: Optional[str] = None,
        parent_id: Optional[str] = None,
        subtasks: Optional[List[str]] = None
    ):
        """Initialize task with validation.
        
        Args:
            description: Task description (1-500 chars, non-empty)
            task_id: UUID4 task identifier (generated if not provided)
            completed: Task completion status
            priority: Priority level (high/medium/low)
            created_at: ISO format timestamp (generated if not provided)
            parent_id: Parent task UUID (None for top-level tasks)
            subtasks: List of child task UUIDs
            
        Raises:
            ValidationError: If validation fails
        """
        self.id = task_id or str(uuid.uuid4())
        self.description = self._validate_description(description)
        self.completed = bool(completed)
        self.priority = self._validate_priority(priority)
        self.created_at = created_at or datetime.utcnow().isoformat()
        self.parent_id = parent_id
        self.subtasks = subtasks or []
    
    def _validate_description(self, description: str) -> str:
        """Validate task description.
        
        Args:
            description: Description to validate
            
        Returns:
            Validated description
            
        Raises:
            ValidationError: If description is invalid
        """
        if not description or not description.strip():
            raise ValidationError("Task description cannot be empty")
        
        if len(description) > self.MAX_DESCRIPTION_LENGTH:
            raise ValidationError(
                f"Task description cannot exceed {self.MAX_DESCRIPTION_LENGTH} characters"
            )
        
        return description.strip()
    
    def _validate_priority(self, priority: str) -> str:
        """Validate priority level.
        
        Args:
            priority: Priority to validate
            
        Returns:
            Validated priority
            
        Raises:
            ValidationError: If priority is invalid
        """
        if priority not in self.VALID_PRIORITIES:
            raise ValidationError(
                f"Invalid priority '{priority}'. Must be one of: {', '.join(self.VALID_PRIORITIES)}"
            )
        
        return priority
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary.
        
        Returns:
            Dictionary representation of task
        """
        return {
            'id': self.id,
            'description': self.description,
            'completed': self.completed,
            'priority': self.priority,
            'created_at': self.created_at,
            'parent_id': self.parent_id,
            'subtasks': self.subtasks
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """Create task from dictionary.
        
        Args:
            data: Dictionary with task data
            
        Returns:
            Task instance
        """
        return cls(
            description=data['description'],
            task_id=data['id'],
            completed=data.get('completed', False),
            priority=data.get('priority', 'medium'),
            created_at=data.get('created_at'),
            parent_id=data.get('parent_id'),
            subtasks=data.get('subtasks', [])
        )
    
    @staticmethod
    def validate_circular_dependency(task_id: str, parent_id: Optional[str], all_tasks: List['Task']) -> None:
        """Validate that adding parent_id doesn't create circular dependency.
        
        Args:
            task_id: ID of task being updated
            parent_id: Proposed parent ID
            all_tasks: List of all tasks
            
        Raises:
            ValidationError: If circular dependency detected
        """
        if not parent_id:
            return
        
        # Check if task would be its own ancestor
        visited = set()
        current_id = parent_id
        task_map = {t.id: t for t in all_tasks}
        
        while current_id:
            if current_id == task_id:
                raise ValidationError("Circular dependency detected: task cannot be its own ancestor")
            
            if current_id in visited:
                # Circular reference in existing tree (shouldn't happen, but check anyway)
                break
            
            visited.add(current_id)
            current_task = task_map.get(current_id)
            if not current_task:
                break
            
            current_id = current_task.parent_id
    
    @staticmethod
    def validate_depth(parent_id: Optional[str], all_tasks: List['Task'], max_depth: int = MAX_DEPTH) -> None:
        """Validate that adding task won't exceed maximum depth.
        
        Args:
            parent_id: Parent task ID
            all_tasks: List of all tasks
            max_depth: Maximum allowed depth
            
        Raises:
            ValidationError: If depth limit would be exceeded
        """
        if not parent_id:
            return
        
        task_map = {t.id: t for t in all_tasks}
        depth = 1
        current_id = parent_id
        
        while current_id and depth < max_depth:
            current_task = task_map.get(current_id)
            if not current_task:
                break
            
            current_id = current_task.parent_id
            depth += 1
        
        if depth >= max_depth:
            raise ValidationError(f"Maximum task depth of {max_depth} levels would be exceeded")
