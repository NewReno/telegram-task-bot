import re
from datetime import datetime


def parse_task(message_text: str) -> dict:
    """
    Parse natural language task commands.
    
    Supports:
    - "Remind me [task] at HH:MM"
    - "add task [task] at HH:MM"
    
    Returns:
        dict: {
            'success': bool,
            'task_name': str (if success),
            'time': str (if success),
            'error': str (if not success)
        }
    """
    message_text = message_text.strip()
    
    # Pattern 1: "Remind me [task] at HH:MM"
    pattern1 = r'^remind\s+me\s+(.+?)\s+at\s+(\d{1,2}:\d{2})$'
    match = re.match(pattern1, message_text, re.IGNORECASE)
    
    if not match:
        # Pattern 2: "add task [task] at HH:MM"
        pattern2 = r'^add\s+task\s+(.+?)\s+at\s+(\d{1,2}:\d{2})$'
        match = re.match(pattern2, message_text, re.IGNORECASE)
    
    if not match:
        # Check if it's partially correct to give better error
        has_remind = re.search(r'remind\s+me', message_text, re.IGNORECASE)
        has_add = re.search(r'add\s+task', message_text, re.IGNORECASE)
        
        if has_remind or has_add:
            # Check for empty task name (e.g., "Remind me at 13:00")
            if re.search(r'remind\s+me\s+at\s+', message_text, re.IGNORECASE) or \
               re.search(r'add\s+task\s+at\s+', message_text, re.IGNORECASE):
                return {
                    'success': False,
                    'error': 'Task name cannot be empty'
                }
            
            # Check for missing time
            if ' at ' not in message_text.lower():
                return {
                    'success': False,
                    'error': 'Please specify a time using "at HH:MM" format'
                }
            
            # Check for invalid time format (no colon)
            time_match = re.search(r'at\s+(\S+)$', message_text.lower())
            if time_match:
                time_part = time_match.group(1)
                if ':' not in time_part:
                    return {
                        'success': False,
                        'error': f'Invalid time format "{time_part}". Use 24-hour format (HH:MM, e.g., 13:00, 08:30)'
                    }
            
            return {
                'success': False,
                'error': 'Invalid format. Use: "Remind me [task] at HH:MM" or "add task [task] at HH:MM"'
            }
        else:
            return {
                'success': False,
                'error': 'Unrecognized command. Try: "Remind me [task] at HH:MM"'
            }
    
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
