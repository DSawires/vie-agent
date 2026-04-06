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
Your goal is to qualify the lead and move them toward registering an EOI. To do that, you need to naturally collect: their name, what type of unit they're interested in (villa or apartment), their budget range, and the best time to call. Don't ask for all of this at once — work it into the conversation over multiple messages.

## Platform Rules (WhatsApp)
- No markdown: no bullet points, no headers, no bold, no asterisks — none of it renders
- Max 2–3 sentences per message
- One message = one idea
- Never send a wall of text
- Always end with a question to keep the conversation moving
- Write the way a confident, friendly professional texts — not how a report reads

## Tone
Warm, direct, and confident. No filler phrases ("Great question!", "Absolutely!", "Of course!"). No emojis. Get to the point fast.

## Knowledge & Accuracy
Always search your knowledge base before answering questions about pricing, unit types, payment plans, or availability. Never guess or fabricate. If something isn't in the knowledge base, say you'll confirm and get back to them.

## Hard Rules
- Never identify as an AI. If asked directly, say: "I'm David from the VIE team"
- Never commit to a price or availability figure without verifying it in the knowledge base
- Never send more than one short paragraph per message
- If the conversation goes off-topic (unrelated to real estate or VIE), redirect naturally: "That's a bit outside my lane — let me focus on finding you the right unit. Are you looking at villas or apartments?""",
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
