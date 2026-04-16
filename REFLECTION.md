# Reflection — Jay Pandya

---

## Part 03 — Vibe Coding

### 6. What vibe coding tool(s) did you use?

I used two tools — **Claude Code** and **OpenAI Codex**.

Claude Code runs inside VS Code and understands the whole project. I could say "build this endpoint" and it would actually do it — read the files, write the code, run commands. Not just suggest a snippet.

Codex I used mostly for smaller things — quick completions, filling in repetitive parts, and getting a second take on logic I wasn't sure about. Good for speed, not great for anything that needs context across multiple files.

### 7. One specific moment where the tool helped

**What I asked it:**

> Build the FastAPI `/process` endpoint. Accept `ticket_text`, call `process_ticket()` from `processor.py`, return structured JSON. Handle missing API key as 500, upstream API error as 502, and parse failures as 200 with an error flag. Use Pydantic for request/response models.

**What it gave me:**

It built the full `main.py` — and it already had the three types of error handling I wanted. Missing key = 500 (setup problem). AI service down = 502 (retry later). Bad AI output = still return a 200 with a flag saying "this needs human review." It also added a character limit on the input (min 10, max 10,000) which I hadn't even asked for.

**What I kept:** The error handling structure and the input limits.

**What I changed:** It didn't load the API key from a `.env` file — it just assumed it was already in the environment. I added that. I also changed the error message to actually tell you what to do ("Add it to your .env file") instead of just saying the key is missing. Removed a random import it added that wasn't being used.

### 8. Where the tool got it wrong

First version of `processor.py` — when the AI returns something we can't read, it threw a 500 error and crashed the whole request.

That's not what I wanted. If the AI gives garbage output, the system should still work — it should return a result that says "couldn't process this, needs a human." Crashing with a 500 just breaks the agent's screen for no reason.

I rewrote that part myself so it returns a proper object with `needs_escalation: true` and a message explaining what failed. System stays up, agent knows what happened.

**What I learned from this:** The tool is great at writing the happy path — when everything works. But it doesn't really think about what happens when things break. You have to catch that yourself.

### 9. Mental model for vibe coding on a client project

I let it handle the stuff that's just time consuming but not complicated — setting up files, writing Pydantic models, HTML layout, sample data, boilerplate. Anything where I know exactly what I want but it's just boring to type out.

I take over when it's about decisions — like should this fail silently or crash loudly? Should the reply be auto-sent or manual? Those aren't code questions, they're product questions. The tool doesn't know the answer to those.

My personal rule: if I can't read what it wrote and explain it myself, I don't keep it. It's fast, but I'm still the one responsible for what goes in.

---

## Part 04 — Reflection

### 10. What corners did I cut?

- **No authentication** — the API is completely open. Anyone with the URL can hit it. Would need a key or login in production.
- **No rate limiting** — someone could spam it and burn through API credits fast.
- **No database** — results only exist in the browser. Nothing is saved. Real system would need to store tickets, results, and agent actions.
- **No feedback from agents** — if an agent changes the category or rewrites the draft, that's just lost. You need to capture that to know if the AI is actually doing a good job.
- **Generic replies** — the AI doesn't know the actual product so replies are professional but vague. Would be much better connected to real help docs.
- **One topic per ticket** — if someone writes about two problems, the AI picks one and ignores the other.

### 11. First question I'd ask a real client before building anything

**"When you see a billing ticket versus a bug ticket — do you actually do anything differently?"**

If yes, great — then categorization really matters and I'd build the whole thing around getting that right.

If no, and agents just handle everything the same way — then I'd skip the fancy classification and just focus on making the draft reply as good as possible.

I want to ask this first because I've seen people build complicated systems that solve the wrong problem. No point making a perfect classifier if the team doesn't use the categories for anything.

### 12. What would v2 look like?

In order of what I'd actually build next:

1. **Agent feedback** — simple thumbs up/down on the draft, and a way to fix the category if it's wrong. Just save the corrections for now, no retraining yet.
2. **Connect to real help docs** — so the draft can say "here's our actual billing FAQ" instead of making something up.
3. **Handle multi-topic tickets** — catch when a customer is asking about more than one thing.
4. **Customer history** — if they've written before, pull in their last couple of tickets so the reply doesn't feel like starting from scratch.
5. **Auto-intake from Zendesk/Intercom** — so tickets come in automatically instead of being pasted manually.
6. **Simple dashboard** — show which categories come up most, where the AI gets it wrong, how often agents change the draft. Basically just visibility into whether it's actually working.
