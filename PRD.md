# PRD: Telegram Task Reminder Bot

## Problem Statement

I need a simple way to manage my daily tasks through Telegram. Currently, I have to remember everything myself or use separate apps. I want a lightweight solution where I can quickly add tasks with specific times using natural language, and get reminded exactly when I need to do them. I also want to track my task completion history to see what I've accomplished each day.

## Solution

A Python-based Telegram bot that:
- Accepts natural language task commands ("Remind me Vacuum at 13:00" or "add task Wake up at 8:00")
- Stores tasks in daily JSON files with task name, date, time, and status
- Sends notification messages at the exact scheduled time
- Provides full task management: add, list, complete, delete, and view history
- Maintains a history of completed tasks for daily review

## User Stories

### Core Task Creation

1. As a user, I want to add a task by sending "Remind me [task] at [HH:MM]", so that I can quickly schedule reminders using natural language.

2. As a user, I want to add a task by sending "add task [task] at [HH:MM]", so that I have flexibility in command syntax.

3. As a user, I want the bot to only accept 24-hour time format, so that there is no ambiguity between AM and PM.

4. As a user, I want to reject tasks scheduled in the past, so that I don't accidentally create invalid reminders.

### Task Management

5. As a user, I want to list all tasks for today, so that I can see what's pending and completed.

6. As a user, I want to list all tasks for a specific date, so that I can review past or future days.

7. As a user, I want to mark a task as completed, so that I can track my progress.

8. As a user, I want to delete a task, so that I can remove tasks I no longer need.

9. As a user, I want to edit an existing task's time, so that I can reschedule without deleting and recreating.

10. As a user, I want to edit an existing task's name, so that I can correct typos or change details.

### Reminders

11. As a user, I want to receive a message at the exact scheduled time, so that I'm reminded when I need to act.

12. As a user, I want to receive only the reminder at the scheduled time (no queuing of missed reminders), so that I don't get overwhelmed with old notifications.

### History and Tracking

13. As a user, I want completed tasks to be kept in the JSON file, so that I can review what I accomplished each day.

14. As a user, I want to see statistics about my task completion (e.g., "5/8 tasks completed today"), so that I can track my productivity.

15. As a user, I want to view all tasks from previous days, so that I can review my task history.

### Error Handling

16. As a user, I want clear error messages when I use invalid time format, so that I know how to correct my command.

17. As a user, I want clear error messages when I try to schedule a task in the past, so that I understand why it was rejected.

18. As a user, I want confirmation when a task is successfully created, so that I know the bot understood my request.

## Implementation Decisions

### Architecture

- **Single-user bot**: No authentication needed, designed for personal use
- **Local system timezone**: Uses the server's local timezone for all time calculations
- **Polling-based bot**: Uses python-telegram-bot library with long polling for simplicity
- **JSON file storage**: One JSON file per day, stored in a data directory

### Data Structure

Each task stored as:
```json
{
  "task_name": "string",
  "date": "YYYY-MM-DD",
  "time": "HH:MM",
  "status": "pending" | "completed",
  "created_at": "ISO timestamp",
  "completed_at": "ISO timestamp or null"
}
```

Files named: `tasks_YYYY-MM-DD.json`

### Command Interface

**Add task:**
- "Remind me [task] at HH:MM" or "add task [task] at HH:MM"
- Validates: time is in 24h format, time is not in the past

**List tasks:**
- "list" or "tasks" - shows today's tasks
- "list YYYY-MM-DD" - shows tasks for specific date

**Complete task:**
- "done [task_number]" or "complete [task_number]" - marks task as completed

**Delete task:**
- "delete [task_number]" or "remove [task_number]"

**Edit task:**
- "edit [task_number] time HH:MM" - changes task time
- "edit [task_number] name [new_name]" - changes task name

**Help:**
- "help" - shows available commands

### Reminder System

- Background scheduler checks every minute for tasks due
- Sends reminder message at exact scheduled time
- No queuing - if user is offline, the moment passes
- Reminder format: "🔔 Reminder: [task_name] at [time]"

### Validation Rules

- Time format: Strictly HH:MM (24-hour)
- Past time rejection: Any time before current time is rejected
- No recurring tasks: Each task is a one-time event

## Module Design

### Module: Telegram Bot Handler

- **Name**: `bot.py`
- **Responsibility**: Handle Telegram API interactions, parse user messages, route commands
- **Interface**: 
  - Input: Telegram updates/messages
  - Output: Response messages, task operations
  - Failure modes: Network errors, invalid commands
- **Tested**: Yes

### Module: Task Parser

- **Name**: `parser.py`
- **Responsibility**: Parse natural language task commands into structured data
- **Interface**:
  - Input: Raw message text (e.g., "Remind me Vacuum at 13:00")
  - Output: Parsed dict with task_name, time, or error message
  - Failure modes: Unparseable message, invalid time format
- **Tested**: Yes

### Module: Task Storage

- **Name**: `storage.py`
- **Responsibility**: CRUD operations on daily JSON files
- **Interface**:
  - Input: Task data, date, operation type
  - Output: Task object, list of tasks, success/failure
  - Failure modes: File I/O errors, invalid dates
- **Tested**: Yes

### Module: Reminder Scheduler

- **Name**: `scheduler.py`
- **Responsibility**: Background checking and triggering of due reminders
- **Interface**:
  - Input: Current time
  - Output: List of due tasks to notify
  - Failure modes: None (returns empty list if no tasks due)
- **Tested**: Yes

### Module: Task Manager

- **Name**: `task_manager.py`
- **Responsibility**: Business logic for task operations (create, complete, edit, delete)
- **Interface**:
  - Input: Command type, parameters
  - Output: Operation result, success message, error message
  - Failure modes: Task not found, invalid operation
- **Tested**: Yes

## Testing Decisions

### Unit Tests

- Test task parser with various natural language inputs
- Test time validation (past time rejection, format validation)
- Test storage operations (CRUD on JSON files)
- Test scheduler logic (identifying due tasks)

### Integration Tests

- End-to-end flow: message received → parsed → stored → reminder triggered
- Error handling: invalid commands, file errors

### Test Data

- Use temporary JSON files for testing (cleaned up after tests)
- Mock Telegram API for bot handler tests

## Out of Scope

- Multi-user support or authentication
- Recurring tasks (daily/weekly reminders)
- AM/PM time format support
- Push notifications (mobile app integration)
- Cloud synchronization
- Task categories or priorities
- Reminder snoozing
- Task attachments or notes
- Web dashboard
- Database migration (staying with JSON files)
- Internationalization (English only)
- Configurable timezone (using system local time only)

## Open Questions

None - all requirements clarified.

## Further Notes

### JSON File Location

Tasks stored in `/home/tony/Projects/telegram-bot/data/tasks_YYYY-MM-DD.json`

### Dependencies

- `python-telegram-bot` - Telegram Bot API wrapper
- Standard library only for other functionality (json, datetime, threading)

### Bot Setup

1. Create bot via @BotFather on Telegram
2. Store bot token in environment variable or config file
3. Run bot with Python 3.8+

### Sample JSON Structure

```json
{
  "date": "2026-04-27",
  "tasks": [
    {
      "id": 1,
      "task_name": "Vacuum",
      "time": "13:00",
      "status": "pending",
      "created_at": "2026-04-27T09:00:00",
      "completed_at": null
    },
    {
      "id": 2,
      "task_name": "Wake up",
      "time": "08:00",
      "status": "completed",
      "created_at": "2026-04-27T07:30:00",
      "completed_at": "2026-04-27T08:05:00"
    }
  ]
}
```

### Command Examples

**Adding tasks:**
```
User: Remind me Vacuum at 13:00
Bot: ✅ Task "Vacuum" scheduled for 13:00 today

User: add task Wake up at 08:00
Bot: ✅ Task "Wake up" scheduled for 08:00 today
```

**Listing tasks:**
```
User: list
Bot: 📋 Tasks for 2026-04-27:
1. ⏳ Wake up - 08:00
2. ⏳ Vacuum - 13:00

User: list 2026-04-26
Bot: 📋 Tasks for 2026-04-26:
1. ✅ Read book - 20:00 (completed)
2. ❌ Call mom - 18:00 (missed)
```

**Managing tasks:**
```
User: done 1
Bot: ✅ Task "Wake up" marked as completed

User: delete 2
Bot: 🗑️ Task "Vacuum" deleted

User: edit 1 time 14:00
Bot: ✏️ Task "Vacuum" rescheduled to 14:00
```

**Reminders:**
```
Bot: 🔔 Reminder: Vacuum at 13:00
```
