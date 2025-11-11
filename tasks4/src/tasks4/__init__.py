from openai import OpenAI
from typing import List, Optional

def inc(n: int) -> int:
    """Increment a number by 1"""
    return n + 1

class TaskSummarizer:
    """A class to summarize tasks using OpenAI API"""
    
    def __init__(self, api_key: str, model: str = "gpt-4.1-mini"):
        """
        Initialize the TaskSummarizer
        
        Args:
            api_key: OpenAI API key
            model: Model to use for summarization
        """
        self.client = OpenAI(api_key=api_key)
        self.model = model
    
    def summarize_task(self, task: str) -> str:
        """
        Summarize a single task
        
        Args:
            task: The task description to summarize
            
        Returns:
            The summarized task
        """
        response = self.client.responses.create(
            model=self.model,
            input=[{
                "role": "user",
                "content": f"Summarize this task concisely (do not perform it): {task}"
            }]
        )
        return response.output_text
    
    def summarize_tasks(self, tasks: List[str]) -> List[str]:
        """
        Summarize multiple tasks
        
        Args:
            tasks: List of task descriptions
            
        Returns:
            List of summarized tasks
        """
        summaries = []
        for task in tasks:
            summary = self.summarize_task(task)
            summaries.append(summary)
        return summaries
    
    def print_summaries(self, tasks: List[str]) -> None:
        """
        Print summaries for all tasks
        
        Args:
            tasks: List of task descriptions
        """
        for i, task in enumerate(tasks, 1):
            summary = self.summarize_task(task)
            print(f"Task {i} summary:")
            print(summary)
            print()


def main():
    """Main entry point"""
    api_key = "xxxxx"  # In production, use environment variables
    
    summarizer = TaskSummarizer(api_key=api_key)
    
    tasks = [
        "Your first task is to make a video game. To make a video game, start by planning your concept — decide on the genre, story, characters, and overall gameplay mechanics. Next, design a game development plan outlining the levels, art style, and user interface. Choose a game engine such as Unity, Unreal Engine, or Godot, and begin building your game world by creating or importing assets like characters, backgrounds, and sound effects. Then, write the game logic using the engine's scripting language (for example, C# in Unity or Blueprint/C++ in Unreal) to control movement, interactions, and objectives. Continuously test and debug to fix any errors or balance issues. Finally, add polish with music, menus, and visual effects, and prepare your game for release by packaging it for your chosen platform (PC, console, or mobile) and sharing it with players.",
        
        "Your second task is to make a PC. To build a PC, start by choosing compatible components — including a CPU, motherboard, RAM, storage drive (SSD or HDD), GPU, power supply, and case. Once you have everything, prepare a clean workspace and ground yourself to prevent static damage. Begin by installing the CPU onto the motherboard, applying a small amount of thermal paste, and attaching the CPU cooler. Next, insert the RAM sticks into the appropriate slots and mount the motherboard inside the case using standoffs. After that, install the power supply and connect its cables to the motherboard, CPU, and GPU. Add your storage drives, securing them in place and connecting the SATA or NVMe cables. Then, install the graphics card into the PCIe slot and connect any required power cables. Once all components are connected, double-check all connections, close the case, and connect a monitor, keyboard, and mouse. Power on the system to ensure everything works, then install your operating system and drivers to complete your custom-built PC."
    ]
    
    summarizer.print_summaries(tasks)


if __name__ == "__main__":
    main()