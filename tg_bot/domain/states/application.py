from aiogram.fsm.state import State, StatesGroup


class ApplicationForm(StatesGroup):
    WaitingForCityChoice = State()
    WaitingForVacancyChoice = State()
    WaitingForFullName = State()
    WaitingForPhoneNumber = State()
    WaitingForTaxStatus = State()
    WaitingForCarTonnage = State()
    WaitingForDocumentChoice = State()
    WaitingForDocuments = State()
    WaitingForAppointmentDate = State()
