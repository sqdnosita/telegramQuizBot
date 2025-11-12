from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_main_menu() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    builder.button(
        text="📝 Пройти тест",
        callback_data="take_quiz"
    )
    builder.button(
        text="➕ Создать тест",
        callback_data="create_quiz"
    )
    
    builder.adjust(1)
    
    return builder.as_markup()