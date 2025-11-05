from .tasks import main as task_main

def inc(n: int) -> int:
    return n + 1

def main():
    task_main()  # Calls your main function from tasks.py
