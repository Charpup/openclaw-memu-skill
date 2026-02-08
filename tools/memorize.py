#!/usr/bin/env python3
"""Memorize tool - stores memories to MemU."""
import sys
import json
import asyncio
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lib.memu_service import get_memu_service


async def main():
    # Read input from stdin
    input_data = json.load(sys.stdin)
    
    content = input_data.get("content")
    user_id = input_data.get("user_id", "default")
    
    if not content:
        print(json.dumps({"error": "Missing 'content' field"}), file=sys.stderr)
        sys.exit(1)
    
    service = get_memu_service()
    result = await service.memorize(content, user_id)
    
    print(json.dumps({"success": True, "result": result}))


if __name__ == "__main__":
    asyncio.run(main())
