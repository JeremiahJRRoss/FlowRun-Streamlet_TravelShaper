# TravelShaper

**AI travel planning assistant** — fill in a form, get an opinionated briefing with flights, hotels, cultural prep, and activity picks.

Every recommendation includes a hyperlink and an explanation of *why* it was chosen. The agent runs two distinct voices depending on budget mode, and the entire request flow is instrumented with Arize Phoenix for observability.

---

## Before You Begin

TravelShaper needs two things from the outside world: an OpenAI key to think with, and a SerpAPI key to search with. Everything else — the agent, the tools, the UI, the tracing stack — lives inside the project. Getting these keys configured correctly is the single most important step in setup, and the one most likely to cause confusion later if skipped.

### 1. Create your environment file

```bash
cd src
cp .env.example .env
```

Open `.env` in any editor and fill in your keys:

```
OPENAI_API_KEY=sk-...
SERPAPI_API_KEY=...
PHOENIX_COLLECTOR_ENDPOINT=http://localhost:6006/v1/traces
```

**Where to get keys:**

- **OpenAI** (required) — [platform.openai.com/api-keys](https://platform.openai.com/api-keys). The agent cannot function without this. The `openai` SDK is also used by the place and preference validation classifiers in `api.py`.
- **SerpAPI** (required for flights, hotels, and cultural guide) — [serpapi.com/manage-api-key](https://serpapi.com/manage-api-key). The free tier provides 250 searches per month, which supports roughly 60–125 full trip briefings. Without this key, the agent falls back to DuckDuckGo for everything — functional, but limited.
- **Phoenix endpoint** — leave the default. It points to the Phoenix container that Docker Compose starts automatically. Only change this if you are running Phoenix on a different host.

The `.env` file is listed in `.gitignore` and will never be committed. If you see an auth error later, this is the first place to check.

---

## Choose How to Run

There are three ways to run TravelShaper. All three produce identical results — the app, the API, and the tracing stack work the same regardless of how you start them. Pick the one that matches your comfort level and tooling.

**Prerequisites for all options:**

- **Docker** and **Docker Compose** — required for Options A and B, and recommended for Option C if you want Phoenix tracing. Install from [docs.docker.com/get-docker](https://docs.docker.com/get-docker/). After installing, verify both are available:

```bash
docker --version          # should print Docker version 20+
docker compose version    # should print Docker Compose version 2+
```

If `docker compose` (with a space) does not work but `docker-compose` (with a hyphen) does, you have the legacy v1 CLI — that works too. Substitute `docker-compose` wherever you see `docker compose` below.

- **Python 3.11+** — required for Option C only. Check with `python3 --version`.

### Option A: Docker Compose (manual steps)

Use this if you want full control over each step — building the containers yourself, starting the stack yourself, and seeing exactly what happens at each stage. Nothing runs until you tell it to.

**Step 1.** Navigate into the `src/` directory. All commands assume you are inside `src/`, which is where the `Dockerfile`, `docker-compose.yml`, and application code live:

```bash
cd src
```

**Step 2.** Create your `.env` file if you have not already (see the "Before You Begin" section above):

```bash
cp .env.example .env
# Open .env in your editor and add your OpenAI and SerpAPI keys
```

**Step 3.** Build the Docker images. The `--no-cache` flag is optional on the first build, but recommended after any code changes to ensure Docker does not serve stale cached layers:

```bash
docker compose build --no-cache
```

This will take 1–3 minutes. Docker installs Python, Poetry, all project dependencies, the Phoenix tracing packages, and the OpenAI SDK inside the container. You do not need any of these installed on your host machine.

**Step 4.** Start both services in the background. The `-d` flag runs the containers detached so you get your terminal back:

```bash
docker compose up -d
```

**Step 5.** Verify the app is running:

```bash
curl http://localhost:8000/health
# Expected output: {"status":"ok"}
```

If you get a "connection refused" error, the container may still be starting. Wait 10–15 seconds and try again — the Dockerfile includes a health check that retries automatically.

When both services are up:

| Service | URL |
|---------|-----|
| TravelShaper (app + API) | [http://localhost:8000](http://localhost:8000) |
| Phoenix (tracing UI) | [http://localhost:6006](http://localhost:6006) |

Open [http://localhost:8000](http://localhost:8000) in your browser to use the trip planning form, or use curl to hit the API directly.

**Stopping the stack:**

```bash
docker compose down
```

**Rebuilding after code changes:**

```bash
docker compose down
docker compose build --no-cache
docker compose up -d
```

### Option B: Setup script (automated Docker path)

Use this if you want the same Docker Compose result as Option A but prefer a single command that handles everything — prerequisite checks, API key configuration, building, and starting. This is the fastest path from clone to running app.

**Step 1.** Navigate into the `src/` directory:

```bash
cd src
```

**Step 2.** Make the setup script executable. This is required the first time because Git does not always preserve file permissions:

```bash
chmod +x setup.sh
```

**Step 3.** Run the script:

```bash
./setup.sh
```

The script will walk you through each step interactively. Specifically, it will check that Docker and Docker Compose are installed (it detects both `docker compose` v2 and legacy `docker-compose` automatically), prompt you for your OpenAI and SerpAPI keys if no `.env` file exists yet, build the containers with `--no-cache`, start both services, and wait for the health check to pass before printing a summary.

When it finishes:

| Service | URL |
|---------|-----|
| TravelShaper (app + API) | [http://localhost:8000](http://localhost:8000) |
| Phoenix (tracing UI) | [http://localhost:6006](http://localhost:6006) |

**Stopping the stack** works the same as Option A:

```bash
docker compose down
```

### Option C: Local virtual environment

Use this if you prefer working outside Docker, want hot-reload during development, or need to debug with local tools. This path requires Python 3.11+ installed on your machine. A virtual environment is required — do not install into your system Python.

**Step 1.** Navigate into the `src/` directory:

```bash
cd src
```

**Step 2.** Create your `.env` file if you have not already:

```bash
cp .env.example .env
# Open .env in your editor and add your OpenAI and SerpAPI keys
```

**Step 3.** Create and activate a virtual environment. This isolates all project dependencies from your system Python:

```bash
python3 -m venv .venv
source .venv/bin/activate       # macOS / Linux
# .venv\Scripts\activate        # Windows
```

Your terminal prompt should now show `(.venv)` at the beginning. All subsequent commands assume the venv is active. If you open a new terminal window, you will need to run `source .venv/bin/activate` again.

**Step 4.** Install pip and Poetry inside the venv:

```bash
pip install --upgrade pip
pip install poetry==1.8.2
```

**Step 5.** Install project dependencies using Poetry:

```bash
poetry install -E dev
```

The `-E dev` flag includes test dependencies (pytest, httpx). This step takes 1–2 minutes on a fresh install.

**Step 6.** Install the OpenAI SDK. This is required but is not declared in `pyproject.toml` (it is installed via pip in the Dockerfile for the Docker paths). Without it, the server will crash on startup with `ModuleNotFoundError: No module named 'openai'`, because `api.py` imports it for the place and preference validation classifiers:

```bash
pip install openai
```

**Step 7.** Start the server. The `--reload` flag watches for file changes and restarts automatically, which is useful during development:

```bash
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

The app is now running at [http://localhost:8000](http://localhost:8000). Verify with:

```bash
curl http://localhost:8000/health
# Expected output: {"status":"ok"}
```

**Step 8 (optional). Enable Phoenix tracing.** The Phoenix packages have Python version constraints that conflict with Poetry's resolver on Python 3.11/3.12, so they must be installed directly with pip rather than through Poetry:

```bash
pip install arize-phoenix arize-phoenix-evals arize-phoenix-otel \
            openinference-instrumentation-langchain
```

You will also need to run the Phoenix server itself. The simplest way is Docker (even if you are running the app locally, Phoenix can still run in a container):

```bash
docker run -d -p 6006:6006 arizephoenix/phoenix:latest
```

The `-d` flag runs Phoenix detached. Traces will appear at [http://localhost:6006](http://localhost:6006) once you send a query to the app. If you skip this step, the app still works — it just silently skips tracing because the Phoenix instrumentation in `agent.py` is wrapped in a `try/except ImportError` block.

---

## Running Tests

Here is the thing about the tests that matters most: they are entirely self-contained. All 14 tests use mocked external calls. They do not need API keys, a running server, or Docker. They need only the right Python packages available to import.

The principle is simple: every command that runs Python code should execute inside either a container or an activated virtual environment. Never bare system Python.

### If you are using a local virtual environment

Run tests in the same venv where you installed dependencies:

```bash
cd src
source .venv/bin/activate
pytest tests/ -v
```

### If you are using Docker

The `docker-compose.yml` does not include a dedicated test service, so you run pytest inside the existing `travelshaper` container:

```bash
cd src
docker compose exec travelshaper pytest tests/ -v
```

If the container is not already running, start it first with `docker compose up -d`, then run the command above.

Expected output: **14 tests passing**.

---

## What It Does

TravelShaper takes a departure city, destination, dates, budget preference, and interests, then dispatches four tools to gather live data:

- **search_flights** — Google Flights via SerpAPI (prices, airlines, layovers)
- **search_hotels** — Google Hotels via SerpAPI (rates, ratings, amenities)
- **get_cultural_guide** — scoped Google search for etiquette, language, dress code
- **duckduckgo_search** — open web search for interests and gaps (no key needed)

It synthesises the results into a single briefing covering getting there, where to stay, cultural prep, and what to do — tailored to your budget mode and selected interests.

The agent runs two distinct voices depending on budget mode. "Save money" activates a Bourdain / Billy Dee Williams / Gladwell voice — muscular prose, insider knowledge, budget as philosophy. "Full experience" activates a Robin Leach / Pharrell / Rushdie voice — theatrical, joyful, literary. Both are instructed to include a markdown hyperlink for every named place, hotel, restaurant, and attraction.

Voice routing works by keyword matching on the assembled message string. The browser UI always includes the exact phrase "save money" or "full experience" in the message it constructs, so routing is reliable from the form. When using curl or the API directly, include one of these keywords in your message: `save money`, `budget`, `cheapest`, or `spend as little` to trigger the budget voice. Any message without these keywords defaults to the full-experience voice.

---

## API Endpoints

**`GET /`** — Browser UI. Open [http://localhost:8000](http://localhost:8000) in any browser. No curl required.

**`POST /chat`** — Synchronous chat. Returns the full JSON response when the agent finishes. Useful for curl, scripts, and tests.

The request body accepts four fields: `message` (required), plus optional `departure`, `destination`, and `preferences`. When `departure` and `destination` are provided, gpt-4o validates them as real places before the agent runs — correcting misspellings and rejecting fictional names. When they are omitted, place validation is skipped and the agent receives the message as-is.

```bash
# Full request with place validation:
curl -s -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Plan a trip from NYC to Rome, September, save money, food and history.",
    "departure": "NYC",
    "destination": "Rome"
  }' | python3 -m json.tool

# Minimal request (no place validation):
curl -s -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Plan a trip from NYC to Rome, September, save money, food and history."}' \
  | python3 -m json.tool
```

**`POST /chat/stream`** — SSE streaming. Same request body as `/chat`. The browser UI uses this to show real-time status updates as each tool executes. Emits `status`, `place_corrected`, `place_error`, `validation_error`, `done`, and `error` event types.

**`GET /health`** — Returns `{"status": "ok"}`. Used by Docker's health check and useful for verifying the server is alive.

---

## Running Traces and Evaluations

Traces are generated by running real queries against the live API. Do this after starting the full Docker Compose stack (or after starting both the app and Phoenix in venv mode).

### Generate traces

The trace script must be run from within the `src/` directory, since it calls Python modules with relative imports:

```bash
cd src
chmod +x run_traces.sh
./run_traces.sh
```

This fires 11 queries covering every tool combination, both budget voices, auto-correction, vague inputs, past-date error handling, and edge cases. All dates in the queries are computed dynamically relative to today, so the script never goes stale. Each query generates a trace visible in Phoenix at [http://localhost:6006](http://localhost:6006).

You can optionally pass a custom base URL:

```bash
./run_traces.sh http://localhost:8000
```

### Run evaluations

```bash
cd src
python -m evaluations.run_evals
```

This runs three LLM-as-judge metrics against the collected traces:

- **User Frustration** — uses Phoenix's built-in `USER_FRUSTRATION_PROMPT_TEMPLATE` (the `frustration.py` file in `evaluations/metrics/` contains a custom reference prompt but it is not used in production)
- **Tool Usage Correctness** — custom LLM-as-judge prompt
- **Answer Completeness** — custom LLM-as-judge prompt with scope awareness

Results are logged back to Phoenix and visible in the Evaluations tab. A `frustrated_interactions` dataset is automatically created from any traces flagged as frustrated.

See [docs/trace-queries.md](src/docs/trace-queries.md) for the full query list and [docs/evaluation-prompts.md](src/docs/evaluation-prompts.md) for evaluation methodology.

---

## Project Structure

```
src/
├── api.py                          # FastAPI server — /chat, /chat/stream, /health, static UI
├── agent.py                        # LangGraph agent — dual system prompts, voice routing
├── static/index.html               # Browser UI — Bebas Neue / Cormorant Garamond / DM Sans
├── tools/
│   ├── __init__.py                 # serpapi_request() helper
│   ├── flights.py                  # search_flights (SerpAPI Google Flights)
│   ├── hotels.py                   # search_hotels (SerpAPI Google Hotels)
│   └── cultural_guide.py          # get_cultural_guide (scoped Google search)
├── evaluations/
│   ├── run_evals.py                # Phoenix evaluation runner (3 metrics)
│   └── metrics/
│       ├── frustration.py          # Reference frustration prompt (production uses Phoenix built-in)
│       ├── answer_completeness.py  # ANSWER_COMPLETENESS_PROMPT
│       └── tool_correctness.py     # TOOL_CORRECTNESS_PROMPT
├── scripts/
│   └── export_spans.py             # Export Phoenix spans to CSV
├── tests/
│   ├── test_tools.py               # 4 tool tests
│   ├── test_agent.py               # 2 agent graph tests
│   └── test_api.py                 # 8 endpoint + validation tests
├── docs/
│   ├── ARCHITECTURE.md
│   ├── PRD.md
│   ├── system-prompt-spec.md
│   ├── test-specification.md
│   ├── docker-spec.md
│   ├── evaluation-prompts.md
│   ├── trace-queries.md
│   ├── implementation-plan.md
│   └── presentation-outline.md
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── run_traces.sh                   # 11 trace queries + span export
├── setup.sh                        # One-command setup (Docker path)
├── RUNNING.md                      # Extended setup guide (some sections outdated — prefer this README)
└── CHANGELOG.md
```

---

## Documentation

The `docs/` directory contains the full design record for the project. Each document covers a specific dimension of the system and is written to be self-contained — you can read any one of them without needing the others first.

| Document | Description |
|----------|-------------|
| [ARCHITECTURE.md](src/docs/ARCHITECTURE.md) | Software architecture document covering component design, data flow, LLM decision making, system prompt rationale, tool design patterns, input validation architecture, deployment topology, and the decision log for every major technical choice. The most comprehensive single document in the project. |
| [PRD.md](src/docs/PRD.md) | Product requirements document defining the target user, jobs to be done, functional and non-functional requirements, scope boundaries, API contract, evaluation criteria, and the future roadmap. Start here if you want to understand *what* TravelShaper is and *why* it makes the choices it does. |
| [system-prompt-spec.md](src/docs/system-prompt-spec.md) | Specification for the two system prompts (save-money and full-experience) including the voice definitions, routing logic, shared structural requirements, tool usage instructions, and the design reasoning behind using two prompts instead of one. |
| [test-specification.md](src/docs/test-specification.md) | Complete specification for all 14 tests across three test files, including mock path rules, exact mock data shapes, and assertion criteria for every test case. |
| [docker-spec.md](src/docs/docker-spec.md) | Dockerfile and docker-compose.yml with line-by-line commentary explaining why each decision was made — including why Phoenix packages are installed via pip, why the full `arize-phoenix` server is excluded from the app container, and the `temperature` model_kwargs workaround. |
| [evaluation-prompts.md](src/docs/evaluation-prompts.md) | The exact prompts used in the Phoenix evaluation pipeline for all three metrics (user frustration, tool usage correctness, answer completeness), with rationale for why each metric was chosen based on specific failure modes observed during development. |
| [trace-queries.md](src/docs/trace-queries.md) | All 11 trace queries with their expected tool dispatch, voice routing, and a coverage matrix showing which tools, budget modes, and edge cases each query exercises. |
| [implementation-plan.md](src/docs/implementation-plan.md) | Step-by-step build plan used during development, with acceptance criteria for each step. Useful for understanding the order in which the system was assembled. |
| [presentation-outline.md](src/docs/presentation-outline.md) | 20–25 minute presentation outline covering architecture, observability (OpenTelemetry / OpenInference concepts), evaluation methodology, deployment design, and a live demo script with both browser UI and curl options. |

---

## Architecture

The agent uses a standard LangGraph ReAct loop. The graph topology is unchanged from the starter app — the extension adds tools, not complexity.

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

For the full architecture narrative — component design, data flow, LLM decision making, prompt design rationale, deployment topology, and security considerations — see [docs/ARCHITECTURE.md](src/docs/ARCHITECTURE.md).

---

## Design Decisions

There is a pattern in how TravelShaper makes its choices, and the pattern is worth naming: every decision optimises for the shortest path to a working demo that is still architecturally honest.

- **Single HTML file UI** — no npm, no build step; served directly by FastAPI alongside the REST API. The constraint produced a better result: one file that loads instantly and has zero deployment friction.
- **SerpAPI as single data provider** — one key powers flights, hotels, and scoped web searches with structured JSON. The alternative was three separate APIs with three approval processes.
- **Cultural guide as a first-class tool** — etiquette and language prep is what separates a useful travel briefing from a price comparison. Most travel tools skip this entirely.
- **DuckDuckGo as fallback** — covers general queries without requiring an additional API key. Already present in the starter code.
- **Two system prompts, not one** — a single prompt with conditional voice instructions produces blended, inconsistent output. Two separate prompts let the model commit fully to one register.
- **Place validation before agent** — gpt-4o catches misspellings and rejects fictional places before the expensive agent runs. A 1-second validation call saves 30 seconds of wasted agent time. Validation only runs when `departure` and `destination` fields are explicitly provided in the request body.
- **Single-turn design** — each request is independent. This is a deliberate product boundary, not a gap.
- **`openai` SDK installed via pip, not Poetry** — the OpenAI SDK is used only by the validation classifiers in `api.py`. It is installed via pip in the Dockerfile (and must be installed manually in venv mode) rather than declared in `pyproject.toml`, to keep the Poetry dependency graph clean alongside the Phoenix packages that also require special handling.

---

## Known Limitations

- Planning assistant only — recommends options but does not book.
- Flight and hotel prices reflect time of search, not guaranteed availability.
- Cultural guidance is practical advice based on common norms, not absolute rules.
- Designed for English-speaking American travellers; guidance assumes U.S. norms as baseline.
- Single-turn: no conversation memory between requests.
- SerpAPI free tier supports ~60–125 full briefings per month.
- Voice routing uses keyword matching — the budget voice triggers on `save money`, `budget`, `cheapest`, or `spend as little` appearing in the message. Synonyms like "frugal" or "inexpensive" will not trigger it and will default to the full-experience voice.

---

## Troubleshooting

**Server won't start** — confirm your `.env` exists with valid keys. If running locally, confirm the venv is activated, you have run `poetry install -E dev`, and you have installed the `openai` package with `pip install openai`. If running Docker, try `docker compose build --no-cache`.

**Auth error from OpenAI or SerpAPI** — check your `.env` file. Verify the SerpAPI key at [serpapi.com/manage-api-key](https://serpapi.com/manage-api-key). Verify the OpenAI key at [platform.openai.com/api-keys](https://platform.openai.com/api-keys).

**`ModuleNotFoundError: No module named 'openai'`** — the `openai` SDK is not in `pyproject.toml`. In venv mode, install it with `pip install openai`. In Docker mode, it is pre-installed in the container via the Dockerfile.

**Tests fail with ModuleNotFoundError** — you are running pytest outside of an isolated environment. Either activate your venv (`source .venv/bin/activate`) or run tests inside the Docker container (`docker compose exec travelshaper pytest tests/ -v`). Confirm that `pyproject.toml` contains `[tool.pytest.ini_options]` with `pythonpath = ["."]`.

**Poor or incomplete results** — include origin, destination, dates, and budget in your request. Check SerpAPI usage (free tier: 250 searches/month). Try well-known destinations first.

**Missing traces in Phoenix** — confirm Phoenix is running. If using Docker Compose, both services start together. If using a venv, you need to start Phoenix separately. Run at least one `/chat` query, then refresh the Phoenix UI at [http://localhost:6006](http://localhost:6006).

**`ModuleNotFoundError: No module named 'phoenix'`** — the Phoenix packages are not installed. In venv mode, install them with pip (see the venv setup section above). In Docker mode, they are pre-installed in the container.

**`run_traces.sh` fails with import errors** — make sure you are running the script from inside the `src/` directory. The script calls `python3 -m scripts.export_spans` and `python3 -m evaluations.run_evals`, which require `src/` as the working directory for Python's module resolution to work.

---

MIT License — see [LICENSE](LICENSE).
