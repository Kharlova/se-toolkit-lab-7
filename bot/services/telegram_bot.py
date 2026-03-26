"""Telegram bot service using aiogram."""

import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import load_config
from handlers.start import handle_start
from handlers.help import handle_help
from handlers.health import handle_health
from handlers.labs import handle_labs
from handlers.scores import handle_scores
from handlers.text_message import handle_text_message


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_main_keyboard() -> InlineKeyboardMarkup:
    """Get main inline keyboard for common actions."""
    keyboard = [
        [
            InlineKeyboardButton(text="📚 Labs", callback_data="labs"),
            InlineKeyboardButton(text="🟢 Health", callback_data="health"),
        ],
        [
            InlineKeyboardButton(text="📊 Scores lab-04", callback_data="scores_lab-04"),
            InlineKeyboardButton(text="📊 Scores lab-07", callback_data="scores_lab-07"),
        ],
        [
            InlineKeyboardButton(text="❓ Help", callback_data="help"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


async def start_command_handler(message: types.Message) -> None:
    """Handle /start command with inline keyboard."""
    response = handle_start()
    keyboard = get_main_keyboard()
    await message.reply(response, reply_markup=keyboard)


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


async def callback_query_handler(callback_query: types.CallbackQuery) -> None:
    """Handle inline button callbacks."""
    action = callback_query.data

    if action == "labs":
        response = handle_labs()
    elif action == "health":
        response = handle_health()
    elif action == "help":
        response = handle_help()
    elif action.startswith("scores_"):
        lab = action.replace("scores_", "")
        response = handle_scores(lab)
    else:
        response = "Unknown action."

    await callback_query.message.edit_text(response)


async def text_message_handler(message: types.Message) -> None:
    """Handle natural language text messages."""
    user_message = message.text
    if not user_message:
        return

    # Check if it's a command (starts with /)
    if user_message.startswith("/"):
        return  # Commands are handled separately

    # Process as natural language query
    response = handle_text_message(user_message)
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
    dp.message.register(text_message_handler)  # For natural language messages
    dp.callback_query.register(callback_query_handler)

    logger.info("Bot started!")
    await dp.start_polling(bot)


def start_telegram_bot() -> None:
    """Start the Telegram bot."""
    asyncio.run(run_bot())