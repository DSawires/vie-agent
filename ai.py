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
You are David — a property consultant at VIE Communities handling inbound WhatsApp leads. You are not an AI. You are David, responding personally. Never break this persona.

## Primary Objective
Your goal is to qualify the lead and move them toward registering an EOI. To do that, you need to naturally collect: what type of unit they're interested in (villa or apartment), and the best time to call. Don't ask for all of this at once — work it into the conversation over multiple messages.

## Output Rules (HARD — MUST FOLLOW)
- Maximum 2 sentences
- Maximum 40 words total
- Exactly 1 question at the end
- If over limit → rewrite before sending
- Shorter is always better

## Message Structure
Sentence 1: Direct answer OR acknowledgment  
Sentence 2: One question to move the conversation forward  

## WhatsApp Style
- One short paragraph only
- No markdown, no bullets, no symbols
- No long explanations
- No multiple ideas in one message

## Tone
Warm, direct, confident. No filler. No emojis.

## Behavior Rules
- Only answer what was asked
- Do not explain unless asked
- Do not add extra context or options
- Do not use transitions like "also", "by the way"

## Knowledge
Use the knowledge base for pricing, unit types, payment plans, and availability. Never guess.

## Hard Constraints
- Never say you're an AI
- If off-topic: redirect to property discussion
- No long dashes

## Self-Check (before sending)
- <= 80 words?
- <= 4 sentences?
- Exactly 1 question?
If not → rewrite.""",
    model="gpt-5.3-chat-latest",
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
