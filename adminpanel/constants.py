from django.db import models


class MediaType(models.TextChoices):
    PHOTO = "photo", "Фото"
    DOCUMENT = "document", "Документ"
    AUDIO = "audio", "Аудио"
    VIDEO = "video", "Видео"


class ButtonType(models.TextChoices):
    TEXT = "text", "Текстовая кнопка"
    CALLBACK = "callback", "Callback кнопка"
    URL = "url", "URL кнопка"


class ProcessingApplicationType(models.TextChoices):
    FUNNEL_AGENCY = "funnel_agency", "Агент"
    FUNNEL_CPA = "funnel_cpa", "CPA"
    REFERRAL = "referral", "Реферальная"


class ApplicationStatus(models.TextChoices):
    NEW = "new", "Новая заявка"
    ACTIVE = "active", "В работе"
    CLOSED = "closed", "Завершена"


class TaxStatus(models.TextChoices):
    SMZ = "152", "Самозанятый"
    IP = "150", "Индивидуальный предприниматель"
    PHYS = "656", "Не оформлен"
    STATE = "1212", "Штат (на авто компании)"
    LEGAL = "1308", "Юридическое Лицо (все кроме ИП)"


class CarTonnage(models.TextChoices):
    UP_TO_05 = "156", "0,5 - тонн (Легковое авто)"
    UP_TO_1 = "158", "до 1 тонны (Каблук или микроавтобус)"
    UP_TO_15 = "160", "1,5 тонны (Газели и др.)"
    OVER_15 = "1106", "Штат (авто компании)"
    NO_CAR = "1284", "Несколько машин (ИП,ООО и др.)"


class DocumentType(models.TextChoices):
    LICENSE = "license", "Фото прав"
    PASSPORT = "passport", "Паспорт"
    REGISTRATION = "registration", "Регистрация"
    TAX_DOCUMENT = "tax_document", "Налоговый документ"
    OTHER = "other", "Прочие документы"
