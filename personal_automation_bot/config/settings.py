"""
Global settings for the Personal Automation Bot.
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Telegram settings
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Google API settings
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8080/")

# OpenAI settings
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Notion settings
NOTION_API_KEY = os.getenv("NOTION_API_KEY")

# Buffer settings
BUFFER_API_KEY = os.getenv("BUFFER_API_KEY")

# Metricool settings
METRICOOL_API_KEY = os.getenv("METRICOOL_API_KEY")

# Development settings
DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Storage settings
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
VECTOR_STORE_DIR = os.path.join(DATA_DIR, "vector_store")

# Create directories if they don't exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(VECTOR_STORE_DIR, exist_ok=True)
