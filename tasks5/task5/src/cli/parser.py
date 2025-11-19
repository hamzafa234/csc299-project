"""Command-line argument parser."""

import argparse
from typing import List

from src import __version__


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser with all commands and options.
    
    Returns:
        Configured ArgumentParser instance
    """
    parser = argparse.ArgumentParser(
        prog='task',
        description='Task Management System - Organize and track your tasks from the command line',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Global flags
    parser.add_argument(
        '--version',
        action='version',
        version=f'%(prog)s {__version__}'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output in JSON format'
    )
    parser.add_argument(
        '--data-file',
        metavar='PATH',
        help='Specify custom data file location (default: tasks.json)'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show detailed operation information'
    )
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Suppress all non-error output'
    )
    
    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Add command
    add_parser = subparsers.add_parser('add', help='Add a new task')
    add_parser.add_argument('description', help='Task description')
    add_parser.add_argument(
        '--priority',
        choices=['high', 'medium', 'low'],
        default='medium',
        help='Task priority (default: medium)'
    )
    add_parser.add_argument(
        '--parent',
        metavar='TASK_ID',
        help='Parent task ID (for subtasks)'
    )
    
    # List command
    list_parser = subparsers.add_parser('list', help='List all tasks')
    list_parser.add_argument(
        '--priority',
        choices=['high', 'medium', 'low'],
        help='Filter by priority'
    )
    list_parser.add_argument(
        '--status',
        choices=['complete', 'incomplete'],
        help='Filter by completion status'
    )
    list_parser.add_argument(
        '--parent',
        metavar='TASK_ID',
        help='Show only subtasks of specified parent'
    )
    
    # Complete command
    complete_parser = subparsers.add_parser('complete', help='Mark task as complete')
    complete_parser.add_argument('task_id', metavar='TASK_ID', help='Task ID (full UUID or first 8 chars)')
    
    # Uncomplete command
    uncomplete_parser = subparsers.add_parser('uncomplete', help='Mark task as incomplete')
    uncomplete_parser.add_argument('task_id', metavar='TASK_ID', help='Task ID (full UUID or first 8 chars)')
    
    # Remove command
    remove_parser = subparsers.add_parser('remove', help='Remove a task')
    remove_parser.add_argument('task_id', metavar='TASK_ID', help='Task ID (full UUID or first 8 chars)')
    remove_parser.add_argument(
        '--force', '-f',
        action='store_true',
        help='Skip confirmation prompt'
    )
    
    # Priority command
    priority_parser = subparsers.add_parser('priority', help='Set task priority')
    priority_parser.add_argument('task_id', metavar='TASK_ID', help='Task ID (full UUID or first 8 chars)')
    priority_parser.add_argument(
        'priority_level',
        choices=['high', 'medium', 'low'],
        help='New priority level'
    )
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search tasks by keywords')
    search_parser.add_argument('keywords', nargs='+', help='Keywords to search for')
    search_parser.add_argument(
        '--case-sensitive',
        action='store_true',
        help='Enable case-sensitive search'
    )
    
    # Show command
    show_parser = subparsers.add_parser('show', help='Show detailed task information')
    show_parser.add_argument('task_id', metavar='TASK_ID', help='Task ID (full UUID or first 8 chars)')
    
    return parser


def parse_args(args: List[str] = None) -> argparse.Namespace:
    """Parse command-line arguments.
    
    Args:
        args: List of argument strings (None to use sys.argv)
        
    Returns:
        Parsed arguments namespace
    """
    parser = create_parser()
    return parser.parse_args(args)
