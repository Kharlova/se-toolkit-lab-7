#!/usr/bin/env python3
"""Telegram bot entry point.

Usage:
    uv run bot.py              # Start Telegram bot
    uv run bot.py --test "/start"  # Test mode (no Telegram connection)
"""

import argparse
import sys
from handlers.start import handle_start
from handlers.help import handle_help
from handlers.health import handle_health
from handlers.labs import handle_labs
from handlers.scores import handle_scores


def get_handler_response(command: str) -> str:
    """Route command to appropriate handler.
    
    Args:
        command: The command string (e.g., "/start", "/help", "/scores lab-04")
    
    Returns:
        Response text from the handler.
    """
    if command == "/start":
        return handle_start()
    elif command == "/help":
        return handle_help()
    elif command == "/health":
        return handle_health()
    elif command == "/labs":
        return handle_labs()
    elif command.startswith("/scores"):
        # Extract lab argument if provided
        parts = command.split(maxsplit=1)
        lab = parts[1] if len(parts) > 1 else ""
        return handle_scores(lab)
    else:
        return f"Command '{command}' not implemented yet."


def test_mode(command: str) -> None:
    """Run bot in test mode - print response to stdout.

    Args:
        command: The command to test (e.g., "/start")
    """
    response = get_handler_response(command)
    print(response)
    # Close API client to clean up connections
    from services.api_client import get_api_client
    client = get_api_client()
    client.close()
    sys.exit(0)


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="LMS Telegram Bot")
    parser.add_argument(
        "--test",
        type=str,
        metavar="COMMAND",
        help="Test mode: run a command and print response (no Telegram connection)"
    )
    
    args = parser.parse_args()
    
    if args.test:
        test_mode(args.test)
        return
    
    # Normal mode: start Telegram bot
    from services.telegram_bot import start_telegram_bot
    start_telegram_bot()


if __name__ == "__main__":
    main()
