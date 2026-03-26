"""Handler for text messages (natural language queries)."""

from handlers.intent_router import route_intent


def handle_text_message(message: str) -> str:
    """Handle natural language message.
    
    Args:
        message: User's text message
    
    Returns:
        Response from the intent router.
    """
    return route_intent(message)
