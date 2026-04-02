from fastapi import FastAPI, BackgroundTasks, Request

from webhook import handle_webhook

app = FastAPI(title="VIE Collective WhatsApp Bot")


@app.get("/")
async def root():
    return {"status": "running", "service": "vie-agent"}


@app.post("/webhook")
async def webhook(request: Request, background_tasks: BackgroundTasks):
    payload = await request.json()

    # Only process if no operator is handling (operatorName is null)
    if payload.get("operatorName") is not None:
        return {"status": "ignored", "reason": "operator handling"}

    return await handle_webhook(payload, background_tasks)
