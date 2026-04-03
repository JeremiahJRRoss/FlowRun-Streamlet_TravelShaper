# System Prompt Specification — TravelShaper Agent

**Version:** 2.1 (v0.3.2)

TravelShaper uses **three system prompts** — two voice prompts for synthesis and one
minimal dispatch prompt for tool selection. All are defined as constants in `agent.py`.

The routing function `get_system_prompt(message, phase)` selects the appropriate prompt
based on the current phase and the user's budget preference. `llm_call()` calls this
function on every invocation, determining the phase from the message history.

---

## Phase-based prompt selection (v0.3.2)

The agent graph calls `llm_call` at least twice per request: once before tools run
(dispatch phase) and once after tools return results (synthesis phase). Each phase
uses a different prompt to reduce token usage and improve focus.

**Dispatch phase:** The LLM receives only `DISPATCH_PROMPT` (~150 tokens) — a minimal
instruction set focused on deciding which tools to call. No voice instructions, no
formatting rules, no section structure. This saves ~300–600 tokens per full-trip request
compared to sending the full voice prompt before any tools have run.

**Synthesis phase:** The LLM receives the appropriate voice prompt (`SYSTEM_PROMPT_SAVE_MONEY`
or `SYSTEM_PROMPT_FULL_EXPERIENCE`), selected by budget keyword matching.

### Phase detection in `llm_call`

```python
last_message = state["messages"][-1] if state["messages"] else None
is_synthesis = isinstance(last_message, ToolMessage)
phase = "synthesis" if is_synthesis else "dispatch"
```

If the last message in the graph state is a `ToolMessage`, tools have just returned
results and we are in the synthesis phase. Otherwise (the last message is a `HumanMessage`
or an `AIMessage` without tool results), we are in the dispatch phase.

---

## Routing logic

```python
def get_system_prompt(message: str, phase: str = "synthesis") -> str:
    """Return the correct system prompt based on phase and budget preference.

    phase="dispatch"  — minimal tool-routing prompt, sent on first llm_call
                        before any tools have run
    phase="synthesis" — full voice + structure prompt, sent when writing
                        the final response after tools have returned results
    """
    if phase == "dispatch":
        return DISPATCH_PROMPT
    lower = message.lower()
    if "save money" in lower or "budget" in lower \
       or "cheapest" in lower or "spend as little" in lower:
        return SYSTEM_PROMPT_SAVE_MONEY
    return SYSTEM_PROMPT_FULL_EXPERIENCE
```

Default (no budget keyword detected): `SYSTEM_PROMPT_FULL_EXPERIENCE`.
Dispatch phase always returns `DISPATCH_PROMPT` regardless of budget keywords.

---

## Prompt 0: DISPATCH_PROMPT (v0.3.2)

A minimal prompt (~150 tokens) that tells the LLM only how to decide which tools to call.

**Key instructions:**
- Convert city names to IATA codes for `search_flights`
- Set `sort_by=3` for budget, `sort_by=13` for full experience in `search_hotels`
- Call `get_cultural_guide` for every international destination
- Use `duckduckgo_search` for interest-based discovery
- Call all relevant tools in a single turn
- Do not respond to the user yet (response comes in synthesis phase)

**Why a separate dispatch prompt?**
The full voice prompts are ~200+ tokens each and contain prose style instructions,
section formatting rules, and closing-line requirements that are irrelevant during
tool selection. Sending a minimal dispatch prompt on the first `llm_call` reduces
input tokens and prevents the model from prematurely generating prose before tools
have returned data.

---

## Prompt 1: SYSTEM_PROMPT_SAVE_MONEY

**Voice:** Anthony Bourdain's honesty and curiosity + Billy Dee Williams' effortless cool
+ Malcolm Gladwell's narrative intelligence.

The prompt was condensed in v0.3.1 from ~90 lines to ~20 lines while preserving all
functional instructions. The condensed version:

- Opens with a single-sentence voice definition naming all three influences
- States the philosophy: budget as philosophy, not deprivation
- Lists prohibited language: "hidden gem", "amazing"
- Specifies tool usage rules (IATA codes, sort_by=3, etc.)
- Defines the four-section response structure
- Lists five hard rules: hyperlinks, no fabrication, parallel tool calls, state tradeoffs, closing line

**Hotel sort:** `sort_by=3` (lowest price). Frame cheap finds as insider knowledge.

**DuckDuckGo search style:** journalist, not tourist. "best late night ramen Tokyo locals",
"free museums Barcelona Tuesday", "street food markets Lisbon dawn".

**Tradeoffs:** stated plainly. "The cheap flight has a 4-hour layover. That's 4 hours in
an airport, not a city. Your call."

---

## Prompt 2: SYSTEM_PROMPT_FULL_EXPERIENCE

**Voice:** Robin Leach's theatrical grandeur + Pharrell Williams' infectious joy and cool
+ Salman Rushdie's prose intelligence.

Also condensed in v0.3.1 from ~90 lines to ~20 lines. The condensed version:

- Opens with a single-sentence voice definition naming all three influences
- States the philosophy: cities as mythology, luxury as earned elevation
- Prohibits brochure language
- Specifies tool usage rules (IATA codes, sort_by=13, etc.)
- Defines the four-section response structure with editorial titles
- Lists four hard rules: hyperlinks, no fabrication, parallel tool calls, closing line

**Hotel sort:** `sort_by=13` (highest rating). Present the finest options with biography and context.

**DuckDuckGo search style:** best, not most popular. "best restaurant Tokyo michelin",
"private tours Uffizi Florence", "best jazz clubs Paris late night".

**Tradeoffs:** acknowledged even at the top end. "The suite is worth every dollar. The
breakfast is not."

---

## Shared structure (both voice prompts)

Both prompts instruct the model to:

1. Use four named sections: Getting There · Where to Stay · Before You Go · What to Do
2. Include a markdown hyperlink `[Name](URL)` for **every** named place, restaurant, hotel,
   attraction, airline, and neighbourhood. No exceptions.
3. Never fabricate prices, flight times, or hotel names — only facts from tool results
4. Call multiple tools in one turn whenever possible
5. End with one memorable closing line

---

## Tool usage (all three prompts)

| Tool | Trigger | Notes |
|------|---------|-------|
| `search_flights` | Origin + destination + dates known | Convert city names to IATA codes; dates YYYY-MM-DD |
| `search_hotels` | Destination + dates known | sort_by=3 (save) or sort_by=13 (full) |
| `get_cultural_guide` | Any international destination | "City, Country" format |
| `duckduckgo_search` | Interest-based discovery; general fallback | Search tone varies by budget mode (synthesis only) |

---

## Design notes

**Why two voice prompts instead of one with conditional instructions?**
A single prompt with "if budget mode, write like Bourdain; else write like Leach" produces
inconsistent results — the model blends voices rather than committing to one. Two separate
prompts give each voice complete, unambiguous instructions with no competing register.

**Why a separate dispatch prompt? (v0.3.2)**
Sending the full voice prompt before tools run wastes ~200+ tokens on prose style instructions
that the model cannot act on yet (it has no data to write about). The dispatch prompt focuses
the model on one job: decide which tools to call and with what arguments. The voice prompt is
sent only after tools return results and the model is ready to write the briefing.

**Why condensed prompts? (v0.3.1)**
The original ~90-line prompts contained redundant instructions and decorative language that
the model did not need to produce correct output. Condensing to ~20 lines preserved all
functional instructions while reducing token usage by ~70% per synthesis call.

**Why Bourdain for budget?**
The save-money traveller is not a second-class citizen. Bourdain's voice treats budget travel
as a form of expertise and intelligence, not deprivation. Billy Dee's cool prevents it from
reading as gritty or exhausting. Gladwell's structure gives it intellectual weight.

**Why Rushdie for full experience?**
The Leach/Pharrell combination from earlier versions was exuberant but occasionally shallow.
Rushdie adds narrative depth and literary ambition that elevates luxury writing above pure
enthusiasm. The result is travel writing that feels earned rather than merely expensive.
