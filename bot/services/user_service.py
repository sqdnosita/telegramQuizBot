from typing import Optional

import aiosqlite

from bot.repositories.user_repository import UserRepository

class UserService:
    
    def __init__(self, user_repository: UserRepository) -> None:
        self._user_repository: UserRepository = user_repository
    
    async def register_user(
        self,
        telegram_id: int,
        username: Optional[str],
        first_name: Optional[str]
    ) -> int:
        if telegram_id <= 0:
            raise ValueError("telegram_id must be positive integer")
        
        return await self._user_repository.create_user(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name
        )
    
    async def get_or_create_user(
        self,
        telegram_id: int,
        username: Optional[str],
        first_name: Optional[str]
    ) -> dict:
        if telegram_id <= 0:
            raise ValueError("telegram_id must be positive integer")
        
        user = await self._user_repository.get_user_by_telegram_id(
            telegram_id
        )
        
        if user is not None:
            return user
        
        try:
            user_id = await self._user_repository.create_user(
                telegram_id=telegram_id,
                username=username,
                first_name=first_name
            )
            
            user = await self._user_repository.get_user_by_telegram_id(
                telegram_id
            )
            
            if user is None:
                raise RuntimeError(
                    "Failed to retrieve user after creation"
                )
            
            return user
            
        except aiosqlite.IntegrityError:
            user = await self._user_repository.get_user_by_telegram_id(
                telegram_id
            )
            
            if user is None:
                raise RuntimeError(
                    "User exists but could not be retrieved"
                )
            
            return user