import json
import logging
import os
from datetime import datetime
from config import DATA_DIR

logger = logging.getLogger(__name__)


def _get_filename(date_str: str = None) -> str:
    """Get the JSON filename for a specific date."""
    if date_str is None:
        date_str = datetime.now().strftime('%Y-%m-%d')
    return os.path.join(DATA_DIR, f'tasks_{date_str}.json')


def _load_data(filename: str) -> dict:
    """Load data from JSON file or return empty structure."""
    if not os.path.exists(filename):
        return {'date': os.path.basename(filename).replace('tasks_', '').replace('.json', ''), 'tasks': []}
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Failed to load {filename}: {e}")
        return {'date': os.path.basename(filename).replace('tasks_', '').replace('.json', ''), 'tasks': []}


def _save_data(filename: str, data: dict) -> None:
    """Save data to JSON file."""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def save_task(task_name: str, time_str: str, date_str: str = None) -> dict:
    """
    Save a task to the daily JSON file.
    
    Args:
        task_name: Name/description of the task
        time_str: Time in HH:MM format
        date_str: Date in YYYY-MM-DD format (defaults to today)
    
    Returns:
        dict: The saved task with all fields
    """
    if date_str is None:
        date_str = datetime.now().strftime('%Y-%m-%d')
    
    filename = _get_filename(date_str)
    data = _load_data(filename)
    
    # Generate new task ID
    task_id = 1
    if data['tasks']:
        task_id = max(task['id'] for task in data['tasks']) + 1
    
    STATUS_PENDING = 'pending'
    STATUS_COMPLETED = 'completed'
    
    task = {
        'id': task_id,
        'task_name': task_name,
        'date': date_str,
        'time': time_str,
        'status': STATUS_PENDING,
        'created_at': datetime.now().isoformat(),
        'completed_at': None
    }
    
    data['tasks'].append(task)
    _save_data(filename, data)
    
    return task


def get_tasks(date_str: str = None) -> list:
    """
    Get all tasks for a specific date.
    
    Args:
        date_str: Date in YYYY-MM-DD format (defaults to today)
    
    Returns:
        list: List of task dictionaries
    """
    filename = _get_filename(date_str)
    data = _load_data(filename)
    return data['tasks']
