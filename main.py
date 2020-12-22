#! /usr/bin/env python3
# -*- coding: utf-8 -*-
from colorama import init
from crawler import Crawler


def save_data(crawler):
    crawler.save_data()


def main():
    """
    Грабит данные с https://partners.v8.1c.ru/forum и сохраняет в директорию
    указанную в settings.py get_data_directory() для последующего построения модели анализа тональности.

    Необходимо самостоятельно создать модуль secret.py и разместить в нем функции:
    def authorization_data():
    return {
        'username': '', # Логин на форуме
        'password': '' # Пароль на форуме
    }

    def mongo_db_data():
    return {
        'ip': '', # IP, где расположена база
        'port':  # <int> Порт, на котором открыт монго
    }
    Используемые сторонние библиотеки:
        * requests
        * beautifulsoup4
        * colorama

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
