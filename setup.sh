#!/bin/bash
# MemU Skill Setup Script

set -e

echo "🦞 MemU Skill Setup"
echo "===================="

# Check Python version
python_version=$(python3 --version 2>&1 | grep -oP '\d+\.\d+')
echo "✓ Python version: $python_version"

# Activate virtual environment
echo "→ Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "→ Installing dependencies..."
pip install -q pgvector

# Validate configuration
echo "→ Validating configuration..."
python3 -c "
import sys
sys.path.insert(0, '.')
from lib.memu_service import validate_config
try:
    validate_config()
    print('✅ Configuration valid')
except ValueError as e:
    print(f'❌ {e}')
    sys.exit(1)
"

# Test connection
echo "→ Testing database connection..."
python3 test_service.py || true

echo ""
echo "✅ Setup complete!"
echo ""
echo "Usage:"
echo "  echo '{\"content\": \"test\"}' | python tools/memorize.py"
echo "  echo '{\"query\": \"test\"}' | python tools/retrieve.py"
