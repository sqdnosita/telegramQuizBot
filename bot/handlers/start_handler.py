from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.keyboards.main_menu import get_main_menu
from bot.logger import get_logger
from bot.services.user_service import UserService

logger = get_logger(__name__)

start_router = Router(name="start")

async def cmd_start(message: Message, user_service: UserService) -> None:
    if message.from_user is None:
        await message.answer(
            "❌ Не удалось определить пользователя. "
            "Попробуйте позже."
        )
        return
    
    try:
        user = await user_service.get_or_create_user(
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name
        )
        
        logger.info(
            f"User started bot: id={user['id']}, "
            f"telegram_id={message.from_user.id}"
        )
        
        welcome_text = (
            "👋 Добро пожаловать в Quiz Bot!\n\n"
            "Этот бот позволяет:\n"
            "📝 Проходить тесты по программированию\n"
            "➕ Создавать собственные квизы\n"
            "📊 Получать результаты с процентами\n\n"
            "Выберите действие из меню ниже:"
        )
        
        await message.answer(
            text=welcome_text,
            reply_markup=get_main_menu()
        )
        
    except Exception as e:
        logger.error(
            f"Failed to process /start command: {e}",
            exc_info=True
        )
        await message.answer(
            "❌ Произошла техническая ошибка. "
            "Пожалуйста, попробуйте позже."
        )

async def cmd_help(message: Message) -> None:
    help_text = (
        "📚 Доступные команды:\n\n"
        "/start - Запустить бота и показать главное меню\n"
        "/help - Показать это сообщение\n"
        "/create_quiz - Создать новый квиз\n"
        "/cancel - Отменить текущее действие\n\n"
        "🎯 Как использовать бота:\n\n"
        "1️⃣ Прохождение тестов:\n"
        "   • Нажмите 'Пройти тест' в главном меню\n"
        "   • Выберите квиз из списка\n"
        "   • Отвечайте на вопросы, выбирая варианты\n"
        "   • Используйте кнопку 'Назад' для возврата\n"
        "   • Получите результат в конце\n\n"
        "2️⃣ Создание квизов:\n"
        "   • Нажмите 'Создать тест' или /create_quiz\n"
        "   • Введите название квиза\n"
        "   • Укажите количество вопросов (1-20)\n"
        "   • Для каждого вопроса:\n"
        "     - Введите текст вопроса\n"
        "     - Введите варианты ответов (2-6 штук)\n"
        "     - Укажите номер правильного ответа\n"
        "   • Используйте /cancel для отмены\n\n"
        "💡 Совет: Все взаимодействие происходит через кнопки "
        "и текстовые сообщения."
    )
    
    await message.answer(text=help_text)

def register_start_handlers(router: Router) -> None:
    router.message.register(cmd_start, Command("start"))
    router.message.register(cmd_help, Command("help"))