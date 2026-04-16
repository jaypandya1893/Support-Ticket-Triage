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

Every support ticket takes an agent 2–3 minutes just to read, figure out what type it is, and write a first reply — before they even start solving the actual problem. If you have 300–500 tickets a day, that adds up to a lot of wasted time on work that doesn't really need a human. The real problem is not answering tickets — it is the reading and sorting part that slows everything down.

### 2. Workflow — ticket arrives to agent acts

1. **Ticket comes in** — Customer sends an email through something like Zendesk or Intercom.
2. **AI reads it** — One AI call looks at the ticket and gives back: what type it is, how urgent, how the customer is feeling, a short summary, a draft reply, and whether it needs escalation.
3. **Low confidence check** — If the AI is not very sure about its answer (below 70% confidence), it still sends a draft but marks it clearly so the agent knows to double-check.
4. **Escalation check** — If the ticket needs a senior person, it goes to a different queue with the reason attached. The draft is still included so they are not starting from scratch.
5. **Agent reviews** — The agent sees everything laid out. They can send the draft as-is, edit it, or write their own. They always click send — the AI never sends automatically.
6. **Done** — Customer gets a reply faster, agent spent less time on the boring part.

### 3. AI models/APIs — and why

| Task | Choice | Why |
|---|---|---|
| Reading and replying to tickets | **Llama 3.3 70B via Groq** | It is free to use (14,400 requests per day), very fast (under 1 second), and it follows instructions well when you ask it to return structured JSON. |
| Complex or escalated tickets | Same model | For a prototype at this scale, one model is enough. If accuracy becomes a problem later, we can upgrade. |

I used one single AI call per ticket instead of multiple calls — one call gives us the category, draft reply, and escalation decision all at once. Splitting it into separate calls would be slower and more expensive with no real benefit.

I picked Groq with Llama because it is open source, completely free for this scale, and does not have the quota problems that OpenAI and Gemini free tiers have.

### 4. Two biggest failure points in production

**Problem 1: Customer writes about multiple things in one ticket**

In testing, tickets are usually clean — one topic. But real customers write things like "my bill is wrong AND I can't log in AND can you also add dark mode?" The AI picks one category and writes a reply for that, ignoring the rest.

*Fix:* Ask the AI to also list any secondary topics it notices. The agent can then see everything the customer mentioned. If there are too many topics, flag it for manual review.

**Problem 2: AI makes up product details**

The AI does not know your actual product. It might write a reply mentioning features that do not exist, or promise things your team cannot do. If a customer then says "but you told me X was possible," that is a trust problem.

*Fix:* The system prompt tells the AI clearly — do not invent product names, timelines, or features. A better long-term fix is to connect it to your actual help docs so it only says things that are true. That is planned for v2.

### 5. What I would NOT automate

**Actually sending the reply.** The AI drafts it, the agent sends it. One wrong reply going out — bad tone, wrong information, a promise you cannot keep — can damage a customer relationship. The time saved by auto-sending is not worth that risk.

**Deciding how to handle VIP or upset customers.** The AI can flag "this customer said they are going to cancel" — but what to do about that is a human decision. Do you call them? Offer a discount? That depends on context the AI does not have.

**Legal or compliance tickets.** Anything about GDPR, data deletion, security issues, or legal complaints should go straight to the right person at the company, not get an AI-drafted reply.

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
