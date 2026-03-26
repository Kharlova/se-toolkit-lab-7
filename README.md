# Lab 7 — Build a Client with an AI Coding Agent

[Sync your fork](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/syncing-a-fork#syncing-a-fork-branch-from-the-command-line) regularly — the lab gets updated.

## Product brief

> Build a Telegram bot that lets users interact with the LMS backend through chat. Users should be able to check system health, browse labs and scores, and ask questions in plain language. The bot should use an LLM to understand what the user wants and fetch the right data. Deploy it alongside the existing backend on the VM.

This is what a customer might tell you. Your job is to turn it into a working product using an AI coding agent (Qwen Code) as your development partner.

```
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│  ┌──────────────┐     ┌──────────────────────────────────┐   │
│  │  Telegram    │────▶│  Your Bot                        │   │
│  │  User        │◀────│  (aiogram / python-telegram-bot) │   │
│  └──────────────┘     └──────┬───────────────────────────┘   │
│                              │                               │
│                              │ slash commands + plain text    │
│                              ├───────▶ /start, /help         │
│                              ├───────▶ /health, /labs        │
│                              ├───────▶ intent router ──▶ LLM │
│                              │                    │          │
│                              │                    ▼          │
│  ┌──────────────┐     ┌──────┴───────┐    tools/actions      │
│  │  Docker      │     │  LMS Backend │◀───── GET /items      │
│  │  Compose     │     │  (FastAPI)   │◀───── GET /analytics  │
│  │              │     │  + PostgreSQL│◀───── POST /sync      │
│  └──────────────┘     └──────────────┘                       │
└──────────────────────────────────────────────────────────────┘
```

## Requirements

### P0 — Must have

1. Testable handler architecture — handlers work without Telegram
2. CLI test mode: `cd bot && uv run bot.py --test "/command"` prints response to stdout
3. `/start` — welcome message
4. `/help` — lists all available commands
5. `/health` — calls backend, reports up/down status
6. `/labs` — lists available labs
7. `/scores <lab>` — per-task pass rates
8. Error handling — backend down produces a friendly message, not a crash

### P1 — Should have

1. Natural language intent routing — plain text interpreted by LLM
2. All 9 backend endpoints wrapped as LLM tools
3. Inline keyboard buttons for common actions
4. Multi-step reasoning (LLM chains multiple API calls)

### P2 — Nice to have

1. Rich formatting (tables, charts as images)
2. Response caching
3. Conversation context (multi-turn)

### P3 — Deployment

1. Bot containerized with Dockerfile
2. Added as service in `docker-compose.yml`
3. Deployed and running on VM
4. README documents deployment

## Learning advice

Notice the progression above: **product brief** (vague customer ask) → **prioritized requirements** (structured) → **task specifications** (precise deliverables + acceptance criteria). This is how engineering work flows.

You are not following step-by-step instructions — you are building a product with an AI coding agent. The learning comes from planning, building, testing, and debugging iteratively.

## Learning outcomes

By the end of this lab, you should be able to say:

1. I turned a vague product brief into a working Telegram bot.
2. I can ask it questions in plain language and it fetches the right data.
3. I used an AI coding agent to plan and build the whole thing.

## Tasks

### Prerequisites

1. Complete the [lab setup](./lab/setup/setup-simple.md#lab-setup)

> **Note**: First time in this course? Do the [full setup](./lab/setup/setup-full.md#lab-setup) instead.

### Required

1. [Plan and Scaffold](./lab/tasks/required/task-1.md) — P0: project structure + `--test` mode
2. [Backend Integration](./lab/tasks/required/task-2.md) — P0: slash commands + real data
3. [Intent-Based Natural Language Routing](./lab/tasks/required/task-3.md) — P1: LLM tool use
4. [Containerize and Document](./lab/tasks/required/task-4.md) — P3: containerize + deploy

### Optional

1. [Flutter Web Chatbot](./lab/tasks/optional/task-1.md)

## Deploy

### Prerequisites

Before deploying, ensure you have:

1. **VM with backend running** — backend, postgres, caddy services
2. **`.env.docker.secret`** configured with:
   - `BOT_TOKEN` — Telegram bot token from @BotFather
   - `LMS_API_KEY` — Backend API key
   - `LLM_API_BASE_URL` — LLM proxy URL (e.g., `http://host.docker.internal:42005/v1` or `http://localhost:42005/v1` on VM)
   - `LLM_API_KEY` — LLM API key
   - `LLM_API_MODEL` — Model name (e.g., `coder-model`)

3. **`.env.bot.secret`** for local testing (same values as above)

### Deploy on VM

1. **Stop the background bot process** (if running):
   ```terminal
   pkill -f "bot.py" 2>/dev/null
   ```

2. **Pull latest changes**:
   ```terminal
   cd ~/se-toolkit-lab-7
   git pull
   ```

3. **Build and start all services**:
   ```terminal
   docker compose --env-file .env.docker.secret up --build -d
   ```

4. **Verify services are running**:
   ```terminal
   docker compose --env-file .env.docker.secret ps
   ```
   
   You should see `bot` service alongside `backend`, `postgres`, `caddy`.

5. **Check bot logs**:
   ```terminal
   docker compose --env-file .env.docker.secret logs bot --tail 30
   ```
   
   Look for:
   - "Bot started!" — successful startup
   - "Polling started" — connected to Telegram
   - No Python tracebacks

### Verify in Telegram

Send these commands to your bot:

| Message | Expected Response |
|---------|------------------|
| `/start` | Welcome message with inline keyboard |
| `/health` | "🟢 Backend is healthy. X items available." |
| `/labs` | List of available labs |
| `/scores lab-04` | Pass rates for lab-04 tasks |
| "what labs are available?" | Natural language response with lab list |
| "which lab has the lowest pass rate?" | Multi-step analysis with comparison |

### Troubleshooting

| Symptom | Solution |
|---------|----------|
| Bot container restarting | Check logs: `docker compose logs bot`. Usually missing env var or import error. |
| `/health` fails | `LMS_API_BASE_URL` must be `http://backend:8000` (not `localhost`). Inside Docker, `localhost` is the container itself. |
| LLM queries fail | `LLM_API_BASE_URL` may need `host.docker.internal` instead of `localhost` to reach the Qwen proxy on a different network. |
| "BOT_TOKEN is required" | Add `BOT_TOKEN` to `.env.docker.secret`. |
| Build fails at `uv sync` | Ensure `uv.lock` exists and is copied in Dockerfile. |

### Local Testing

Before deploying, test locally:

```terminal
cd bot
uv sync
uv run bot.py --test "/start"
uv run bot.py --test "what labs are available"
```
