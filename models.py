from pydantic import BaseModel


"""
Раздел с описаниями форм для их валидации с использованием pydantic моделей
Все формы в последующем используются для формирования JSON-ответа


Для поиска ответов на формы для идентификации и поиска используются form_uid и author
    TODO: Сменить author на author_id при создании аккаунтов

Хранятся данные в БД sqlite и значения форм хранятся в форме текста
    TODO: Сменить БД на реляционную поддерживающую хранение чистого JSON (postgresql)

"""


""" Пример JSON Формы
    {"form_uid": 1,
    "author": "Alex",
    "time": 1653964718,
    "name": "Form by Alex",
    "fields": [ {"name": "Your name", "f_type": "input", "values": [], "value":""},
                {"name": "Tell about yourself", "f_type": "textarea", "values": [], "value":""},
                {"name": "Choose your city", "f_type": "select", "values": ["Moscow", "Novosibirsk", "Vladivistok"], "value":""}
            ]}"""

""" Пример JSON Ответа на форму
    {"form_uid": 1,
    "author": "Alice",
    "time": 1653964718,
    "value": [  {"name": "Your name", "f_type": "input", "values": [], "value":"Alice"},
                {"name": "Tell about yourself", "f_type": "textarea", "values": [], "value":"Student in Moscow State University!"},
                {"name": "Choose your city", "f_type": "select", "values": ["Moscow", "Novosibirsk", "Vladivistok"], "value":"Moscow"}
            ]
    }"""

class FormField(BaseModel):
    """Описание сущности поля формы"""

    """Название поля"""
    name: str

    """Тип поля, один из 3 вариантов: input, textarea, select
        В случае select, значение поля берется одно из вариантов в списке values"""
    f_type: str

    """Список значений для select"""
    values: list[str]

    """Указанное в ответе значение / по умолчанию пустое"""
    value: str = ""


class FormTemplate(BaseModel):
    """Описание формы"""

    """Идентификатор"""
    form_uid: int

    """Автор формы"""
    author: str

    """Unixtime timestamp времени создания формы/последней модификации"""
    time: int

    """Название формы"""
    name: str

    """Список полей формы"""
    fields: list[FormField]


class FormRecord(BaseModel):
    """Описание ответа на форму"""

    """Идентификатор формы"""
    form_uid: int

    """Автор ответа"""
    author: str

    """Unixtime timestamp времени ответа/последней модификации"""
    time: int

    """Список значения ответов на поля формы"""
    value: list[FormField]
