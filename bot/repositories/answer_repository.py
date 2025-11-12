import aiosqlite

from bot.database.connection import DatabaseConnection

class AnswerRepository:
    
    def __init__(self, db_path: str) -> None:
        self._db_path: str = db_path
    
    async def create_answer(
        self,
        question_id: int,
        text: str,
        position: int
    ) -> int:
        async with DatabaseConnection(self._db_path) as conn:
            cursor = await conn.execute(
                """
                INSERT INTO answers (question_id, text, position)
                VALUES (?, ?, ?)
                """,
                (question_id, text, position)
            )
            await conn.commit()
            
            if cursor.lastrowid is None:
                raise RuntimeError("Failed to create answer")
            
            return cursor.lastrowid
    
    async def get_answers_by_question_id(
        self,
        question_id: int
    ) -> list[dict]:
        async with DatabaseConnection(self._db_path) as conn:
            conn.row_factory = aiosqlite.Row
            cursor = await conn.execute(
                """
                SELECT id, question_id, text, position
                FROM answers
                WHERE question_id = ?
                ORDER BY position ASC
                """,
                (question_id,)
            )
            rows = await cursor.fetchall()
            
            return [dict(row) for row in rows]