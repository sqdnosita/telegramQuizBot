import asyncio
import os

from bot.config import config
from bot.database.schema import init_db
from bot.logger import setup_logging, get_logger

logger = get_logger(__name__)

async def reset_database():
    setup_logging()
    
    db_path = config.database_path
    
    if os.path.exists(db_path):
        logger.info(f"Удаление существующей базы данных: {db_path}")
        os.remove(db_path)
    
    logger.info(f"Создание новой базы данных: {db_path}")
    await init_db(db_path)
    
    logger.info("База данных успешно пересоздана!")

if __name__ == "__main__":
    asyncio.run(reset_database())