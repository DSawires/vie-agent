import logging
import httpx

from config import WATI_API_URL, WATI_API_TOKEN

logger = logging.getLogger(__name__)


async def send_message(phone: str, text: str) -> dict:
    """Send a message via Wati API."""
    url = f"{WATI_API_URL}/api/ext/v3/conversations/messages/text"
    headers = {
        "Authorization": f"Bearer {WATI_API_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {"target": phone, "text": text}

    logger.info(f"Wati Request URL: {url}")
    logger.info(f"Wati Request Body: {payload}")

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=headers)
        logger.info(f"Wati Response Status: {response.status_code}")
        logger.info(f"Wati Response Body: {response.text}")
        response.raise_for_status()
        return response.json()
