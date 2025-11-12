from typing import Dict, Any

from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.keyboards.main_menu import get_main_menu
from bot.keyboards.question_keyboard import get_question_keyboard
from bot.keyboards.quiz_list import (
    get_quiz_list_keyboard,
    get_quiz_list_keyboard_paginated
)
from bot.logger import get_logger
from bot.services.quiz_service import QuizService

logger = get_logger(__name__)

quiz_router = Router(name="quiz")

_user_progress: Dict[str, Dict[str, Any]] = {}

async def callback_take_quiz(
    callback: CallbackQuery,
    quiz_service: QuizService
) -> None:
    if callback.message is None:
        await callback.answer(
            "❌ Ошибка обработки запроса",
            show_alert=True
        )
        return
    
    try:
        pagination = await quiz_service.get_quizzes_paginated(page=1)
        
        if pagination['total'] == 0:
            await callback.message.edit_text(
                "📝 Пока нет доступных квизов.\n\n"
                "Вы можете создать первый квиз, нажав "
                "'Создать тест' в главном меню.",
                reply_markup=get_main_menu()
            )
        else:
            await callback.message.edit_text(
                "📚 Выберите квиз для прохождения:",
                reply_markup=get_quiz_list_keyboard_paginated(
                    quizzes=pagination['quizzes'],
                    page=pagination['page'],
                    total_pages=pagination['total_pages'],
                    has_prev=pagination['has_prev'],
                    has_next=pagination['has_next']
                )
            )
        
        await callback.answer()
        
    except Exception as e:
        logger.error(
            f"Failed to load quiz list: {e}",
            exc_info=True
        )
        await callback.answer(
            "❌ Произошла техническая ошибка. Попробуйте позже.",
            show_alert=True
        )

async def callback_start_quiz(
    callback: CallbackQuery,
    quiz_service: QuizService
) -> None:
    if callback.message is None or callback.from_user is None:
        await callback.answer(
            "❌ Ошибка обработки запроса",
            show_alert=True
        )
        return
    
    if callback.data is None:
        await callback.answer(
            "❌ Некорректные данные",
            show_alert=True
        )
        return
    
    try:
        quiz_id_str = callback.data.split("_")[1]
        quiz_id = int(quiz_id_str)
        
        if quiz_id <= 0:
            raise ValueError("Invalid quiz_id")
        
    except (IndexError, ValueError):
        await callback.answer(
            "❌ Некорректный ID квиза",
            show_alert=True
        )
        return
    
    try:
        quiz = await quiz_service.get_quiz_with_questions(quiz_id)
        
        if quiz is None:
            logger.warning(f"Quiz not found: id={quiz_id}")
            await callback.answer(
                "❌ Квиз не найден",
                show_alert=True
            )
            return
        
        if not quiz.get('questions'):
            logger.warning(f"Quiz has no questions: id={quiz_id}")
            await callback.answer(
                "❌ В квизе нет вопросов",
                show_alert=True
            )
            return
        
        progress_key = f"{callback.from_user.id}:{quiz_id}"
        _user_progress[progress_key] = {
            'quiz_id': quiz_id,
            'quiz_title': quiz['title'],
            'questions': quiz['questions'],
            'current_index': 0,
            'answers': {}
        }
        
        logger.info(
            f"Quiz started: id={quiz_id}, "
            f"questions={len(quiz['questions'])}"
        )
        
        first_question = quiz['questions'][0]
        total_questions = len(quiz['questions'])
        
        question_text = (
            f"📝 {quiz['title']}\n\n"
            f"Вопрос 1 из {total_questions}\n\n"
            f"{first_question['text']}"
        )
        
        await callback.message.edit_text(
            text=question_text,
            reply_markup=get_question_keyboard(
                question_id=first_question['id'],
                answers=first_question['answers'],
                show_back=False
            )
        )
        
        await callback.answer()
        
    except Exception as e:
        logger.error(
            f"Failed to start quiz {quiz_id}: {e}",
            exc_info=True
        )
        await callback.answer(
            "❌ Произошла техническая ошибка. Попробуйте позже.",
            show_alert=True
        )

async def callback_answer_question(
    callback: CallbackQuery,
    quiz_service: QuizService
) -> None:
    if callback.message is None or callback.from_user is None:
        await callback.answer(
            "❌ Ошибка обработки запроса",
            show_alert=True
        )
        return
    
    if callback.data is None:
        await callback.answer(
            "❌ Некорректные данные",
            show_alert=True
        )
        return
    
    try:
        parts = callback.data.split("_")
        question_id = int(parts[1])
        answer_pos = int(parts[2])
        
        if question_id <= 0 or answer_pos <= 0:
            raise ValueError("Invalid IDs")
        
    except (IndexError, ValueError):
        await callback.answer(
            "❌ Некорректные данные ответа",
            show_alert=True
        )
        return
    
    progress_keys = [
        key for key in _user_progress.keys()
        if key.startswith(f"{callback.from_user.id}:")
    ]
    
    if not progress_keys:
        await callback.answer(
            "❌ Прогресс прохождения не найден. Начните квиз заново.",
            show_alert=True
        )
        return
    
    progress_key = progress_keys[0]
    progress = _user_progress[progress_key]
    
    progress['answers'][question_id] = answer_pos
    
    current_index = progress['current_index']
    questions = progress['questions']
    total_questions = len(questions)
    
    next_index = current_index + 1
    
    if next_index >= total_questions:
        finish_keyboard = InlineKeyboardBuilder()
        finish_keyboard.button(
            text="✅ Завершить квиз",
            callback_data=f"finish_quiz_{progress['quiz_id']}"
        )
        finish_keyboard.adjust(1)
        
        await callback.message.edit_text(
            text=(
                f"📝 {progress['quiz_title']}\n\n"
                f"Вы ответили на все вопросы!\n"
                f"Всего вопросов: {total_questions}\n\n"
                f"Нажмите кнопку ниже, чтобы увидеть результаты."
            ),
            reply_markup=finish_keyboard.as_markup()
        )
    else:
        progress['current_index'] = next_index
        next_question = questions[next_index]
        
        question_text = (
            f"📝 {progress['quiz_title']}\n\n"
            f"Вопрос {next_index + 1} из {total_questions}\n\n"
            f"{next_question['text']}"
        )
        
        await callback.message.edit_text(
            text=question_text,
            reply_markup=get_question_keyboard(
                question_id=next_question['id'],
                answers=next_question['answers'],
                show_back=True
            )
        )
    
    await callback.answer()

async def callback_back_question(
    callback: CallbackQuery,
    quiz_service: QuizService
) -> None:
    if callback.message is None or callback.from_user is None:
        await callback.answer(
            "❌ Ошибка обработки запроса",
            show_alert=True
        )
        return
    
    if callback.data is None:
        await callback.answer(
            "❌ Некорректные данные",
            show_alert=True
        )
        return
    
    try:
        question_id = int(callback.data.split("_")[1])
        
        if question_id <= 0:
            raise ValueError("Invalid question_id")
        
    except (IndexError, ValueError):
        await callback.answer(
            "❌ Некорректный ID вопроса",
            show_alert=True
        )
        return
    
    progress_keys = [
        key for key in _user_progress.keys()
        if key.startswith(f"{callback.from_user.id}:")
    ]
    
    if not progress_keys:
        await callback.answer(
            "❌ Прогресс прохождения не найден. Начните квиз заново.",
            show_alert=True
        )
        return
    
    progress_key = progress_keys[0]
    progress = _user_progress[progress_key]
    
    current_index = progress['current_index']
    
    if current_index <= 0:
        await callback.answer(
            "❌ Это первый вопрос",
            show_alert=True
        )
        return
    
    prev_index = current_index - 1
    progress['current_index'] = prev_index
    
    questions = progress['questions']
    total_questions = len(questions)
    prev_question = questions[prev_index]
    
    question_text = (
        f"📝 {progress['quiz_title']}\n\n"
        f"Вопрос {prev_index + 1} из {total_questions}\n\n"
        f"{prev_question['text']}"
    )
    
    prev_answer = progress['answers'].get(prev_question['id'])
    if prev_answer:
        question_text += f"\n\n✅ Ранее выбран ответ: {prev_answer}"
    
    await callback.message.edit_text(
        text=question_text,
        reply_markup=get_question_keyboard(
            question_id=prev_question['id'],
            answers=prev_question['answers'],
            show_back=(prev_index > 0)
        )
    )
    
    await callback.answer()

async def callback_finish_quiz(
    callback: CallbackQuery,
    quiz_service: QuizService
) -> None:
    if callback.message is None or callback.from_user is None:
        await callback.answer(
            "❌ Ошибка обработки запроса",
            show_alert=True
        )
        return
    
    if callback.data is None:
        await callback.answer(
            "❌ Некорректные данные",
            show_alert=True
        )
        return
    
    try:
        quiz_id = int(callback.data.split("_")[2])
        
        if quiz_id <= 0:
            raise ValueError("Invalid quiz_id")
        
    except (IndexError, ValueError):
        await callback.answer(
            "❌ Некорректный ID квиза",
            show_alert=True
        )
        return
    
    progress_key = f"{callback.from_user.id}:{quiz_id}"
    
    if progress_key not in _user_progress:
        await callback.answer(
            "❌ Прогресс прохождения не найден. Начните квиз заново.",
            show_alert=True
        )
        return
    
    progress = _user_progress[progress_key]
    
    try:
        result = await quiz_service.calculate_quiz_result(
            quiz_id=quiz_id,
            user_answers=progress['answers']
        )
        
        logger.info(
            f"Quiz completed: id={quiz_id}, "
            f"score={result['correct_answers']}/{result['total_questions']}, "
            f"percentage={result['percentage']}%"
        )
        
        result_text = (
            f"🎉 Квиз завершен!\n\n"
            f"📝 {progress['quiz_title']}\n\n"
            f"✅ Правильных ответов: {result['correct_answers']} "
            f"из {result['total_questions']}\n"
            f"📊 Процент: {result['percentage']}%\n\n"
        )
        
        if result['percentage'] >= 90:
            result_text += "🏆 Отличный результат!"
        elif result['percentage'] >= 70:
            result_text += "👍 Хороший результат!"
        elif result['percentage'] >= 50:
            result_text += "📚 Неплохо, но есть куда расти!"
        else:
            result_text += "💪 Попробуйте еще раз!"
        
        del _user_progress[progress_key]
        
        await callback.message.edit_text(
            text=result_text,
            reply_markup=get_main_menu()
        )
        
        await callback.answer()
        
    except Exception as e:
        logger.error(
            f"Failed to calculate quiz results for quiz {quiz_id}: {e}",
            exc_info=True
        )
        await callback.answer(
            "❌ Произошла техническая ошибка при подсчете результатов.",
            show_alert=True
        )

async def callback_quiz_page(
    callback: CallbackQuery,
    quiz_service: QuizService
) -> None:
    if callback.message is None:
        await callback.answer(
            "❌ Ошибка обработки запроса",
            show_alert=True
        )
        return
    
    if callback.data is None:
        await callback.answer(
            "❌ Некорректные данные",
            show_alert=True
        )
        return
    
    if callback.data == "quiz_page_current":
        await callback.answer()
        return
    
    try:
        page_str = callback.data.split("_")[2]
        page = int(page_str)
        
        if page < 1:
            raise ValueError("Invalid page number")
        
    except (IndexError, ValueError):
        await callback.answer(
            "❌ Некорректный номер страницы",
            show_alert=True
        )
        return
    
    try:
        pagination = await quiz_service.get_quizzes_paginated(page=page)
        
        await callback.message.edit_text(
            "📚 Выберите квиз для прохождения:",
            reply_markup=get_quiz_list_keyboard_paginated(
                quizzes=pagination['quizzes'],
                page=pagination['page'],
                total_pages=pagination['total_pages'],
                has_prev=pagination['has_prev'],
                has_next=pagination['has_next']
            )
        )
        
        await callback.answer()
        
    except Exception as e:
        logger.error(
            f"Failed to load quiz page {page}: {e}",
            exc_info=True
        )
        await callback.answer(
            "❌ Произошла техническая ошибка. Попробуйте позже.",
            show_alert=True
        )

async def callback_back_to_menu(callback: CallbackQuery) -> None:
    if callback.message is None:
        await callback.answer(
            "❌ Ошибка обработки запроса",
            show_alert=True
        )
        return
    
    welcome_text = (
        "👋 Главное меню\n\n"
        "Выберите действие:"
    )
    
    await callback.message.edit_text(
        text=welcome_text,
        reply_markup=get_main_menu()
    )
    
    await callback.answer()

def register_quiz_handlers(router: Router) -> None:
    router.callback_query.register(
        callback_take_quiz,
        F.data == "take_quiz"
    )
    router.callback_query.register(
        callback_quiz_page,
        F.data.startswith("quiz_page_")
    )
    router.callback_query.register(
        callback_start_quiz,
        F.data.startswith("quiz_")
    )
    router.callback_query.register(
        callback_answer_question,
        F.data.startswith("answer_")
    )
    router.callback_query.register(
        callback_back_question,
        F.data.startswith("back_")
    )
    router.callback_query.register(
        callback_finish_quiz,
        F.data.startswith("finish_quiz_")
    )
    router.callback_query.register(
        callback_back_to_menu,
        F.data == "back_to_menu"
    )