"""
Task Manager Module for ESP32 IoT Control System
===============================================

Provides scheduled task management with persistent storage for automated
device operations. Supports time-based scheduling with JSON file storage
and configurable task limits for memory efficiency.

Author: Erfan Mohamadnia
License: MIT
Version: 1.0.0

Features:
- Persistent task storage in JSON format
- Configurable maximum task limits
- Time-based task scheduling (date/time format)
- Device-specific task management
- Duration-based operations
- Automatic task cleanup after execution

Task Format:
    {
        "date": "YYYY-MM-DD",    # Execution date
        "time": "HH:MM",         # Execution time (24-hour format)
        "device": "device_name", # Target device (pump1, pump2, pump3, dcmotor)
        "duration": 300          # Duration in seconds
    }

Usage Example:
    task_manager = TaskManager('tasks.json', max_tasks=50)
    task_manager.add_task('2024-12-25', '14:30', 'pump1', 300)
    tasks = task_manager.get_tasks()
    task_manager.delete_task(0)
"""

import ujson
import os


class TaskManager:
    """
    Manages scheduled tasks with persistent JSON storage.
    
    This class provides functionality for creating, storing, and managing
    scheduled tasks for IoT device automation. Tasks are stored persistently
    in JSON format and can be executed at specified times.
    
    Attributes:
        filename (str): JSON file path for task storage
        max_tasks (int): Maximum number of tasks allowed
        tasks (list): List of scheduled task dictionaries
    """
    
    def __init__(self, filename='tasks.json', max_tasks=20):
        """
        Initialize task manager with storage file and limits.
        
        Args:
            filename (str): JSON file for persistent task storage
            max_tasks (int): Maximum number of tasks to prevent memory issues
        """
        self.filename = filename
        self.max_tasks = max_tasks
        self._load_tasks()

    def _load_tasks(self):
        """
        Load tasks from JSON storage file.
        
        Attempts to read tasks from the specified JSON file. If the file
        doesn't exist or is corrupted, initializes with an empty task list.
        """
        try:
            if self.filename in os.listdir():
                with open(self.filename, 'r') as f:
                    self.tasks = ujson.load(f)
                print(f"📋 Loaded {len(self.tasks)} scheduled tasks")
            else:
                self.tasks = []
                print("📋 No existing tasks found, starting with empty list")
        except Exception as e:
            print(f"⚠️ Error loading tasks: {e}")
            self.tasks = []

    def _save_tasks(self):
        """
        Save current tasks to JSON storage file.
        
        Writes the current task list to the JSON file for persistent storage.
        Handles file I/O errors gracefully.
        """
        try:
            with open(self.filename, 'w') as f:
                ujson.dump(self.tasks, f)
            print(f"💾 Tasks saved successfully ({len(self.tasks)} tasks)")
        except Exception as e:
            print(f"❌ Error saving tasks: {e}")

    def add_task(self, date, time, device, duration):
        """
        Add a new scheduled task.
        
        Creates a new task with the specified parameters and adds it to the
        task list. Enforces maximum task limits to prevent memory issues.
        
        Args:
            date (str): Execution date in "YYYY-MM-DD" format
            time (str): Execution time in "HH:MM" format (24-hour)
            device (str): Target device name (pump1, pump2, pump3, dcmotor)
            duration (int): Operation duration in seconds
            
        Raises:
            ValueError: If maximum task limit is reached
        """
        if len(self.tasks) >= self.max_tasks:
            raise ValueError(f"Maximum number of tasks reached ({self.max_tasks})")
        
        task = {
            "date": date,           # Format: "YYYY-MM-DD"
            "time": time,           # Format: "HH:MM" (24-hour)
            "device": device,       # Device identifier
            "duration": duration    # Duration in seconds
        }

        self.tasks.append(task)
        self._save_tasks()
        print(f"✅ Task scheduled: {device} on {date} at {time} for {duration}s")

    def get_tasks(self):
        """
        Get all scheduled tasks.
        
        Returns:
            list: List of task dictionaries
        """
        return self.tasks

    def delete_task(self, index):
        """
        Delete a task by its index.
        
        Args:
            index (int): Task index in the task list
            
        Returns:
            bool: True if task was deleted successfully, False if index invalid
        """
        if 0 <= index < len(self.tasks):
            deleted_task = self.tasks[index]
            del self.tasks[index]
            self._save_tasks()
            print(f"🗑️ Task deleted: {deleted_task['device']} on {deleted_task['date']} at {deleted_task['time']}")
            return True
        else:
            print(f"❌ Invalid task index: {index}")
            return False
