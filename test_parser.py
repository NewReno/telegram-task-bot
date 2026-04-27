import pytest
from parser import parse_task


class TestParseTask:
    """Test cases for parse_task function."""
    
    def test_remind_me_valid(self):
        """Test 'Remind me' syntax with valid input."""
        result = parse_task("Remind me Vacuum at 13:00")
        assert result['success'] is True
        assert result['task_name'] == "Vacuum"
        assert result['time'] == "13:00"
    
    def test_add_task_valid(self):
        """Test 'add task' syntax with valid input."""
        result = parse_task("add task Wake up at 08:00")
        assert result['success'] is True
        assert result['task_name'] == "Wake up"
        assert result['time'] == "08:00"
    
    def test_remind_me_lowercase(self):
        """Test case insensitivity."""
        result = parse_task("remind me test at 15:30")
        assert result['success'] is True
        assert result['task_name'] == "test"
        assert result['time'] == "15:30"
    
    def test_task_name_with_spaces(self):
        """Test task name with multiple words."""
        result = parse_task("Remind me Clean the kitchen at 16:00")
        assert result['success'] is True
        assert result['task_name'] == "Clean the kitchen"
        assert result['time'] == "16:00"
    
    def test_invalid_time_format_hour_too_high(self):
        """Test time with hour > 23."""
        result = parse_task("Remind me Test at 25:00")
        assert result['success'] is False
        assert "Invalid time format" in result['error']
    
    def test_invalid_time_format_minute_too_high(self):
        """Test time with minute > 59."""
        result = parse_task("Remind me Test at 12:60")
        assert result['success'] is False
        assert "Invalid time format" in result['error']
    
    def test_invalid_time_format_no_colon(self):
        """Test time without colon."""
        result = parse_task("Remind me Test at 1300")
        assert result['success'] is False
        assert "Invalid time format" in result['error']
    
    def test_missing_at_keyword(self):
        """Test missing 'at' keyword."""
        result = parse_task("Remind me Test 13:00")
        assert result['success'] is False
        assert "at HH:MM" in result['error']
    
    def test_missing_time(self):
        """Test missing time entirely."""
        result = parse_task("Remind me Test")
        assert result['success'] is False
    
    def test_empty_task_name(self):
        """Test empty task name."""
        result = parse_task("Remind me at 13:00")
        assert result['success'] is False
        assert "empty" in result['error'].lower()
    
    def test_unrecognized_command(self):
        """Test completely unrelated message."""
        result = parse_task("Hello bot, how are you?")
        assert result['success'] is False
        assert "Unrecognized" in result['error']
    
    # Tests for relative time parsing
    def test_remind_me_in_minutes(self):
        """Test 'in X minutes' syntax."""
        from datetime import datetime, timedelta
        result = parse_task("Remind me Test task in 10 minutes")
        assert result['success'] is True
        assert result['task_name'] == "Test task"
        # Verify time is approximately 10 minutes from now
        expected_time = (datetime.now() + timedelta(minutes=10)).strftime('%H:%M')
        assert result['time'] == expected_time
    
    def test_remind_me_in_hours(self):
        """Test 'in X hours' syntax."""
        from datetime import datetime, timedelta
        result = parse_task("Remind me Test task in 2 hours")
        assert result['success'] is True
        assert result['task_name'] == "Test task"
        expected_time = (datetime.now() + timedelta(hours=2)).strftime('%H:%M')
        assert result['time'] == expected_time
    
    def test_remind_me_in_hours_and_minutes(self):
        """Test 'in X hours and Y minutes' syntax."""
        from datetime import datetime, timedelta
        result = parse_task("Remind me Test task in 1 hour and 30 minutes")
        assert result['success'] is True
        assert result['task_name'] == "Test task"
        expected_time = (datetime.now() + timedelta(hours=1, minutes=30)).strftime('%H:%M')
        assert result['time'] == expected_time
    
    def test_remind_me_in_mins_abbr(self):
        """Test 'in X mins' abbreviation."""
        from datetime import datetime, timedelta
        result = parse_task("Remind me Test in 15 mins")
        assert result['success'] is True
        expected_time = (datetime.now() + timedelta(minutes=15)).strftime('%H:%M')
        assert result['time'] == expected_time
    
    def test_remind_me_in_hrs_abbr(self):
        """Test 'in X hrs' abbreviation."""
        from datetime import datetime, timedelta
        result = parse_task("Remind me Test in 3 hrs")
        assert result['success'] is True
        expected_time = (datetime.now() + timedelta(hours=3)).strftime('%H:%M')
        assert result['time'] == expected_time
    
    def test_add_task_in_minutes(self):
        """Test 'add task ... in X minutes' syntax."""
        from datetime import datetime, timedelta
        result = parse_task("add task Test task in 5 minutes")
        assert result['success'] is True
        assert result['task_name'] == "Test task"
        expected_time = (datetime.now() + timedelta(minutes=5)).strftime('%H:%M')
        assert result['time'] == expected_time
    
    def test_remind_me_in_single_hour(self):
        """Test 'in 1 hour' syntax."""
        from datetime import datetime, timedelta
        result = parse_task("Remind me Test in 1 hour")
        assert result['success'] is True
        expected_time = (datetime.now() + timedelta(hours=1)).strftime('%H:%M')
        assert result['time'] == expected_time
    
    def test_remind_me_in_compact_format(self):
        """Test 'in 1h30m' compact format."""
        from datetime import datetime, timedelta
        result = parse_task("Remind me Test in 1h30m")
        assert result['success'] is True
        expected_time = (datetime.now() + timedelta(hours=1, minutes=30)).strftime('%H:%M')
        assert result['time'] == expected_time
    
    def test_relative_time_invalid_format(self):
        """Test invalid relative time format."""
        result = parse_task("Remind me Test in abc minutes")
        assert result['success'] is False
        assert "Invalid time format" in result['error']
    
    def test_relative_time_empty_after_in(self):
        """Test 'in' with nothing after it."""
        result = parse_task("Remind me Test in")
        assert result['success'] is False
        assert "Task name cannot be empty" in result['error']
