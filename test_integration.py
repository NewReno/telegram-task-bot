import pytest
import os
import json
from datetime import datetime
from parser import parse_task
from storage import save_task, get_tasks
from config import DATA_DIR


class TestIntegration:
    """End-to-end integration tests."""
    
    @pytest.fixture
    def temp_data_dir(self, tmp_path, monkeypatch):
        """Create temporary data directory for tests."""
        import storage
        import config
        monkeypatch.setattr(storage, 'DATA_DIR', str(tmp_path))
        monkeypatch.setattr(config, 'DATA_DIR', str(tmp_path))
        yield str(tmp_path)
    
    def test_full_task_creation_flow(self, temp_data_dir):
        """Test complete flow: message → parse → save → verify storage."""
        # Simulate user message
        message = "Remind me Test Task at 14:30"
        
        # Step 1: Parse the message
        result = parse_task(message)
        assert result['success'] is True
        assert result['task_name'] == "Test Task"
        assert result['time'] == "14:30"
        
        # Step 2: Save to storage
        task = save_task(result['task_name'], result['time'])
        
        # Step 3: Verify in storage
        today = datetime.now().strftime('%Y-%m-%d')
        tasks = get_tasks(today)
        
        assert len(tasks) == 1
        assert tasks[0]['task_name'] == "Test Task"
        assert tasks[0]['time'] == "14:30"
        assert tasks[0]['status'] == "pending"
        assert tasks[0]['id'] == 1
    
    def test_add_task_syntax_flow(self, temp_data_dir):
        """Test flow with 'add task' syntax."""
        message = "add task Wake up at 08:00"
        
        result = parse_task(message)
        assert result['success'] is True
        
        task = save_task(result['task_name'], result['time'])
        
        today = datetime.now().strftime('%Y-%m-%d')
        tasks = get_tasks(today)
        
        assert len(tasks) == 1
        assert tasks[0]['task_name'] == "Wake up"
        assert tasks[0]['time'] == "08:00"
    
    def test_error_flow_invalid_time(self, temp_data_dir):
        """Test error handling flow."""
        message = "Remind me Test at 25:00"
        
        result = parse_task(message)
        assert result['success'] is False
        assert "Invalid time format" in result['error']
        
        # Verify nothing was saved
        today = datetime.now().strftime('%Y-%m-%d')
        tasks = get_tasks(today)
        assert len(tasks) == 0
    
    def test_multiple_tasks_flow(self, temp_data_dir):
        """Test creating multiple tasks."""
        messages = [
            "Remind me Task 1 at 10:00",
            "add task Task 2 at 11:00",
            "Remind me Task 3 at 12:00"
        ]
        
        for msg in messages:
            result = parse_task(msg)
            assert result['success'] is True
            save_task(result['task_name'], result['time'])
        
        today = datetime.now().strftime('%Y-%m-%d')
        tasks = get_tasks(today)
        
        assert len(tasks) == 3
        assert tasks[0]['task_name'] == "Task 1"
        assert tasks[1]['task_name'] == "Task 2"
        assert tasks[2]['task_name'] == "Task 3"
        # Check IDs are sequential
        assert tasks[0]['id'] == 1
        assert tasks[1]['id'] == 2
        assert tasks[2]['id'] == 3
