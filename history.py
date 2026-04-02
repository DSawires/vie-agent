from config import MAX_HISTORY_TURNS

# In-memory conversation history store
# Key: phone number (waId), Value: list of message dicts {role, content}
_history: dict[str, list[dict]] = {}


def get_history(phone: str) -> list[dict]:
    """Get conversation history for a phone number."""
    return _history.get(phone, [])


def append_message(phone: str, role: str, content: str) -> None:
    """Append a message to the conversation history."""
    if phone not in _history:
        _history[phone] = []

    _history[phone].append({"role": role, "content": content})

    # Trim to keep last N turns (each turn = 2 messages: user + assistant)
    max_messages = MAX_HISTORY_TURNS * 2
    if len(_history[phone]) > max_messages:
        _history[phone] = _history[phone][-max_messages:]


def clear_history(phone: str) -> None:
    """Clear conversation history for a phone number."""
    if phone in _history:
        del _history[phone]
