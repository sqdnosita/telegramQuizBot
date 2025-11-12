import asyncio
import aiosqlite

async def check_database():
    db_path = "quiz_bot.db"
    
    async with aiosqlite.connect(db_path) as db:
        cursor = await db.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
        tables = await cursor.fetchall()
        
        print(f"Таблицы в базе данных {db_path}:")
        for table in tables:
            print(f"  - {table[0]}")
            
            cursor = await db.execute(f"PRAGMA table_info({table[0]})")
            columns = await cursor.fetchall()
            print(f"    Колонки:")
            for col in columns:
                print(f"      {col[1]} ({col[2]})")

if __name__ == "__main__":
    asyncio.run(check_database())