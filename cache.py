#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import pymongo
from json import dump, load
from settings import data_directory, save_to, mongo_db
from secret import mongo_db_data


class Cache:

    def __init__(self):
        self.last_id = self.restore_last_id()
        self.last_date = self.restore_last_date()

    @staticmethod
    def restore_last_id():
        """
        Восстанавливет ID последней отработанной темы.
        :return: None
        """
        if save_to() == 'file':
            try:
                data = open(data_directory() + 'last_id.data')
            except IOError:
                print('Внимание! Не найден файл ID темы. Будет создан новый.')
                return 0
        else:
            mongo_data = mongo_db_data()
            client = pymongo.MongoClient(mongo_data['ip'], mongo_data['port'])
            db = client[mongo_db()]
            record = db.cache.find_one()
            if record is None:
                print('Внимание! Не найдена запись ID темы. Будет записана новая.')
                return 0
            data = record['last_id']

        return load(data)

    @staticmethod
    def restore_last_date():
        """
        Восстанавливет ID последней отработанной темы.
        :return: None
        """
        if save_to() == 'file':
            try:
                data = open(data_directory() + 'last_datetime.data')
            except IOError:
                print('Внимание! Не найден файл с датой последней темы. Будет создан новый.')
                return None
        else:
            mongo_data = mongo_db_data()
            client = pymongo.MongoClient(mongo_data['ip'], mongo_data['port'])
            db = client[mongo_db()]
            record = db.cache.find_one()
            if record is None:
                print('Внимание! Не найдена запись с датой последней темы. Будет записана новая.')
                return None
            data = record['datetime']

        return load(data)

    def save(self):
        """
        Сохраняет кеш. При повторном запуске краулера кеш восстанавливается в load()
        :return: None
        """
        if save_to() == 'file':
            with open(data_directory() + 'last_id.data', 'w') as data:
                dump(self.last_id, data)
            with open(data_directory() + 'last_datetime.data', 'w') as data:
                dump(self.last_date, data)

        else:
            mongo_data = mongo_db_data()
            client = pymongo.MongoClient(mongo_data["ip"], mongo_data["port"])
            db = client[mongo_db()]

            db.cache.insert_one({'last_id': self.last_id, 'last_date': self.last_date})
