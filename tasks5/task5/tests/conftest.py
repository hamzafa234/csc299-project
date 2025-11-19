"""Pytest configuration and fixtures."""

import pytest
import tempfile
import os
from pathlib import Path


@pytest.fixture
def temp_task_file():
    """Create a temporary task file for testing.
    
    Yields:
        Path to temporary JSON file
    """
    # Create temporary file
    fd, path = tempfile.mkstemp(suffix='.json')
    os.close(fd)
    
    # Initialize with empty task list
    with open(path, 'w') as f:
        f.write('{"tasks": []}')
    
    yield path
    
    # Cleanup
    try:
        os.unlink(path)
    except:
        pass
