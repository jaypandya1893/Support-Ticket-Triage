# Support Ticket Triage — NOTIONMIND AI Engineer Assignment

**Jay Pandya · pandyajay12@gmail.com**

---

## Setup & Run

**Requirements:** Python 3.11+

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set your API key
cp .env.example .env
# Edit .env and paste your GROQ_API_KEY

# 3. Run the server
cd src
python -m uvicorn main:app --reload

# 4. Open the UI
# http://localhost:8000
```

The UI lets you pick a sample ticket or paste your own. The `/process` endpoint returns structured JSON — visible via the "Show raw JSON" toggle.

**API-only usage:**
```bash
curl -X POST http://localhost:8000/process \
  -H "Content-Type: application/json" \
  -d '{"ticket_text": "I was charged twice this month, please refund one payment."}'
```

---

## Part 01 — Solution Design

### 1. What is the core problem you are solving?

Support agents waste a lot of time just reading a ticket, deciding what type it is, and typing a first reply — and they haven't even started fixing the problem yet. With 300–500 tickets a day, that's hours of work that honestly doesn't need a human to do it. The AI handles that boring first step so agents can jump straight to actually helping.

### 2. Workflow — ticket arrives to agent acts

1. **Ticket comes in** — Customer emails through Zendesk or Intercom.
2. **AI looks at it** — One AI call figures out the category, urgency, how the customer is feeling, writes a short summary, drafts a reply, and says if it needs escalation.
3. **Not sure? Flag it** — If the AI isn't very confident, it still shows the draft but puts a warning so the agent knows to double check.
4. **Needs escalation?** — Goes to a senior agent with the reason included. Draft is still there so they don't start from zero.
5. **Agent decides** — Agent reads the result, edits the draft if needed, and clicks send. The AI never sends on its own.
6. **Done** — Faster reply for the customer, less boring work for the agent.

### 3. AI models/APIs — and why

| Task | Choice | Why |
|---|---|---|
| Classifying and drafting replies | **Llama 3.3 70B via Groq** | Free (14,400 requests/day), fast, and really good at following instructions to return clean JSON. |
| Hard or escalated tickets | Same model | One model is fine for a prototype. Can always upgrade later if needed. |

I kept it to one AI call per ticket. One call returns everything — category, draft, escalation. No need to make three separate calls and wait longer for the same result.

I went with Groq and Llama because it's open source and free with no surprise quota blocks, unlike OpenAI or Gemini free tiers.

### 4. Two biggest failure points in production

**Problem 1: One ticket, multiple issues**

When I tested it, tickets were simple — one problem. But real customers write messy tickets like "my payment failed, also I can't log in, also can you add this feature?" The AI picks one thing and ignores the rest.

*How to fix it:* Tell the AI to also mention any other topics it noticed. That way the agent sees the full picture. If there are too many issues in one ticket, just send it straight to a human.

**Problem 2: AI invents things**

The AI has no idea what your product actually does. It can write something like "you can do this in the settings menu" when that feature doesn't even exist. Customer then comes back angry saying "you told me this was possible."

*How to fix it:* The prompt already tells it — don't make up features or timelines. The proper fix is connecting it to your real help docs so it only says things that are actually true. That's for v2.

### 5. What I would NOT automate

**Sending the reply.** AI writes it, human sends it. One bad reply going out can really upset a customer. Not worth the risk just to save one click.

**Handling angry or VIP customers.** The AI can spot "this person said they're cancelling" — but what to actually do about it is a human call. Maybe you call them, maybe you offer something. The AI doesn't have enough context for that.

**Legal stuff.** GDPR requests, data deletion, anything that sounds legal — those should go directly to the right person, not get an AI reply.

---

## Project Structure

```
.
├── README.md           ← This file (setup + Part 1)
├── REFLECTION.md       ← Part 3 (Vibe Coding) + Part 4
├── requirements.txt
├── .env.example
└── src/
    ├── main.py         ← FastAPI app, routes
    ├── processor.py    ← LLM call, JSON parsing, failure handling
    ├── prompts.py      ← System prompt + user prompt builder
    ├── samples.py      ← Hardcoded sample tickets
    └── templates/
        └── index.html  ← Minimal agent UI
```
