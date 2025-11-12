from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_quiz_list_keyboard(quizzes: list[dict]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    for quiz in quizzes:
        builder.button(
            text=quiz["title"],
            callback_data=f"quiz_{quiz['id']}"
        )
    
    builder.button(
        text="🔙 Назад в меню",
        callback_data="back_to_menu"
    )
    
    builder.adjust(1)
    
    return builder.as_markup()

def get_quiz_list_keyboard_paginated(
    quizzes: list[dict],
    page: int,
    total_pages: int,
    has_prev: bool,
    has_next: bool
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    for quiz in quizzes:
        builder.button(
            text=quiz["title"],
            callback_data=f"quiz_{quiz['id']}"
        )
    
    builder.adjust(1)
    
    nav_buttons = []
    
    if has_prev:
        nav_buttons.append({
            "text": "⬅️ Назад",
            "callback_data": f"quiz_page_{page - 1}"
        })
    
    nav_buttons.append({
        "text": f"📄 {page}/{total_pages}",
        "callback_data": "quiz_page_current"
    })
    
    if has_next:
        nav_buttons.append({
            "text": "Вперёд ➡️",
            "callback_data": f"quiz_page_{page + 1}"
        })
    
    for btn in nav_buttons:
        builder.button(text=btn["text"], callback_data=btn["callback_data"])
    
    builder.button(
        text="🔙 Назад в меню",
        callback_data="back_to_menu"
    )
    
    builder.adjust(1, *([len(nav_buttons)] if nav_buttons else []), 1)
    
    return builder.as_markup()