# LMS Telegram Bot - Implementation Plan

## Overview

This document outlines the development plan for building a Telegram bot that integrates with the LMS backend. The bot allows users to check system health, browse labs and scores, and ask questions in natural language using an LLM for intent routing.

## Architecture

The bot follows a **separation of concerns** pattern:
- **Handlers** (`handlers/`): Pure functions that take input and return text. No Telegram dependency.
- **Services** (`services/`): External API clients (LMS backend, LLM API, Telegram bot).
- **Entry point** (`bot.py`): Telegram bot startup and `--test` mode for offline testing.
- **Configuration** (`config.py`): Environment variable loading from `.env.bot.secret`.

This architecture enables testable handlers: the same handler function works in `--test` mode, unit tests, and Telegram without modification.

## Task 1: Scaffold and Test Mode

**Goal:** Create project structure with testable handlers.

### Completed
- [x] Create `bot/` directory with `handlers/`, `services/`
- [x] Create `bot.py` with `--test` mode
- [x] Implement placeholder handlers: `/start`, `/help`, `/health`, `/labs`, `/scores`
- [x] Create `pyproject.toml` with dependencies (aiogram, httpx, python-dotenv)
- [x] Create `config.py` for environment loading
- [x] Write PLAN.md

### Testing
```terminal
uv run bot.py --test "/start"    # Prints welcome message
uv run bot.py --test "/help"     # Prints command list
```

## Task 2: Backend Integration

**Goal:** Connect handlers to real LMS backend data.

### Completed
- [x] Create `services/api_client.py` with Bearer token authentication
- [x] Implement `/health` — calls `GET /items/`, reports item count
- [x] Implement `/labs` — calls `GET /items/`, filters and formats labs
- [x] Implement `/scores <lab>` — calls `GET /analytics/pass-rates?lab=`, shows per-task rates
- [x] Handle errors gracefully (HTTP errors, connection errors with friendly messages)
- [x] Added methods: `get_learners()`, `get_analytics_scores()`, `get_analytics_timeline()`, `get_analytics_groups()`, `get_analytics_top_learners()`, `get_analytics_completion_rate()`, `trigger_sync()`

### API Client Pattern
```python
from services.api_client import get_api_client

client = get_api_client()
items = client.get_items()  # Bearer auth from .env.bot.secret
```

### Error Handling
- `httpx.ConnectError` → "connection refused. Check that the services are running."
- `httpx.HTTPStatusError` → "HTTP 502. The backend service may be down."
- No raw tracebacks shown to users.

## Task 3: Intent-Based Natural Language Routing

**Goal:** Use LLM to understand plain text questions and route to tools.

### Completed
- [x] Create `services/llm_client.py` for LLM API calls with tool calling support
- [x] Create `services/llm_tools.py` with 9 tool definitions
- [x] Create `handlers/intent_router.py` with system prompt and tool execution loop
- [x] Create `handlers/text_message.py` for natural language message handling
- [x] Update `bot.py` to route non-command text to LLM
- [x] Add inline keyboard buttons in `services/telegram_bot.py`

### Tool Definitions (9 tools)
| Tool | Endpoint | Description |
|------|----------|-------------|
| `get_items` | `GET /items/` | List all labs and tasks |
| `get_learners` | `GET /learners/` | List enrolled students |
| `get_scores` | `GET /analytics/scores?lab=` | Score distribution (4 buckets) |
| `get_pass_rates` | `GET /analytics/pass-rates?lab=` | Per-task pass rates |
| `get_timeline` | `GET /analytics/timeline?lab=` | Submissions per day |
| `get_groups` | `GET /analytics/groups?lab=` | Per-group performance |
| `get_top_learners` | `GET /analytics/top-learners?lab=&limit=` | Top N learners |
| `get_completion_rate` | `GET /analytics/completion-rate?lab=` | Completion percentage |
| `trigger_sync` | `POST /pipeline/sync` | Refresh data from autochecker |

### Intent Router Flow
```
User: "which lab has the lowest pass rate?"
  → LLM receives message + tool definitions + system prompt
  → LLM calls get_items() → receives 50 items
  → LLM calls get_pass_rates() for each lab (7 calls)
  → LLM compares results and summarizes
  → Bot returns: "Lab-02 has the lowest pass rate at 48.3%..."
```

### System Prompt
The system prompt instructs the LLM to:
1. Think about what data the user needs
2. Call appropriate tool(s) to fetch data
3. Use tool results to provide a clear answer
4. Handle greetings and unclear messages helpfully

### Debug Output
```terminal
$ uv run bot.py --test "which lab has the lowest pass rate"
[tool] LLM called: get_items({})
[tool] Result: 50 items
[tool] LLM called: get_pass_rates({"lab": "lab-01"})
[tool] Result: 8 items
...
[summary] Feeding 7 tool result(s) back to LLM
Based on the data, Lab-02 has the lowest pass rate...
```

### Inline Keyboard Buttons
- Labs, Health, Help
- Scores for lab-04, lab-07
- Callback handlers execute same handlers as commands

### Testing
```terminal
uv run bot.py --test "what labs are available"
uv run bot.py --test "which lab has the lowest pass rate"
uv run bot.py --test "show me scores for lab 4"
uv run bot.py --test "hello"           # Greeting
uv run bot.py --test "asdfgh"          # Fallback with helpful message
```

## Task 4: Containerize and Deploy

**Goal:** Deploy bot alongside backend on VM.

### Pending
- [ ] Create `Dockerfile` for bot
- [ ] Add bot service to `docker-compose.yml`
- [ ] Configure Docker networking (containers use service names, not localhost)
- [ ] Document deployment in README
- [ ] Test end-to-end in Telegram

**Note:** Telegram API may be blocked on some networks. If polling fails, consider:
- Using a proxy (MTProxy, HTTP proxy)
- Running bot on a different network
- Using webhook mode instead of polling

## Testing Strategy

1. **Unit tests:** Test handlers directly (no Telegram, no network)
2. **Test mode:** `--test "/command"` for manual verification (works offline)
3. **Integration tests:** Test with real backend (requires running backend)
4. **Manual testing:** Send commands in Telegram (requires network access)

## Git Workflow

For each task:
1. Create issue on GitHub
2. Create branch: `task-1-scaffold`, `task-2-backend`, `task-3-intent`
3. Commit changes with meaningful messages
4. Create PR with "Closes #..." in description
5. Partner review → merge

## Environment Files

- `.env.bot.example`: Template with placeholder values (committed to git)
- `.env.bot.secret`: Real secrets (gitignored, deployed on VM)
  - `BOT_TOKEN`: Telegram bot token
  - `LMS_API_BASE_URL`: Backend URL (e.g., `http://localhost:42002`)
  - `LMS_API_KEY`: Backend API key
  - `LLM_API_BASE_URL`: LLM proxy URL (e.g., `http://localhost:42005/v1`)
  - `LLM_API_KEY`: LLM API key
  - `LLM_API_MODEL`: Model name (e.g., `coder-model`)

## Dependencies

- `aiogram>=3.0.0`: Async Telegram bot framework
- `httpx>=0.27.0`: Async HTTP client for API calls
- `python-dotenv>=1.0.0`: Load environment from `.env` files

## File Structure

```
bot/
├── bot.py                  # Entry point with --test mode
├── config.py               # Environment loading
├── pyproject.toml          # Dependencies
├── PLAN.md                 # This file
├── handlers/
│   ├── __init__.py
│   ├── start.py            # /start handler
│   ├── help.py             # /help handler
│   ├── health.py           # /health handler (with backend call)
│   ├── labs.py             # /labs handler (with backend call)
│   ├── scores.py           # /scores handler (with backend call)
│   ├── intent_router.py    # LLM intent router (Task 3)
│   └── text_message.py     # Natural language handler (Task 3)
└── services/
    ├── __init__.py
    ├── api_client.py       # LMS API client (Task 2)
    ├── telegram_bot.py     # Telegram bot service
    ├── llm_client.py       # LLM client (Task 3)
    └── llm_tools.py        # Tool definitions (Task 3)
```
