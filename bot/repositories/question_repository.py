from typing import Optional

import aiosqlite

from bot.database.connection import DatabaseConnection

class QuestionRepository:
    
    def __init__(self, db_path: str) -> None:
        self._db_path: str = db_path
    
    async def create_question(
        self,
        quiz_id: int,
        text: str,
        position: int,
        correct_answer: int
    ) -> int:
        async with DatabaseConnection(self._db_path) as conn:
            cursor = await conn.execute(
                """
                INSERT INTO questions (quiz_id, text, position, correct_answer)
                VALUES (?, ?, ?, ?)
                """,
                (quiz_id, text, position, correct_answer)
            )
            await conn.commit()
            
            if cursor.lastrowid is None:
                raise RuntimeError("Failed to create question")
            
            return cursor.lastrowid
    
    async def get_questions_by_quiz_id(self, quiz_id: int) -> list[dict]:
        async with DatabaseConnection(self._db_path) as conn:
            conn.row_factory = aiosqlite.Row
            cursor = await conn.execute(
                """
                SELECT id, quiz_id, text, position, correct_answer
                FROM questions
                WHERE quiz_id = ?
                ORDER BY position ASC
                """,
                (quiz_id,)
            )
            rows = await cursor.fetchall()
            
            return [dict(row) for row in rows]
    
    async def get_question_by_id(self, question_id: int) -> Optional[dict]:
        async with DatabaseConnection(self._db_path) as conn:
            conn.row_factory = aiosqlite.Row
            cursor = await conn.execute(
                """
                SELECT id, quiz_id, text, position, correct_answer
                FROM questions
                WHERE id = ?
                """,
                (question_id,)
            )
            row = await cursor.fetchone()
            
            if row is None:
                return None
            
            return dict(row)