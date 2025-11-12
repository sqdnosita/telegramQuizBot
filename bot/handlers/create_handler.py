from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from bot.keyboards.main_menu import get_main_menu
from bot.logger import get_logger
from bot.services.quiz_service import QuizService
from bot.services.user_service import UserService
from bot.states.quiz_states import CreateQuizStates

logger = get_logger(__name__)

create_router = Router(name="create")

async def callback_create_quiz(
    callback: CallbackQuery,
    state: FSMContext
) -> None:
    if callback.message is None or callback.from_user is None:
        await callback.answer(
            "❌ Ошибка обработки запроса",
            show_alert=True
        )
        return
    
    await state.set_state(CreateQuizStates.waiting_for_title)
    
    await callback.message.edit_text(
        "📝 Создание нового квиза\n\n"
        "Шаг 1: Введите название квиза\n\n"
        "Используйте /cancel для отмены создания."
    )
    
    await callback.answer()

async def cmd_create_quiz(
    message: Message,
    state: FSMContext
) -> None:
    if message.from_user is None:
        await message.answer(
            "❌ Не удалось определить пользователя."
        )
        return
    
    await state.set_state(CreateQuizStates.waiting_for_title)
    
    await message.answer(
        "📝 Создание нового квиза\n\n"
        "Шаг 1: Введите название квиза\n\n"
        "Используйте /cancel для отмены создания."
    )

async def cmd_cancel(
    message: Message,
    state: FSMContext
) -> None:
    current_state = await state.get_state()
    
    if current_state is None:
        await message.answer(
            "Нет активного процесса создания квиза.",
            reply_markup=get_main_menu()
        )
        return
    
    await state.clear()
    
    await message.answer(
        "❌ Создание квиза отменено.\n\n"
        "Вы можете начать заново, выбрав 'Создать тест' в меню.",
        reply_markup=get_main_menu()
    )

async def handle_title_input(
    message: Message,
    state: FSMContext
) -> None:
    if message.text is None or not message.text.strip():
        await message.answer(
            "❌ Название квиза не может быть пустым.\n\n"
            "Пожалуйста, введите название квиза:"
        )
        return
    
    title = message.text.strip()
    
    if len(title) > 200:
        await message.answer(
            "❌ Название квиза слишком длинное (максимум 200 символов).\n\n"
            "Пожалуйста, введите более короткое название:"
        )
        return
    
    await state.update_data(quiz_title=title)
    await state.set_state(CreateQuizStates.waiting_for_question_count)
    
    await message.answer(
        f"✅ Название квиза: {title}\n\n"
        "Шаг 2: Введите количество вопросов (от 1 до 20)\n\n"
        "Используйте /cancel для отмены создания."
    )

async def handle_question_count_input(
    message: Message,
    state: FSMContext
) -> None:
    if message.text is None or not message.text.strip():
        await message.answer(
            "❌ Пожалуйста, введите число от 1 до 20."
        )
        return
    
    try:
        question_count = int(message.text.strip())
    except ValueError:
        await message.answer(
            "❌ Некорректный ввод. Введите целое число от 1 до 20.\n\n"
            "Например: 5"
        )
        return
    
    if question_count < 1 or question_count > 20:
        await message.answer(
            "❌ Количество вопросов должно быть от 1 до 20.\n\n"
            "Пожалуйста, введите корректное число:"
        )
        return
    
    await state.update_data(
        question_count=question_count,
        current_question_index=0,
        questions=[]
    )
    await state.set_state(CreateQuizStates.waiting_for_question_text)
    
    await message.answer(
        f"✅ Количество вопросов: {question_count}\n\n"
        "Шаг 3: Введите текст вопроса 1\n\n"
        "Используйте /cancel для отмены создания."
    )

async def handle_question_text_input(
    message: Message,
    state: FSMContext
) -> None:
    if message.text is None or not message.text.strip():
        await message.answer(
            "❌ Текст вопроса не может быть пустым.\n\n"
            "Пожалуйста, введите текст вопроса:"
        )
        return
    
    question_text = message.text.strip()
    
    if len(question_text) > 500:
        await message.answer(
            "❌ Текст вопроса слишком длинный (максимум 500 символов).\n\n"
            "Пожалуйста, введите более короткий вопрос:"
        )
        return
    
    data = await state.get_data()
    current_index = data.get('current_question_index', 0)
    
    await state.update_data(current_question_text=question_text)
    await state.set_state(CreateQuizStates.waiting_for_answers)
    
    await message.answer(
        f"✅ Вопрос {current_index + 1}: {question_text}\n\n"
        "Шаг 4: Введите варианты ответов\n\n"
        "Введите от 2 до 6 вариантов ответа, каждый на новой строке.\n\n"
        "Пример:\n"
        "Python\n"
        "JavaScript\n"
        "Java\n"
        "C++\n\n"
        "Используйте /cancel для отмены создания."
    )

async def handle_answers_input(
    message: Message,
    state: FSMContext
) -> None:
    if message.text is None or not message.text.strip():
        await message.answer(
            "❌ Варианты ответов не могут быть пустыми.\n\n"
            "Введите от 2 до 6 вариантов ответа, каждый на новой строке."
        )
        return
    
    answers = [
        line.strip()
        for line in message.text.split('\n')
        if line.strip()
    ]
    
    if len(answers) < 2:
        await message.answer(
            "❌ Необходимо минимум 2 варианта ответа.\n\n"
            "Введите варианты ответов, каждый на новой строке:"
        )
        return
    
    if len(answers) > 6:
        await message.answer(
            "❌ Максимум 6 вариантов ответа.\n\n"
            "Введите от 2 до 6 вариантов ответа, каждый на новой строке:"
        )
        return
    
    for idx, answer in enumerate(answers, 1):
        if len(answer) > 200:
            await message.answer(
                f"❌ Вариант ответа {idx} слишком длинный "
                "(максимум 200 символов).\n\n"
                "Пожалуйста, введите более короткие варианты:"
            )
            return
    
    await state.update_data(current_answers=answers)
    await state.set_state(CreateQuizStates.waiting_for_correct_answer)
    
    answers_text = "\n".join(
        f"{idx}. {answer}"
        for idx, answer in enumerate(answers, 1)
    )
    
    await message.answer(
        f"✅ Варианты ответов:\n{answers_text}\n\n"
        "Шаг 5: Введите номер правильного ответа\n\n"
        f"Введите число от 1 до {len(answers)}\n\n"
        "Используйте /cancel для отмены создания."
    )

async def handle_correct_answer_input(
    message: Message,
    state: FSMContext,
    quiz_service: QuizService,
    user_service: UserService
) -> None:
    if message.text is None or not message.text.strip():
        await message.answer(
            "❌ Пожалуйста, введите номер правильного ответа."
        )
        return
    
    if message.from_user is None:
        await message.answer(
            "❌ Не удалось определить пользователя."
        )
        await state.clear()
        return
    
    try:
        correct_answer = int(message.text.strip())
    except ValueError:
        await message.answer(
            "❌ Некорректный ввод. Введите целое число.\n\n"
            "Например: 1"
        )
        return
    
    data = await state.get_data()
    current_answers = data.get('current_answers', [])
    
    if correct_answer < 1 or correct_answer > len(current_answers):
        await message.answer(
            f"❌ Номер ответа должен быть от 1 до {len(current_answers)}.\n\n"
            "Пожалуйста, введите корректный номер:"
        )
        return
    
    questions = data.get('questions', [])
    questions.append({
        'text': data.get('current_question_text', ''),
        'answers': current_answers,
        'correct_answer': correct_answer
    })
    
    current_index = data.get('current_question_index', 0)
    question_count = data.get('question_count', 0)
    
    next_index = current_index + 1
    
    if next_index < question_count:
        await state.update_data(
            questions=questions,
            current_question_index=next_index
        )
        await state.set_state(CreateQuizStates.waiting_for_question_text)
        
        await message.answer(
            f"✅ Вопрос {current_index + 1} сохранен!\n\n"
            f"Шаг 3: Введите текст вопроса {next_index + 1}\n\n"
            "Используйте /cancel для отмены создания."
        )
    else:
        await state.update_data(questions=questions)
        
        try:
            user = await user_service.get_or_create_user(
                telegram_id=message.from_user.id,
                username=message.from_user.username,
                first_name=message.from_user.first_name
            )
            
            quiz_title = data.get('quiz_title', '')
            
            quiz_id = await quiz_service.create_quiz_with_questions(
                title=quiz_title,
                creator_id=user['id'],
                questions_data=questions
            )
            
            await state.clear()
            
            logger.info(
                f"Quiz created successfully: id={quiz_id}, "
                f"title='{quiz_title}', questions={len(questions)}"
            )
            
            await message.answer(
                f"🎉 Квиз успешно создан!\n\n"
                f"📝 Название: {quiz_title}\n"
                f"📊 Вопросов: {len(questions)}\n"
                f"🆔 ID квиза: {quiz_id}\n\n"
                "Теперь другие пользователи могут пройти ваш квиз!",
                reply_markup=get_main_menu()
            )
            
        except Exception as e:
            logger.error(
                f"Failed to create quiz: {e}",
                exc_info=True
            )
            await message.answer(
                "❌ Произошла ошибка при создании квиза. "
                "Пожалуйста, попробуйте позже.",
                reply_markup=get_main_menu()
            )
            await state.clear()

def register_create_handlers(router: Router) -> None:
    router.callback_query.register(
        callback_create_quiz,
        F.data == "create_quiz"
    )
    router.message.register(
        cmd_create_quiz,
        Command("create_quiz")
    )
    router.message.register(
        cmd_cancel,
        Command("cancel")
    )
    router.message.register(
        handle_title_input,
        CreateQuizStates.waiting_for_title
    )
    router.message.register(
        handle_question_count_input,
        CreateQuizStates.waiting_for_question_count
    )
    router.message.register(
        handle_question_text_input,
        CreateQuizStates.waiting_for_question_text
    )
    router.message.register(
        handle_answers_input,
        CreateQuizStates.waiting_for_answers
    )
    router.message.register(
        handle_correct_answer_input,
        CreateQuizStates.waiting_for_correct_answer
    )