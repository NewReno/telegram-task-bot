# Telegram Task Reminder Bot 🤖

A simple Python Telegram bot for managing daily tasks with reminders.

## Features ✨

- **Natural Language Commands**: Add tasks using conversational syntax
  - `Remind me Vacuum at 13:00`
  - `add task Wake up at 08:00`
- **Button Interface**: Easy-to-use buttons for:
  - 📋 Show Tasks - View all tasks for today
  - ➕ Add Task - Get help on adding tasks
  - ❓ Help - Show available commands
- **Daily Task Management**: Tasks stored in daily JSON files
- **Task Statistics**: See completion progress (e.g., "2/5 tasks completed")
- **24-Hour Time Format**: Clear time specification (HH:MM)

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

## Usage 📱

### Adding Tasks
Send messages like:
- `Remind me Task Name at 14:30`
- `add task Another Task at 09:00`

### Viewing Tasks
- Click **📋 Show Tasks** button
- Or type `/list`

### Bot Commands
- `/start` - Start the bot and show welcome message
- `/help` - Show available commands
- `/list` - List today's tasks

## Project Structure 📁

```
telegram-task-bot/
├── bot.py              # Telegram bot handlers and UI
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
- Each task includes: id, task_name, date, time, status, created_at

Example:
```json
{
  "date": "2026-04-27",
  "tasks": [
    {
      "id": 1,
      "task_name": "Vacuum",
      "time": "13:00",
      "status": "pending",
      "created_at": "2026-04-27T09:00:00"
    }
  ]
}
```

## Testing 🧪

Run tests with pytest:
```bash
pytest test_parser.py test_storage.py test_integration.py -v
```

All 22 tests passing ✅

## Technologies Used 🛠️

- [python-telegram-bot](https://python-telegram-bot.org/) - Telegram Bot API wrapper
- Python 3.8+
- JSON for data storage

## License 📄

This project is open source and available under the MIT License.

## Author ✍️

Created by [NewReno](https://github.com/NewReno)

---

**Note**: This bot is designed for single-user personal use. The `.env` file containing your bot token is excluded from git via `.gitignore` for security.
