import asyncio
import logging
from collections import defaultdict

from fastapi import BackgroundTasks

from history import get_history, append_message
from ai import get_ai_response
from wati import send_message

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Per-user locks to ensure sequential processing
_locks: dict[str, asyncio.Lock] = defaultdict(asyncio.Lock)


async def process_message(wa_id: str, text: str) -> None:
    """Process an incoming message and send a response."""
    async with _locks[wa_id]:
        logger.info(f"[{wa_id}] Received: {text}")

        # Append user message to history
        append_message(wa_id, "user", text)

        # Get conversation history
        history = get_history(wa_id)

        # Get AI response
        response = await get_ai_response(history)
        logger.info(f"[{wa_id}] AI Response: {response}")

        # Append assistant response to history
        append_message(wa_id, "assistant", response)

        # Send response via Wati
        try:
            result = await send_message(wa_id, response)
            logger.info(f"[{wa_id}] Wati API: {result}")
        except Exception as e:
            logger.error(f"[{wa_id}] Wati API Error: {e}")


async def handle_webhook(payload: dict, background_tasks: BackgroundTasks) -> dict:
    """Handle incoming Wati webhook."""
    # Extract waId and text from payload
    wa_id = payload.get("waId")
    text = payload.get("text")

    if not wa_id or not text:
        logger.debug(f"Ignored payload: {payload}")
        return {"status": "ignored", "reason": "missing waId or text"}

    # Process message in background to return quickly
    background_tasks.add_task(process_message, wa_id, text)

    return {"status": "ok"}
