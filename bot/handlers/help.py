"""Handler for /help command."""


def handle_help() -> str:
    """Handle /help command.
    
    Returns:
        List of available commands.
    """
    return """Available commands:
/start - Welcome message
/help - Show this help message
/health - Check backend system status
/labs - List available labs
/scores <lab> - Show scores for a specific lab"""
