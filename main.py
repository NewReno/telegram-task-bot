import logging
from telegram import Update
from bot import setup_bot

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def main():
    """Run the bot."""
    logger.info("Starting Telegram Task Reminder Bot...")
    
    application = setup_bot()
    
    # Run the bot until Ctrl-C is pressed
    application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)


if __name__ == '__main__':
    main()
