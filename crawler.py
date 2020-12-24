#! /usr/bin/env python3
# -*- coding: utf-8 -*-
from time import sleep
from bs4 import BeautifulSoup
import requests
from colorama import Fore
from my_parser import MyParser
from cache import Cache
from file_io_driver import FileIODriver
from mongo_io_driver import MongoIODriver
from secret import authorization_data
from settings import base_url, no_page_found, sleep_timer, max_attempts, login_url, crawl_start_id, save_to


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
        self.current_url_id = int(self.cache.last_id) if self.cache.last_id else crawl_start_id()
        self.current_url = ''

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

    def load_topic(self, page):
        print(Fore.BLUE + 'Найдена новая страница темы')
        self.parser.parse_page(page, self)
        self.io_driver.save_messages(self.parser)
        self.current_url_id = self.parser.next_url_id(page)

    def load_data(self):
        while self.current_url_id:
            # page=0 - первая страница темы, pageSize=Size5 - 50 сообщений на странице, максимальная порция.
            full_url = '{base_url}/topic/{url_id}'.format(base_url = self.__base_url, url_id = str(self.current_url_id))

            self.cache.last_id = self.current_url_id
            page = self.__session.get(full_url)
            if no_page_found() in page.text:
                print(Fore.RED + 'Страница не найдена')
                self.__failures += 1
                # Странная ситуация, битых ссылок в этом алгоритме быть не должно. Но если попали на такую ссылку,
                # то ищем следующую рабочую перебором.
                self.current_url_id += 1
                sleep(sleep_timer())
            else:
                print(Fore.WHITE + 'Скачана страница -->', Fore.GREEN + str(self.current_url_id))
                self.load_topic(page)
                self.__failures = 0
            if self.break_data_load():
                print(Fore.YELLOW + 'Достигнуто максимальное количество попыток. Работа завершена id',
                      str(self.current_url_id))
                break
        else:
            print(Fore.GREEN + 'Работа успешно завершена')

    def save_data(self):
        self.cache.save()
        self.io_driver.save_messages(self.parser)
