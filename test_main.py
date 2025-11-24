from main import *  # or import specific functions
import subprocess
import json
from pathlib import Path

def test_bg(tmp_path):
    # Get the path to main.py (in the project root)
    main_py = Path(__file__).parent.parent / "main.py"
    
    result = subprocess.run(
        ["python3", str(main_py), "bg", "ORCL"], 
        cwd=tmp_path,  # Run in tmp_path so output files go there
        capture_output=True,
        text=True 
    )
    
    # Check the result
    assert result.returncode == 0, f"Command failed: {result.stderr}"
    assert (tmp_path / "ORCL_notes.json").exists()
    assert (tmp_path /"ORCL_financials.json").exists()

def test_wac(tmp_path): 
    # Get the path to main.py (in the project root)
    main_py = Path(__file__).parent.parent / "main.py"
    
    result = subprocess.run(
        ["python3", str(main_py), "bg", "CELH"], 
        cwd=tmp_path,  # Run in tmp_path so output files go there
        capture_output=True,
        text=True 
    )

    result = subprocess.run(
        ["python3", str(main_py), "wac"], 
        cwd=tmp_path,  # Run in tmp_path so output files go there
        capture_output=True,
        text=True 
    )

    assert (tmp_path / "CELH_notes.json").exists()
    assert (tmp_path /"CELH_financials.json").exists()
    assert (tmp_path / "CELH_summary.md").exists()
