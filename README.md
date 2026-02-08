# OpenClaw MemU Skill

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Long-term memory integration for [OpenClaw](https://openclaw.ai) AI agents using the [MemU](https://github.com/NevaMind-AI/memU) memory framework.

## ✨ Features

- 🔒 **Privacy-First**: Direct PostgreSQL connection, no cloud dependency
- ⚡ **Lightweight**: No MemU Server required, direct library usage  
- 🧠 **Smart Triggers**: Automatic memory detection with customizable triggers
- 💰 **Cost-Effective**: ~$0.65/month (LLM costs only)
- 🔄 **Dual Memory**: Complements OpenClaw's built-in session memory

## 🚀 Quick Start

### Prerequisites

- Python 3.13+
- PostgreSQL with pgvector extension
- API key for embeddings (OpenAI-compatible provider)

### Installation

```bash
# Clone the repository
git clone https://github.com/Charpup/openclaw-memu-skill.git
cd openclaw-memu-skill

# Setup environment
cp .env.example .env
# Edit .env with your API keys

# Install
./setup.sh
```

### Configuration

Create `.env` file:

```bash
# Required: API key for embeddings (e.g., API 易, OpenAI)
APIYI_API_KEY=your_api_key_here

# Required: API key for LLM (e.g., OpenRouter)
OPENROUTER_API_KEY=your_openrouter_key_here

# Optional: PostgreSQL connection string
MEMU_POSTGRES_DSN=postgresql://memu:password@localhost:5432/memu_db
```

### Usage

```bash
# Store a memory
echo '{"content": "User prefers dark mode", "user_id": "user123"}' | python tools/memorize.py

# Retrieve memories
echo '{"query": "user preferences", "user_id": "user123"}' | python tools/retrieve.py
```

## 🏗️ Architecture

```
OpenClaw Agent
    ↓
MemU Skill (Python 3.13)
    ↓
memu.app.service.MemoryService (direct library call)
    ↓
PostgreSQL + pgvector (local)
    ↓
LLM API (OpenRouter/API 易)
```

## 📝 Auto-Trigger Patterns

The skill automatically detects and stores:

| Pattern | Example | Category |
|---------|---------|----------|
| "我喜欢..." | "我喜欢简洁回复" | Preference |
| "我有...病" | "我有偏头痛" | Health |
| "我的...是..." | "我的职业是..." | Personal |
| "记住这个..." | "记住明天检查" | Important |

## 🔧 Components

- **lib/memu_service.py**: Core MemoryService wrapper with caching
- **lib/auto_trigger.py**: Automatic trigger detection
- **tools/memorize.py**: CLI tool for storing memories
- **tools/retrieve.py**: CLI tool for retrieving memories

## 🧪 Testing

```bash
# Run tests
python test_service.py
python test_inmemory_mode.py
```

## 📚 Documentation

- [Integration Guide](../MEMORY_SYSTEM_GUIDE.md) - Dual memory system usage
- [Architecture](../AGENTS.md) - System design details

## 🤝 Contributing

Contributions are welcome! Please ensure:
- Code follows existing style
- Tests pass
- No hardcoded secrets
- Sensitive data in `.env` only

## ⚠️ Security

- Never commit `.env` files
- Use environment variables for all secrets
- Review [SECURITY.md](SECURITY.md) for reporting issues

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [MemU](https://github.com/NevaMind-AI/memU) - The memory framework
- [OpenClaw](https://openclaw.ai) - The AI agent platform
