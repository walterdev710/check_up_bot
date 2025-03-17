from aiogram.fsm.state import State, StatesGroup

class TestStates(StatesGroup):
    choosing_category = State()
    answering_questions = State()