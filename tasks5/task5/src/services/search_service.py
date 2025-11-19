"""Search service for keyword-based task search."""

from typing import List

from src.models.task import Task, ValidationError


class SearchService:
    """Service for searching tasks by keywords."""
    
    MAX_KEYWORD_LENGTH = 100
    
    @staticmethod
    def search_tasks(
        tasks: List[Task],
        keywords: List[str],
        case_sensitive: bool = False
    ) -> List[Task]:
        """Search tasks by keywords.
        
        Uses substring matching with OR logic (any keyword matches).
        
        Args:
            tasks: List of tasks to search
            keywords: List of keywords to search for
            case_sensitive: Enable case-sensitive search
            
        Returns:
            List of matching tasks
            
        Raises:
            ValidationError: If keywords are invalid
        """
        # Validate keywords
        for keyword in keywords:
            if not keyword or not keyword.strip():
                raise ValidationError("Keywords cannot be empty")
            if len(keyword) > SearchService.MAX_KEYWORD_LENGTH:
                raise ValidationError(
                    f"Keyword exceeds maximum length of {SearchService.MAX_KEYWORD_LENGTH} characters"
                )
        
        # Prepare keywords
        search_keywords = keywords if case_sensitive else [k.lower() for k in keywords]
        
        # Search
        matching_tasks = []
        for task in tasks:
            description = task.description if case_sensitive else task.description.lower()
            
            # Check if any keyword matches
            for keyword in search_keywords:
                if keyword in description:
                    matching_tasks.append(task)
                    break
        
        return matching_tasks
