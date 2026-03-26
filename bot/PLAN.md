# LMS Telegram Bot - Implementation Plan

## Overview

This document outlines the development plan for building a Telegram bot that integrates with the LMS backend. The bot allows users to check system health, browse labs and scores, and ask questions in natural language using an LLM for intent routing.

## Architecture

The bot follows a **separation of concerns** pattern:
- **Handlers** (`handlers/`): Pure functions that take input and return text. No Telegram dependency.
- **Services** (`services/`): External API clients (LMS backend, LLM API).
- **Entry point** (`bot.py`): Telegram bot startup and `--test` mode for offline testing.
- **Configuration** (`config.py`): Environment variable loading from `.env.bot.secret`.

This architecture enables testable handlers: the same handler function works in `--test` mode, unit tests, and Telegram without modification.

## Task 1: Scaffold and Test Mode

**Goal:** Create project structure with testable handlers.

- [x] Create `bot/` directory with `handlers/`, `services/`
- [x] Create `bot.py` with `--test` mode
- [x] Implement placeholder handlers: `/start`, `/help`, `/health`, `/labs`, `/scores`
- [x] Create `pyproject.toml` with dependencies (aiogram, httpx, python-dotenv)
- [x] Create `config.py` for environment loading
- [ ] Write this PLAN.md

**Testing:** `uv run bot.py --test "/start"` prints welcome message to stdout.

## Task 2: Backend Integration

**Goal:** Connect handlers to real LMS backend data.

- [ ] Create `services/api_client.py` with Bearer token authentication
- [ ] Implement `/health` — call `GET /health` on backend, report up/down
- [ ] Implement `/labs` — call `GET /items?category=lab`, format list
- [ ] Implement `/scores <lab>` — call `GET /analytics/<lab>`, show pass rates
- [ ] Handle errors gracefully (backend down → friendly message, not crash)

**Key pattern:** API client reads `LMS_API_BASE_URL` and `LMS_API_KEY` from environment. Never hardcode secrets.

## Task 3: Intent-Based Natural Language Routing

**Goal:** Use LLM to understand plain text questions and route to tools.

- [ ] Create `services/llm_client.py` for LLM API calls
- [ ] Define tools for each backend endpoint (e.g., `get_labs()`, `get_scores(lab)`)
- [ ] Write system prompt explaining tool descriptions
- [ ] Implement intent router: user text → LLM → tool call → response
- [ ] Handle multi-step reasoning (LLM chains multiple API calls)

**Key insight:** LLM routing quality depends on tool description clarity, not prompt engineering.

## Task 4: Containerize and Deploy

**Goal:** Deploy bot alongside backend on VM.

- [ ] Create `Dockerfile` for bot
- [ ] Add bot service to `docker-compose.yml`
- [ ] Configure Docker networking (containers use service names, not localhost)
- [ ] Document deployment in README
- [ ] Test end-to-end in Telegram

**Key concept:** Docker containers communicate via service names (`http://backend:42002`), not `localhost`.

## Testing Strategy

1. **Unit tests:** Test handlers directly (no Telegram, no network)
2. **Test mode:** `--test "/command"` for manual verification
3. **Integration tests:** Test with real backend (requires running backend)
4. **Manual testing:** Send commands in Telegram

## Git Workflow

For each task:
1. Create issue on GitHub
2. Create branch: `task-1-scaffold`, `task-2-backend`, etc.
3. Commit changes with meaningful messages
4. Create PR with "Closes #..." in description
5. Partner review → merge

## Environment Files

- `.env.bot.example`: Template with placeholder values (committed to git)
- `.env.bot.secret`: Real secrets (gitignored, deployed on VM)
- `.env.docker.secret`: Backend API credentials (gitignored)

## Dependencies

- `aiogram`: Async Telegram bot framework
- `httpx`: Async HTTP client for API calls
- `python-dotenv`: Load environment from `.env` files
