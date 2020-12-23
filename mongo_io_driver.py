#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import pymongo
import datetime
from secret import mongo_db_data
from settings import mongo_db, mongo_table, base_url


class MongoIODriver:
    """
    Запись в MongoDB с полями:
        * datetime - время и дата сообщения,
        * category - раздел форума,
        * topic - тема форума,
        * total_score - итоговый рейтинг сообщения: положительный рейтинг + отрицательный рейтинг,
        * pros_score - положительный рейтинг,
        * cons_score - отрицательный рейтинг,
        * id - идентификатор сообщения,
        * url - идентификатор темы,
        * full_url - идентификатор темы,
        * username - имя пользователя,
        * company - компания в которой работает пользователь,
        * city - город, в котором зарегистрирована компания,
        * text - текст сообщения.
    """
    def __init__(self):
        mongo_data = mongo_db_data()
        client = pymongo.MongoClient(mongo_data['ip'], mongo_data['port'])
        self.db = client[mongo_db()]
        self.table = self.db[mongo_table()]

    def save_messages(self, parser):
        for message in parser.messages:
            record = self.table.find_one({'id': message.id})
            if record is not None:
                # Пропускаем сообщение
                continue
            message_dict = message.message_representation()
            # Разделим компанию и город
            company = message_dict['company'].split(',')
            if len(company) > 1:
                message_dict['company'] = company[0].strip()
                message_dict['city'] = company[1].strip()
            else:
                message_dict['company'] = message_dict['company'].strip()
                message_dict['city'] = 'Неизвестно'
            # Разделим заголовок на раздел и тему
            category = message_dict['category'].strip().split('→')
            message_dict['category'] = category[0].strip()
            message_dict['topic'] = category[1].strip()
            # Приведем строковое представление даты к типу datetime
            message_dict['datetime'] = datetime.datetime.strptime(message_dict['datetime'], '%d.%m.%Y %H:%M')
            # Соберем полный адрес сообщения
            message_dict['full_url'] = 'https://partners.v8.1c.ru/forum/message/{message_url}#m_{message_url}'.format(
                message_url=message_dict['id'])

            self.table.insert_one(message_dict)
