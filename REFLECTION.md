# Reflection — Jay Pandya

---

## Part 03 — Vibe Coding

### 6. What vibe coding tool(s) did you use?

I used **Claude Code** — it is Anthropic's AI coding tool that runs inside VS Code. It can read and write files, run commands, and search the codebase, so I could tell it what I wanted to build and it would actually do it, not just suggest code for me to copy.

### 7. One specific moment where the tool helped

**What I asked:**

> Build the FastAPI `/process` endpoint. It should accept `ticket_text`, call `process_ticket()` from `processor.py`, and return structured JSON. Handle: missing API key (500), upstream API error (502), and parse failures (200 with error flag). Use Pydantic for request/response models.

**What it built:**

It wrote the full `main.py` with three different ways to handle errors — a 500 error if the API key is missing (that is a setup problem, not a user problem), a 502 if the AI service fails (so the client knows to retry), and a "soft failure" where if the AI returns something we cannot read, we still return a usable response instead of crashing. It also added input validation on the ticket text that I had not asked for — minimum 10 characters, maximum 10,000.

**What I kept:** The three-level error handling idea and the input validation.

**What I changed:** It assumed the `GROQ_API_KEY` was already set in the environment. I added the `python-dotenv` part so it loads from the `.env` file. I also made the error message more helpful — instead of just "key not found" it now says "Add it to your .env file." I removed a `background_tasks` import it added for no reason.

### 8. Where the tool got it wrong

When it first wrote `processor.py`, it made the JSON parse error throw an HTTP 500 exception. That means if the AI returns something weird and we cannot read it, the whole request crashes with an error page.

That is the wrong behaviour. If the AI gives bad output, we should still return something useful to the agent — like "we could not process this automatically, a human needs to look at it." The system should stay running, not crash.

I rewrote that part to return a proper result with `needs_escalation: true` and a message explaining what went wrong. The agent sees it clearly and can handle it manually.

**What this shows about AI coding tools:** They are good at writing code that works in the normal case. They are not as good at thinking about what happens when things go wrong. That is the part you always have to check yourself.

### 9. Mental model for vibe coding on a client project

**Let it handle:** Setting up boilerplate, writing repetitive code, HTML structure, Pydantic models, sample data — anything where the pattern is clear and I just need it done fast.

**I take over for:** Error handling, any decision that affects the user experience ("should this be auto-sent or manual?"), and anything the tool wrote that I cannot fully explain myself.

My rule is simple: if I cannot read the generated code and explain why it is correct, I do not use it. The tool writes fast, but I am still responsible for what gets submitted. Using it without understanding is how you build something that looks fine but breaks in ways you did not expect.

---

## Part 04 — Reflection

### 10. What corners did I cut?

- **No login or security on the API.** Anyone who knows the URL can use it. In a real product it would need authentication.
- **No rate limiting.** Right now one person could spam the endpoint and rack up API costs. That needs to be capped.
- **No database.** Every result only exists in the browser response. A real system would save results so you can track trends, review past tickets, and measure accuracy.
- **No way for agents to give feedback.** If an agent changes the category or rewrites the draft, that information just disappears. Capturing those corrections is how you improve the system over time.
- **The draft reply is generic.** It does not know your actual product, your help articles, or your past resolutions. It writes something professional but not specific. Connecting it to real docs would make it much more useful.
- **One category per ticket.** If a customer writes about two different problems, the AI picks one and ignores the other.

### 11. First question I'd ask a real client before building anything

**"When a ticket comes in as a billing issue versus a bug report — does your team actually do something different with it?"**

If yes — they route it to different teams, different response times, different templates — then getting the category right really matters and I should design the whole prompt around those exact categories.

If no — agents just respond to everything the same way — then classification is not actually the problem and I should focus on making the draft reply better instead.

I want to know this first because it is easy to build a very accurate classifier that does not actually help anyone.

### 12. What would v2 look like?

In order of what I would build first:

1. **Let agents correct mistakes** — add a thumbs up/down on the draft and a way to fix the category. Just log it for now. After a few weeks you have real data on where the AI is wrong.
2. **Connect to your actual help docs** — so the draft reply references real articles and real solutions instead of writing something generic.
3. **Handle tickets with multiple topics** — detect when a customer is asking about more than one thing and make sure the reply covers all of it.
4. **Show the customer's history** — if they have emailed before, include their last few tickets so the reply is not treating them like a stranger.
5. **Automatic ticket intake** — connect to Zendesk or Intercom via webhook so tickets flow in automatically instead of being pasted manually.
6. **A simple dashboard** — show how often each category comes up, how often agents change the AI's answer, and where confidence is lowest. This makes the system something you can actually trust and improve.
