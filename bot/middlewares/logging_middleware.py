import time
from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Update, Message, CallbackQuery

from bot.logger import get_logger

logger = get_logger(__name__)

class LoggingMiddleware(BaseMiddleware):
    
    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any]
    ) -> Any:
        start_time = time.time()
        
        update_type = self._get_update_type(event)
        user_id = self._get_user_id(event)
        
        logger.debug(
            f"Processing {update_type} from user {user_id}"
        )
        
        try:
            result = await handler(event, data)
            
            processing_time = (time.time() - start_time) * 1000
            
            logger.info(
                f"Processed {update_type} from user {user_id} "
                f"in {processing_time:.2f}ms"
            )
            
            if processing_time > 1000:
                logger.warning(
                    f"Slow processing detected: {update_type} "
                    f"took {processing_time:.2f}ms"
                )
            
            return result
            
        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            
            logger.error(
                f"Error processing {update_type} from user {user_id} "
                f"after {processing_time:.2f}ms: {e}",
                exc_info=True
            )
            
            raise
    
    def _get_update_type(self, event: Update) -> str:
        if event.message:
            return "message"
        elif event.callback_query:
            return "callback_query"
        elif event.edited_message:
            return "edited_message"
        elif event.inline_query:
            return "inline_query"
        else:
            return "unknown"
    
    def _get_user_id(self, event: Update) -> int:
        if event.message and event.message.from_user:
            return event.message.from_user.id
        elif event.callback_query and event.callback_query.from_user:
            return event.callback_query.from_user.id
        elif event.edited_message and event.edited_message.from_user:
            return event.edited_message.from_user.id
        elif event.inline_query and event.inline_query.from_user:
            return event.inline_query.from_user.id
        else:
            return 0