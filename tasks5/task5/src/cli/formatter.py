"""Output formatting for human and JSON output."""

import json
import sys
from typing import List, Dict, Any, Optional

from src.models.task import Task


class Formatter:
    """Format task output for human and JSON consumption."""
    
    # ANSI color codes
    COLORS = {
        'red': '\033[91m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'green': '\033[92m',
        'gray': '\033[90m',
        'reset': '\033[0m',
        'bold': '\033[1m',
        'dim': '\033[2m'
    }
    
    def __init__(self, use_color: Optional[bool] = None):
        """Initialize formatter.
        
        Args:
            use_color: Force color on/off (None for auto-detect)
        """
        if use_color is None:
            # Auto-detect TTY and check environment
            import os
            no_color = os.environ.get('TASK_NO_COLOR', '').lower() in ('1', 'true', 'yes')
            self.use_color = sys.stdout.isatty() and not no_color
        else:
            self.use_color = use_color
    
    def _colorize(self, text: str, color: str) -> str:
        """Apply color to text if color is enabled.
        
        Args:
            text: Text to colorize
            color: Color name
            
        Returns:
            Colorized text or plain text
        """
        if not self.use_color or color not in self.COLORS:
            return text
        return f"{self.COLORS[color]}{text}{self.COLORS['reset']}"
    
    def format_json(self, data: Any) -> str:
        """Format data as JSON.
        
        Args:
            data: Data to format
            
        Returns:
            JSON string
        """
        return json.dumps(data, indent=2, ensure_ascii=False)
    
    def format_human(self, tasks: List[Task], show_tree: bool = False) -> str:
        """Format tasks as human-readable output.
        
        Args:
            tasks: List of tasks to format
            show_tree: Show hierarchical tree structure
            
        Returns:
            Formatted string
        """
        if not tasks:
            return "No tasks found."
        
        lines = []
        
        if show_tree:
            # Show hierarchical structure
            lines.extend(self._format_tree(tasks))
        else:
            # Group by priority
            groups = {
                'high': [],
                'medium': [],
                'low': []
            }
            
            for task in tasks:
                groups[task.priority].append(task)
            
            for priority in ['high', 'medium', 'low']:
                priority_tasks = groups[priority]
                if not priority_tasks:
                    continue
                
                # Priority header
                priority_color = {'high': 'red', 'medium': 'yellow', 'low': 'blue'}[priority]
                header = f"\n{priority.upper()} PRIORITY ({len(priority_tasks)})"
                lines.append(self._colorize(header, priority_color))
                lines.append(self._colorize("─" * 40, priority_color))
                
                for task in sorted(priority_tasks, key=lambda t: t.created_at, reverse=True):
                    lines.append(self._format_task(task))
        
        return '\n'.join(lines)
    
    def _format_task(self, task: Task, indent: int = 0, is_last: bool = True) -> str:
        """Format a single task.
        
        Args:
            task: Task to format
            indent: Indentation level
            is_last: Whether this is the last item in its group
            
        Returns:
            Formatted task string
        """
        # Completion symbol
        symbol = '✓' if task.completed else '○'
        
        # Task ID (first 8 chars)
        task_id = task.id[:8]
        
        # Build task line
        prefix = "  " * indent
        description = task.description
        
        # Apply dimming for completed tasks
        if task.completed:
            symbol = self._colorize(symbol, 'green')
            description = self._colorize(description, 'gray')
            task_id = self._colorize(task_id, 'gray')
        else:
            task_id = self._colorize(task_id, 'blue')
        
        # Show subtask count if present
        subtask_info = ""
        if task.subtasks:
            subtask_info = self._colorize(f" [{len(task.subtasks)} subtask(s)]", 'dim')
        
        return f"{prefix}{symbol} {task_id} - {description}{subtask_info}"
    
    def _format_tree(self, tasks: List[Task]) -> List[str]:
        """Format tasks as hierarchical tree.
        
        Args:
            tasks: List of all tasks
            
        Returns:
            List of formatted lines
        """
        lines = []
        task_map = {t.id: t for t in tasks}
        
        # Find root tasks (no parent)
        root_tasks = [t for t in tasks if not t.parent_id]
        
        def format_subtree(task: Task, indent: int = 0, prefix: str = ""):
            """Recursively format task and its subtasks."""
            lines.append(f"{prefix}{self._format_task(task)}")
            
            # Format subtasks
            for i, subtask_id in enumerate(task.subtasks):
                subtask = task_map.get(subtask_id)
                if not subtask:
                    continue
                
                is_last = i == len(task.subtasks) - 1
                branch = "└─ " if is_last else "├─ "
                continuation = "   " if is_last else "│  "
                
                format_subtree(subtask, indent + 1, prefix + continuation)
        
        # Format each root task
        for task in sorted(root_tasks, key=lambda t: t.created_at, reverse=True):
            format_subtree(task)
        
        return lines
    
    def format_task_detail(self, task: Task, all_tasks: List[Task]) -> str:
        """Format detailed task information.
        
        Args:
            task: Task to format
            all_tasks: All tasks (for parent/subtask context)
            
        Returns:
            Formatted detail string
        """
        lines = []
        task_map = {t.id: t for t in all_tasks}
        
        # Header
        lines.append(self._colorize("TASK DETAILS", 'bold'))
        lines.append(self._colorize("─" * 40, 'gray'))
        
        # Basic info
        lines.append(f"ID:          {task.id}")
        lines.append(f"Description: {task.description}")
        lines.append(f"Status:      {'✓ Complete' if task.completed else '○ Incomplete'}")
        
        priority_color = {'high': 'red', 'medium': 'yellow', 'low': 'blue'}[task.priority]
        priority_text = self._colorize(task.priority.upper(), priority_color)
        lines.append(f"Priority:    {priority_text}")
        
        lines.append(f"Created:     {task.created_at}")
        
        # Parent info
        if task.parent_id:
            parent = task_map.get(task.parent_id)
            parent_desc = parent.description if parent else "Unknown"
            lines.append(f"Parent:      {task.parent_id[:8]} - {parent_desc}")
        
        # Subtasks
        if task.subtasks:
            lines.append(f"\nSubtasks ({len(task.subtasks)}):")
            for subtask_id in task.subtasks:
                subtask = task_map.get(subtask_id)
                if subtask:
                    symbol = '✓' if subtask.completed else '○'
                    lines.append(f"  {symbol} {subtask_id[:8]} - {subtask.description}")
        
        return '\n'.join(lines)
