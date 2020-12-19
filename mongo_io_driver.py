#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import pymongo
from secret import mongo_db_data


class MongoIODriver:
    """
    Запись в MongoDB с полями:
        * datetime - время и дата сообщения,
        * category - раздел форума,
        * total_score - итоговый рейтинг сообщения: положительный рейтинг + отрицательный рейтинг,
        * pros_score - положительный рейтинг,
        * cons_score - отрицательный рейтинг,
        * id - идентификатор сообщения,
        * url - ссылка на сообщение,
        * username - имя пользователя,
        * company - компания в которой работает пользователь,
        * text - текст сообщения.
    """
    def __init__(self):
        mongo_data = mongo_db_data()
        client = pymongo.MongoClient(mongo_data['ip'], mongo_data['port'])
        self.db = client[mongo_data['db']]
        self.table = self.db[mongo_data['table']]

    def save_messages(self, parser):
        for message in parser.messages:
            self.table.insert_one(message)