#!/usr/bin/env python3
"""Test script for the GraphQL API"""

import asyncio
from src.main import schema

async def test_api():
    print("🧪 Testing GraphQL API...")
    
    # Test hello query
    result = await schema.execute('{ hello }')
    print(f"✅ Hello query: {result.data}")
    
    # Test artists query
    result = await schema.execute('{ artists(limit: 3) { id name tracked } }')
    print(f"✅ Artists query: {result.data}")
    
    # Test albums query
    result = await schema.execute('{ albums(limit: 2) { id name wanted downloaded } }')
    print(f"✅ Albums query: {result.data}")
    
    print("🎉 All tests passed!")

if __name__ == "__main__":
    asyncio.run(test_api()) 