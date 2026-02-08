#!/usr/bin/env python3
"""Retrieve tool - fetches memories from MemU."""
import sys
import json
import asyncio
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lib.memu_service import get_memu_service


async def main():
    input_data = json.load(sys.stdin)
    
    query = input_data.get("query")
    user_id = input_data.get("user_id", "default")
    limit = input_data.get("limit", 5)
    
    if not query:
        print(json.dumps({"error": "Missing 'query' field"}), file=sys.stderr)
        sys.exit(1)
    
    service = get_memu_service()
    results = await service.retrieve(query, user_id, limit)
    
    print(json.dumps({"success": True, "results": results}))


if __name__ == "__main__":
    asyncio.run(main())
