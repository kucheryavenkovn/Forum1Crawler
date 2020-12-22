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
        * text - текст сообщения.
    """
    def __init__(self):
        mongo_data = mongo_db_data()
        client = pymongo.MongoClient(mongo_data['ip'], mongo_data['port'])
        self.db = client[mongo_db()]
        self.table = self.db[mongo_table()]

    def save_messages(self, parser):
        for message in parser.messages:
            message_dict = message.message_representation()
            # Разделим заголовок на раздел и тему
            category = message_dict['category'].strip().split('→')
            message_dict['category'] = category[0].strip()
            message_dict['topic'] = category[1].strip()
            # Приведем строковое представление даты к типу datetime
            message_dict['datetime'] = datetime.datetime.strptime(message_dict['datetime'], '%d.%m.%Y %H:%M')
            # Соберем полный адрес сообщения
            message_dict['full_url'] = '{base_url}/t/{topic_url}/m/{message_url}'.format(
                base_url=base_url(), topic_url=message_dict['url'], message_url=message_dict['id'])

            self.table.insert_one(message_dict)
