"""Task storage with atomic writes."""

import json
import os
import tempfile
from pathlib import Path
from typing import List, Dict, Any

from .task import Task


class TaskStore:
    """JSON-based task storage with atomic writes."""
    
    def __init__(self, data_file: str = 'tasks.json'):
        """Initialize task store.
        
        Args:
            data_file: Path to JSON data file
        """
        self.data_file = Path(data_file)
    
    def load(self) -> List[Task]:
        """Load tasks from JSON file.
        
        Returns:
            List of Task instances
            
        Raises:
            Exception: If file read fails
        """
        if not self.data_file.exists():
            return []
        
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                tasks_data = data.get('tasks', [])
                return [Task.from_dict(task_data) for task_data in tasks_data]
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse task data: {e}")
        except Exception as e:
            raise Exception(f"Failed to load tasks: {e}")
    
    def save(self, tasks: List[Task]) -> None:
        """Save tasks to JSON file using atomic write pattern.
        
        Uses temp file + rename to ensure atomic writes.
        
        Args:
            tasks: List of Task instances to save
            
        Raises:
            Exception: If file write fails
        """
        data = {
            'tasks': [task.to_dict() for task in tasks]
        }
        
        # Write to temporary file first
        temp_fd, temp_path = tempfile.mkstemp(
            dir=self.data_file.parent if self.data_file.parent.exists() else None,
            prefix='.tasks_tmp_',
            suffix='.json'
        )
        
        try:
            with os.fdopen(temp_fd, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                f.flush()
                os.fsync(f.fileno())
            
            # Atomic rename
            os.replace(temp_path, self.data_file)
        except Exception as e:
            # Clean up temp file on error
            try:
                os.unlink(temp_path)
            except:
                pass
            raise Exception(f"Failed to save tasks: {e}")
