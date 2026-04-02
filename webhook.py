from fastapi import BackgroundTasks

from history import get_history, append_message
from ai import get_ai_response
from wati import send_message


async def process_message(wa_id: str, text: str) -> None:
    """Process an incoming message and send a response."""
    # Append user message to history
    append_message(wa_id, "user", text)

    # Get conversation history
    history = get_history(wa_id)

    # Get AI response
    response = await get_ai_response(history)

    # Append assistant response to history
    append_message(wa_id, "assistant", response)

    # Send response via Wati
    await send_message(wa_id, response)


async def handle_webhook(payload: dict, background_tasks: BackgroundTasks) -> dict:
    """Handle incoming Wati webhook."""
    # Extract waId and text from payload
    wa_id = payload.get("waId")
    text = payload.get("text")

    if not wa_id or not text:
        return {"status": "ignored", "reason": "missing waId or text"}

    # Process message in background to return quickly
    background_tasks.add_task(process_message, wa_id, text)

    return {"status": "ok"}
