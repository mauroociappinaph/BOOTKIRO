#!/usr/bin/env python3
"""
Personal Automation Bot - A free personal automation system that centralizes
productivity tasks and content creation through a Telegram bot interface.
"""
import os
import logging
import argparse
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def main():
    """Main entry point for the application."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Personal Automation Bot")
    parser.add_argument("--dev", action="store_true", help="Run in development mode")
    args = parser.parse_args()

    # Load environment variables
    load_dotenv()

    # Log startup information
    logger.info("Starting Personal Automation Bot")
    if args.dev:
        logger.info("Running in development mode")

    try:
        # Import and initialize the bot
        from personal_automation_bot.bot import setup_bot

        # Set up the bot
        application = setup_bot()

        logger.info("Bot initialized and ready to receive commands")

        # Start the bot
        logger.info("Bot is now polling for updates...")
        application.run_polling()

    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        logger.error("Please check your .env file and ensure TELEGRAM_BOT_TOKEN is set")
        return 1
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        return 1

    logger.info("Bot stopped")
    return 0


if __name__ == "__main__":
    main()
