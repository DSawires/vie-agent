import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WATI_API_URL = os.getenv("WATI_API_URL")
WATI_API_TOKEN = os.getenv("WATI_API_TOKEN")
SYSTEM_PROMPT_PATH = os.getenv("SYSTEM_PROMPT_PATH", "prompts/vie_agent.txt")
WORKFLOW_ID = os.getenv("WORKFLOW_ID")

# Conversation history settings
MAX_HISTORY_TURNS = 20
