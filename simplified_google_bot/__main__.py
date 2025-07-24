"""
Main entry point for the Simplified Google Bot.
"""

import logging
import argparse
import signal
import sys
from pathlib import Path

from simplified_google_bot.config import settings
from simplified_google_bot.utils.config_validator import validate_environment, print_validation_results, setup_wizard
from simplified_google_bot.bot.core import setup_bot, run_bot
from simplified_google_bot.web.oauth_handler import start_oauth_server, stop_oauth_server

# Set up logger
logger = logging.getLogger(__name__)

def signal_handler(sig, frame):
    """Handle termination signals."""
    logger.info("Shutting down bot...")
    stop_oauth_server()
    sys.exit(0)

def main():
    """Main entry point."""
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Simplified Google Bot")
    parser.add_argument("--setup", action="store_true", help="Run setup wizard")
    parser.add_argument("--validate", action="store_true", help="Validate configuration")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    args = parser.parse_args()

    # Configure logging
    log_level = logging.DEBUG if args.debug else getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    logging.basicConfig(
        level=log_level,
        format=settings.LOG_FORMAT,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(settings.LOG_FILE)
        ]
    )

    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Run setup wizard if requested
    if args.setup:
        setup_wizard()
        return

    # Validate configuration if requested
    if args.validate:
        is_valid, errors = validate_environment()
        print_validation_results(is_valid, errors)
        return

    # Validate configuration before starting
    is_valid, errors = validate_environment()
    if not is_valid:
        print_validation_results(is_valid, errors)
        logger.error("Invalid configuration. Please run with --setup to configure the bot.")
        return

    logger.info("Starting Simplified Google Bot...")

    # Start OAuth web server
    start_oauth_server()

    try:
        # Set up and run the bot
        application = setup_bot()
        run_bot(application)
    except Exception as e:
        logger.error(f"Error running bot: {e}")
    finally:
        # Stop OAuth web server
        stop_oauth_server()

if __name__ == "__main__":
    main()
