import asyncio

from bot.config import config
from bot.database.schema import init_db
from bot.logger import setup_logging, get_logger
from bot.repositories.answer_repository import AnswerRepository
from bot.repositories.question_repository import QuestionRepository
from bot.repositories.quiz_repository import QuizRepository
from bot.repositories.user_repository import UserRepository
from bot.services.quiz_service import QuizService
from bot.services.user_service import UserService

logger = get_logger(__name__)

SAMPLE_QUIZZES = [
    {
        "title": "Python Основы",
        "questions": [
            {
                "text": "Какой тип данных используется для хранения "
                        "целых чисел в Python?",
                "answers": ["int", "float", "str", "bool"],
                "correct_answer": 1
            },
            {
                "text": "Какая функция используется для вывода текста "
                        "в консоль?",
                "answers": ["echo()", "print()", "console.log()", "write()"],
                "correct_answer": 2
            },
            {
                "text": "Какой оператор используется для проверки "
                        "равенства в Python?",
                "answers": ["=", "==", "===", "eq"],
                "correct_answer": 2
            },
            {
                "text": "Как создать список в Python?",
                "answers": [
                    "list = (1, 2, 3)",
                    "list = {1, 2, 3}",
                    "list = [1, 2, 3]",
                    "list = <1, 2, 3>"
                ],
                "correct_answer": 3
            },
            {
                "text": "Какой метод используется для добавления "
                        "элемента в конец списка?",
                "answers": ["add()", "append()", "push()", "insert()"],
                "correct_answer": 2
            }
        ]
    },
    {
        "title": "JavaScript Основы",
        "questions": [
            {
                "text": "Какое ключевое слово используется для "
                        "объявления константы в JavaScript?",
                "answers": ["var", "let", "const", "final"],
                "correct_answer": 3
            },
            {
                "text": "Какой метод используется для преобразования "
                        "строки в число?",
                "answers": [
                    "parseInt()",
                    "toNumber()",
                    "convert()",
                    "number()"
                ],
                "correct_answer": 1
            },
            {
                "text": "Что вернет typeof null в JavaScript?",
                "answers": ["'null'", "'undefined'", "'object'", "'number'"],
                "correct_answer": 3
            },
            {
                "text": "Какой оператор используется для строгого "
                        "сравнения в JavaScript?",
                "answers": ["==", "===", "=", "eq"],
                "correct_answer": 2
            }
        ]
    },
    {
        "title": "SQL Запросы",
        "questions": [
            {
                "text": "Какая команда используется для выборки "
                        "данных из таблицы?",
                "answers": ["GET", "SELECT", "FETCH", "RETRIEVE"],
                "correct_answer": 2
            },
            {
                "text": "Какое ключевое слово используется для "
                        "фильтрации результатов?",
                "answers": ["FILTER", "WHERE", "HAVING", "IF"],
                "correct_answer": 2
            },
            {
                "text": "Какая команда используется для добавления "
                        "новой записи в таблицу?",
                "answers": ["ADD", "INSERT", "CREATE", "APPEND"],
                "correct_answer": 2
            },
            {
                "text": "Какой оператор используется для объединения "
                        "двух таблиц?",
                "answers": ["MERGE", "COMBINE", "JOIN", "UNION"],
                "correct_answer": 3
            },
            {
                "text": "Какая команда используется для удаления "
                        "записей из таблицы?",
                "answers": ["REMOVE", "DELETE", "DROP", "CLEAR"],
                "correct_answer": 2
            },
            {
                "text": "Какое ключевое слово используется для "
                        "сортировки результатов?",
                "answers": ["SORT", "ORDER BY", "ARRANGE", "RANK"],
                "correct_answer": 2
            }
        ]
    },
    {
        "title": "HTML & CSS",
        "questions": [
            {
                "text": "Какой тег используется для создания заголовка "
                        "первого уровня?",
                "answers": ["<header>", "<h1>", "<title>", "<head>"],
                "correct_answer": 2
            },
            {
                "text": "Какое свойство CSS используется для изменения "
                        "цвета текста?",
                "answers": ["text-color", "color", "font-color", "fg-color"],
                "correct_answer": 2
            },
            {
                "text": "Какой тег используется для создания ссылки?",
                "answers": ["<link>", "<a>", "<href>", "<url>"],
                "correct_answer": 2
            },
            {
                "text": "Какое свойство CSS используется для изменения "
                        "размера шрифта?",
                "answers": [
                    "text-size",
                    "font-size",
                    "size",
                    "text-height"
                ],
                "correct_answer": 2
            }
        ]
    },
    {
        "title": "Git Основы",
        "questions": [
            {
                "text": "Какая команда используется для клонирования "
                        "репозитория?",
                "answers": [
                    "git copy",
                    "git clone",
                    "git download",
                    "git pull"
                ],
                "correct_answer": 2
            },
            {
                "text": "Какая команда используется для создания "
                        "коммита?",
                "answers": [
                    "git save",
                    "git commit",
                    "git push",
                    "git add"
                ],
                "correct_answer": 2
            },
            {
                "text": "Какая команда показывает статус репозитория?",
                "answers": [
                    "git info",
                    "git status",
                    "git state",
                    "git check"
                ],
                "correct_answer": 2
            },
            {
                "text": "Какая команда используется для отправки "
                        "изменений на сервер?",
                "answers": [
                    "git send",
                    "git push",
                    "git upload",
                    "git commit"
                ],
                "correct_answer": 2
            }
        ]
    },
    {
        "title": "Docker Основы",
        "questions": [
            {
                "text": "Какая команда используется для запуска "
                        "контейнера?",
                "answers": [
                    "docker start",
                    "docker run",
                    "docker execute",
                    "docker launch"
                ],
                "correct_answer": 2
            },
            {
                "text": "Какая команда показывает список запущенных "
                        "контейнеров?",
                "answers": ["docker list", "docker ps", "docker show", "docker ls"],
                "correct_answer": 2
            },
            {
                "text": "Какой файл используется для описания образа?",
                "answers": [
                    "docker.yml",
                    "Dockerfile",
                    "docker.json",
                    "image.txt"
                ],
                "correct_answer": 2
            },
            {
                "text": "Какая команда используется для остановки "
                        "контейнера?",
                "answers": [
                    "docker end",
                    "docker stop",
                    "docker kill",
                    "docker pause"
                ],
                "correct_answer": 2
            }
        ]
    },
    {
        "title": "Linux Команды",
        "questions": [
            {
                "text": "Какая команда используется для просмотра "
                        "содержимого директории?",
                "answers": ["dir", "ls", "list", "show"],
                "correct_answer": 2
            },
            {
                "text": "Какая команда используется для изменения "
                        "текущей директории?",
                "answers": ["chdir", "cd", "move", "goto"],
                "correct_answer": 2
            },
            {
                "text": "Какая команда используется для создания "
                        "новой директории?",
                "answers": ["create", "mkdir", "newdir", "makedir"],
                "correct_answer": 2
            },
            {
                "text": "Какая команда используется для удаления файла?",
                "answers": ["delete", "rm", "del", "remove"],
                "correct_answer": 2
            }
        ]
    },
    {
        "title": "REST API",
        "questions": [
            {
                "text": "Какой HTTP метод используется для получения "
                        "данных?",
                "answers": ["POST", "GET", "PUT", "DELETE"],
                "correct_answer": 2
            },
            {
                "text": "Какой HTTP метод используется для создания "
                        "нового ресурса?",
                "answers": ["GET", "POST", "PUT", "PATCH"],
                "correct_answer": 2
            },
            {
                "text": "Какой код статуса означает успешный запрос?",
                "answers": ["404", "200", "500", "301"],
                "correct_answer": 2
            },
            {
                "text": "Какой HTTP метод используется для обновления "
                        "ресурса?",
                "answers": ["POST", "PUT", "GET", "DELETE"],
                "correct_answer": 2
            }
        ]
    },
    {
        "title": "Базы данных",
        "questions": [
            {
                "text": "Что такое первичный ключ?",
                "answers": [
                    "Любое поле таблицы",
                    "Уникальный идентификатор записи",
                    "Внешний ключ",
                    "Индекс таблицы"
                ],
                "correct_answer": 2
            },
            {
                "text": "Что такое внешний ключ?",
                "answers": [
                    "Первичный ключ другой таблицы",
                    "Ссылка на первичный ключ другой таблицы",
                    "Уникальное поле",
                    "Индекс"
                ],
                "correct_answer": 2
            },
            {
                "text": "Какая команда используется для создания "
                        "таблицы?",
                "answers": [
                    "NEW TABLE",
                    "CREATE TABLE",
                    "ADD TABLE",
                    "MAKE TABLE"
                ],
                "correct_answer": 2
            },
            {
                "text": "Что такое индекс в базе данных?",
                "answers": [
                    "Номер записи",
                    "Структура для ускорения поиска",
                    "Первичный ключ",
                    "Внешний ключ"
                ],
                "correct_answer": 2
            }
        ]
    },
    {
        "title": "Алгоритмы",
        "questions": [
            {
                "text": "Какая сложность у бинарного поиска?",
                "answers": ["O(n)", "O(log n)", "O(n²)", "O(1)"],
                "correct_answer": 2
            },
            {
                "text": "Какая структура данных работает по принципу "
                        "LIFO?",
                "answers": ["Очередь", "Стек", "Список", "Дерево"],
                "correct_answer": 2
            },
            {
                "text": "Какая структура данных работает по принципу "
                        "FIFO?",
                "answers": ["Стек", "Очередь", "Массив", "Граф"],
                "correct_answer": 2
            },
            {
                "text": "Какая сложность у быстрой сортировки в "
                        "среднем случае?",
                "answers": ["O(n)", "O(n log n)", "O(n²)", "O(log n)"],
                "correct_answer": 2
            }
        ]
    },
    {
        "title": "Тестирование",
        "questions": [
            {
                "text": "Что такое unit-тест?",
                "answers": [
                    "Тест всей системы",
                    "Тест отдельного модуля",
                    "Тест интерфейса",
                    "Нагрузочный тест"
                ],
                "correct_answer": 2
            },
            {
                "text": "Что такое интеграционный тест?",
                "answers": [
                    "Тест одной функции",
                    "Тест взаимодействия компонентов",
                    "Тест производительности",
                    "Тест безопасности"
                ],
                "correct_answer": 2
            },
            {
                "text": "Что такое mock в тестировании?",
                "answers": [
                    "Реальный объект",
                    "Имитация объекта",
                    "Тестовые данные",
                    "Ошибка теста"
                ],
                "correct_answer": 2
            },
            {
                "text": "Что такое TDD?",
                "answers": [
                    "Тестирование после разработки",
                    "Разработка через тестирование",
                    "Автоматическое тестирование",
                    "Ручное тестирование"
                ],
                "correct_answer": 2
            }
        ]
    },
    {
        "title": "Сети",
        "questions": [
            {
                "text": "Какой протокол используется для передачи "
                        "веб-страниц?",
                "answers": ["FTP", "HTTP", "SMTP", "SSH"],
                "correct_answer": 2
            },
            {
                "text": "Какой порт по умолчанию использует HTTP?",
                "answers": ["443", "80", "22", "21"],
                "correct_answer": 2
            },
            {
                "text": "Какой протокол используется для безопасной "
                        "передачи данных?",
                "answers": ["HTTP", "HTTPS", "FTP", "SMTP"],
                "correct_answer": 2
            },
            {
                "text": "Что такое DNS?",
                "answers": [
                    "Протокол передачи файлов",
                    "Система доменных имен",
                    "Протокол электронной почты",
                    "Сетевой протокол"
                ],
                "correct_answer": 2
            }
        ]
    },
    {
        "title": "Безопасность",
        "questions": [
            {
                "text": "Что такое SQL-инъекция?",
                "answers": [
                    "Ошибка в SQL запросе",
                    "Атака через внедрение SQL кода",
                    "Оптимизация запросов",
                    "Резервное копирование"
                ],
                "correct_answer": 2
            },
            {
                "text": "Что такое XSS?",
                "answers": [
                    "Протокол шифрования",
                    "Атака через внедрение скриптов",
                    "Тип базы данных",
                    "Метод аутентификации"
                ],
                "correct_answer": 2
            },
            {
                "text": "Что такое CSRF?",
                "answers": [
                    "Протокол безопасности",
                    "Подделка межсайтовых запросов",
                    "Алгоритм шифрования",
                    "Тип токена"
                ],
                "correct_answer": 2
            },
            {
                "text": "Что такое хеширование пароля?",
                "answers": [
                    "Шифрование пароля",
                    "Преобразование пароля в хеш",
                    "Сжатие пароля",
                    "Кодирование пароля"
                ],
                "correct_answer": 2
            }
        ]
    },
    {
        "title": "Паттерны проектирования",
        "questions": [
            {
                "text": "Что такое паттерн Singleton?",
                "answers": [
                    "Множество экземпляров класса",
                    "Единственный экземпляр класса",
                    "Наследование классов",
                    "Композиция объектов"
                ],
                "correct_answer": 2
            },
            {
                "text": "Что такое паттерн Factory?",
                "answers": [
                    "Прямое создание объектов",
                    "Создание объектов через фабричный метод",
                    "Копирование объектов",
                    "Удаление объектов"
                ],
                "correct_answer": 2
            },
            {
                "text": "Что такое паттерн Observer?",
                "answers": [
                    "Прямой вызов методов",
                    "Подписка на события объекта",
                    "Наследование классов",
                    "Инкапсуляция данных"
                ],
                "correct_answer": 2
            },
            {
                "text": "Что такое паттерн Strategy?",
                "answers": [
                    "Фиксированный алгоритм",
                    "Выбор алгоритма во время выполнения",
                    "Создание объектов",
                    "Удаление объектов"
                ],
                "correct_answer": 2
            }
        ]
    },
    {
        "title": "Agile & Scrum",
        "questions": [
            {
                "text": "Что такое Sprint в Scrum?",
                "answers": [
                    "Встреча команды",
                    "Итерация разработки фиксированной длины",
                    "Список задач",
                    "Роль в команде"
                ],
                "correct_answer": 2
            },
            {
                "text": "Что такое Daily Standup?",
                "answers": [
                    "Планирование спринта",
                    "Ежедневная короткая встреча",
                    "Ретроспектива",
                    "Демонстрация продукта"
                ],
                "correct_answer": 2
            },
            {
                "text": "Что такое Product Backlog?",
                "answers": [
                    "Завершенные задачи",
                    "Приоритизированный список требований",
                    "Текущий спринт",
                    "Документация"
                ],
                "correct_answer": 2
            },
            {
                "text": "Кто такой Product Owner?",
                "answers": [
                    "Разработчик",
                    "Владелец продукта, определяющий требования",
                    "Тестировщик",
                    "Менеджер проекта"
                ],
                "correct_answer": 2
            }
        ]
    }
]

async def seed_database() -> None:
    setup_logging()
    
    logger.info("Starting database seeding...")
    
    try:
        await init_db(config.database_path)
        logger.info("Database initialized")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}", exc_info=True)
        return
    
    user_repo = UserRepository(config.database_path)
    quiz_repo = QuizRepository(config.database_path)
    question_repo = QuestionRepository(config.database_path)
    answer_repo = AnswerRepository(config.database_path)
    
    user_service = UserService(user_repo)
    quiz_service = QuizService(
        quiz_repo,
        question_repo,
        answer_repo,
        config.database_path
    )
    
    try:
        test_user = await user_service.get_or_create_user(
            telegram_id=123456789,
            username="test_user",
            first_name="Test"
        )
        logger.info(f"Test user created: id={test_user['id']}")
        
        for quiz_data in SAMPLE_QUIZZES:
            questions_data = [
                {
                    "text": q["text"],
                    "answers": q["answers"],
                    "correct_answer": q["correct_answer"]
                }
                for q in quiz_data["questions"]
            ]
            
            quiz_id = await quiz_service.create_quiz_with_questions(
                title=quiz_data["title"],
                creator_id=test_user["id"],
                questions_data=questions_data
            )
            
            logger.info(
                f"Quiz created: id={quiz_id}, "
                f"title='{quiz_data['title']}', "
                f"questions={len(questions_data)}"
            )
        
        logger.info(
            f"Database seeding completed successfully! "
            f"Created {len(SAMPLE_QUIZZES)} quizzes."
        )
        
    except Exception as e:
        logger.error(f"Seeding failed: {e}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(seed_database())