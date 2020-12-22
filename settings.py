#! /usr/bin/env python3
# -*- coding: utf-8 -*-
def save_to() -> str:
    """
    Куда сохраняем данные в файл или в MongoDB:
        mongo - Сохраняем в MongoDB
        file - Сохраняем в файл.
    :rtype: str
    """
    return 'mongo'


def data_directory() -> str:
    """
    Рабочий каталог в котором краулер сохраняет результат свой работы.
    :rtype: str
    """
    # TODO нужно создавать все необходимые директории
    return 'result/'


def mongo_db() -> str:
    """
    База данных mongo db, в которой будет храниться вся информация
    :rtype: str
    """
    return 'forum1c'


def mongo_table() -> str:
    """
    Таблица в базе данных, в которой будут храниться сообщения с форума
    :rtype: str
    """
    return 'messages'


def base_url() -> str:
    """
    Неизменяемая часть адреса для получения данных.
    :rtype: str
    """
    return 'https://partners.v8.1c.ru/forum/topic/'


def login_url() -> str:
    """
    Ссылка на страницу авторизации.
    :rtype: str
    """
    return 'https://login.1c.ru/login'


def crawl_start_id() -> int:
    """
    Идентификатор темы с которой начнется загрузка сообщений, если это первый запуск программы.
    :rtype: int
    """
    return 225_047


def max_attempts() -> int:
    """
    Максимальное количество попыток получения данных. Если за указанное число попыток не будет
    получена новая порция данных, то программа закончит свою работу.
    :rtype: int
    """
    return 50


def sleep_timer() -> float:
    """
    Время ожидания, в секундах, между обращениями к серверу.
    В идеале брать из robots.txt, но сейчас не разумно тратить время на парсинг робота.
    :rtype: float
    """
    return 1.0


def no_page_found() -> str:
    """
    Текст сообщения который возвращает форум если сообщение с указанным id не найдено.
    :rtype: str
    """
    return 'Такой страницы нет.'


def no_next_page_found() -> str:
    """
    Текст сообщения который возвращает форум если страницы с указанным id не найдено.
    :rtype: str
    """
    return "Пока еще нет такой страницы в этой теме."

