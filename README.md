# Telegram Task Reminder Bot 🤖

A smart Python Telegram bot for managing daily tasks with automatic reminders.

## Features ✨

- **🤖 Automatic Reminders**: Get notified when tasks are due
  - Background scheduler checks every minute
  - Sends "🔔 Reminder!" message at task time
  - No more forgetting your tasks!

- **⏱️ Flexible Time Input**: Add tasks with absolute or relative time
  - **Absolute**: `Remind me Vacuum at 13:00`
  - **Relative**: `Remind me Call friend in 10 minutes`
  - **Combined**: `Remind me Meeting in 1 hour and 30 minutes`

- **📱 Smart Button Interface**:
  - 📋 Show Tasks - View all tasks with completion stats
  - ➕ Add Task - Get help on adding new tasks
  - ✅ Complete Task - Mark tasks as done with inline buttons
  - 🔔 Reminders - Manually check for due tasks
  - ❓ Help - Show all available commands

- **📊 Task Statistics**: Track your productivity
  - See completed vs pending tasks
  - Daily progress tracking

- **⏰ 24-Hour Time Format**: Clear and simple time entry

- **💾 Daily Task Storage**: Tasks saved in daily JSON files
  - Easy backup and access
  - No database setup required

## Setup 🚀

### Prerequisites
- Python 3.8+
- Telegram Bot Token (get from [@BotFather](https://t.me/BotFather))

### Installation

1. **Clone the repository**:
```bash
git clone https://github.com/NewReno/telegram-task-bot.git
cd telegram-task-bot
```

2. **Create virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Configure environment**:
```bash
cp .env.example .env
# Edit .env and add your bot token:
# BOT_TOKEN=your_bot_token_here
```

5. **Run the bot**:
```bash
python main.py
```

### Docker Setup 🐳

You can also run the bot using Docker:

1. **Configure environment**:
```bash
cp .env.example .env
# Edit .env and add your bot token
```

2. **Build and run with Docker Compose**:
```bash
docker-compose up -d
```

3. **View logs**:
```bash
docker-compose logs -f
```

4. **Stop the bot**:
```bash
docker-compose down
```

**Note**: The `data/` directory is mounted as a volume, so your tasks persist between container restarts.

## Usage 📱

### Adding Tasks

**With Absolute Time (specific time):**
- `Remind me Task Name at 14:30`
- `add task Another Task at 09:00`

**With Relative Time (from now):**
- `Remind me Call a friend in 10 minutes`
- `Remind me Meeting in 2 hours`
- `Remind me Lunch in 1 hour and 30 minutes`

**Supported Relative Formats:**
- `in X minutes` / `in X mins` / `in Xm`
- `in X hours` / `in X hrs` / `in Xh`
- `in X hours and Y minutes`
- `in XhYm` (compact format)

The bot will confirm and automatically remind you when it's time!

### Automatic Reminders
Once you add a task, the bot will:
1. Send a confirmation: "✅ Task scheduled... I'll remind you when it's time!"
2. Monitor the task time in the background
3. Send a reminder notification when the task is due

### Managing Tasks

**View Tasks:**
- Click **📋 Show Tasks** button
- Or type `/list`

**Complete Tasks:**
- Click **✅ Complete Task** button
- Select from pending tasks
- Or type `/done`

**Manual Reminder Check:**
- Click **🔔 Reminders** button
- Or type `/reminders`

### Bot Commands
- `/start` - Start the bot and show welcome message
- `/help` - Show available commands
- `/list` - List today's tasks
- `/done` - Mark tasks as complete
- `/reminders` - Check for due reminders

## Project Structure 📁

```
telegram-task-bot/
├── bot.py              # Telegram bot handlers and UI
├── scheduler.py        # ⭐ Background reminder scheduler
├── parser.py           # Natural language command parser
├── storage.py          # JSON file storage operations
├── config.py           # Configuration and constants
├── main.py             # Entry point
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variables template
├── .gitignore          # Git ignore rules
└── test_*.py          # Unit and integration tests
```

## Data Storage 💾

Tasks are stored in JSON files in the `data/` directory:
- File format: `tasks_YYYY-MM-DD.json`
- Each task includes:
  ```json
  {
    "id": 1,
    "task_name": "Vacuum",
    "date": "2026-04-27",
    "time": "13:00",
    "status": "pending",
    "created_at": "2026-04-27T09:00:00",
    "reminded": false,
    "reminded_at": null
  }
  ```

## Testing 🧪

Run tests with pytest:
```bash
pytest test_parser.py test_storage.py test_integration.py -v
```

All 33+ tests passing ✅

## Technologies Used 🛠️

- [python-telegram-bot](https://python-telegram-bot.org/) - Telegram Bot API wrapper
- Python 3.8+
- JSON for data storage
- Asyncio for background scheduling

## How Reminders Work 🔔

1. **Task Creation**: When you add a task, it's saved with time and reminder status
2. **Background Scheduler**: Runs every minute checking for due tasks
3. **Reminder Detection**: When current time matches task time (within 1-minute window)
4. **Notification**: Sends "🔔 Reminder! It's time for: [Task Name]" message
5. **Completion**: Use "✅ Complete Task" button to mark as done

## License 📄

This project is open source and available under the MIT License.

## Author ✍️

Created by [NewReno](https://github.com/NewReno)

---

**Note**: This bot is designed for single-user personal use. The `.env` file containing your bot token is excluded from git via `.gitignore` for security.
