# Telegram Task Reminder Bot - Implementation Issues

## Issue 1: Basic Task Creation

**Type**: AFK  
**Blocked by**: None — can start immediately

### Parent PRD

`PRD.md`

### What to build

Implement the core task creation flow end-to-end. User sends "Remind me [task] at HH:MM" or "add task [task] at HH:MM", bot parses the message, validates 24-hour time format, stores the task in a daily JSON file, and sends confirmation. This slice includes the telegram bot handler, message parser, storage layer, and basic error handling for format validation.

### How to verify

**Manual:**
1. Send "Remind me Test at 14:30" to the bot
2. Verify bot responds with confirmation message
3. Check that JSON file `tasks_YYYY-MM-DD.json` is created with the task
4. Verify task has correct structure: id, task_name, time, status=pending, created_at timestamp

**Automated:**
- Test parser correctly extracts task_name and time from "Remind me X at HH:MM" and "add task X at HH:MM"
- Test storage creates JSON file with proper structure
- Test bot responds with confirmation message
- Test invalid time format returns error

### Acceptance criteria

- [ ] Given user sends "Remind me Vacuum at 13:00", when bot processes it, then task is stored and confirmation sent
- [ ] Given user sends "add task Wake up at 08:00", when bot processes it, then task is stored and confirmation sent
- [ ] Given invalid time format "at 25:00", when user sends message, then bot responds with error about 24-hour format
- [ ] Given valid command, when bot stores task, then JSON file has correct structure with all required fields

### User stories addressed

- User story 1: Add task with "Remind me" syntax
- User story 2: Add task with "add task" syntax
- User story 3: Only accept 24-hour time format
- User story 18: Confirmation when task created

---

## Issue 2: List Today's Tasks

**Type**: AFK  
**Blocked by**: Issue 1

### Parent PRD

`PRD.md`

### What to build

Implement the task listing feature. User can send "list" or "tasks" to see all tasks for today with their numbers, statuses, and times. The list should show pending and completed tasks separately, with visual indicators (emoji or symbols).

### How to verify

**Manual:**
1. Create 2-3 tasks using Issue 1
2. Send "list" command
3. Verify bot shows numbered list with task names, times, and status indicators
4. Mark one task as complete (manually edit JSON)
5. Send "list" again and verify completed task shows differently

**Automated:**
- Test listing returns all tasks for today's date
- Test tasks are displayed with numbers
- Test pending and completed tasks are distinguished
- Test empty list returns friendly message

### Acceptance criteria

- [ ] Given tasks exist for today, when user sends "list", then numbered task list is displayed
- [ ] Given tasks with different statuses, when listed, then pending and completed tasks are visually distinguished
- [ ] Given no tasks exist, when user sends "list", then friendly "no tasks" message is shown
- [ ] Given user sends "tasks", when processed, then same output as "list" command

### User stories addressed

- User story 5: List all tasks for today

---

## Issue 3: Complete Task

**Type**: AFK  
**Blocked by**: Issue 2

### Parent PRD

`PRD.md`

### What to build

Implement task completion. User sends "done [number]" or "complete [number]" to mark a task as completed. The task status changes to "completed", completed_at timestamp is set, and bot confirms the action. Completed tasks remain in the JSON file for history.

### How to verify

**Manual:**
1. Create a task
2. Send "list" to see its number
3. Send "done 1"
4. Verify bot confirms completion
5. Check JSON file shows status=completed and has completed_at timestamp
6. Send "list" and verify task shows as completed

**Automated:**
- Test marking task as completed updates status and adds completed_at
- Test invalid task number returns error
- Test completing already completed task returns appropriate message

### Acceptance criteria

- [ ] Given task #1 exists, when user sends "done 1", then task is marked completed with timestamp
- [ ] Given task is completed, when listing tasks, then it appears with completed status
- [ ] Given invalid task number, when user tries to complete, then error message is shown
- [ ] Given task is completed, when viewing JSON, then completed_at field is populated

### User stories addressed

- User story 7: Mark task as completed
- User story 13: Completed tasks kept in JSON

---

## Issue 4: Delete Task

**Type**: AFK  
**Blocked by**: Issue 2

### Parent PRD

`PRD.md`

### What to build

Implement task deletion. User sends "delete [number]" or "remove [number]" to permanently remove a task from the day's JSON file. Bot asks for confirmation or directly deletes and confirms.

### How to verify

**Manual:**
1. Create 2 tasks
2. Send "list" to see their numbers
3. Send "delete 2"
4. Verify bot confirms deletion
5. Send "list" and verify only task #1 remains
6. Check JSON file has only one task

**Automated:**
- Test deleting task removes it from JSON
- Test invalid task number returns error
- Test renumbering of remaining tasks if applicable

### Acceptance criteria

- [ ] Given task #2 exists, when user sends "delete 2", then task is removed from JSON
- [ ] Given task is deleted, when listing tasks, then it no longer appears
- [ ] Given invalid task number, when user tries to delete, then error message is shown
- [ ] Given deletion succeeds, when bot responds, then confirmation message is sent

### User stories addressed

- User story 8: Delete task

---

## Issue 5: Edit Task

**Type**: AFK  
**Blocked by**: Issue 2

### Parent PRD

`PRD.md`

### What to build

Implement task editing. User can edit task time with "edit [number] time HH:MM" or task name with "edit [number] name [new_name]". Bot validates changes and confirms updates. Past time validation applies to time edits.

### How to verify

**Manual:**
1. Create a task "Meeting at 14:00"
2. Send "edit 1 time 15:30"
3. Verify bot confirms and list shows new time
4. Send "edit 1 name Team Meeting"
5. Verify bot confirms and list shows new name
6. Try "edit 1 time 08:00" when current time is 12:00 and verify rejection

**Automated:**
- Test editing time updates task time
- Test editing name updates task name
- Test past time validation on time edits
- Test invalid task number returns error
- Test invalid edit format returns error

### Acceptance criteria

- [ ] Given task exists, when user sends "edit 1 time 16:00", then task time is updated
- [ ] Given task exists, when user sends "edit 1 name New Name", then task name is updated
- [ ] Given time edit is in the past, when user tries to edit, then error message is shown
- [ ] Given edit succeeds, when bot responds, then confirmation with updated details is shown

### User stories addressed

- User story 9: Edit task time
- User story 10: Edit task name

---

## Issue 6: Background Reminders

**Type**: AFK  
**Blocked by**: Issue 1

### Parent PRD

`PRD.md`

### What to build

Implement background scheduler that checks every minute for tasks due now and sends reminder messages. Uses threading or asyncio to run alongside the bot. Reminders are sent at exact scheduled time without queuing missed ones.

### How to verify

**Manual:**
1. Create a task 2 minutes in the future
2. Wait for the time
3. Verify bot sends "🔔 Reminder: [task_name] at [time]"
4. Create another task when bot is offline
5. Start bot after task time passes
6. Verify NO reminder is sent for missed task

**Automated:**
- Test scheduler identifies tasks due now
- Test reminder message is sent at exact time
- Test only pending tasks trigger reminders
- Test no queuing of missed reminders

### Acceptance criteria

- [ ] Given task scheduled for 14:00, when time reaches 14:00, then reminder message is sent
- [ ] Given reminder is sent, when user receives it, then format includes task name and time
- [ ] Given task time passed while bot was offline, when bot restarts, then no reminder is sent
- [ ] Given task is completed, when time reaches, then no reminder is sent

### User stories addressed

- User story 11: Receive reminder at exact time
- User story 12: No queuing of missed reminders

---

## Issue 7: Past Time Validation

**Type**: AFK  
**Blocked by**: Issue 1

### Parent PRD

`PRD.md`

### What to build

Add validation to reject tasks scheduled in the past. When user tries to create a task with time before current time, bot responds with clear error message explaining the task time has already passed.

### How to verify

**Manual:**
1. Check current time (e.g., 14:30)
2. Send "Remind me Test at 13:00"
3. Verify bot rejects with error about past time
4. Send "Remind me Test at 15:00"
5. Verify task is created successfully

**Automated:**
- Test past time is rejected with appropriate error
- Test current time is handled correctly (edge case)
- Test future time is accepted
- Test error message is clear and helpful

### Acceptance criteria

- [ ] Given current time is 14:00, when user sends "Remind me Task at 13:00", then error about past time is shown
- [ ] Given current time is 14:00, when user sends "Remind me Task at 15:00", then task is created
- [ ] Given rejection occurs, when error message is shown, then it clearly explains time has passed

### User stories addressed

- User story 4: Reject tasks scheduled in the past
- User story 17: Clear error for past time scheduling

---

## Issue 8: List by Date and Statistics

**Type**: AFK  
**Blocked by**: Issue 2

### Parent PRD

`PRD.md`

### What to build

Extend listing to support specific dates and show statistics. User can send "list YYYY-MM-DD" to view tasks from any date. Today's list includes completion statistics like "3/5 tasks completed today". User can view task history from previous days.

### How to verify

**Manual:**
1. Create some tasks and complete some
2. Send "list" and verify statistics shown (e.g., "📊 2/3 tasks completed")
3. Manually create a JSON file for yesterday's date with some tasks
4. Send "list 2026-04-26" (yesterday's date)
5. Verify yesterday's tasks are displayed
6. Send "list 2026-04-20" (date with no tasks)
7. Verify "no tasks" message shown

**Automated:**
- Test listing by specific date returns correct tasks
- Test statistics calculation (completed/total)
- Test historical dates load correct files
- Test non-existent date returns friendly message

### Acceptance criteria

- [ ] Given tasks exist, when user sends "list", then completion statistics are shown
- [ ] Given tasks for 2026-04-26 exist, when user sends "list 2026-04-26", then those tasks are displayed
- [ ] Given no tasks for a date, when user lists that date, then "no tasks" message is shown
- [ ] Given statistics are shown, when calculated, then format is "X/Y tasks completed"

### User stories addressed

- User story 6: List tasks for specific date
- User story 14: Task completion statistics
- User story 15: View previous days' tasks

---

## Issue 9: Comprehensive Error Handling

**Type**: AFK  
**Blocked by**: Issue 1

### Parent PRD

`PRD.md`

### What to build

Implement comprehensive error handling and user-friendly error messages. Cover invalid commands, malformed messages, file I/O errors, and edge cases. Ensure bot never crashes and always provides helpful feedback.

### How to verify

**Manual:**
1. Send invalid command "hello bot"
2. Verify bot responds with help message
3. Send malformed task "Remind me at 13:00" (missing task name)
4. Verify error about missing task name
5. Send invalid time "Remind me Task at 25:00"
6. Verify error about invalid time format
7. Test with corrupted JSON file (manually edit)
8. Verify bot handles gracefully with error message

**Automated:**
- Test unknown commands return help
- Test malformed natural language returns specific error
- Test file I/O errors are caught and reported
- Test bot continues operating after errors

### Acceptance criteria

- [ ] Given unknown command, when sent to bot, then help message is shown
- [ ] Given malformed task message, when sent, then specific error about what's wrong is shown
- [ ] Given invalid time like "25:00", when sent, then error explains 24-hour format
- [ ] Given file error occurs, when operation fails, then user-friendly error is shown and bot continues

### User stories addressed

- User story 16: Clear error for invalid time format
- User story 17: Clear error for past time (also covered in Issue 7)

---
