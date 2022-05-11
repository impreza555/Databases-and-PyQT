class ServerError(Exception):
    """
    Класс - исключение, для обработки ошибок сервера.
    При генерации требует строку с описанием ошибки,
    полученную с сервера.
    """
    def __init__(self, text):
        """
        Инициализация класса.
        :param text: str
        """
        self.text = text

    def __str__(self):
        """
        Возвращает строку с описанием ошибки.
        :return: str
        """
        return self.text


class ReqFieldMissingError(Exception):
    def __init__(self, missing_field):
        self.missing_field = missing_field

    def __str__(self):
        return f'В принятом словаре отсутствует обязательное поле {self.missing_field}.'
