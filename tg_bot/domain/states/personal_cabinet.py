from aiogram.fsm.state import State, StatesGroup


class PersonalCabinetForm(StatesGroup):
    WaitingForFunnelStatus = State()
    WaitingForStatusChoice = State()
    WaitingForCityChoice = State()
    WaitingForDate = State()
