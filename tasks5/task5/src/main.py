"""Main entry point for task management system."""

import sys
import os
from typing import Optional

from src.cli.parser import parse_args
from src.cli import commands
from src.models.task import ValidationError, TaskNotFoundError


def get_data_file(args) -> str:
    """Get data file path from args or environment.
    
    Args:
        args: Parsed arguments
        
    Returns:
        Data file path
    """
    # Priority: --data-file flag > TASK_DATA_FILE env > default
    if args.data_file:
        return args.data_file
    
    env_file = os.environ.get('TASK_DATA_FILE')
    if env_file:
        return env_file
    
    return 'tasks.json'


def main(argv: Optional[list] = None) -> int:
    """Main entry point.
    
    Args:
        argv: Command-line arguments (None to use sys.argv)
        
    Returns:
        Exit code (0=success, 1=usage error, 2=runtime error)
    """
    args = None
    
    try:
        # Parse arguments
        args = parse_args(argv)
        
        # Check if command was provided
        if not args.command:
            parse_args(['--help'])
            return 1
        
        # Get data file
        data_file = get_data_file(args)
        
        # Route to command handler
        command_handlers = {
            'add': commands.handle_add,
            'list': commands.handle_list,
            'complete': commands.handle_complete,
            'uncomplete': commands.handle_uncomplete,
            'remove': commands.handle_remove,
            'priority': commands.handle_priority,
            'search': commands.handle_search,
            'show': commands.handle_show
        }
        
        handler = command_handlers.get(args.command)
        if not handler:
            print(f"Unknown command: {args.command}", file=sys.stderr)
            return 1
        
        # Execute command
        handler(args, data_file)
        return 0
        
    except ValidationError as e:
        if not args or not args.quiet:
            print(f"Validation error: {e}", file=sys.stderr)
        return e.exit_code
    
    except TaskNotFoundError as e:
        if not args or not args.quiet:
            print(f"Error: {e}", file=sys.stderr)
        return e.exit_code
    
    except KeyboardInterrupt:
        if not args or not args.quiet:
            print("\nOperation cancelled by user", file=sys.stderr)
        return 1
    
    except Exception as e:
        if not args or not args.quiet:
            print(f"Error: {e}", file=sys.stderr)
        if args and args.verbose:
            import traceback
            traceback.print_exc()
        return 2


if __name__ == '__main__':
    sys.exit(main())
