def format_conversation_for_llm(conversation_history: list) -> str:
    """
    Converts a conversation history into a plain-text format for easy LLM consumption.

    Args:
        conversation_history (list of dict): List of conversation turns with 'role', 'content', and 'timestamp'.

    Returns:
        str: Formatted conversation history.
    """
    formatted_history = []
    for turn in conversation_history:
        role = turn.get('role', 'unknown').capitalize()
        content = turn.get('content', '')
        formatted_history.append(f"{role}: {content}")
    
    return "\n".join(formatted_history)
