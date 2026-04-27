import os
from dotenv import load_dotenv

load_dotenv()

# Constants
STATUS_PENDING = 'pending'
STATUS_COMPLETED = 'completed'
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
os.makedirs(DATA_DIR, exist_ok=True)


def get_config():
    """Get configuration. Validates on first call."""
    token = os.getenv('BOT_TOKEN')
    if not token:
        raise ValueError("BOT_TOKEN environment variable is not set")
    return {'token': token}
