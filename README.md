# BrifAI

Automated news briefing system with AI agents, Discord onboarding, scheduled delivery, and clean layered architecture.

## Project Overview

This repository implements the Briefy protocol for a modular briefing platform. It follows:

- Clean Architecture / SOLID
- Spec-Driven Development (SDD)
- async network I/O with `httpx`
- dependency injection through abstract interfaces

## Directory Structure

```
src/
├── agent/             # AI briefing agent implementation
├── bot/               # Discord onboarding bot
├── core/              # Domain models
├── delivery/          # News, email, discord delivery and scheduling
├── interfaces/        # Abstract contracts for each module
├── storage/           # JSON persistence implementation
└── main.py            # Application composition root
```

## Setup

1. Install dependencies:

```bash
uv sync
```

2. Copy the example environment file:

```bash
cp .env.example .env
```

3. Fill in the required variables in `.env`.

## Running the application

```bash
uv run python src/main.py
```

## Notes

- `DISCORD_BOT_TOKEN`, `GROQ_API_KEY`, `NEWS_API_KEY`, and SMTP credentials are loaded from environment variables.
- The bot starts a daily scheduler when the Discord client becomes ready.
- User preferences are persisted in `data/users.json`.
