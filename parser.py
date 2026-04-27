import re
from datetime import datetime, timedelta


def parse_task(message_text: str) -> dict:
    """
    Parse natural language task commands.
    
    Supports:
    - "Remind me [task] at HH:MM"
    - "add task [task] at HH:MM"
    - "Remind me [task] in X minutes/hours"
    - "add task [task] in X minutes/hours"
    
    Returns:
        dict: {
            'success': bool,
            'task_name': str (if success),
            'time': str (if success),
            'error': str (if not success)
        }
    """
    message_text = message_text.strip()
    
    # Try absolute time patterns first
    result = _parse_absolute_time(message_text)
    if result:
        return result
    
    # Try relative time patterns
    result = _parse_relative_time(message_text)
    if result:
        return result
    
    # No match found, provide error feedback
    return _get_error_feedback(message_text)


def _parse_absolute_time(message_text: str) -> dict:
    """Parse absolute time format: "at HH:MM"""
    # Pattern 1: "Remind me [task] at HH:MM"
    pattern1 = r'^remind\s+me\s+(.+?)\s+at\s+(\d{1,2}:\d{2})$'
    match = re.match(pattern1, message_text, re.IGNORECASE)
    
    if not match:
        # Pattern 2: "add task [task] at HH:MM"
        pattern2 = r'^add\s+task\s+(.+?)\s+at\s+(\d{1,2}:\d{2})$'
        match = re.match(pattern2, message_text, re.IGNORECASE)
    
    if not match:
        return None
    
    task_name = match.group(1).strip()
    time_str = match.group(2)
    
    if not task_name:
        return {
            'success': False,
            'error': 'Task name cannot be empty'
        }
    
    # Validate 24-hour time format
    try:
        datetime.strptime(time_str, '%H:%M')
    except ValueError:
        return {
            'success': False,
            'error': f'Invalid time format "{time_str}". Use 24-hour format (HH:MM), hours 00-23, minutes 00-59'
        }
    
    return {
        'success': True,
        'task_name': task_name,
        'time': time_str
    }


def _parse_relative_time(message_text: str) -> dict:
    """Parse relative time format: "in X minutes/hours"""
    # Pattern 1: "Remind me [task] in X minutes/hours"
    pattern1 = r'^remind\s+me\s+(.+?)\s+in\s+(.+)$'
    match = re.match(pattern1, message_text, re.IGNORECASE)
    
    if not match:
        # Pattern 2: "add task [task] in X minutes/hours"
        pattern2 = r'^add\s+task\s+(.+?)\s+in\s+(.+)$'
        match = re.match(pattern2, message_text, re.IGNORECASE)
    
    if not match:
        return None
    
    task_name = match.group(1).strip()
    time_spec = match.group(2).strip()
    
    if not task_name:
        return {
            'success': False,
            'error': 'Task name cannot be empty'
        }
    
    # Parse the relative time
    minutes = _parse_relative_time_spec(time_spec)
    
    if minutes is None:
        return {
            'success': False,
            'error': f'Invalid time format "{time_spec}". Use: "10 minutes", "2 hours", "1 hour and 30 minutes"'
        }
    
    # Calculate the actual time
    future_time = datetime.now() + timedelta(minutes=minutes)
    time_str = future_time.strftime('%H:%M')
    
    return {
        'success': True,
        'task_name': task_name,
        'time': time_str
    }


def _parse_relative_time_spec(time_spec: str) -> int:
    """
    Parse relative time specification and return total minutes.
    
    Supports:
    - "10 minutes", "10 mins", "10 min"
    - "2 hours", "2 hrs", "2 hr"
    - "1 hour and 30 minutes"
    - "1h30m", "1h 30m"
    
    Returns:
        int: Total minutes, or None if invalid
    """
    time_spec = time_spec.lower().strip()
    total_minutes = 0
    
    # Pattern: "1 hour and 30 minutes" or "1 hour 30 minutes"
    combined_pattern = r'^(\d+)\s*(?:hour|hours|hr|hrs)\s*(?:and\s+)?(\d+)\s*(?:minute|minutes|min|mins)$'
    match = re.match(combined_pattern, time_spec)
    if match:
        hours = int(match.group(1))
        minutes = int(match.group(2))
        return hours * 60 + minutes
    
    # Pattern: "1h30m" or "1h 30m"
    compact_pattern = r'^(\d+)h\s*(\d+)m?$'
    match = re.match(compact_pattern, time_spec)
    if match:
        hours = int(match.group(1))
        minutes = int(match.group(2)) if match.group(2) else 0
        return hours * 60 + minutes
    
    # Pattern: single unit - "10 minutes", "2 hours", etc.
    # Try hours first
    hour_pattern = r'^(\d+)\s*(?:hour|hours|hr|hrs|h)$'
    match = re.match(hour_pattern, time_spec)
    if match:
        return int(match.group(1)) * 60
    
    # Try minutes
    minute_pattern = r'^(\d+)\s*(?:minute|minutes|min|mins|m)$'
    match = re.match(minute_pattern, time_spec)
    if match:
        return int(match.group(1))
    
    return None


def _get_error_feedback(message_text: str) -> dict:
    """Provide helpful error feedback when parsing fails."""
    has_remind = re.search(r'remind\s+me', message_text, re.IGNORECASE)
    has_add = re.search(r'add\s+task', message_text, re.IGNORECASE)
    
    if has_remind or has_add:
        # Check for empty task name
        if re.search(r'remind\s+me\s+(?:at|in)\s+', message_text, re.IGNORECASE) or \
           re.search(r'add\s+task\s+(?:at|in)\s+', message_text, re.IGNORECASE):
            return {
                'success': False,
                'error': 'Task name cannot be empty'
            }
        
        # Check for missing time indicator
        if ' at ' not in message_text.lower() and ' in ' not in message_text.lower():
            return {
                'success': False,
                'error': 'Please specify time using "at HH:MM" or "in X minutes/hours"'
            }
        
        # Check for invalid time format after "at"
        if ' at ' in message_text.lower():
            time_match = re.search(r'at\s+(\S+)$', message_text.lower())
            if time_match:
                time_part = time_match.group(1)
                if ':' not in time_part:
                    return {
                        'success': False,
                        'error': f'Invalid time format "{time_part}". Use 24-hour format (HH:MM, e.g., 13:00, 08:30) or relative time (e.g., "in 10 minutes")'
                    }
        
        return {
            'success': False,
            'error': 'Invalid format. Use: "Remind me [task] at HH:MM" or "Remind me [task] in X minutes/hours"'
        }
    else:
        return {
            'success': False,
            'error': 'Unrecognized command. Try: "Remind me [task] at HH:MM" or "Remind me [task] in 10 minutes"'
        }
