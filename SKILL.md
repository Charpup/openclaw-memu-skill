# MemU Skill

Local memory integration for OpenClaw using MemU framework.

## Overview

This skill provides long-term memory capabilities for OpenClaw agents by integrating the MemU memory framework directly with PostgreSQL (no server required).

## Architecture

```
OpenClaw → memu library → PostgreSQL + pgvector → LLM API
```

## Prerequisites

- Python 3.13+
- PostgreSQL with pgvector extension
- OpenRouter API key (or other LLM provider)

## Installation

1. Ensure PostgreSQL is running:
   ```bash
   docker ps | grep memu-postgres
   ```

2. The skill uses Python 3.13.1 virtual environment at:
   `~/openclaw/workspace/skills/memu-skill/venv`

3. Set environment variables:
   ```bash
   export OPENROUTER_API_KEY="your_key_here"
   export MEMU_POSTGRES_DSN="postgresql://memu:password@localhost:5432/memu_db"
   ```

## Tools

### memorize

Store content to long-term memory.

**Input** (JSON via stdin):
```json
{
  "content": "User prefers dark mode interface",
  "user_id": "user_123"
}
```

**Output**:
```json
{
  "success": true,
  "result": {...}
}
```

### retrieve

Retrieve relevant memories.

**Input** (JSON via stdin):
```json
{
  "query": "user preferences",
  "user_id": "user_123",
  "limit": 5
}
```

**Output**:
```json
{
  "success": true,
  "results": [...]
}
```

## Embedding Configuration

This skill uses **API 易** for text embeddings:

- **Base URL**: `https://api.apiyi.com/v1`
- **Model**: `text-embedding-3-small`
- **Required Environment Variable**: `APIYI_API_KEY`

### Quick Setup

1. Copy environment template:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your credentials:
   ```bash
   APIYI_API_KEY=sk-0nGygIa73bGnqNON03B0F8D573174b21A58fDbA89e5a16C8
   OPENROUTER_API_KEY=your_key_here
   ```

3. Run setup:
   ```bash
   ./setup.sh
   ```

## Configuration

Environment variables:
- `APIYI_API_KEY` - API key for API 易 embeddings (required)
- `OPENROUTER_API_KEY` - API key for LLM (required)
- `MEMU_POSTGRES_DSN` - PostgreSQL connection string (optional, has default)

## Testing

Run verification:
```bash
cd ~/openclaw/workspace/skills/memu-skill
source venv/bin/activate
echo '{"content": "test memory"}' | python tools/memorize.py
```

## Notes

- Uses direct library mode (no MemU Server required)
- Supports both PostgreSQL and InMemory providers
- Embeddings generated via OpenRouter API
