import time
from config import MAX_HISTORY_TURNS

# TTL in seconds (24 hours)
HISTORY_TTL = 24 * 60 * 60

# In-memory conversation history store
# Key: phone number (waId), Value: list of message dicts {role, content}
_history: dict[str, list[dict]] = {}

# Last activity timestamp per phone
_last_activity: dict[str, float] = {}


def _cleanup_stale() -> None:
    """Remove histories that haven't been active for 24 hours."""
    now = time.time()
    stale_phones = [
        phone for phone, last_time in _last_activity.items()
        if now - last_time > HISTORY_TTL
    ]
    for phone in stale_phones:
        del _history[phone]
        del _last_activity[phone]


def get_history(phone: str) -> list[dict]:
    """Get conversation history for a phone number."""
    _cleanup_stale()

    # Check if this user's history has expired
    if phone in _last_activity:
        if time.time() - _last_activity[phone] > HISTORY_TTL:
            clear_history(phone)
            return []

    return _history.get(phone, [])


def append_message(phone: str, role: str, content: str) -> None:
    """Append a message to the conversation history."""
    if phone not in _history:
        _history[phone] = []

    _history[phone].append({"role": role, "content": content})
    _last_activity[phone] = time.time()

    # Trim to keep last N turns (each turn = 2 messages: user + assistant)
    max_messages = MAX_HISTORY_TURNS * 2
    if len(_history[phone]) > max_messages:
        _history[phone] = _history[phone][-max_messages:]


def clear_history(phone: str) -> None:
    """Clear conversation history for a phone number."""
    if phone in _history:
        del _history[phone]
    if phone in _last_activity:
        del _last_activity[phone]
