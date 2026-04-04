import re
from agents import Agent, Runner, RunConfig, FileSearchTool, WebSearchTool

from config import WORKFLOW_ID


def clean_response(text: str) -> str:
    """Remove file citations and Unicode control characters from agent response."""
    # Remove citation blocks: \ue200...\ue201 (start/end of reference)
    text = re.sub(r'\ue200[\s\S]*?\ue201', '', text)
    # Remove hidden content blocks: \ue203...\ue204
    text = re.sub(r'\ue203[\s\S]*?\ue204', '', text)
    # Remove any stray control characters
    text = re.sub(r'[\ue200-\ue204]', '', text)
    # Remove any leftover filecite text patterns
    text = re.sub(r'filecite\w*', '', text)
    text = re.sub(r'turn\d+file\d+', '', text)
    # Clean up extra whitespace and newlines
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r' +', ' ', text)
    return text.strip()


# Tools
file_search = FileSearchTool(vector_store_ids=["vs_69cdad9d06448191bf9ce678b786c81e"])
web_search = WebSearchTool(search_context_size="medium")

# Agent definition
agent = Agent(
    name="Agent",
    instructions="""
## Role
You are David — a property consultant at VIE Communities handling inbound WhatsApp conversations. You are not an AI assistant. You are David, responding personally.

## Platform (WhatsApp)
- No bullet points, no headers, no markdown — none of it renders
- 1 short paragraph per message, 2–3 sentences max per message
- One idea per message, one question per message
- Write the way a real person texts, not the way a report reads
- Never send a wall of text

## Tone
Warm but direct. Confident without being pushy. Get to the point fast. No filler phrases. No emojis.

## Hard rules
- Never identify yourself as an AI. If asked, say: "I'm David from the VIE team"
- No prices or availability commitments without checking your knowledge base first
- Never send more than 1 paragraph in a single message
- Always ask a question at the end of your message to keep the conversation going
- Always use the tools when relevant to get the most up-to-date info""",
    model="gpt-5.4-nano",
    tools=[file_search, web_search],
)


async def get_ai_response(history: list[dict]) -> str:
    """Get a response from the agent given the conversation history."""
    # Convert history to agent input format
    input_items = []
    for msg in history:
        if msg["role"] == "user":
            input_items.append({
                "role": "user",
                "content": [{"type": "input_text", "text": msg["content"]}]
            })
        else:
            input_items.append({
                "role": "assistant",
                "content": [{"type": "output_text", "text": msg["content"]}]
            })

    result = await Runner.run(
        agent,
        input_items,
        run_config=RunConfig(
            trace_metadata={
                "__trace_source__": "agent-builder",
                "workflow_id": WORKFLOW_ID,
            }
        ),
    )

    return clean_response(result.final_output)
