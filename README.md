# TravelShaper

**AI travel planning assistant** — fill in a form, get an opinionated briefing with flights, hotels, cultural prep, and activity picks.

Every recommendation includes a hyperlink and an explanation of *why* it was chosen. The agent runs two distinct voices depending on budget mode, and the entire request flow is instrumented with configurable OpenTelemetry tracing for observability.

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

## Before You Begin

TravelShaper needs two API keys: an OpenAI key (powers the agent and validation classifiers) and a SerpAPI key (powers flight, hotel, and cultural guide searches). Everything else lives inside the project.

**Where to get keys:**

- **OpenAI** (required) — [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
- **SerpAPI** (required for flights, hotels, cultural guide) — [serpapi.com/manage-api-key](https://serpapi.com/manage-api-key). Free tier: 250 searches/month (~60–125 full briefings). Without this key, the agent falls back to DuckDuckGo for everything — functional, but limited.

You will create a `.env` file with these keys during setup. The `.env` file is listed in `.gitignore` and will never be committed.

---

## Prerequisites

You need **Docker** (with Docker Compose) to run the app, and **Python 3.11+** to run tests and traces locally.

**macOS:** Install Docker Desktop for Mac from [docs.docker.com/desktop/install/mac-install](https://docs.docker.com/desktop/install/mac-install/). Python 3.11+ ships with macOS or can be installed via [python.org](https://www.python.org/downloads/) or `brew install python`.

**Windows 10/11:** Install Docker Desktop for Windows from [docs.docker.com/desktop/install/windows-install](https://docs.docker.com/desktop/install/windows-install/) with WSL 2 backend enabled. Install Python 3.11+ from [python.org/downloads](https://www.python.org/downloads/) — check "Add Python to PATH" during install.

**Linux (Desktop):** Install Docker Engine and the Docker Compose plugin from [docs.docker.com/engine/install](https://docs.docker.com/engine/install/). Python 3.11+ ships with most distributions. On Ubuntu/Debian, if missing: `sudo apt install python3 python3-venv python3-pip`.

Verify both are available:

```
docker compose version
python3 --version
```

On Windows, use `python --version` instead of `python3 --version`. If `python` is not recognized, the installer's "Add to PATH" checkbox was likely not checked — reinstall or add it manually.

If `docker compose` (with a space) does not work but `docker-compose` (hyphenated) does, you have the legacy v1 CLI — that works too, just substitute `docker-compose` wherever you see `docker compose` below.

On Linux, if you get a permission error from Docker, either prefix commands with `sudo` or add yourself to the docker group: `sudo usermod -aG docker $USER` (requires logout/login to take effect).

---

## Quick Start with Make

If you have Make installed, the entire workflow can be driven from `src/`:

```bash
cd src
cp .env.example .env              # add your API keys
make help                          # show all available targets
make demo                          # full pipeline: build, test, traces, evaluate, export
```

Individual targets: `make up`, `make test`, `make traces`, `make evals`, `make export`, `make down`, `make clean`.

---
# DEMO WITH DOCKER 
##  Start the App

All commands in this section are run from inside the `src/` directory.

**Step 1.** Create your `.env` file:

On macOS or Linux:

```
cd src
cp .env.example .env
```

On Windows:

```
cd src
copy .env.example .env
```

Open `.env` in any text editor and add your OpenAI and SerpAPI keys. Optionally configure the telemetry destination:

```
OPENAI_API_KEY=sk-...
SERPAPI_API_KEY=...

# Telemetry routing — controls where traces are sent
# Options: phoenix | arize | otlp | both | all | none
OTEL_DESTINATION=phoenix

# Project name in Phoenix/Arize dashboards
OTEL_PROJECT_NAME=travelshaper

# Local Phoenix (default)
PHOENIX_ENDPOINT=http://localhost:6006/v1/traces

# Arize Cloud (optional — only needed if OTEL_DESTINATION=arize or both)
# ARIZE_API_KEY=
# ARIZE_SPACE_ID=

# Generic OTLP (optional — only needed if OTEL_DESTINATION=otlp or all)
# OTLP_PROTOCOL=http                        # "http" (default) or "grpc"
# OTLP_ENDPOINT=http://localhost:4318/v1/traces  # http (port 4318, path required)
# OTLP_ENDPOINT=http://localhost:4317            # grpc (port 4317, no path)
# OTLP_HEADERS=                              # comma-separated key=value pairs
```

**Step 2.** Build and start the stack:

```
docker compose --profile phoenix up -d --build
```

Or use the Makefile, which reads `OTEL_DESTINATION` from `.env` and starts Phoenix only when needed:

```
make up
```

This builds the TravelShaper container with all dependencies and starts both the app and Phoenix (if the profile is active). Takes 1–3 minutes on first build.

**Step 3.** Verify both containers are running:

```
docker ps
```

You should see two containers — one on port 8000 (TravelShaper) and one on port 6006 (Phoenix), both with `Up` status.

When the stack is running:

| Service | URL |
|---------|-----|
| TravelShaper (app + API) | [http://localhost:8000](http://localhost:8000) |
| Phoenix (tracing UI) | [http://localhost:6006](http://localhost:6006) |

To stop the stack: `docker compose down`. To rebuild after code changes: `docker compose down && docker compose up -d --build`.

---

## Quick Reference

Once the Docker stack is running and your venv is set up, these are the things you will do most often.

### Access the browser UI

Open [http://localhost:8000](http://localhost:8000) in any browser. The form collects departure, destination, dates, budget mode, interests, and optional preferences. Click "Plan my trip →" to get a full briefing streamed in real time. No login, no setup — the browser talks directly to the same API that curl uses.

### Access Phoenix (tracing UI)

Open [http://localhost:6006](http://localhost:6006) in any browser. Every request to `/chat` or `/chat/stream` generates a trace. Click into any trace to see the full tool call chain — which tools were called, what arguments were passed, how long each step took, and the agent's final response. Phoenix runs as a separate container started by Docker Compose and requires no additional setup.

### Test the API with a single curl request

```
curl -s -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I am planning a trip departing from San Francisco, CA (please identify the nearest major international airport). Destination: Tokyo, Japan. Departure: 2026-06-15. Return: 2026-06-29 (2 weeks). Budget preference: save money. Interests: food and dining, photography. Please provide a complete travel briefing with hyperlinks for every named place, restaurant, hotel, and attraction.",
    "departure": "San Francisco, CA",
    "destination": "Tokyo, Japan"
  }' | python3 -m json.tool
```

On Windows, replace `python3` with `python` and use double quotes for the outer shell quoting (or run the command inside WSL or Git Bash). The response is a JSON object with a `response` field containing the full travel briefing in markdown.

To verify the server is alive without triggering a full agent run:

```
curl http://localhost:8000/health
```

Expected output: `{"status":"ok"}`

---

## Set Up Python for Traces and Evaluations

Traces and evaluations both run on your local machine, outside Docker. They use a Python virtual environment inside `src/`. You only need to set this up once.

**Step 1.** Open a second terminal and navigate to `src/`:

```
cd src
```

**Step 2.** Create the virtual environment:

On macOS or Linux:

```
python3 -m venv .venv
```

On Windows:

```
python -m venv .venv
```

**Step 3.** Activate the virtual environment:

On macOS or Linux:

```
source .venv/bin/activate
```

On Windows (Command Prompt):

```
.venv\Scripts\activate.bat
```

On Windows (PowerShell):

```
.venv\Scripts\Activate.ps1
```

If PowerShell blocks the script with a security error, run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` first, then try again.

**Step 4.** Install dependencies:

```
pip install requests arize-phoenix arize-phoenix-evals pandas openai
```

---

## Generate Traces and Run Evaluations

This is the core observability workflow: generate traces by sending real queries to the agent, then score those traces with three LLM-as-judge metrics.

Make sure you are in the `src/` directory with the venv active and the Docker stack is running.

### Generate traces

```
python -m traces.run_traces
```

This fires 11 real queries against the server at `localhost:8000`, covering every tool combination, both budget voices, auto-correction, vague inputs, past-date error handling, and edge cases. All dates are computed dynamically relative to today so the script never goes stale.

### Run evaluations

Once traces exist in Phoenix, score them:

```
python -m evaluations.run_evals
```

The script connects to Phoenix at `localhost:6006`, pulls the most recent traces, groups all spans by trace ID to identify the root span (user input + agent output) and child spans (actual tool calls), and scores each trace against three metrics.

### What the three metrics measure

**User Frustration** detects responses that are technically correct but experientially poor.

**Tool Usage Correctness** evaluates whether the agent called the right tools for the request, using actual tool calls extracted from trace child spans.

**Answer Completeness** checks whether the response covers everything the user asked for, with scope awareness.

For the full evaluation prompt text and design rationale, see [docs/evaluation-prompts.md](src/docs/evaluation-prompts.md).

---
# HOW TO RUN THE APP IN PYTHON FOR DEVELOPMENT & TESTING 

## Run Everything Locally (Python venv — no Docker)

This section covers running the server, tests, traces, and evaluations entirely from a local Python virtual environment.

**Avoid port binding conflicts: Make sure that you don't have docker running containers before you deploy the app using python**

### 1. Create and activate the virtual environment

All commands assume you are inside the `src/` directory.

**macOS / Linux:**

```bash
cd src
python3 -m venv .venv
source .venv/bin/activate
```

**Windows (Command Prompt):**

```bash
cd src
python -m venv .venv
.venv\Scripts\activate.bat
```

### 2. Install all dependencies

```bash
pip install --upgrade pip
pip install poetry==1.8.2
poetry install --no-interaction --no-ansi --no-root -E dev
pip install arize-phoenix arize-phoenix-evals arize-phoenix-otel \
            openinference-instrumentation-langchain openai pandas requests
```

### 3. Configure environment variables

```bash
cp .env.example .env
```

Open `.env` and add your keys:

```
OPENAI_API_KEY=sk-...
SERPAPI_API_KEY=...
OTEL_DESTINATION=phoenix
OTEL_PROJECT_NAME=travelshaper
PHOENIX_ENDPOINT=http://localhost:6006/v1/traces
```

Tests do **not** need API keys — all external calls are mocked.

### 4. Run all 31 tests

```bash
pytest tests/ -v
```

Expected output:

```
tests/test_tools.py::test_search_flights_formats_results          PASSED
tests/test_tools.py::test_search_flights_handles_empty_results    PASSED
tests/test_tools.py::test_search_hotels_formats_results           PASSED
tests/test_tools.py::test_cultural_guide_returns_guidance         PASSED
tests/test_agent.py::test_agent_graph_has_expected_nodes          PASSED
tests/test_agent.py::test_agent_tools_registered                  PASSED
tests/test_agent.py::test_cultural_guide_tool_has_routing_docstring PASSED
tests/test_agent.py::test_voice_routing_selects_correct_prompt    PASSED
tests/test_agent.py::test_llm_call_uses_dispatch_prompt_before_tools PASSED
tests/test_agent.py::test_llm_call_uses_synthesis_prompt_after_tools PASSED
tests/test_api.py::test_health_endpoint                           PASSED
tests/test_api.py::test_chat_endpoint_accepts_message             PASSED
tests/test_api.py::test_chat_accepts_valid_preferences            PASSED
tests/test_api.py::test_chat_rejects_invalid_preferences          PASSED
tests/test_api.py::test_chat_skips_validation_for_empty_preferences PASSED
tests/test_api.py::test_chat_accepts_valid_places                 PASSED
tests/test_api.py::test_chat_rejects_invalid_place                PASSED
tests/test_api.py::test_chat_auto_corrects_misspelled_place       PASSED
tests/test_otel_routing.py::test_phoenix_destination_creates_one_exporter  PASSED
tests/test_otel_routing.py::test_phoenix_api_key_added_to_headers_when_present PASSED
tests/test_otel_routing.py::test_phoenix_no_api_key_sends_no_auth_header   PASSED
tests/test_otel_routing.py::test_arize_destination_calls_arize_register    PASSED
tests/test_otel_routing.py::test_arize_missing_credentials_skips_silently  PASSED
tests/test_otel_routing.py::test_both_destination_uses_arize_and_phoenix   PASSED
tests/test_otel_routing.py::test_otlp_destination_creates_one_exporter     PASSED
tests/test_otel_routing.py::test_otlp_headers_parsed_and_passed            PASSED
tests/test_otel_routing.py::test_otlp_missing_endpoint_skips_silently      PASSED
tests/test_otel_routing.py::test_all_destination_creates_all_exporters     PASSED
tests/test_otel_routing.py::test_otlp_grpc_protocol_uses_grpc_exporter    PASSED
tests/test_otel_routing.py::test_otlp_grpc_headers_passed_correctly        PASSED
tests/test_otel_routing.py::test_otlp_grpc_fallback_when_package_missing   PASSED
tests/test_otel_routing.py::test_otlp_http_protocol_explicit               PASSED
tests/test_otel_routing.py::test_none_destination_creates_no_exporters     PASSED
tests/test_otel_routing.py::test_project_name_sets_service_name            PASSED
tests/test_otel_routing.py::test_default_project_name_is_travelshaper      PASSED

31 passed
```

You can also run individual test files:

```bash
pytest tests/test_tools.py -v          # 4 tool tests
pytest tests/test_agent.py -v          # 6 agent graph + routing + dispatch tests
pytest tests/test_api.py -v            # 8 API + validation tests
pytest tests/test_otel_routing.py -v   # 17 OTel routing tests
```

A deprecation warning about `temperature` in `model_kwargs` is expected and harmless.

### 5. Start Phoenix (tracing UI)

Phoenix needs to be running before you start the server if you want traces.

**Option A — Docker (recommended):**

```bash
docker run -d -p 6006:6006 --name phoenix arizephoenix/phoenix:latest
```

**Option B — Python (in a separate terminal):**

```bash
cd src && source .venv/bin/activate && phoenix serve
```

### 6. Start the TravelShaper server

```bash
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

### 7. Generate traces

```bash
python -m traces.run_traces              # all 11 queries
python -m traces.run_traces 3            # first 3 only
```

### 8. Run evaluations

```bash
python -m evaluations.run_evals
```

---

## Project Structure

```
src/
├── api.py                          # FastAPI server — /chat, /chat/stream, /health, static UI
├── agent.py                        # LangGraph agent — three system prompts, voice routing, dispatch phase
├── otel_routing.py                 # OTel config routing (OTEL_DESTINATION in .env)
├── static/index.html               # Browser UI — Bebas Neue / Cormorant Garamond / DM Sans
├── tools/
│   ├── __init__.py                 # serpapi_request() helper
│   ├── flights.py                  # search_flights (SerpAPI Google Flights)
│   ├── hotels.py                   # search_hotels (SerpAPI Google Hotels)
│   └── cultural_guide.py          # get_cultural_guide (scoped Google search)
├── evaluations/
│   ├── __init__.py
│   ├── run_evals.py                # Evaluation runner — 3 LLM-as-judge metrics, trace-level
│   ├── export_spans.py             # Export Phoenix spans to CSV
│   ├── README.md                   # Evaluation methodology and usage
│   └── metrics/
│       ├── __init__.py
│       ├── frustration.py          # USER_FRUSTRATION_PROMPT (reference)
│       ├── answer_completeness.py  # ANSWER_COMPLETENESS_PROMPT
│       └── tool_correctness.py     # TOOL_CORRECTNESS_PROMPT
├── traces/
│   ├── __init__.py
│   ├── run_traces.py               # Trace generator — 11 queries, cross-platform Python
│   └── README.md                   # Trace query documentation and usage
├── tests/
│   ├── test_tools.py               # 4 tool tests
│   ├── test_agent.py               # 6 agent graph, routing + dispatch tests
│   ├── test_api.py                 # 8 API + validation tests
│   └── test_otel_routing.py        # 17 OTel routing tests
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
├── Makefile                        # Build/test/demo automation
├── pyproject.toml
├── RUNNING.md
└── CHANGELOG.md
```

---

## Documentation

The `docs/` directory contains the full design record for the project. Each document covers a specific dimension of the system and is written to be self-contained.

| Document | Description |
|----------|-------------|
| [ARCHITECTURE.md](src/docs/ARCHITECTURE.md) | Software architecture document covering component design, data flow, LLM decision making, system prompt rationale, tool design patterns, input validation architecture, OTel routing, deployment topology, and the decision log. |
| [PRD.md](src/docs/PRD.md) | Product requirements document defining the target user, jobs to be done, functional and non-functional requirements, scope boundaries, API contract, and evaluation criteria. |
| [system-prompt-spec.md](src/docs/system-prompt-spec.md) | Specification for the three system prompts (dispatch, save-money, full-experience) including voice definitions, phase-based routing logic, and design reasoning. |
| [test-specification.md](src/docs/test-specification.md) | Complete specification for all 26 tests across four test files, including mock path rules, exact mock data shapes, and assertion criteria. |
| [docker-spec.md](src/docs/docker-spec.md) | Dockerfile and docker-compose.yml with line-by-line commentary, including why OTel packages are installed via pip and why Phoenix uses Docker profiles. |
| [evaluation-prompts.md](src/docs/evaluation-prompts.md) | The exact prompts used in the Phoenix evaluation pipeline for all three metrics, with rationale for why each metric was chosen. |
| [trace-queries.md](src/docs/trace-queries.md) | All 11 trace queries with their expected tool dispatch, voice routing, and a coverage matrix. |
| [implementation-plan.md](src/docs/implementation-plan.md) | Step-by-step build plan used during development. |
| [presentation-outline.md](src/docs/presentation-outline.md) | 20–25 minute presentation outline. |

---

## Architecture

The agent uses a standard LangGraph ReAct loop. The graph topology is unchanged from the starter app — the extension adds tools, not complexity. Token usage is optimized with a two-phase prompt strategy: a minimal dispatch prompt before tools run, and a full voice prompt during synthesis.

```
Browser / curl
  │
  ├── POST /chat/stream  (SSE — browser UI)
  └── POST /chat         (sync — curl / tests)
           │
           ▼
     Place + Preference Validation (gpt-4o-mini)
           │
           ▼
     LangGraph Agent
           │
     get_system_prompt(message, phase)
           ├── phase="dispatch" → DISPATCH_PROMPT (tool selection only)
           └── phase="synthesis"
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
     tool_node → llm_call (synthesis with voice prompt)
           │
     SSE stream / JSON response → browser / client
```

For the full architecture narrative, see [docs/ARCHITECTURE.md](src/docs/ARCHITECTURE.md).

---

## Telemetry Configuration

TravelShaper uses configurable OTel routing controlled by `OTEL_DESTINATION` in your `.env` file. This determines where traces are sent without any code changes.

| Value | Destination | Required env vars |
|-------|-------------|-------------------|
| `phoenix` (default) | Local Phoenix or Phoenix Cloud | `PHOENIX_ENDPOINT`; optionally `PHOENIX_API_KEY` for Cloud |
| `arize` | Arize Cloud | `ARIZE_API_KEY`, `ARIZE_SPACE_ID` |
| `otlp` | Any OTLP-compatible backend (Jaeger, Tempo, Honeycomb, etc.) | `OTLP_ENDPOINT`; optionally `OTLP_PROTOCOL`, `OTLP_HEADERS` |
| `both` | Phoenix and Arize simultaneously | All Phoenix + Arize vars above |
| `all` | Phoenix, Arize, and generic OTLP simultaneously | All of the above |
| `none` | Disabled — no traces sent | None |

Set `OTEL_PROJECT_NAME` to control the project name in Phoenix/Arize dashboards (default: `travelshaper`).

**Generic OTLP protocol selection:** When using `otlp` or `all`, set `OTLP_PROTOCOL` to `http` (default) or `grpc`. HTTP uses port 4318 with a `/v1/traces` path suffix; gRPC uses port 4317 with no path. If the gRPC package is not installed, the exporter falls back to HTTP with a warning.

The routing module (`otel_routing.py`) reads these variables at startup and configures a `TracerProvider`. For Phoenix, it uses a manual `TracerProvider` with an `OTLPSpanExporter`. For Arize, it uses the official `arize.otel.register()` SDK, which handles endpoints, authentication, and project naming internally. For `both`, it starts with the Arize provider and adds a Phoenix exporter to it. For `otlp`, it builds an HTTP or gRPC exporter based on `OTLP_PROTOCOL`. The `TracerProvider` resource `service.name` is set from `OTEL_PROJECT_NAME` (default: `travelshaper`). If credentials are missing for a destination, it logs a warning and skips that destination gracefully.

---

## Design Decisions

There is a pattern in how TravelShaper makes its choices, and the pattern is worth naming: every decision optimises for the shortest path to a working demo that is still architecturally honest.

- **Single HTML file UI** — no npm, no build step; served directly by FastAPI alongside the REST API.
- **SerpAPI as single data provider** — one key powers flights, hotels, and scoped web searches with structured JSON.
- **Cultural guide as a first-class tool** — etiquette and language prep is what separates a useful travel briefing from a price comparison.
- **DuckDuckGo as fallback** — covers general queries without requiring an additional API key.
- **Two voice prompts, not one** — a single prompt with conditional voice instructions produces blended, inconsistent output.
- **Dispatch prompt for tool selection** — sending the full voice prompt before tools run wastes ~300–600 tokens on instructions the model cannot act on yet.
- **Place validation before agent** — gpt-4o-mini catches misspellings and rejects fictional places before the expensive agent runs.
- **gpt-4o-mini for validation** — faster and cheaper than gpt-4o for simple classification tasks; sufficient accuracy for binary decisions.
- **Single-turn design** — each request is independent. This is a deliberate product boundary, not a gap.
- **Configurable OTel routing** — `OTEL_DESTINATION` in `.env` controls where traces go, supporting local Phoenix, Arize Cloud, any OTLP-compatible backend (via HTTP or gRPC), all three simultaneously, or none.

---

## Security Considerations and Input Validation

TravelShaper validates user input in three stages before the agent processes a request.

### The validation pipeline

The first stage is Pydantic schema validation. The second stage is place validation — `validate_place()` sends each place name to gpt-4o-mini with a structured prompt. The third stage is preferences validation — `validate_preferences()` sends the text to gpt-4o-mini with a safety classifier prompt.

Place validation is designed to fail open (validation outage does not block the user). Preference validation fails closed (unvalidated text is not passed to the agent).

### What is not protected

The `message` field itself is not validated for content safety. There is no rate limiting. There is no input sanitization before tool dispatch.

---

## Known Limitations

- Planning assistant only — recommends options but does not book.
- Flight and hotel prices reflect time of search, not guaranteed availability.
- Cultural guidance is practical advice based on common norms, not absolute rules.
- Designed for English-speaking American travellers; guidance assumes U.S. norms as baseline.
- Single-turn: no conversation memory between requests.
- SerpAPI free tier supports ~60–125 full briefings per month.
- Voice routing uses keyword matching — the budget voice triggers on `save money`, `budget`, `cheapest`, or `spend as little`.

---

## Troubleshooting

### Checking Docker status

```
docker ps                # running containers
docker ps -a             # including stopped
docker compose logs --tail 100 travelshaper
docker compose logs --tail 100 phoenix
```

### Common issues

**Server won't start** — confirm your `.env` exists with valid keys. Check `docker compose logs --tail 50 travelshaper`.

**Auth error from OpenAI or SerpAPI** — check your `.env` file.

**Tests fail with ModuleNotFoundError** — ensure venv is active (`(.venv)` in prompt). Run `poetry install -E dev`. If the missing module is `openai`, run `pip install openai`.

**Trace generator fails with `ConnectionError`** — the TravelShaper server is not running.

**Missing traces in Phoenix** — confirm Phoenix is running (`docker ps`). Run at least one `/chat` query.

**Phoenix not starting** — if `OTEL_DESTINATION` is set to `arize` or `none`, Phoenix won't start (by design). Set it to `phoenix` or `both` and use `make up` or `docker compose --profile phoenix up -d`.

---

MIT License — see [LICENSE](LICENSE).
