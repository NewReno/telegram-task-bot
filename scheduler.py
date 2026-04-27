import asyncio
import logging
from datetime import datetime, timedelta
from typing import Callable, Optional

from storage import get_pending_tasks, mark_task_reminded

logger = logging.getLogger(__name__)


class TaskScheduler:
    """
    Background scheduler that checks for due tasks and sends reminders.
    """
    
    def __init__(self, reminder_callback: Callable[[int, str, str], None]):
        """
        Initialize the scheduler.
        
        Args:
            reminder_callback: Function to call when a task is due.
                              Signature: (user_id: int, task_name: str, time_str: str) -> None
        """
        self.reminder_callback = reminder_callback
        self.running = False
        self._task: Optional[asyncio.Task] = None
        self._reminded_tasks: set = set()  # Track (task_id, date) tuples to avoid duplicates
    
    async def start(self):
        """Start the scheduler loop."""
        if self.running:
            logger.warning("Scheduler is already running")
            return
        
        self.running = True
        self._task = asyncio.create_task(self._scheduler_loop())
        logger.info("Task scheduler started")
    
    async def stop(self):
        """Stop the scheduler loop."""
        if not self.running:
            return
        
        self.running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Task scheduler stopped")
    
    async def _scheduler_loop(self):
        """Main scheduler loop - checks for due tasks every minute."""
        while self.running:
            try:
                await self._check_due_tasks()
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
            
            # Wait 1 minute before next check
            await asyncio.sleep(60)
    
    async def _check_due_tasks(self):
        """Check for tasks that are due and send reminders."""
        now = datetime.now()
        current_date = now.strftime('%Y-%m-%d')
        current_time = now.strftime('%H:%M')
        
        # Get pending tasks for today
        pending_tasks = get_pending_tasks(current_date)
        
        for task in pending_tasks:
            # Skip if already reminded
            task_key = (task['id'], current_date)
            if task_key in self._reminded_tasks or task.get('reminded'):
                continue
            
            # Parse task time
            try:
                task_time = task['time']
                task_hour, task_minute = map(int, task_time.split(':'))
                task_datetime = now.replace(hour=task_hour, minute=task_minute, second=0, microsecond=0)
                
                # Check if task is due (within the last minute)
                time_diff = (now - task_datetime).total_seconds()
                if 0 <= time_diff <= 60:
                    # Task is due! Send reminder
                    await self._send_reminder(task, current_date)
                    
            except (ValueError, KeyError) as e:
                logger.error(f"Error parsing task time for task {task['id']}: {e}")
    
    async def _send_reminder(self, task: dict, date_str: str):
        """Send a reminder for a specific task."""
        task_id = task['id']
        task_name = task['task_name']
        task_time = task['time']
        
        # Mark as reminded in storage
        if mark_task_reminded(task_id, date_str):
            # Track in memory to avoid duplicates
            task_key = (task_id, date_str)
            self._reminded_tasks.add(task_key)
            
            logger.info(f"Sending reminder for task: {task_name} at {task_time}")
            
            # Call the reminder callback (this will send the actual message)
            # We need user_id - for now we'll need to pass it through
            # This is a limitation of the current architecture
            pass
    
    def register_user_chat(self, user_id: int, chat_id: int):
        """
        Register a user-chat mapping so we know where to send reminders.
        This should be called when a user interacts with the bot.
        """
        # Store the mapping for reminder delivery
        if not hasattr(self, '_user_chat_map'):
            self._user_chat_map = {}
        self._user_chat_map[user_id] = chat_id
        logger.debug(f"Registered user {user_id} with chat {chat_id}")
    
    async def check_and_remind(self, user_id: int, chat_id: int):
        """
        Check for due tasks and send reminders to a specific user.
        This should be called periodically or when user interacts.
        """
        now = datetime.now()
        current_date = now.strftime('%Y-%m-%d')
        current_time = now.strftime('%H:%M')
        
        # Get pending tasks for today
        pending_tasks = get_pending_tasks(current_date)
        
        reminders_sent = 0
        for task in pending_tasks:
            # Skip if already reminded
            task_key = (task['id'], current_date)
            if task_key in self._reminded_tasks or task.get('reminded'):
                continue
            
            # Parse task time
            try:
                task_time = task['time']
                task_hour, task_minute = map(int, task_time.split(':'))
                task_datetime = now.replace(hour=task_hour, minute=task_minute, second=0, microsecond=0)
                
                # Check if task is due (time has passed)
                if now >= task_datetime:
                    # Task is due! Send reminder
                    await self._send_reminder_to_user(user_id, chat_id, task, current_date)
                    reminders_sent += 1
                    
            except (ValueError, KeyError) as e:
                logger.error(f"Error parsing task time for task {task['id']}: {e}")
        
        return reminders_sent
    
    async def _send_reminder_to_user(self, user_id: int, chat_id: int, task: dict, date_str: str):
        """Send a reminder to a specific user."""
        task_id = task['id']
        task_name = task['task_name']
        task_time = task['time']
        
        # Mark as reminded in storage
        if mark_task_reminded(task_id, date_str):
            # Track in memory to avoid duplicates
            task_key = (task_id, date_str)
            self._reminded_tasks.add(task_key)
            
            logger.info(f"Sending reminder to user {user_id} for task: {task_name} at {task_time}")
            
            # Call the reminder callback
            if self.reminder_callback:
                self.reminder_callback(user_id, chat_id, task_name, task_time)
