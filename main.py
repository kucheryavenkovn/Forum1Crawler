#! /usr/bin/env python3
# -*- coding: utf-8 -*-
from colorama import init
from crawler import Crawler


def save_data(crawler):
    crawler.save_data()


def main():
    """
    Собирает данные с https://partners.v8.1c.ru/forum и сохраняет либо в директорию, либо в mongoDB.
    Вариант сохранения указавается в settings.py save_to().
    Можно собирать данные по конкретной компании (settings.py filter_company())

    Необходимо самостоятельно создать модуль secret.py и разместить в нем функции:
    def authorization_data():
    return {
        'username': '', # Логин на форуме
        'password': '' # Пароль на форуме
    }

    def mongo_db_data():
    return {
        'ip': '', # IP, где расположена база
        'port': 0 # Порт, на котором открыт монго
    }

    Если используется сохранение в файл,
    то необходимо создать директорию и указать к ней путь в settings.py data_directory

    Используемые сторонние библиотеки:
        * requests
        * beautifulsoup4
        * colorama
        * pymongo

    """
    init()
    crawler = Crawler()

    try:
        crawler.load_data()

    except KeyboardInterrupt:
        save_data(crawler)

    else:
        save_data(crawler)


if __name__ == '__main__':
    main()
