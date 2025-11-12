from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_question_keyboard(
    question_id: int,
    answers: list[dict],
    show_back: bool = False
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    for answer in answers:
        builder.button(
            text=answer["text"],
            callback_data=f"answer_{question_id}_{answer['position']}"
        )
    
    if show_back:
        builder.button(
            text="⬅️ Назад",
            callback_data=f"back_{question_id}"
        )
    
    builder.adjust(1)
    
    return builder.as_markup()