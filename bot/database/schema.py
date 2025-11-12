from typing import Protocol

import aiosqlite

class DatabaseConnection(Protocol):
    
    async def execute(self, sql: str, parameters: tuple = ()) -> aiosqlite.Cursor:
        ...
    
    async def commit(self) -> None:
        ...

CREATE_USERS_TABLE = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER UNIQUE NOT NULL,
    username TEXT,
    first_name TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""

CREATE_QUIZZES_TABLE = """
CREATE TABLE IF NOT EXISTS quizzes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    creator_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (creator_id) REFERENCES users(id)
)
"""

CREATE_QUESTIONS_TABLE = """
CREATE TABLE IF NOT EXISTS questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    quiz_id INTEGER NOT NULL,
    text TEXT NOT NULL,
    position INTEGER NOT NULL,
    correct_answer INTEGER NOT NULL,
    FOREIGN KEY (quiz_id) REFERENCES quizzes(id) ON DELETE CASCADE
)
"""

CREATE_ANSWERS_TABLE = """
CREATE TABLE IF NOT EXISTS answers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question_id INTEGER NOT NULL,
    text TEXT NOT NULL,
    position INTEGER NOT NULL,
    FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE
)
"""

CREATE_USERS_TELEGRAM_ID_INDEX = """
CREATE INDEX IF NOT EXISTS idx_users_telegram_id 
ON users(telegram_id)
"""

CREATE_QUIZZES_CREATOR_ID_INDEX = """
CREATE INDEX IF NOT EXISTS idx_quizzes_creator_id 
ON quizzes(creator_id)
"""

CREATE_QUESTIONS_QUIZ_ID_INDEX = """
CREATE INDEX IF NOT EXISTS idx_questions_quiz_id 
ON questions(quiz_id)
"""

CREATE_ANSWERS_QUESTION_ID_INDEX = """
CREATE INDEX IF NOT EXISTS idx_answers_question_id 
ON answers(question_id)
"""

async def init_db(db_path: str) -> None:
    import logging
    logger = logging.getLogger(__name__)
    
    async with aiosqlite.connect(db_path) as db:
        await db.execute("PRAGMA foreign_keys = ON")
        
        logger.info("Creating users table...")
        await db.execute(CREATE_USERS_TABLE)
        
        logger.info("Creating quizzes table...")
        await db.execute(CREATE_QUIZZES_TABLE)
        
        logger.info("Creating questions table...")
        await db.execute(CREATE_QUESTIONS_TABLE)
        
        logger.info("Creating answers table...")
        await db.execute(CREATE_ANSWERS_TABLE)
        
        logger.info("Creating indexes...")
        await db.execute(CREATE_USERS_TELEGRAM_ID_INDEX)
        await db.execute(CREATE_QUIZZES_CREATOR_ID_INDEX)
        await db.execute(CREATE_QUESTIONS_QUIZ_ID_INDEX)
        await db.execute(CREATE_ANSWERS_QUESTION_ID_INDEX)
        
        await db.commit()
        logger.info("Database schema initialized successfully")