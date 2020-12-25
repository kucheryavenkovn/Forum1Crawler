#! /usr/bin/env python3
# -*- coding: utf-8 -*-
from time import sleep
from bs4 import BeautifulSoup
import requests
import datetime
from colorama import Fore
from my_parser import MyParser
from cache import Cache
from file_io_driver import FileIODriver
from mongo_io_driver import MongoIODriver
from secret import authorization_data
from settings import base_url, no_page_found, sleep_timer, max_attempts, login_url, crawl_start_date, \
    save_to, filter_company, datetime_format


class Crawler:

    def __init__(self):
        self.parser = MyParser()
        self.__base_url = base_url()
        self.__login_url = login_url()
        self.__failures = 0
        self.__session = self.open_session()
        self.cache = Cache()
        if save_to() == 'file':
            self.io_driver = FileIODriver()
        else:
            self.io_driver = MongoIODriver()
        self.current_url_id = 0
        last_date = self.cache.last_date if self.cache.last_date is not None else crawl_start_date()
        self.last_date_processing = datetime.datetime.strptime(last_date, datetime_format()).date()

        self.all_pages_done = False

    def break_data_load(self):
        return True if self.__failures == max_attempts() else False

    def open_session(self):

        session = requests.Session()

        auth_data = authorization_data()
        
        url = login_url()
        session.headers = {"Connection": "keep-alive"}
        response = session.get(url, allow_redirects=False)
        cooks = response.headers.get('Set-Cookie').split(';')[0]
        
        soup = BeautifulSoup(response.text, 'html.parser')
        auth_data['execution'] = soup.findAll(attrs={'name': 'execution'})[0]['value']

        post_body = "inviteCode=&username=" + auth_data['username']
        post_body += "&password=" + auth_data['password']
        post_body += "&execution=" + auth_data['execution']
        post_body += "&_eventId=submit"
        post_body += "&geolocation="
        post_body += "&submit=Войти"
        post_body += "&rememberMe=on"

        session.headers.update(
            {"Content-Type": "application/x-www-form-urlencoded", "Cookie": cooks + "; i18next=ru-RU"})
        session.headers.update({"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/534.30 (KHTML, like Gecko) Ubuntu/11.04 Chromium/12.0.742.112 Chrome/12.0.742.112 Safari/534.30"})
        session.post(url, data=post_body.encode('utf-8'), allow_redirects=False)

        return session

    def process_messages(self):
        message_to_delete = []
        all_messages_before_the_date = True
        for message in self.parser.messages:
            # Проверяем дату всех сообщений в теме, если они все меньше чем дата последней обработки,
            # то заканчиваем работу программы.
            message_date = datetime.datetime.strptime(message.datetime, datetime_format()).date()
            if self.last_date_processing < message_date:
                all_messages_before_the_date = False
            else:
                # Дата сообщения меньше, чем дата последней обработки.
                # Поэтому не добавляем это сообщение для сохранения.
                message_to_delete.append(message)
                continue

            # Фильтруем сообщения по компании
            if len(filter_company()) > 0:
                company = message.company.split(',')[0].strip()
                if company not in filter_company():
                    # Если не соответствует фильтр, то не добавляем сообщение
                    message_to_delete.append(message)

        for message in message_to_delete:
            self.parser.messages.remove(message)

        if all_messages_before_the_date:
            self.all_pages_done = True

        print(Fore.GREEN + 'Добавлено {} сообщений из темы'.format(len(self.parser.messages)))

    def load_topic(self, page):
        print(Fore.BLUE + 'Найдена новая страница темы')
        self.parser.parse_page(page, self)
        self.process_messages()
        self.io_driver.save_messages(self.parser)

    def load_data(self):
        number_page = 0
        while not self.all_pages_done:
            # Парсим страничку со всеми темами, отсортированные по дате последнего сообщения
            # Идем по этим страничкам до тех пор, пока не будет выполнено условие, что все сообщения в теме младше,
            # чем дата последней обработки форума.
            full_url = '{base_url}/forum/186/topics?page={number_page}'.format(
                base_url=self.__base_url, number_page=number_page)
            page = self.__session.get(full_url)
            for topic in self.parser.get_topics(page):
                self.current_url_id = int(topic)
                page_url = '{base_url}/topic/{topic}'.format(base_url=base_url(), topic=topic)
                page = self.__session.get(page_url)
                if no_page_found() in page.text:
                    print(Fore.RED + 'Страница не найдена')
                    self.__failures += 1
                    # Такая ситуация возможна, если тема была удалена. Поэтому просто переходим к следующей теме.
                    sleep(sleep_timer())
                else:
                    print(Fore.WHITE + 'Скачана страница -->', Fore.GREEN + topic)
                    self.load_topic(page)
                    self.__failures = 0

                if self.break_data_load():
                    print(Fore.YELLOW + 'Достигнуто максимальное количество попыток. Работа завершена id {}'.format(
                        topic))
                    break

                if self.all_pages_done:
                    break
            number_page += 1

        else:
            print(Fore.GREEN + 'Работа успешно завершена')

    def save_data(self):
        self.cache.last_date = datetime.datetime.now().strftime(datetime_format())
        self.cache.save()
        self.io_driver.save_messages(self.parser)
