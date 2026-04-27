import pytest
import os
import json
from datetime import datetime
from storage import save_task, get_tasks, _get_filename
from config import DATA_DIR


class TestStorage:
    """Test cases for storage module."""
    
    @pytest.fixture
    def temp_data_dir(self, tmp_path):
        """Create temporary data directory for tests."""
        original_dir = DATA_DIR
        # Override DATA_DIR for tests
        import storage
        storage.DATA_DIR = str(tmp_path)
        yield str(tmp_path)
        # Cleanup
        storage.DATA_DIR = original_dir
    
    def test_save_task_creates_file(self, temp_data_dir):
        """Test that saving a task creates the JSON file."""
        task = save_task("Test Task", "14:30", "2026-04-27")
        
        filename = os.path.join(temp_data_dir, "tasks_2026-04-27.json")
        assert os.path.exists(filename)
    
    def test_save_task_structure(self, temp_data_dir):
        """Test that saved task has all required fields."""
        task = save_task("Test Task", "14:30", "2026-04-27")
        
        assert 'id' in task
        assert 'task_name' in task
        assert 'date' in task
        assert 'time' in task
        assert 'status' in task
        assert 'created_at' in task
        assert 'completed_at' in task
        
        assert task['task_name'] == "Test Task"
        assert task['time'] == "14:30"
        assert task['date'] == "2026-04-27"
        assert task['status'] == "pending"
        assert task['completed_at'] is None
    
    def test_save_task_assigns_sequential_ids(self, temp_data_dir):
        """Test that tasks get sequential IDs."""
        task1 = save_task("Task 1", "10:00", "2026-04-27")
        task2 = save_task("Task 2", "11:00", "2026-04-27")
        task3 = save_task("Task 3", "12:00", "2026-04-27")
        
        assert task1['id'] == 1
        assert task2['id'] == 2
        assert task3['id'] == 3
    
    def test_get_tasks_empty(self, temp_data_dir):
        """Test getting tasks for date with no tasks."""
        tasks = get_tasks("2026-04-27")
        assert tasks == []
    
    def test_get_tasks_returns_saved_tasks(self, temp_data_dir):
        """Test that get_tasks returns saved tasks."""
        save_task("Task 1", "10:00", "2026-04-27")
        save_task("Task 2", "11:00", "2026-04-27")
        
        tasks = get_tasks("2026-04-27")
        
        assert len(tasks) == 2
        assert tasks[0]['task_name'] == "Task 1"
        assert tasks[1]['task_name'] == "Task 2"
    
    def test_save_to_different_dates(self, temp_data_dir):
        """Test saving tasks to different dates."""
        save_task("Today Task", "10:00", "2026-04-27")
        save_task("Tomorrow Task", "11:00", "2026-04-28")
        
        today_tasks = get_tasks("2026-04-27")
        tomorrow_tasks = get_tasks("2026-04-28")
        
        assert len(today_tasks) == 1
        assert len(tomorrow_tasks) == 1
        assert today_tasks[0]['task_name'] == "Today Task"
        assert tomorrow_tasks[0]['task_name'] == "Tomorrow Task"
    
    def test_json_file_format(self, temp_data_dir):
        """Test that JSON file has correct structure."""
        save_task("Test", "14:00", "2026-04-27")
        
        filename = os.path.join(temp_data_dir, "tasks_2026-04-27.json")
        with open(filename, 'r') as f:
            data = json.load(f)
        
        assert 'date' in data
        assert 'tasks' in data
        assert data['date'] == "2026-04-27"
        assert isinstance(data['tasks'], list)
        assert len(data['tasks']) == 1
