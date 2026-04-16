"""
AI processing layer.

Calls the Groq API (Llama 3.3 70B) once per ticket, parses the JSON response,
and handles the two most common failure modes:
  1. The model returns valid JSON but low confidence → flag for human review
  2. The model returns malformed output → surface a safe fallback instead of crashing
"""

import json
import os
from dataclasses import dataclass
from typing import Optional

from openai import OpenAI

from prompts import SYSTEM_PROMPT, build_user_prompt

# Low-confidence threshold: below this, route to human review regardless of other signals
CONFIDENCE_THRESHOLD = 0.70

# Model choice: llama-3.3-70b-versatile via Groq — free tier, fast, strong at
# structured JSON output. Switch to mixtral-8x7b-32768 if output quality drops.
MODEL = "llama-3.3-70b-versatile"


@dataclass
class TicketResult:
    category: str
    urgency: str
    sentiment: str
    confidence: float
    summary: str
    draft_reply: str
    needs_escalation: bool
    escalation_reason: Optional[str]
    suggested_tags: list[str]
    # Internal signals — not shown in primary UI output
    low_confidence_flag: bool = False
    raw_input_chars: int = 0
    error: Optional[str] = None

    def to_agent_output(self) -> dict:
        """Clean dict an agent (or the UI) acts on."""
        return {
            "category": self.category,
            "urgency": self.urgency,
            "sentiment": self.sentiment,
            "confidence": self.confidence,
            "summary": self.summary,
            "draft_reply": self.draft_reply,
            "needs_escalation": self.needs_escalation,
            "escalation_reason": self.escalation_reason,
            "suggested_tags": self.suggested_tags,
            "flags": {
                "low_confidence": self.low_confidence_flag,
                "review_recommended": self.low_confidence_flag or self.needs_escalation,
            },
        }


def _parse_response(raw_text: str) -> dict:
    """
    Extract JSON from the model response.
    The prompt instructs no markdown fences, but models sometimes add them anyway.
    Strip them defensively before parsing.
    """
    text = raw_text.strip()
    # Strip ```json ... ``` or ``` ... ``` if present
    if text.startswith("```"):
        lines = text.splitlines()
        text = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
    return json.loads(text)


def process_ticket(ticket_text: str) -> TicketResult:
    """
    Main entry point. Sends one ticket to the LLM and returns a TicketResult.

    Failure handling:
    - JSON parse error → returns a safe TicketResult with error field set
      (agent sees it, system doesn't crash)
    - API error → propagates as exception (caller handles HTTP 500)
    - Low confidence → sets low_confidence_flag, does not change category
    """
    client = OpenAI(
        api_key=os.environ["GROQ_API_KEY"],
        base_url="https://api.groq.com/openai/v1",
    )

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_user_prompt(ticket_text)},
        ],
        temperature=0.2,
        max_tokens=1024,
    )
    raw_text = response.choices[0].message.content

    try:
        data = _parse_response(raw_text)
    except (json.JSONDecodeError, IndexError, KeyError) as e:
        # Model returned something unparseable — surface a safe fallback
        return TicketResult(
            category="other",
            urgency="medium",
            sentiment="neutral",
            confidence=0.0,
            summary="Could not parse model output — manual review required.",
            draft_reply="",
            needs_escalation=True,
            escalation_reason=f"Automated processing failed (parse error: {e}). Human must triage.",
            suggested_tags=["parse-error", "needs-review"],
            low_confidence_flag=True,
            raw_input_chars=len(ticket_text),
            error=str(e),
        )

    confidence = float(data.get("confidence", 1.0))
    low_confidence = confidence < CONFIDENCE_THRESHOLD

    return TicketResult(
        category=data.get("category", "other"),
        urgency=data.get("urgency", "medium"),
        sentiment=data.get("sentiment", "neutral"),
        confidence=confidence,
        summary=data.get("summary", ""),
        draft_reply=data.get("draft_reply", ""),
        needs_escalation=bool(data.get("needs_escalation", False)),
        escalation_reason=data.get("escalation_reason"),
        suggested_tags=data.get("suggested_tags", []),
        low_confidence_flag=low_confidence,
        raw_input_chars=len(ticket_text),
    )
