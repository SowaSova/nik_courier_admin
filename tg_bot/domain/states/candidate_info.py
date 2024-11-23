from aiogram.fsm.state import State, StatesGroup


class TrainingCandidateForm(StatesGroup):
    WaitingForCityChoice = State()
    WaitingForVacancyChoice = State()
