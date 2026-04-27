# Tasks for Issue 1: Basic Task Creation

Parent issue: Issue 1
Parent PRD: PRD.md

## Tasks

### 1. Project Setup and Dependencies

**Type**: CONFIG  
**Output**: `requirements.txt`, `config.py`, and `data/` directory exist  
**Depends on**: none

Create the initial project structure. Create `requirements.txt` with dependencies: python-telegram-bot (latest stable), python-dotenv for environment management. Create `config.py` to load BOT_TOKEN from environment variables with validation. Create `data/` directory for JSON storage. Add `.env.example` file showing required variables. Follow standard Python project layout conventions.

---

### 2. Create Task Parser Module

**Type**: WRITE  
**Output**: `parser.py` with parse_task() function that extracts task_name and time  
**Depends on**: Task 1

Implement the natural language parser in `parser.py`. Create `parse_task(message_text: str) -> dict` function that supports both "Remind me [task] at HH:MM" and "add task [task] at HH:MM" syntax patterns. Extract task name (everything between command and "at") and time (HH:MM format). Validate time is 24-hour format (00:00-23:59). Return dict with `task_name`, `time`, `success: True` or `error: str` if parsing fails. Handle edge cases: missing "at", missing time, malformed time. Do NOT handle past time validation here (that's Issue 7).

---

### 3. Create Task Storage Module

**Type**: WRITE  
**Output**: `storage.py` with save_task() and get_tasks() functions  
**Depends on**: Task 1

Implement JSON storage layer in `storage.py`. Create `save_task(task_data: dict) -> dict` that saves to daily JSON file named `tasks_YYYY-MM-DD.json` in the data directory. Task structure: `id` (auto-increment), `task_name`, `date` (YYYY-MM-DD), `time` (HH:MM), `status` ("pending"), `created_at` (ISO timestamp). Create `get_tasks(date: str = None) -> list` that loads tasks for a specific date or today if not specified. Handle file creation if doesn't exist, file reading with error handling. Return task dict with all fields on save success.

---

### 4. Create Telegram Bot Handler

**Type**: WRITE  
**Output**: `bot.py` with message handlers for add commands  
**Depends on**: Tasks 2, 3

Implement Telegram bot message handlers in `bot.py`. Create handlers for:
- "Remind me [task] at HH:MM" pattern
- "add task [task] at HH:MM" pattern

Flow: receive message → call parser → if success, call storage.save_task() → send confirmation message "✅ Task '[name]' scheduled for [time] today". If parser fails, send error message explaining what went wrong (invalid format, missing time, etc.). Use python-telegram-bot's Application builder pattern with CommandHandler and MessageHandler. Import parser and storage modules created in previous tasks.

---

### 5. Create Main Bot Runner

**Type**: WRITE  
**Output**: `main.py` that starts the bot  
**Depends on**: Task 4

Create entry point `main.py` that initializes and runs the bot. Load BOT_TOKEN from config. Import bot handlers from `bot.py`. Set up python-telegram-bot Application with token, add all handlers, start polling with drop_pending_updates=True. Add basic logging setup. Handle keyboard interrupt gracefully. This is the file you run to start the bot: `python main.py`

---

### 6. Write Parser Tests

**Type**: TEST  
**Output**: `test_parser.py` with passing tests  
**Depends on**: Task 2

Create comprehensive tests for the parser module in `test_parser.py`. Test cases:
- Valid "Remind me Vacuum at 13:00" → returns task_name="Vacuum", time="13:00"
- Valid "add task Wake up at 08:00" → returns task_name="Wake up", time="08:00"
- Invalid time "25:00" → returns error about invalid time
- Missing time "Remind me Task" → returns error about missing time
- Invalid format "hello bot" → returns error about unrecognized format
- Task names with "at" in them (edge case)

Use pytest. Test both success and failure cases. Mocking not needed.

---

### 7. Write Storage Tests

**Type**: TEST  
**Output**: `test_storage.py` with passing tests  
**Depends on**: Task 3

Create tests for storage module in `test_storage.py`. Use temporary directory for test files (pytest tmpdir fixture). Test cases:
- Save task creates new JSON file with correct name format
- Save task assigns sequential IDs
- Save task includes all required fields (id, task_name, date, time, status, created_at)
- Get tasks returns empty list for date with no tasks
- Get tasks returns correct tasks for existing date
- Multiple saves append to same file correctly

Clean up test files after tests. Verify JSON structure matches PRD spec.

---

### 8. Integration Test

**Type**: TEST  
**Output**: `test_integration.py` with end-to-end test  
**Depends on**: Tasks 4, 6, 7

Create end-to-end integration test in `test_integration.py` that simulates the full flow without actual Telegram API. Test: simulate user message "Remind me Test Task at 14:30" → parser extracts data → storage saves → verify JSON file created with correct structure. Mock the Telegram bot response or verify the handler logic returns expected response dict. Use temporary directory for data files. This tests that parser, storage, and bot logic work together correctly.

---
