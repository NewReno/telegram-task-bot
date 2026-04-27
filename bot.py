import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

from config import get_config
from parser import parse_task
from storage import save_task, get_tasks

logger = logging.getLogger(__name__)

# Main menu keyboard
MAIN_MENU = ReplyKeyboardMarkup([
    ['📋 Show Tasks', '➕ Add Task'],
    ['❓ Help']
], resize_keyboard=True)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    await update.message.reply_text(
        "👋 Hello! I'm your task reminder bot.\n\n"
        "Use the buttons below or type:\n"
        "• Remind me Vacuum at 13:00\n"
        "• add task Wake up at 08:00",
        reply_markup=MAIN_MENU
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command."""
    await update.message.reply_text(
        "🤖 Available commands:\n\n"
        "Add tasks:\n"
        "• Remind me [task] at HH:MM\n"
        "• add task [task] at HH:MM\n\n"
        "Or use the 📋 Show Tasks button to see your tasks!",
        reply_markup=MAIN_MENU
    )


async def show_tasks_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle show tasks button or command."""
    tasks = get_tasks()
    
    if not tasks:
        await update.message.reply_text(
            "📋 You have no tasks for today!\n\n"
            "Click '➕ Add Task' or type: Remind me [task] at HH:MM",
            reply_markup=MAIN_MENU
        )
        return
    
    # Format task list
    task_list = []
    for i, task in enumerate(tasks, 1):
        status = "✅" if task['status'] == 'completed' else "⏳"
        task_list.append(f"{i}. {status} {task['task_name']} - {task['time']}")
    
    message = "📋 Today's Tasks:\n\n" + "\n".join(task_list)
    
    # Add stats
    completed = sum(1 for t in tasks if t['status'] == 'completed')
    total = len(tasks)
    message += f"\n\n📊 {completed}/{total} tasks completed"
    
    await update.message.reply_text(message, reply_markup=MAIN_MENU)


async def add_task_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle add task button."""
    await update.message.reply_text(
        "➕ To add a task, type:\n\n"
        "• Remind me [task name] at HH:MM\n"
        "• add task [task name] at HH:MM\n\n"
        "Example: Remind me Vacuum at 13:00",
        reply_markup=MAIN_MENU
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming messages."""
    message_text = update.message.text
    
    # Handle button clicks
    if message_text == '📋 Show Tasks':
        await show_tasks_command(update, context)
        return
    elif message_text == '➕ Add Task':
        await add_task_prompt(update, context)
        return
    elif message_text == '❓ Help':
        await help_command(update, context)
        return
    
    # Try to parse as a task command
    result = parse_task(message_text)
    
    if result['success']:
        # Save the task
        task = save_task(result['task_name'], result['time'])
        
        await update.message.reply_text(
            f"✅ Task \"{task['task_name']}\" scheduled for {task['time']} today",
            reply_markup=MAIN_MENU
        )
        logger.info(f"Task created: {task['task_name']} at {task['time']}")
    else:
        # Parse failed, send error
        await update.message.reply_text(f"❌ {result['error']}", reply_markup=MAIN_MENU)


def setup_bot() -> Application:
    """Create and configure the bot application."""
    config = get_config()
    application = Application.builder().token(config['token']).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("list", show_tasks_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    return application
