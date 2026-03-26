"""Telegram bot service using aiogram."""

import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, CommandStart
from config import load_config
from handlers.start import handle_start
from handlers.help import handle_help
from handlers.health import handle_health
from handlers.labs import handle_labs
from handlers.scores import handle_scores


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_handler_response(command: str) -> str:
    """Route command to appropriate handler."""
    if command == "/start":
        return handle_start()
    elif command == "/help":
        return handle_help()
    elif command == "/health":
        return handle_health()
    elif command == "/labs":
        return handle_labs()
    elif command.startswith("/scores"):
        parts = command.split(maxsplit=1)
        lab = parts[1] if len(parts) > 1 else ""
        return handle_scores(lab)
    else:
        return f"Command '{command}' not implemented yet."


async def start_command_handler(message: types.Message) -> None:
    """Handle /start command."""
    response = handle_start()
    await message.reply(response)


async def help_command_handler(message: types.Message) -> None:
    """Handle /help command."""
    response = handle_help()
    await message.reply(response)


async def health_command_handler(message: types.Message) -> None:
    """Handle /health command."""
    response = handle_health()
    await message.reply(response)


async def labs_command_handler(message: types.Message) -> None:
    """Handle /labs command."""
    response = handle_labs()
    await message.reply(response)


async def scores_command_handler(message: types.Message) -> None:
    """Handle /scores command."""
    parts = message.text.split(maxsplit=1)
    lab = parts[1] if len(parts) > 1 else ""
    response = handle_scores(lab)
    await message.reply(response)


async def run_bot() -> None:
    """Run the Telegram bot."""
    config = load_config()
    
    if not config["bot_token"]:
        logger.error("BOT_TOKEN not found in .env.bot.secret")
        return
    
    bot = Bot(token=config["bot_token"])
    dp = Dispatcher()
    
    # Register handlers
    dp.message.register(start_command_handler, CommandStart())
    dp.message.register(help_command_handler, Command("help"))
    dp.message.register(health_command_handler, Command("health"))
    dp.message.register(labs_command_handler, Command("labs"))
    dp.message.register(scores_command_handler, Command("scores"))
    
    logger.info("Bot started!")
    await dp.start_polling(bot)


def start_telegram_bot() -> None:
    """Start the Telegram bot."""
    asyncio.run(run_bot())
