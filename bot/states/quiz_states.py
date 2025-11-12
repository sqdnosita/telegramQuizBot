from aiogram.fsm.state import State, StatesGroup

class CreateQuizStates(StatesGroup):

    waiting_for_title = State()
    waiting_for_question_count = State()
    waiting_for_question_text = State()
    waiting_for_answers = State()
    waiting_for_correct_answer = State()