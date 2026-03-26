"""Handler for /scores command."""


def handle_scores(lab: str) -> str:
    """Handle /scores command.
    
    Args:
        lab: Lab identifier (e.g., "lab-04")
    
    Returns:
        Scores information for the lab.
    """
    # TODO: Implement actual scores lookup in Task 2
    return f"📊 Scores for {lab}:\n- Task 1: 100%\n- Task 2: 85%\n- Task 3: 92%\n(placeholder)"
