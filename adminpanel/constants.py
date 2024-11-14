from django.db import models

BOT_NAME = "sowa_hw_bot"


class ProcessingApplicationType(models.TextChoices):
    FUNNEL_AGENCY = "funnel_agency", "Воронка 1 (агент)"
    FUNNEL_CPA = "funnel_cpa", "Воронка 2 (CPA)"
    REFERRAL = "referral", "Реферальная"


class ApplicationStatus(models.TextChoices):
    NEW = "new", "Новая заявка"
    ACTIVE = "active", "В работе"
    CLOSED = "closed", "Завершена"


class TaxStatus(models.TextChoices):
    SMZ = "СМЗ", "Самозанятый"
    IP = "ИП", "Индивидуальный предприниматель"
    PHYS = "Физ", "Физическое лицо"


class CarTonnage(models.TextChoices):
    UP_TO_05 = "0.5", "до 0.5 т"
    UP_TO_1 = "1", "до 1 т"
    UP_TO_15 = "1.5", "до 1.5 т"
    OVER_15 = "1.5+", "от 1.5 т"
    NO_CAR = "Нет", "Нет машины (нужна аренда)"


class DocumentType(models.TextChoices):
    LICENSE = "license", "Фото прав"
    PASSPORT = "passport", "Паспорт"
    REGISTRATION = "registration", "Регистрация"
    TAX_DOCUMENT = "tax_document", "Налоговый документ"
    OTHER = "other", "Прочие документы"
