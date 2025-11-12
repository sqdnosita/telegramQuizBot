from typing import Optional

import aiosqlite

from bot.database.connection import DatabaseConnection

class UserRepository:
    
    def __init__(self, db_path: str) -> None:
        self._db_path: str = db_path
    
    async def create_user(
        self,
        telegram_id: int,
        username: Optional[str],
        first_name: Optional[str]
    ) -> int:
        async with DatabaseConnection(self._db_path) as conn:
            cursor = await conn.execute(
                """
                INSERT INTO users (telegram_id, username, first_name)
                VALUES (?, ?, ?)
                """,
                (telegram_id, username, first_name)
            )
            await conn.commit()
            
            if cursor.lastrowid is None:
                raise RuntimeError("Failed to create user")
            
            return cursor.lastrowid
    
    async def get_user_by_telegram_id(
        self,
        telegram_id: int
    ) -> Optional[dict]:
        async with DatabaseConnection(self._db_path) as conn:
            conn.row_factory = aiosqlite.Row
            cursor = await conn.execute(
                """
                SELECT id, telegram_id, username, first_name, created_at
                FROM users
                WHERE telegram_id = ?
                """,
                (telegram_id,)
            )
            row = await cursor.fetchone()
            
            if row is None:
                return None
            
            return dict(row)
    
    async def user_exists(self, telegram_id: int) -> bool:
        async with DatabaseConnection(self._db_path) as conn:
            cursor = await conn.execute(
                """
                SELECT COUNT(*) FROM users WHERE telegram_id = ?
                """,
                (telegram_id,)
            )
            result = await cursor.fetchone()
            
            return result[0] > 0 if result else False