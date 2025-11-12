from typing import Optional

import aiosqlite

class DatabaseConnection:
    
    def __init__(self, db_path: str) -> None:
        self._db_path: str = db_path
        self._connection: Optional[aiosqlite.Connection] = None
    
    async def __aenter__(self) -> aiosqlite.Connection:
        self._connection = await aiosqlite.connect(self._db_path)
        await self._connection.execute("PRAGMA foreign_keys = ON")
        return self._connection
    
    async def __aexit__(
        self,
        exc_type: Optional[type],
        exc_val: Optional[BaseException],
        exc_tb: Optional[object]
    ) -> None:
        if self._connection:
            if exc_type is not None:
                await self._connection.rollback()
            await self._connection.close()
            self._connection = None
    
    async def get_connection(self) -> aiosqlite.Connection:
        if self._connection is None:
            raise RuntimeError(
                "Connection not initialized. "
                "Use DatabaseConnection as context manager."
            )
        return self._connection
    
    async def close(self) -> None:
        if self._connection:
            await self._connection.close()
            self._connection = None