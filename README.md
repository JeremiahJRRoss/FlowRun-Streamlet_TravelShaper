# TravelShaper — AI Travel Assistant

An intelligent travel planning assistant powered by LLM agents. TravelShaper helps you find flights, hotels, and cultural insights for your destination — all through a single conversation.

Built with LangGraph, FastAPI, and instrumented with Arize Phoenix for observability and evaluation. Accessible via a browser chat interface at `http://localhost:8000` or directly through the REST API.

---

## What TravelShaper Does

You tell TravelShaper where you're coming from, where you want to go, your rough travel dates, and what matters to you. It searches live flight and hotel data, gathers cultural and destination intelligence from the web, and delivers a curated travel briefing — not a wall of links, but an opinionated recommendation.

### How It Works
**1. You fill in the form**

TravelShaper's browser interface asks for five structured fields — no need to compose the perfect sentence:

| Field | What you enter |
|-------|----------------|
| **Departing from** | Your city or region — TravelShaper finds the nearest airport |
| **Destination** | Where you're headed |
| **Departure date** | A specific date — pick it from the calendar |
| **Duration** | 1, 2, 3, or 4 weeks |
| **Budget** | One toggle: *Save money* or *Full experience* |

Then select your interests — Food, Arts, Photography, Nature, Fitness, or Nightlife — and hit **Plan my trip.**

**2. Tell TravelShaper more (optional)**

Below the main form is a free-text preferences field where you can say anything that doesn't fit the checkboxes. This is where the real personality comes through. Some examples of what people actually write:

> *"I want to leave feeling like I understand the history and natural landscape of the place — not just the tourist version of it."*

> *"I'm travelling with an elderly couple. We need a safe, walkable neighbourhood where nobody has to think too hard about getting around."*

> *"I have a 5-year-old with me. Everything needs to be kid-friendly — ideally places where a tantrum won't ruin anyone's evening."*

> *"I'm a solo woman traveller. I'd love to know which areas feel genuinely safe at night and which ones I should avoid."*

> *"We're celebrating a 25th anniversary. I want at least one moment that feels genuinely special — not a tourist package, something real."*

> *"I'm pescatarian and my partner keeps halal. Food options matter a lot to us."*

TravelShaper safety-checks this field before use and folds your preferences into every search and recommendation it makes. Up to 500 characters.

> **Note:** The current implementation is single-turn — each request is independent. Include as much as you can in one go for the richest results. Multi-turn conversation memory is a planned production enhancement.

**2. TravelShaper searches on your behalf**

Once it understands your trip, TravelShaper dispatches specialized tools:

- **Flight search** — Queries Google Flights via SerpAPI for structured results: real prices, airlines, layovers, and duration.
- **Hotel search** — Queries Google Hotels via SerpAPI for structured results: nightly rates, ratings, amenities, and images.
- **Cultural guide** — Searches the web for destination-specific etiquette, language phrases, dress codes, and tipping customs. Results are web-sourced and synthesized by the LLM — useful and practical, but not from a structured travel database.
- **General web search** — Fills in gaps with open web results for your specific interests (restaurants, events, photo spots, etc.). Coverage and quality vary by destination.

**3. You receive a travel briefing**

TravelShaper synthesizes everything into a single conversational response covering:

- **Getting there** — Best flight options ranked by your budget preference, with a note on the best value.
- **Where to stay** — Hotel recommendations matched to your budget and neighborhood preferences.
- **What to know before you go** — Key phrases in the local language, etiquette tips, what to wear for the season and culture, and things to avoid.
- **What to do** — Recommendations tailored to your stated interests (food spots, photo locations, art scenes, nature hikes, nightlife, fitness activities).

TravelShaper explains *why* it recommends something, not just *what*. For example: "This hotel is recommended because it's walkable to the food district and under your budget" or "This flight is cheaper but has a 4-hour layover — worth it if you're saving money, skip it if you want to arrive rested."

---

## Your Interests

When TravelShaper asks what you care about, choose from these categories (or combine them):

| Interest | What TravelShaper finds for you |
|----------|---------------------------|
| **Food & Dining** | Local restaurants, street food, food markets, dining customs, must-try dishes |
| **Parties & Events** | Nightlife, live music, festivals, local events happening during your dates |
| **The Arts** | Museums, galleries, street art, architecture, local craft scenes, underground culture |
| **Fitness** | Hiking trails, running routes, local gyms, outdoor activities, cycling |
| **Nature** | National parks, scenic views, beaches, gardens, day trips into the outdoors |
| **Photography** | Photogenic spots, golden hour locations, iconic views, hidden gems worth shooting |

You can pick as many as you want. TravelShaper adjusts its research and recommendations accordingly.

---

## Budget Modes

TravelShaper tailors every recommendation to one of two modes:

**"Save money"** — Prioritizes budget airlines, hostels and guesthouses, free attractions, street food, and public transit tips. TravelShaper will flag when spending a little more is genuinely worth it.

**"Full experience"** — Prioritizes comfort, quality, and memorable experiences. Direct flights, well-reviewed hotels, top-rated restaurants, and skip-the-line suggestions. TravelShaper will still flag obvious overpriced tourist traps.

---

## Cultural & Travel Prep

Every briefing includes a preparation section tailored for American travelers:

### Language Basics
- Essential phrases: hello, thank you, please, excuse me, how much?, where is...?
- Pronunciation tips
- Whether English is widely spoken at your destination

### Etiquette
- Greeting customs (bowing, handshakes, cheek kisses)
- Tipping expectations
- Table manners and dining norms
- Religious site protocols
- Common faux pas to avoid

### What to Wear
- Weather-appropriate clothing for your travel dates
- Cultural dress expectations (covering shoulders for temples, modest dress in conservative areas)
- Practical footwear advice (cobblestones, hiking, temple visits requiring shoe removal)
- Packing suggestions for the season

---

## Running the Application

### Prerequisites

- Python 3.11+
- [Poetry](https://python-poetry.org/docs/#installation)
- A [SerpAPI](https://serpapi.com) API key (free tier: 250 searches/month)
- An [OpenAI](https://platform.openai.com) API key

### The preferred method is to use Docker Compose

**1. Configure environment variables**

```bash
cp .env.example .env
```

Edit `.env` and add your keys:

```
OPENAI_API_KEY=your_openai_key_here
SERPAPI_API_KEY=your_serpapi_key_here
```

**2. Docker Compose (includes Phoenix):**

```bash
docker-compose build --no-cache
docker-compose up -d
```
To stop both containers (TravelShaper & Arize)
```bash
docker-compose down
```

This starts both the TravelShaper API on port 8000 and Phoenix UI on port 6006.

> **Note:** The `docker-compose.yml` is included in the repository. If running Phoenix separately, see the Observability section below.

**Alternative container build method (for if you can't use docker compose):**

```bash
docker build -t travelshaper .
docker run -p 8000:8000 --env-file .env travelshaper
```


### An alternate method is to run the app in a python3 environment

1. Clone the repository:

```bash
git clone <your-repo-url>
cd src
```

2. Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate   # macOS / Linux
# .venv\Scripts\activate    # Windows
```

3. Install Poetry inside the venv and install dependencies:

```bash
pip install --upgrade pip
pip install poetry==1.8.2
poetry install -E dev
```

4. *(Optional)* Install Phoenix tracing packages:

```bash
pip install arize-phoenix arize-phoenix-evals arize-phoenix-otel \
            openinference-instrumentation-langchain
```

> **Note:** Phoenix packages are installed with `pip` rather than via a Poetry
> extra because `arize-phoenix-otel` has Python version constraints that conflict
> with Poetry's resolver on Python 3.11/3.12.

5. Configure environment variables:

```bash
cp .env.example .env
```

Edit `.env` and add your keys:

```
OPENAI_API_KEY=your_openai_key_here
SERPAPI_API_KEY=your_serpapi_key_here
```

4. Start the API server:

```bash
poetry run uvicorn api:app --reload
```

The API is now available at `http://localhost:8000`.


---

## Using the Web Interface

Once the server is running, open your browser and go to:

```
http://localhost:8000
```

You'll see a chat interface where you can type travel queries directly. The interface talks to the same `/chat` endpoint as curl — no difference in behaviour, just a friendlier way to interact during development and demos.

The API endpoints remain fully available alongside the UI. curl, pytest, and any other HTTP client work exactly as before.

---

## API Endpoints

### GET /

Serves the browser UI. Open in any browser.

```
http://localhost:8000
```

---

### POST /chat

Synchronous — waits for the full response, then returns it. Used by curl, tests, and any HTTP client that doesn't consume SSE. The request body mirrors exactly what the browser form submits.

**Full request (all fields):**

```bash
curl -s -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I am planning a trip departing from San Francisco, CA (please identify the nearest major international airport). Destination: Tokyo, Japan. Departure: 2026-04-10. Return: 2026-04-24 (2 weeks). Budget preference: save money. Interests: food and dining, photography. Please provide a complete travel briefing with hyperlinks for every named place, restaurant, hotel, and attraction.",
    "departure": "San Francisco, CA",
    "destination": "Tokyo, Japan",
    "preferences": "I want to leave feeling like I understand the real shape of this city — not just the postcard version. I am happy to walk all day."
  }' | python3 -m json.tool
```

**Minimal request (message only):**

```bash
curl -s -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Plan a trip from New York to Rome in September, save money, I love food and history."
  }' | python3 -m json.tool
```

**Request fields:**

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `message` | string | Yes | Full trip description in natural language |
| `departure` | string | No | Raw departure city — validated by gpt-4o; misspellings auto-corrected |
| `destination` | string | No | Raw destination — validated by gpt-4o; unrecognisable names return 400 |
| `preferences` | string | No | Up to 500 chars; safety-checked by gpt-4o before use |

**Successful response:**

```json
{
  "response": "Nobody tells you about the 6am fish market. Tourists are asleep. That's the point...\n\n## ✈️ Getting There\n\nANA via Los Angeles lands you in Narita for $687 round trip — that's $200 cheaper than the JAL direct and the layover is short enough that you won't notice it...\n\n## 🏨 Where to Stay\n\n[Khaosan Tokyo Kabuki](https://www.khaosan-tokyo.com/en/kabuki/) in Asakusa — $35/night. Walk out the front door and you're eight minutes from Senso-ji at dawn..."
}
```

**Validation error — unrecognisable place (HTTP 400):**

```json
{
  "detail": {
    "field": "destination",
    "message": "We couldn't find a place called 'Fakeville'. Please check the spelling or try a nearby major city."
  }
}
```

**Validation error — unsafe preferences (HTTP 400):**

```json
{
  "detail": "Your additional preferences could not be used: Request contains content that is not permitted."
}
```

---

### POST /chat/stream

SSE streaming endpoint — used by the browser UI. Sends incremental status events as each tool fires, then the final briefing. Same request body as `/chat`.

```bash
curl -s -X POST http://localhost:8000/chat/stream \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Departing San Francisco, going to Tokyo, April 10 for 2 weeks, save money, food and photography.",
    "departure": "San Francisco, CA",
    "destination": "Tokyo, Japan",
    "preferences": "Happy to walk all day. I want the real city, not the tourist version."
  }'
```

**Example SSE stream output:**

```
event: status
data: {"message": "✈️  Searching flights"}

event: status
data: {"message": "🏨  Finding hotels"}

event: status
data: {"message": "🗺️  Gathering cultural guide"}

event: status
data: {"message": "🔍  Searching the web"}

event: status
data: {"message": "📊  Processing search results"}

event: status
data: {"message": "✍️  Writing your personalised briefing"}

event: done
data: {"response": "Nobody tells you about the 6am fish market..."}
```

**If a place name was auto-corrected**, a `place_corrected` event fires before the status stream:

```
event: place_corrected
data: {"field": "destination", "original": "Tokio", "canonical": "Tokyo, Japan"}

event: status
data: {"message": "✈️  Searching flights"}
...
```

**All SSE event types:**

| Event | Payload | When it fires |
|-------|---------|---------------|
| `place_corrected` | `{"field", "original", "canonical"}` | Input was misspelled but identified — agent proceeds with corrected name |
| `place_error` | `{"field", "message"}` | Input is unrecognisable — stream ends, show error on form |
| `validation_error` | `{"message"}` | Preferences failed safety check — stream ends |
| `status` | `{"message"}` | A tool fired or synthesis began |
| `done` | `{"response"}` | Full briefing text — render the report |
| `error` | `{"message"}` | Agent raised an exception |

---

### GET /health

```bash
curl http://localhost:8000/health
# → {"status": "ok"}
```



## Architecture

```
Browser / curl
  │
  ├── POST /chat/stream  (SSE — browser UI)
  └── POST /chat         (sync — curl / tests)
           │
           ▼
     Place + Preference Validation (gpt-4o)
           │
           ▼
     LangGraph Agent
           │
     get_system_prompt(message)
           ├── "save money" → Bourdain / Billy Dee / Gladwell voice
           └── default     → Leach / Pharrell / Rushdie voice
           │
     llm_call (gpt-5.3-chat-latest)
           │
           ├── search_flights       (SerpAPI → Google Flights)
           ├── search_hotels        (SerpAPI → Google Hotels)
           ├── get_cultural_guide   (SerpAPI → Google Search)
           └── duckduckgo_search    (DuckDuckGo, no key needed)
           │
     tool_node → llm_call (synthesis)
           │
     SSE stream / JSON response → browser / client
```

### Tools

| Tool | API | What it returns |
|------|-----|-----------------|
| `search_flights` | SerpAPI (google_flights engine) | Airlines, prices, durations, layovers, booking links |
| `search_hotels` | SerpAPI (google_hotels engine) | Hotel names, nightly rates, ratings, amenities, images |
| `get_cultural_guide` | SerpAPI (google engine, scoped) | Language phrases, etiquette, dress code, local customs |
| `duckduckgo_search` | DuckDuckGo (no key needed) | General search results for interests and open questions |

---

## Observability with Arize Phoenix

TravelShaper is instrumented with Arize Phoenix for full observability of every agent interaction.

### Starting Phoenix

```bash
phoenix serve
```

Phoenix UI is available at `http://localhost:6006`.

### What Phoenix Captures

- **LLM calls** — Every GPT-4o invocation with full prompt, response, token usage, and latency.
- **Tool usage** — Every tool call with input parameters, output data, and execution time.
- **Agent traces** — End-to-end traces showing the full conversation loop: intake → tool dispatch → synthesis.

### Running Evaluations

```bash
poetry run python evaluations/run_evals.py
```

This runs two evaluation metrics on captured traces:

1. **User Frustration** — Detects traces where the user had to repeat themselves, got incomplete answers, or expressed dissatisfaction.
2. **Tool Usage Correctness** — Evaluates whether the agent selected the right tools for the user's query and passed valid parameters.

---

## Testing

Run the full test suite:

```bash
poetry run pytest tests/ -v
```

**14 tests, all mocked — no live API keys required.**

| File | Tests | What they cover |
|------|-------|-----------------|
| `test_tools.py` | 4 | Flight/hotel/cultural guide formatting and empty-result handling |
| `test_agent.py` | 2 | Graph node names, tool registry count and names |
| `test_api.py` | 8 | Health check, chat endpoint, valid/invalid preferences, valid/invalid/corrected place names |

Expected output: `14 passed` (one warning about `temperature` in `model_kwargs` is expected and harmless — it's a LangChain version artifact).

---

## Project Structure

```
src/
├── api.py                  # FastAPI — /chat (sync), /chat/stream (SSE), /health, static UI
│                           # Place validation (gpt-4o) + preference safety check
├── agent.py                # LangGraph agent — dual system prompts, voice routing, tools
├── static/
│   └── index.html          # Browser UI — Bebas Neue / Cormorant Garamond / DM Sans
├── tools/
│   ├── __init__.py         # serpapi_request() helper
│   ├── flights.py          # search_flights — SerpAPI Google Flights
│   ├── hotels.py           # search_hotels — SerpAPI Google Hotels
│   └── cultural_guide.py   # get_cultural_guide — scoped Google search
├── evaluations/
│   ├── run_evals.py        # Phoenix evaluation runner
│   └── metrics/
│       ├── frustration.py  # USER_FRUSTRATION_PROMPT
│       └── tool_correctness.py  # TOOL_CORRECTNESS_PROMPT
├── tests/
│   ├── test_tools.py       # 4 tool tests
│   ├── test_agent.py       # 2 agent graph tests
│   └── test_api.py         # 8 endpoint + validation tests
├── docs/
│   ├── ARCHITECTURE.md
│   ├── system-prompt-spec.md
│   ├── test-specification.md
│   ├── docker-spec.md
│   ├── presentation-outline.md
│   ├── evaluation-prompts.md
│   └── trace-queries.md
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── .env.example
├── CHANGELOG.md
└── RUNNING.md
```

---

## Example Briefing

The following illustrates the kind of output TravelShaper produces on a budget trip to Japan. Actual content depends on live search results and will vary.

**Form inputs:**
- Departing from: San Francisco, CA
- Destination: Tokyo, Japan
- Departure: April 10 · 2 weeks
- Budget: Save money
- Interests: Food, Photography
- Preferences: *"I want to leave feeling like I understand the real shape of this city — not just the postcard version. I'm happy to walk all day."*

**Briefing (abbreviated):**

---

Nobody tells you about the 6am fish market. Tourists are asleep. That's the point. That's where Tokyo shows you who it actually is. Here's how to get there, where to sleep, and what to eat when you arrive.

**01 — GETTING THERE**

ANA via Los Angeles lands you in Narita for $687 round trip — that's $200 cheaper than the JAL direct and the layover is short enough that you won't notice it. If you want to arrive rested and ready to walk all day from the moment your feet hit the pavement, [JAL direct](https://www.jal.com) at $892 is the honest answer.

**02 — WHERE TO STAY**

[Khaosan Tokyo Kabuki](https://www.khaosan-tokyo.com/en/kabuki/) in Asakusa — $35/night. This is not an accident. Asakusa is old Tokyo, the part that remembers what the city looked like before the towers. Walk out the front door and you're eight minutes from Senso-ji at dawn, when it belongs to you and the pigeons.

**03 — BEFORE YOU GO**

*Sumimasen* — say it constantly, for everything. Excuse me, sorry, may I, could you, thank you for your patience. It is the most useful word in the Japanese language and locals will light up when they hear you use it correctly...

**04 — WHAT TO DO**

[Tsukiji Outer Market](https://www.google.com/maps/search/Tsukiji+Outer+Market+Tokyo) at 6am. The inner market moved to Toyosu, but the outer market — the stalls, the tamagoyaki, the fresh tuna on rice in a paper cup — stayed. Get there before 8am or you're eating with the tour groups...

---

*Pack light, walk far, eat everything that has no English menu. Tokyo will do the rest.*

---

## User Experience Principles

**Clear** — TravelShaper does not dump raw search results. It synthesizes, ranks, and explains so the user gets a recommendation, not a research project.

**Personalized** — Every recommendation reflects the traveler's stated budget, interests, and constraints. Two users asking about the same city get different briefings.

**Explainable** — TravelShaper states the reason behind each major recommendation. "This hotel is near the food district and within budget" is more useful than "here's a hotel."

**Actionable** — The user should leave with a workable travel plan: specific flights, named hotels, concrete restaurant picks, and practical packing advice.

**Honest** — If search coverage is thin, data is uncertain, or a recommendation has tradeoffs, TravelShaper says so. It flags when prices may have changed and when its guidance is general rather than verified.

---

## Known Limitations

- TravelShaper is a planning assistant, not a booking engine. It recommends options but does not complete purchases.
- Flight and hotel prices change frequently. Results reflect the time of search, not guaranteed availability.
- Train and ferry data is less structured than flight and hotel data. Coverage varies by region.
- Cultural etiquette and dress guidance is practical advice based on common norms, not absolute rules. Local customs vary within countries.
- Weather-based packing guidance is strongest for trips within the next 1–2 weeks. Seasonal averages are used for trips further out.
- The app is designed for English-speaking American travelers. Guidance assumes U.S. norms as the baseline.

---

## Troubleshooting

**The server does not start**
- Confirm Python 3.11+ is installed: `python --version`
- Confirm the venv is active: your prompt should show `(.venv)`
- Confirm Poetry is installed in the venv: `poetry --version`
- Run `poetry install -E dev` to ensure dependencies are present
- Confirm `.env` exists and contains valid keys

**The app returns an authentication error**
- Check that `OPENAI_API_KEY` is set correctly in `.env`
- Check that `SERPAPI_API_KEY` is set correctly in `.env`
- Verify your SerpAPI key at [serpapi.com/manage-api-key](https://serpapi.com/manage-api-key)

**The app responds but results are poor or incomplete**
- Make sure your message includes origin, destination, timeline, and budget preference
- Check SerpAPI usage — the free tier allows 250 searches/month
- Try a well-known destination (Tokyo, Barcelona, Rome) for the most reliable results

**Traces are missing in Phoenix**
- Confirm Phoenix is running: `phoenix serve`
- Check that the Phoenix endpoint is configured in the app's instrumentation
- Run at least one `/chat` query after Phoenix is started, then refresh the Phoenix UI

---

---

## Design Decisions

**Browser chat interface** — A single self-contained HTML file served directly by FastAPI at `http://localhost:8000`. No separate frontend server, no npm, no build step. The UI calls the same `/chat` endpoint as curl, so the REST API remains fully available for testing and automation alongside it.

**SerpAPI as single data provider** — One API key powers flights, hotels, and scoped web searches. The Google Flights and Google Hotels engines return structured JSON with real pricing data. Cultural and interest searches use SerpAPI's general Google engine — useful and practical, but less structured than the dedicated travel endpoints.

**Cultural guide as a first-class tool** — Most travel chatbots skip cultural preparation entirely. For American travelers especially, etiquette and language guidance prevents real-world embarrassment and shows the agent adds value beyond price comparison.

**DuckDuckGo as fallback** — The original codebase's search tool remains available for general queries that don't fit the specialized tools. No API key required.

**Single-turn design** — Each `/chat` request is currently independent. The user gets the best results by including all trip details in one message. Multi-turn conversation memory (session-based chat history) is a natural production enhancement but is out of scope for this implementation.

**Budget as a lens, not a filter** — Budget preference affects ranking and tone, not hard cutoffs. A budget traveler still sees the occasional splurge-worthy option; a full-experience traveler still gets warned about tourist traps.
