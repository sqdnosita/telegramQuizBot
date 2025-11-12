import asyncio
import sys

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from bot.config import config
from bot.database.connection import DatabaseConnection
from bot.database.schema import init_db
from bot.handlers.create_handler import (
    create_router,
    register_create_handlers
)
from bot.handlers.quiz_handler import (
    quiz_router,
    register_quiz_handlers
)
from bot.handlers.start_handler import (
    start_router,
    register_start_handlers
)
from bot.logger import setup_logging, get_logger
from bot.middlewares.logging_middleware import LoggingMiddleware
from bot.repositories.answer_repository import AnswerRepository
from bot.repositories.question_repository import QuestionRepository
from bot.repositories.quiz_repository import QuizRepository
from bot.repositories.user_repository import UserRepository
from bot.services.quiz_service import QuizService
from bot.services.user_service import UserService

logger = get_logger(__name__)

async def main() -> None:
    setup_logging()
    
    logger.info("Starting Telegram Quiz Bot...")
    
    try:
        logger.info("Configuration loaded successfully")
    except Exception as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)
    
    try:
        await init_db(config.database_path)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}", exc_info=True)
        sys.exit(1)
    
    bot = Bot(token=config.bot_token)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    dp.update.middleware(LoggingMiddleware())
    
    user_repo = UserRepository(config.database_path)
    quiz_repo = QuizRepository(config.database_path)
    question_repo = QuestionRepository(config.database_path)
    answer_repo = AnswerRepository(config.database_path)
    
    user_service = UserService(user_repo)
    quiz_service = QuizService(
        quiz_repo,
        question_repo,
        answer_repo,
        config.database_path
    )
    
    register_start_handlers(start_router)
    register_quiz_handlers(quiz_router)
    register_create_handlers(create_router)
    
    dp.include_router(start_router)
    dp.include_router(quiz_router)
    dp.include_router(create_router)
    
    dp["user_service"] = user_service
    dp["quiz_service"] = quiz_service
    
    logger.info("Bot initialized, starting polling...")
    
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot polling error: {e}", exc_info=True)
    finally:
        await bot.session.close()
        logger.info("Bot shutdown complete")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)