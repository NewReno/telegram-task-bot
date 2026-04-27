import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

from config import get_config
from parser import parse_task
from storage import save_task, get_tasks, complete_task, get_pending_tasks
from scheduler import TaskScheduler

logger = logging.getLogger(__name__)

# Main menu keyboard
MAIN_MENU = ReplyKeyboardMarkup([
    ['📋 Show Tasks', '➕ Add Task'],
    ['✅ Complete Task', '🔔 Reminders'],
    ['❓ Help']
], resize_keyboard=True)

# Global scheduler instance
scheduler = None


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    await update.message.reply_text(
        "👋 Hello! I'm your task reminder bot.\n\n"
        "Use the buttons below or type:\n"
        "• Remind me Vacuum at 13:00\n"
        "• Remind me Call friend in 10 minutes\n"
        "• add task Wake up at 08:00",
        reply_markup=MAIN_MENU
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command."""
    await update.message.reply_text(
        "🤖 Available commands:\n\n"
        "Add tasks (absolute time):\n"
        "• Remind me [task] at HH:MM\n"
        "• add task [task] at HH:MM\n\n"
        "Add tasks (relative time):\n"
        "• Remind me [task] in X minutes\n"
        "• Remind me [task] in X hours\n"
        "• Remind me [task] in 1 hour and 30 minutes\n\n"
        "Buttons:\n"
        "• 📋 Show Tasks - View your tasks\n"
        "• ✅ Complete Task - Mark tasks done\n"
        "• 🔔 Reminders - Check for due tasks\n\n"
        "Automatic reminders will be sent when tasks are due!",
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
        "📍 Absolute time:\n"
        "• Remind me [task name] at HH:MM\n"
        "• add task [task name] at HH:MM\n\n"
        "⏱ Relative time:\n"
        "• Remind me [task name] in X minutes\n"
        "• Remind me [task name] in X hours\n\n"
        "Examples:\n"
        "• Remind me Vacuum at 13:00\n"
        "• Remind me Call friend in 10 minutes\n"
        "• Remind me Meeting in 2 hours",
        reply_markup=MAIN_MENU
    )


async def complete_task_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle complete task button or command."""
    tasks = get_pending_tasks()
    
    if not tasks:
        await update.message.reply_text(
            "✅ No pending tasks to complete!",
            reply_markup=MAIN_MENU
        )
        return
    
    # Show tasks with inline keyboard to select which to complete
    keyboard = []
    for task in tasks:
        callback_data = f"complete_{task['id']}"
        keyboard.append([InlineKeyboardButton(
            f"⏳ {task['task_name']} - {task['time']}",
            callback_data=callback_data
        )])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "✅ Select a task to mark as complete:",
        reply_markup=reply_markup
    )


async def check_reminders_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check for due reminders manually."""
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    
    # Register user for reminders
    if scheduler:
        scheduler.register_user_chat(user_id, chat_id)
        reminders_sent = await scheduler.check_and_remind(user_id, chat_id)
        
        if reminders_sent == 0:
            await update.message.reply_text(
                "🔔 No tasks are due right now.\n\n"
                "I'll automatically remind you when tasks are due!",
                reply_markup=MAIN_MENU
            )
    else:
        await update.message.reply_text(
            "⚠️ Reminder system is not active.",
            reply_markup=MAIN_MENU
        )


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline button callbacks."""
    query = update.callback_query
    await query.answer()
    
    callback_data = query.data
    
    if callback_data.startswith('complete_'):
        # Extract task ID
        try:
            task_id = int(callback_data.split('_')[1])
            if complete_task(task_id):
                await query.edit_message_text(
                    f"✅ Task marked as complete!\n\n"
                    f"Great job! Keep it up! 🎉"
                )
            else:
                await query.edit_message_text(
                    "❌ Could not complete task. It may have been deleted."
                )
        except (ValueError, IndexError):
            await query.edit_message_text("❌ Invalid task selection.")


async def send_reminder(user_id: int, chat_id: int, task_name: str, task_time: str):
    """Send a reminder message to a user."""
    try:
        # We need to get the application instance to send messages
        # This is a bit tricky - we'll need to store the application reference
        if hasattr(send_reminder, 'application'):
            await send_reminder.application.bot.send_message(
                chat_id=chat_id,
                text=f"🔔 **Reminder!**\n\n"
                     f"⏰ It's time for: **{task_name}**\n"
                     f"📅 Scheduled at: {task_time}\n\n"
                     f"Click ✅ Complete Task when you're done!",
                parse_mode='Markdown'
            )
            logger.info(f"Reminder sent to user {user_id} for task: {task_name}")
    except Exception as e:
        logger.error(f"Failed to send reminder: {e}")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming messages."""
    message_text = update.message.text
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    
    # Register user for reminders
    if scheduler:
        scheduler.register_user_chat(user_id, chat_id)
    
    # Handle button clicks
    if message_text == '📋 Show Tasks':
        await show_tasks_command(update, context)
        return
    elif message_text == '➕ Add Task':
        await add_task_prompt(update, context)
        return
    elif message_text == '✅ Complete Task':
        await complete_task_command(update, context)
        return
    elif message_text == '🔔 Reminders':
        await check_reminders_command(update, context)
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
            f"✅ Task \"{task['task_name']}\" scheduled for {task['time']} today\n\n"
            f"🔔 I'll remind you when it's time!",
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
    
    # Store application reference for reminders
    send_reminder.application = application
    
    # Add handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("list", show_tasks_command))
    application.add_handler(CommandHandler("done", complete_task_command))
    application.add_handler(CommandHandler("reminders", check_reminders_command))
    application.add_handler(CallbackQueryHandler(handle_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Initialize and start the scheduler
    global scheduler
    scheduler = TaskScheduler(send_reminder)
    
    async def on_startup(app):
        """Start the scheduler when bot starts."""
        await scheduler.start()
        logger.info("Bot started with reminder scheduler")
    
    async def on_shutdown(app):
        """Stop the scheduler when bot stops."""
        await scheduler.stop()
        logger.info("Bot stopped, scheduler shut down")
    
    application.post_init = on_startup
    application.post_shutdown = on_shutdown
    
    return application
