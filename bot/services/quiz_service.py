from typing import Optional

import aiosqlite

from bot.database.connection import DatabaseConnection
from bot.repositories.answer_repository import AnswerRepository
from bot.repositories.question_repository import QuestionRepository
from bot.repositories.quiz_repository import QuizRepository

class QuizService:
    
    def __init__(
        self,
        quiz_repository: QuizRepository,
        question_repository: QuestionRepository,
        answer_repository: AnswerRepository,
        db_path: str
    ) -> None:
        self._quiz_repository: QuizRepository = quiz_repository
        self._question_repository: QuestionRepository = question_repository
        self._answer_repository: AnswerRepository = answer_repository
        self._db_path: str = db_path

    async def get_available_quizzes(self) -> list[dict]:
        return await self._quiz_repository.get_all_quizzes()
    
    async def get_quizzes_paginated(
        self,
        page: int = 1,
        page_size: int = 6
    ) -> dict:
        return await self._quiz_repository.get_quizzes_paginated(
            page,
            page_size
        )

    async def get_quiz_with_questions(self, quiz_id: int) -> Optional[dict]:
        if quiz_id <= 0:
            raise ValueError("quiz_id must be positive integer")
        
        quiz = await self._quiz_repository.get_quiz_by_id(quiz_id)
        
        if quiz is None:
            return None
        
        questions = await self._question_repository.get_questions_by_quiz_id(
            quiz_id
        )
        
        for question in questions:
            answers = await self._answer_repository.get_answers_by_question_id(
                question['id']
            )
            question['answers'] = answers
        
        quiz['questions'] = questions
        
        return quiz

    async def create_quiz_with_questions(
        self,
        title: str,
        creator_id: int,
        questions_data: list[dict]
    ) -> int:
        if not title or not title.strip():
            raise ValueError("Quiz title cannot be empty")
        
        if creator_id <= 0:
            raise ValueError("creator_id must be positive integer")
        
        if not questions_data:
            raise ValueError("Quiz must have at least one question")
        
        for idx, question in enumerate(questions_data, 1):
            if not question.get('text') or not question['text'].strip():
                raise ValueError(
                    f"Question {idx} text cannot be empty"
                )
            
            answers = question.get('answers', [])
            if len(answers) < 2:
                raise ValueError(
                    f"Question {idx} must have at least 2 answers"
                )
            if len(answers) > 6:
                raise ValueError(
                    f"Question {idx} cannot have more than 6 answers"
                )
            
            correct_answer = question.get('correct_answer', 0)
            if correct_answer < 1 or correct_answer > len(answers):
                raise ValueError(
                    f"Question {idx} correct_answer must be between "
                    f"1 and {len(answers)}"
                )
        
        async with DatabaseConnection(self._db_path) as conn:
            cursor = await conn.execute(
                """
                INSERT INTO quizzes (title, creator_id)
                VALUES (?, ?)
                """,
                (title.strip(), creator_id)
            )
            
            if cursor.lastrowid is None:
                raise RuntimeError("Failed to create quiz")
            
            quiz_id = cursor.lastrowid
            
            for position, question_data in enumerate(questions_data, 1):
                question_cursor = await conn.execute(
                    """
                    INSERT INTO questions 
                    (quiz_id, text, position, correct_answer)
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        quiz_id,
                        question_data['text'].strip(),
                        position,
                        question_data['correct_answer']
                    )
                )
                
                if question_cursor.lastrowid is None:
                    raise RuntimeError(
                        f"Failed to create question {position}"
                    )
                
                question_id = question_cursor.lastrowid
                
                for answer_pos, answer_text in enumerate(
                    question_data['answers'], 1
                ):
                    await conn.execute(
                        """
                        INSERT INTO answers 
                        (question_id, text, position)
                        VALUES (?, ?, ?)
                        """,
                        (question_id, answer_text.strip(), answer_pos)
                    )
            
            await conn.commit()
            
            return quiz_id

    async def calculate_quiz_result(
        self,
        quiz_id: int,
        user_answers: dict[int, int]
    ) -> dict:
        if quiz_id <= 0:
            raise ValueError("quiz_id must be positive integer")
        
        quiz = await self._quiz_repository.get_quiz_by_id(quiz_id)
        
        if quiz is None:
            raise ValueError(f"Quiz with id {quiz_id} does not exist")
        
        questions = await self._question_repository.get_questions_by_quiz_id(
            quiz_id
        )
        
        if not questions:
            return {
                'quiz_id': quiz_id,
                'total_questions': 0,
                'correct_answers': 0,
                'percentage': 0.0
            }
        
        correct_count = 0
        
        for question in questions:
            question_id = question['id']
            correct_answer = question['correct_answer']
            user_answer = user_answers.get(question_id)
            
            if user_answer == correct_answer:
                correct_count += 1
        
        total_questions = len(questions)
        percentage = (correct_count / total_questions * 100) if total_questions > 0 else 0.0
        
        return {
            'quiz_id': quiz_id,
            'total_questions': total_questions,
            'correct_answers': correct_count,
            'percentage': round(percentage, 2)
        }