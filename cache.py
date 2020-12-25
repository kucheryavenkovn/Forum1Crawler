#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import pymongo
from json import dump, load
from settings import data_directory, save_to, mongo_db
from secret import mongo_db_data


class Cache:

    def __init__(self):
        self.last_date = self.restore_last_date()

    @staticmethod
    def restore_last_date():
        """
        Восстанавливет ID последней отработанной темы.
        :return: None
        """
        if save_to() == 'file':
            try:
                data = open(data_directory() + 'last_datetime.data')
                data = load(data)
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
            data = record['last_date']

        return data

    def save(self):
        """
        Сохраняет кеш. При повторном запуске краулера кеш восстанавливается в load()
        :return: None
        """
        if save_to() == 'file':
            with open(data_directory() + 'last_datetime.data', 'w') as data:
                dump(self.last_date, data)

        else:
            mongo_data = mongo_db_data()
            client = pymongo.MongoClient(mongo_data["ip"], mongo_data["port"])
            db = client[mongo_db()]
            cache = db.cache.find_one()
            if cache is None:
                db.cache.insert_one({'last_date': self.last_date})
            else:
                db.cache.update_one({'_id': cache['_id']}, {"$set": {'last_date': self.last_date}})
