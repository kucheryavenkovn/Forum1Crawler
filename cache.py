#! /usr/bin/env python3
# -*- coding: utf-8 -*-
from json import dump, load

from settings import data_directory
from settings import save_to
from mongo_io_driver import last_id_mongo


class Cache:

    def __init__(self):
        self.last_id = self.restore_last_id()

    @staticmethod
    def restore_last_id():
        """
        Восстанавливет ID последней отработанной темы.
        :return: None
        """
        try:
            if save_to() == 'file':
                data = open(data_directory() + 'last_id.data')
            else:
                # TODO Add mongo cache
                data = last_id_mongo()
        except IOError:
            print('Внимание! Не найден файл ID темы. Будет создан новый.')
            return 0
        else:
            with data:
                return load(data)

    def save(self):
        """
        Сохраняет кеш на диск. При повторном запуске краулера кеш восстанавливается в load()
        :return: None
        """
        with open(data_directory() + 'last_id.data', 'w') as data:
            dump(self.last_id, data)
