import asyncio
import logging
from typing import Any, Dict, List, Optional, Tuple, Union

import asyncpg


logger = logging.getLogger(__name__)

class DatabaseManager:
    """
    Factory-based database manager with async context management.
    Simpler and more predictable than singleton pattern.
    """
    
    # _pool: Optional[asyncpg.Pool] = None
    _lock: Optional[asyncio.Lock] = None
    _db_url: Optional[str] = None
    _initialized: bool = False
    
    @classmethod
    def _ensure_lock(cls):
        """Ensure asyncio lock is created in correct event loop context."""
        if cls._lock is None:
            try:
                cls._lock = asyncio.Lock()
            except RuntimeError:
                # No event loop running - will be created when needed
                pass
    
    @classmethod
    async def initialize(cls, db_url: str, min_size: int = 10, max_size: int = 20, 
                        command_timeout: int = 60, **kwargs):
        """Initialize the database pool."""
        cls._ensure_lock()
        
        if cls._lock is None:
            cls._lock = asyncio.Lock()
        
        async with cls._lock:
            if cls._pool is not None:
                logger.warning("Database already initialized")
                return
            
            try:
                cls._db_url = db_url
                cls._pool = await asyncpg.create_pool(
                    db_url,
                    min_size=min_size,
                    max_size=max_size,
                    command_timeout=command_timeout,
                    server_settings=kwargs.get('server_settings', {'jit': 'off'}),
                    **{k: v for k, v in kwargs.items() if k != 'server_settings'}
                )
                cls._initialized = True
                logger.info(f"Database pool initialized with size {min_size}-{max_size}")
                
                # Test connection
                async with cls._pool.acquire() as conn:
                    await conn.fetchval("SELECT 1")
                logger.info("Database connection test successful")
                
            except Exception as e:
                logger.error(f"Failed to initialize database pool: {e}")
                cls._pool = None
                cls._initialized = False
                raise
    
    @classmethod
    async def close(cls):
        """Close the database pool."""
        if cls._lock is None:
            return
            
        async with cls._lock:
            if cls._pool is not None:
                await cls._pool.close()
                cls._pool = None
                cls._initialized = False
                logger.info("Database pool closed")
    
    @classmethod
    async def execute_query(cls, query: str, params: tuple = (), 
                          fetch: str = "all") -> Union[List[Dict[str, Any]], Dict[str, Any], Any, None]:
        """Execute a query using the shared pool."""
        if not cls.is_initialized():
            raise RuntimeError("Database not initialized. Call initialize() first.")
        
        try:
            async with cls._pool.acquire() as conn:
                if fetch == "all":
                    result = await conn.fetch(query, *params)
                    return [dict(record) for record in result]
                elif fetch == "one":
                    result = await conn.fetchrow(query, *params)
                    return dict(result) if result else None
                elif fetch == "val":
                    return await conn.fetchval(query, *params)
                elif fetch == "none":
                    return await conn.execute(query, *params)
                else:
                    raise ValueError(f"Invalid fetch type: {fetch}")
        
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            logger.error(f"Query: {query}")
            logger.error(f"Params: {params}")
            raise
    
    @classmethod
    async def execute_transaction(cls, queries: List[Tuple[str, tuple, str]]) -> List[Any]:
        """Execute multiple operations in a single transaction."""
        if not cls.is_initialized():
            raise RuntimeError("Database not initialized. Call initialize() first.")
        
        try:
            results = []
            async with cls._pool.acquire() as conn:
                async with conn.transaction():
                    for query, params, fetch_type in queries:
                        if fetch_type == "all":
                            result = await conn.fetch(query, *params)
                            results.append([dict(record) for record in result])
                        elif fetch_type == "one":
                            result = await conn.fetchrow(query, *params)
                            results.append(dict(result) if result else None)
                        elif fetch_type == "val":
                            results.append(await conn.fetchval(query, *params))
                        elif fetch_type == "none":
                            results.append(await conn.execute(query, *params))
                        else:
                            raise ValueError(f"Invalid fetch type: {fetch_type}")
            
            logger.info(f"Executed transaction with {len(queries)} operations")
            return results
            
        except Exception as e:
            logger.error(f"Transaction failed: {e}")
            raise
    
    @classmethod
    def get_connection(cls):
        """Get a connection from the pool for advanced operations."""
        if not cls.is_initialized():
            raise RuntimeError("Database not initialized.")
        return cls._pool.acquire()
    
    @classmethod
    def is_initialized(cls) -> bool:
        """Check if the database manager is initialized."""
        return cls._initialized and cls._pool is not None and not cls._pool._closed
    
    @classmethod
    async def health_check(cls) -> bool:
        """Perform a health check on the database connection."""
        try:
            if not cls.is_initialized():
                return False
            result = await cls.execute_query("SELECT 1", fetch="val")
            return result == 1
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
    
    # Context manager support for the class itself
    @classmethod
    async def __aenter__(cls):
        """Class-level async context manager entry."""
        # Assumes initialize() was called before entering context
        if not cls.is_initialized():
            raise RuntimeError("Database not initialized. Call initialize() first.")
        return cls
    
    @classmethod
    async def __aexit__(cls, exc_type, exc_val, exc_tb):
        """Class-level async context manager exit."""
        await cls.close()


class DatabaseContext:
    """
    Instance-based context manager for DatabaseManager.
    Provides more intuitive context management.
    """
    
    def __init__(self, db_url: str, min_size: int = 10, max_size: int = 20, 
                 command_timeout: int = 60, **kwargs):
        self.db_url = db_url
        self.min_size = min_size
        self.max_size = max_size
        self.command_timeout = command_timeout
        self.kwargs = kwargs
        self._should_close = False
    
    async def __aenter__(self):
        """Initialize database if not already done."""
        if not DatabaseManager.is_initialized():
            await DatabaseManager.initialize(
                self.db_url, 
                self.min_size, 
                self.max_size, 
                self.command_timeout, 
                **self.kwargs
            )
            self._should_close = True
        return DatabaseManager
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Close database only if we initialized it."""
        if self._should_close:
            await DatabaseManager.close()