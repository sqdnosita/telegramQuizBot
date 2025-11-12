from typing import Optional

import aiosqlite

from bot.database.connection import DatabaseConnection

class QuizRepository:
    
    def __init__(self, db_path: str) -> None:
        self._db_path: str = db_path
    
    async def create_quiz(self, title: str, creator_id: int) -> int:
        async with DatabaseConnection(self._db_path) as conn:
            cursor = await conn.execute(
                """
                INSERT INTO quizzes (title, creator_id)
                VALUES (?, ?)
                """,
                (title, creator_id)
            )
            await conn.commit()
            
            if cursor.lastrowid is None:
                raise RuntimeError("Failed to create quiz")
            
            return cursor.lastrowid
    
    async def get_all_quizzes(self) -> list[dict]:
        async with DatabaseConnection(self._db_path) as conn:
            conn.row_factory = aiosqlite.Row
            cursor = await conn.execute(
                """
                SELECT id, title, creator_id, created_at
                FROM quizzes
                ORDER BY created_at DESC
                """
            )
            rows = await cursor.fetchall()
            
            return [dict(row) for row in rows]
    
    async def get_quiz_by_id(self, quiz_id: int) -> Optional[dict]:
        async with DatabaseConnection(self._db_path) as conn:
            conn.row_factory = aiosqlite.Row
            cursor = await conn.execute(
                """
                SELECT id, title, creator_id, created_at
                FROM quizzes
                WHERE id = ?
                """,
                (quiz_id,)
            )
            row = await cursor.fetchone()
            
            if row is None:
                return None
            
            return dict(row)
    
    async def get_quizzes_paginated(
        self,
        page: int = 1,
        page_size: int = 6
    ) -> dict:
        if page < 1:
            page = 1
        if page_size < 1:
            page_size = 6
        
        offset = (page - 1) * page_size
        
        async with DatabaseConnection(self._db_path) as conn:
            conn.row_factory = aiosqlite.Row
            
            count_cursor = await conn.execute(
                "SELECT COUNT(*) as total FROM quizzes"
            )
            count_row = await count_cursor.fetchone()
            total = count_row['total'] if count_row else 0
            
            cursor = await conn.execute(
                """
                SELECT id, title, creator_id, created_at
                FROM quizzes
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
                """,
                (page_size, offset)
            )
            rows = await cursor.fetchall()
            
            quizzes = [dict(row) for row in rows]
            total_pages = (total + page_size - 1) // page_size if total > 0 else 1
            
            return {
                'quizzes': quizzes,
                'total': total,
                'page': page,
                'page_size': page_size,
                'total_pages': total_pages,
                'has_next': page < total_pages,
                'has_prev': page > 1
            }