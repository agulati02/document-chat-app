import asyncio
import asyncpg
from typing import Optional, Any, Dict, List, Union, Tuple
import threading
import logging


logger = logging.getLogger(__name__)

class DatabaseClient:
    """
    Singleton PostgreSQL database client for CRUD operations.
    
    Provides async connectivity and operations using SQL statements.
    """
    
    _instance: Optional['DatabaseClient'] = None
    _lock = threading.Lock()
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(DatabaseClient, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, db_url: str):
        if self._initialized:
            return
            
        self.db_url = db_url
        self.client: Optional[asyncpg.Pool] = None
        self._connection_lock = asyncio.Lock()
        self._initialized = True
        logger.info("PostgreSQL DatabaseClient singleton initialized")

    async def connect(self, min_size: int = 10, max_size: int = 20, command_timeout: int = 60, **kwargs):
        """
        Establish connection pool to PostgreSQL database.
        
        Args:
            min_size: Minimum number of connections in the pool
            max_size: Maximum number of connections in the pool
            command_timeout: Command timeout in seconds
            **kwargs: Additional connection parameters
        """
        async with self._connection_lock:
            if self.client is not None:
                logger.warning("Database client is already connected")
                return
            
            try:
                self.client = await asyncpg.create_pool(
                    self.db_url,
                    min_size=min_size,
                    max_size=max_size,
                    command_timeout=command_timeout,
                    server_settings=kwargs.get('server_settings', {'jit': 'off'}),
                    **{k: v for k, v in kwargs.items() if k != 'server_settings'}
                )
                logger.info(f"Connected to PostgreSQL database with pool size {min_size}-{max_size}")
                
                # Test the connection
                await self.execute_query("SELECT 1", fetch="val")
                logger.info("Database connection test successful")
                    
            except Exception as e:
                logger.error(f"Failed to connect to database: {e}") 
                self.client = None
                raise
    
    async def disconnect(self):
        """Close all connections in the pool and cleanup resources."""
        async with self._connection_lock:
            if self.client is None:
                logger.warning("Database client is not connected")
                return
            
            try:
                await self.client.close()
                self.client = None
                logger.info("Disconnected from PostgreSQL database")
            except Exception as e:
                logger.error(f"Error during disconnect: {e}")
                raise
    
    async def execute_query(
        self, 
        query: str, 
        params: tuple = (), 
        fetch: str = "all"
    ) -> Union[List[Dict[str, Any]], Dict[str, Any], Any, None]:
        """
        Execute a SQL query for CRUD operations.
        
        Args:
            query: SQL query string
            params: Query parameters as tuple
            fetch: Type of fetch operation ('all', 'one', 'val', 'none')
                  - 'all': fetchall() - returns list of records
                  - 'one': fetchrow() - returns single record or None
                  - 'val': fetchval() - returns single value or None
                  - 'none': execute() - returns execution result
        
        Returns:
            Query results based on fetch type
        """
        if self.client is None:
            raise RuntimeError("Database client is not connected. Call connect() first.")
        
        try:
            async with self.client.acquire() as conn:
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
    
    async def execute_transaction(self, queries: List[Tuple[str, tuple, str]]) -> List[Any]:
        """
        Execute multiple CRUD operations in a single transaction.
        
        Args:
            queries: List of tuples (query, params, fetch_type)
                    Example: [("INSERT INTO users (name) VALUES ($1)", ("John",), "none")]
        
        Returns:
            List of results for each query
        """
        if self.client is None:
            raise RuntimeError("Database client is not connected. Call connect() first.")
        
        try:
            results = []
            async with self.client.acquire() as conn:
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
    
    async def get_connection(self):
        """
        Get a connection from the pool for advanced operations.
        Use with async context manager.
        
        Example:
            async with db.get_connection() as conn:
                result = await conn.fetch("SELECT * FROM users")
        
        Returns:
            Connection context manager
        """
        if self.client is None:
            raise RuntimeError("Database client is not connected.")
        
        return self.client.acquire()
    
    @property
    def is_connected(self) -> bool:
        """Check if the database client is connected."""
        return self.client is not None and not self.client._closed
    
    async def health_check(self) -> bool:
        """
        Perform a health check on the database connection.
        
        Returns:
            True if database is accessible, False otherwise
        """
        try:
            result = await self.execute_query("SELECT 1", fetch="val")
            return result == 1
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
    
    async def __aenter__(self):
        """Async context manager entry."""
        if not self.is_connected:
            await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()
