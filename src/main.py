"""
FastAPI application — support ticket triage prototype.

Routes:
  GET  /          → simple HTML UI (Jinja2 template)
  POST /process   → accepts ticket text, returns structured JSON
  GET  /samples   → returns the hardcoded sample set (used by UI)
  GET  /health    → liveness check
"""

import json
import os
from pathlib import Path

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

from processor import process_ticket
from samples import SAMPLE_TICKETS

app = FastAPI(
    title="Support Ticket Triage",
    description="AI-assisted triage: classify, draft, escalate — for agent review.",
    version="0.1.0",
)

TEMPLATES_DIR = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


# ── Request / Response models ──────────────────────────────────────────────────

class TicketRequest(BaseModel):
    ticket_text: str = Field(..., min_length=10, max_length=10_000)


class TriageResponse(BaseModel):
    category: str
    urgency: str
    sentiment: str
    confidence: float
    summary: str
    draft_reply: str
    needs_escalation: bool
    escalation_reason: str | None
    suggested_tags: list[str]
    flags: dict


# ── Routes ─────────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/samples")
def get_samples():
    return SAMPLE_TICKETS


@app.get("/", response_class=HTMLResponse)
def ui(request: Request):
    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "samples_json": json.dumps(SAMPLE_TICKETS),
        },
    )


@app.post("/process", response_model=TriageResponse)
def process(req: TicketRequest):
    """
    Core endpoint. Accepts a ticket, calls the LLM, returns structured output.

    Error strategy:
    - Missing API key → 500 with clear message (config error, not user error)
    - Gemini API error → 502 (upstream failure, caller can retry)
    - Parse failure → still returns 200 with error flag set in result
      (agent sees it; system stays up)
    """
    if not os.environ.get("GROQ_API_KEY"):
        raise HTTPException(
            status_code=500,
            detail="GROQ_API_KEY not set. Add it to your .env file.",
        )

    try:
        result = process_ticket(req.ticket_text)
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"Upstream API error: {e}",
        )

    return result.to_agent_output()
