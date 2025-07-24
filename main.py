#!/usr/bin/env python3
"""
Main entry point for the Simplified Google Bot.
"""

import os
import sys
import logging
import argparse
from pathlib import Path

# Add the parent directory to the path so we can import the package
sys.path.insert(0, str(Path(__file__).resolve().parent))

from simplified_google_bot.config import settings
from simplified_google_bot.bot import setup_bot, run_bot
from simplified_google_bot.utils import validate_environment, print_validation_results


def main():
    """
    Main entry point for the application.
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Simplified Google Bot")
    parser.add_argument("--validate", action="store_true", help="Validate configuration only")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    args = parser.parse_args()

    # Set up logging
    log_level = logging.DEBUG if args.debug else getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    logging.basicConfig(
        level=log_level,
        format=settings.LOG_FORMAT,
        handlers=[
            logging.FileHandler(settings.LOG_FILE),
            logging.StreamHandler()
        ]
    )

    # Set specific loggers to different levels
    logging.getLogger("telegram").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)

    logger = logging.getLogger(__name__)
    logger.info("Starting Simplified Google Bot")

    # Validate environment
    is_valid, errors = validate_environment()

    if args.validate:
        print_validation_results(is_valid, errors)
        return 0 if is_valid else 1

    if not is_valid:
        print_validation_results(is_valid, errors)
        logger.error("Configuration validation failed")
        return 1

    try:
        # Set up and run the bot
        application = setup_bot()
        run_bot(application)
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.exception(f"Error running bot: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
