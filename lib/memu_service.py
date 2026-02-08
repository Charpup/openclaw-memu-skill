"""MemU Service wrapper for OpenClaw integration."""
import os
import time
import hashlib
import asyncio
from typing import List, Dict, Any, Optional
from memu.app.service import MemoryService


def validate_config():
    """Validate required environment variables."""
    
    required = {
        "APIYI_API_KEY": os.getenv("APIYI_API_KEY"),
        "OPENROUTER_API_KEY": os.getenv("OPENROUTER_API_KEY")
    }
    
    missing = [k for k, v in required.items() if not v]
    if missing:
        raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
    
    # Log configuration (without exposing secrets)
    print("✅ Configuration validated")
    print(f"   - APIYI_API_KEY: {'Set' if required['APIYI_API_KEY'] else 'Not set'}")
    print(f"   - OPENROUTER_API_KEY: {'Set' if required['OPENROUTER_API_KEY'] else 'Not set'}")
    print(f"   - PostgreSQL: {os.getenv('MEMU_POSTGRES_DSN', 'Using default')}")
    
    return True


class MemUOpenClawService:
    """Singleton wrapper for MemoryService."""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        self._cache = {}  # Simple in-memory cache
        self._cache_ttl = 300  # 5 minutes
        self._last_cache_clear = time.time()
    
    def _get_cache_key(self, query: str, user_id: str) -> str:
        return hashlib.md5(f"{user_id}:{query}".encode()).hexdigest()
    
    def _get_cached(self, key: str):
        """Get cached result if valid."""
        if key in self._cache:
            result, timestamp = self._cache[key]
            if time.time() - timestamp < self._cache_ttl:
                return result
            else:
                del self._cache[key]
        return None
    
    def _set_cached(self, key: str, result):
        """Cache result with timestamp."""
        self._cache[key] = (result, time.time())
        
        # Clear old cache entries periodically
        if time.time() - self._last_cache_clear > 600:  # Every 10 minutes
            self._clear_expired_cache()
    
    def _clear_expired_cache(self):
        """Remove expired cache entries."""
        now = time.time()
        expired = [k for k, (_, ts) in self._cache.items() 
                   if now - ts > self._cache_ttl]
        for k in expired:
            del self._cache[k]
        self._last_cache_clear = now
    
    def initialize(self, 
                   openrouter_key: Optional[str] = None,
                   postgres_dsn: Optional[str] = None):
        """Initialize MemoryService with configuration."""
        if self._initialized:
            return
        
        # Validate configuration
        validate_config()
        
        openrouter_key = openrouter_key or os.getenv("OPENROUTER_API_KEY")
        postgres_dsn = postgres_dsn or os.getenv(
            "MEMU_POSTGRES_DSN",
            "postgresql://memu:memu_secure_password@localhost:5432/memu_db"
        )
        
        # Use apiyi for embeddings (must be set via environment variable)
        apiyi_key = os.getenv("APIYI_API_KEY")
        
        self.service = MemoryService(
            llm_profiles={
                "default": {
                    "provider": "openrouter",
                    "api_key": openrouter_key,
                    "chat_model": "deepseek/deepseek-chat",
                    "embed_model": "openai/text-embedding-3-small"
                },
                "embedding": {
                    "provider": "custom",
                    "base_url": "https://api.apiyi.com/v1",
                    "api_key": apiyi_key,
                    "embed_model": "text-embedding-3-small"
                }
            },
            database_config={
                "metadata_store": {
                    "provider": "postgres",
                    "dsn": postgres_dsn
                },
                "vector_index": {
                    "provider": "pgvector",
                    "dsn": postgres_dsn
                }
            }
        )
        self._initialized = True
    
    async def memorize(self, content: str, user_id: str = "default") -> Dict[str, Any]:
        """Store a memory.
        
        Note: MemU API signature is memorize(resource_url, modality, user).
        For text content, we use resource_url with text:// protocol.
        """
        if not content:
            raise ValueError("content cannot be empty")
        
        if not self._initialized:
            self.initialize()
        
        # Convert text content to text:// URL format as expected by MemU
        import urllib.parse
        encoded_content = urllib.parse.quote(content)
        resource_url = f"text://{encoded_content}"
        
        result = await self.service.memorize(
            resource_url=resource_url,
            modality="text",
            user={"user_id": user_id}
        )
        return result
    
    async def retrieve(self, query: str, user_id: str = "default", 
                       limit: int = 5) -> List[Dict[str, Any]]:
        """Retrieve relevant memories.
        
        Note: MemU API signature is retrieve(queries, where=None).
        We convert user_id to appropriate where clause.
        """
        if not self._initialized:
            self.initialize()
        
        # Check cache first
        cache_key = self._get_cache_key(query, user_id)
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached
        
        # Build queries and where clause as expected by MemU
        queries = [{"role": "user", "content": {"text": query}}]
        where_clause = {"user_id": user_id} if user_id != "default" else None
        
        results = await self.service.retrieve(
            queries=queries,
            where=where_clause
        )
        
        # Cache the results
        limited_results = results[:limit] if results else []
        self._set_cached(cache_key, limited_results)
        
        return limited_results


# Global instance
_memu_service = None

def get_memu_service() -> MemUOpenClawService:
    """Get or create singleton instance."""
    global _memu_service
    if _memu_service is None:
        _memu_service = MemUOpenClawService()
    return _memu_service
