# Documentation Reconciliation Audit — TravelShaper

**Date:** April 3, 2026
**Covers PRs:** v0.3.0 (April 2), v0.3.1 (April 3), v0.3.2 (April 2)

---

## Changes to Propagate

### v0.3.0 — Configurable OTel Routing
- Added `otel_routing.py` — single module owning all telemetry config
- `OTEL_DESTINATION` env var: `phoenix | arize | both | none`
- Phoenix is now optional — Docker Compose `--profile phoenix`
- Arize Cloud support via standard OTLP/HTTP
- Phoenix Cloud support via `PHOENIX_API_KEY`
- Added 7 unit tests (`test_otel_routing.py`) → 23 total at this point
- Renamed `PHOENIX_COLLECTOR_ENDPOINT` → `PHOENIX_ENDPOINT`
- Added `opentelemetry-sdk` and `opentelemetry-exporter-otlp-proto-http` to Dockerfile
- Added `openinference-semantic-conventions` to Dockerfile

### v0.3.1 — Token Reduction (Part 1)
- Condensed both system prompts (~90 lines → ~20 lines)
- Switched `_llm_json` validation model from `gpt-4o` to `gpt-4o-mini`
- Reduced hotel results from 5 to 3 per search
- Bumped API version `0.1.4` → `0.1.5`

### v0.3.2 — Token Reduction (Part 2)
- Added `DISPATCH_PROMPT` (~150 tokens) for tool-dispatch phase
- `llm_call` detects phase from message state: dispatch before tools, synthesis after
- `get_system_prompt` now accepts `phase` parameter (default: `synthesis`)
- Added 2 unit tests for phase detection → **25 total**

---

## Inconsistencies Found Per Document

### README.md
| # | Section | Current (Wrong) | Should Be |
|---|---------|----------------|-----------|
| 1 | Multiple sections | "16 tests" / "all 16 tests" | "25 tests" / "all 25 tests" |
| 2 | Expected test output | Lists 16 tests | Should list all 25 tests across 4 files |
| 3 | Project structure | Missing `otel_routing.py` | Add to root listing |
| 4 | Project structure | Missing `tests/test_otel_routing.py` | Add to tests/ listing |
| 5 | Project structure | `test_agent.py — 4 agent graph + routing tests` | `test_agent.py — 6 agent graph, routing + dispatch tests` |
| 6 | test-specification.md table row | "4 agent graph + routing tests" | "6 agent graph, routing + dispatch tests" |
| 7 | Security section | "gpt-4o" for validation | "gpt-4o-mini" (note: only _llm_json changed; the prompts still say gpt-4o in the PLACE/PREF prompt comments but the code uses gpt-4o-mini) |
| 8 | docker-compose.yml shown | Old version without profiles/env vars | Current version with profiles and env |
| 9 | .env.example section | Missing `OTEL_DESTINATION` docs | Add OTel routing vars |
| 10 | Header version | V0.1.4 in static/index.html | V0.1.5 (but this is UI, not docs) |
| 11 | Architecture diagram | Shows `phoenix.otel` import | Should show `otel_routing` import |
| 12 | Hotel results | "top 5" in various places | "top 3" |

### docs/ARCHITECTURE.md
| # | Section | Current (Wrong) | Should Be |
|---|---------|----------------|-----------|
| 1 | Version header | "Version: 2.0 (v0.1.4)" | "Version: 2.1 (v0.3.2)" |
| 2 | §4.1 Component overview | Missing `otel_routing.py` | Add to file listing |
| 3 | §4.1 | Missing `tests/test_otel_routing.py` | Add to tests listing |
| 4 | §4.1 | `test_agent.py — 4 agent graph + routing tests` | `6 agent graph, routing + dispatch tests` |
| 5 | §4.2 api.py | "calls gpt-4o to verify" | "calls gpt-4o-mini to verify" |
| 6 | §4.2 api.py | "calls gpt-4o to safety-classify" | "calls gpt-4o-mini to safety-classify" |
| 7 | §7.1 Instrumentation | Shows old `phoenix.otel.register` code | Should show `otel_routing.build_tracer_provider()` |
| 8 | §7.5 Code example | Shows `phoenix.otel.register` | Should show `otel_routing.build_tracer_provider()` |
| 9 | §8.4 Response formatting | `flights[:5]` / "Top 5 only" | `flights[:3]` / "Top 3 only" |
| 10 | §9 System Prompt Design | No mention of DISPATCH_PROMPT or phase routing | Add §9.6 for dispatch phase |
| 11 | §10.1 Decision surface | No mention of phase-based prompt selection | Add dispatch vs synthesis description |
| 12 | §11.1 Place validation | "gpt-4o" | "gpt-4o-mini" |
| 13 | §11.2 Preferences validation | "gpt-4o" | "gpt-4o-mini" |
| 14 | §11.4 Validation cost | "gpt-4o" and cost estimates | "gpt-4o-mini" with updated cost estimate |
| 15 | §12.2 Docker Compose | Old compose YAML | Updated with profiles + env vars |
| 16 | §14 Testing | References "test categories" without OTel tests | Add OTel routing test category |
| 17 | §15 Evolution Path | No mention of token optimization | Can note as completed near-term item |

### docs/test-specification.md
| # | Section | Current (Wrong) | Should Be |
|---|---------|----------------|-----------|
| 1 | Header | "Total tests: 16 passing" | "Total tests: 25 passing" |
| 2 | Header | "Version: 2.0 (v0.1.4)" | "Version: 2.1 (v0.3.2)" |
| 3 | test_agent.py header | "(4 tests)" | "(6 tests)" |
| 4 | Missing | No Test 8a or 8b | Add test_llm_call_uses_dispatch_prompt_before_tools + after_tools |
| 5 | Missing | No tests/test_otel_routing.py section | Add full section with 7 tests |
| 6 | Running section | "16 passed" | "25 passed" |
| 7 | Test numbering | Stops at Test 16 | Should go to Test 25 |

### docs/docker-spec.md
| # | Section | Current (Wrong) | Should Be |
|---|---------|----------------|-----------|
| 1 | Header | "Version: 2.0 (v0.1.4)" | "Version: 2.1 (v0.3.2)" |
| 2 | Dockerfile pip install | Missing `opentelemetry-sdk`, `opentelemetry-exporter-otlp-proto-http`, `openinference-semantic-conventions` | Add all three |
| 3 | docker-compose.yml | Old version (no profiles, no env vars) | Updated version with profiles + env overrides |
| 4 | Notes | No mention of OTel routing packages | Add note explaining why OTel SDK is installed |

### docs/system-prompt-spec.md
| # | Section | Current (Wrong) | Should Be |
|---|---------|----------------|-----------|
| 1 | Header | "Version: 2.0 (v0.1.4)" | "Version: 2.1 (v0.3.2)" |
| 2 | Routing logic | Only shows synthesis routing | Add phase parameter and DISPATCH_PROMPT |
| 3 | Prompt text | May reference long-form prompts | Note prompts were condensed in v0.3.1 |
| 4 | Missing | No DISPATCH_PROMPT section | Add section describing dispatch phase prompt |

### docs/PRD.md
| # | Section | Current (Wrong) | Should Be |
|---|---------|----------------|-----------|
| 1 | §11 Testing | "minimum 2, target 4+" | Update to reflect 25 actual tests |
| 2 | §13 Success Criteria | "At least two unit tests" | Note: 25 tests implemented |

### docs/trace-queries.md
| # | Section | Current (Wrong) | Should Be |
|---|---------|----------------|-----------|
| 1 | Title | "10 Queries" | "11 Queries" |
| 2 | Missing | No Query 11 | Add past-dates error handling query |
| 3 | Coverage matrix | 10 rows | 11 rows |

### RUNNING.md
| # | Section | Current (Wrong) | Should Be |
|---|---------|----------------|-----------|
| 1 | §3 Test count | "All 16 tests" / "8 passed" | "All 25 tests" / "25 passed" |
| 2 | Expected output | Lists 8 tests | Should list all 25 |
| 3 | §7 Project structure | Missing otel_routing.py, test_otel_routing.py | Add both |
| 4 | §7 | `test_agent.py — 2 agent structure tests` | `6 agent graph, routing + dispatch tests` |
| 5 | §7 | `test_api.py — 2 API endpoint tests` | `8 API + validation tests` |
| 6 | §7 | `test_tools.py — 4 tool unit tests` | Correct (still 4) |

### CLAUDE.md
| # | Section | Current (Wrong) | Should Be |
|---|---------|----------------|-----------|
| 1 | After every step | "All tests must pass" (no count) | Acceptable — count not specified |
| 2 | Key files | Has otel_routing.py listed | ✓ Correct |

---

## Summary

| Document | Issues | Severity |
|----------|--------|----------|
| README.md | 12 | High — user-facing |
| ARCHITECTURE.md | 17 | High — technical reference |
| test-specification.md | 7 | High — test authority |
| docker-spec.md | 4 | Medium |
| system-prompt-spec.md | 4 | Medium |
| trace-queries.md | 3 | Medium |
| PRD.md | 2 | Low |
| RUNNING.md | 6 | Medium |
| CLAUDE.md | 0 | None |
