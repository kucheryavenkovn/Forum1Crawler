#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import pymongo
import datetime
from secret import mongo_db_data
from settings import mongo_db, mongo_table, base_url, datetime_format, need_emails, mongo_db_user, mongo_table_user


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
        * email - Email пользователя (получается опционально из сторонней таблицы).
        * company - компания в которой работает пользователь,
        * city - город, в котором зарегистрирована компания,
        * text - текст сообщения.
    """
    def __init__(self):
        mongo_data = mongo_db_data()
        client = pymongo.MongoClient(mongo_data['ip'], mongo_data['port'])
        self.db = client[mongo_db()]
        self.table = self.db[mongo_table()]
        self.db_user = client[mongo_db_user()]
        self.table_user = self.db_user[mongo_table_user()]

    def get_user_emails(self):
        users = self.table_user.find()
        email_users = {}

        for user in users:
            author = user['author'].split(' ')
            new_author = ' '.join(author[:2])
            email_users[new_author] = user['email']
        return email_users

    def save_messages(self, parser):
        if need_emails():
            emails = self.get_user_emails()
        else:
            emails = {}

        for message in parser.messages:
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
            message_dict['datetime'] = datetime.datetime.strptime(message_dict['datetime'], datetime_format())
            # Соберем полный адрес сообщения
            message_dict['full_url'] = '{base_url}/message/{message_url}#m_{message_url}'.format(
                base_url=base_url(), message_url=message_dict['id'])
            if need_emails():
                email = emails.get(message_dict['username'])
                if email is None:
                    email = 'Неизвестно'
                message_dict['email'] = email

            record = self.table.find_one({'id': message.id})
            if record is not None:
                # Это сообщение было добавлено раньше,
                # поэтому обновляем его, так как могли измениться оценки
                self.table.update_one({'_id': record['_id']}, {"$set": message_dict})
            else:
                self.table.insert_one(message_dict)
