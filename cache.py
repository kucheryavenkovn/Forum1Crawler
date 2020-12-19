#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import pymongo
from json import dump, load
from settings import data_directory
from settings import save_to
from secret import mongo_db_data


class Cache:

    def __init__(self):
        self.last_id = self.restore_last_id()

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
            db = client[mongo_data['db']]
            data = db.cache.find_one()
            if data is None:
                print('Внимание! Не найдена запись ID темы. Будет записана новая.')
                return 0

        return load(data)

    def save(self):
        """
        Сохраняет кеш. При повторном запуске краулера кеш восстанавливается в load()
        :return: None
        """
        if save_to() == 'file':
            with open(data_directory() + 'last_id.data', 'w') as data:
                dump(self.last_id, data)
        else:
            mongo_data = mongo_db_data()
            client = pymongo.MongoClient(mongo_data.ip, mongo_data.port)
            db = client[mongo_data.db]
            db.cache.update_one({}, self.last_id)
