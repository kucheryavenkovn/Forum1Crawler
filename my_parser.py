#! /usr/bin/env python3
# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup

from forum_message import ForumMessage
import re


class MyParser:

    def __init__(self):
        self.messages = []

    def parse_page(self, page, crawler):
        self.messages = []  # очистим сообщения перед парсингом новой страницы.
        soup = BeautifulSoup(page.text, 'lxml')
        category = soup('div', 'topicSubject')[0].text

        for message in soup('div', 'message'):
            self.parse_message(message, category, crawler)

    def parse_message(self, message, category, crawler):
        
        message_header = message.find('div', 'subject')

        usefull_message = not message_header.find('div', {'class': 'usefulMessageImg'}) is None
        
        message_score = message_header.find('a', {'class': 'messageRating'}).attrs['title'].strip()
        
        message_author = message_header.find('span', {'class': 'userNickIconUrl'}).text.strip()
       
        message_date = message_header.find('div', {'class': 'messageDate'}).text.strip()
        
        message_id = message_header.find('div', {'class': 'subjectNumber'}).find('span').text.strip()
        
        message_text = message.find('div', 'text highlightingContainer messageTextForFormat breakWord').text.strip()

        message = ForumMessage(
            category,
            message_score,
            message_author,
            message_date,
            message_id,
            message_text,
            crawler.current_url_id,
            usefull_message,
            parser=self
        )
        self.messages.append(message)

    @staticmethod
    def next_url_id(page):
        soup = BeautifulSoup(page.text, 'lxml')
        prevTopic = soup.find('div', 'topicPage').find('div', {'class': 'previousNextTopicContainer'}).find('div', {'class': 'previousTopic nextPreviousTopic'})
        
        if prevTopic is None:
            next_url_id = False
        else:
            next_url_id = int(prevTopic.attrs['data-message-id'])

        return next_url_id

    @staticmethod
    def execution_data(page):
        """
        Execution - некий хеш, который приезжает с сервера вместе с формой входа. Этот хеш нужно
        вернуть на сервер вместе с логином и паролем. В противном случае авторизации не произойдет.
        Даже если логин и пароль будут валидными.
        :param page:
        :return:
        """
        soup = BeautifulSoup(page, 'lxml')
        return soup.findAll('input', value=True)[3].get('value', '').strip()

    @staticmethod
    def parse_score(message_score):
        """
        Парсит строковое представление рейтинга сообщения.
        :param message_score: строка вида 'Всего 0 :↑0 ↓0'. Формат: общий рейтинг, голоса "за", голоса "против".
        :return: словарь со значениями голосов разделенных по ключам:
            * total_score
            * pros_score
            * cons_score
        """
        scores = re.findall(r'\d+', message_score)

        return {
            'pros_score': int(scores[1]),
            'cons_score': int(scores[2]),
            'total_score': int(scores[1]) - int(scores[2])
        }

    @staticmethod
    def parse_user_info(message_author):
        """
        Парсит строковое представление пользователя.
        :param message_author: строка вида "Скиданов Николай (Информационные Технологии, Южно-Сахалинск)"
        :return: словарь с ключами
            * username - имя пользователя (ФИО)
            * company - наименование фирмы в которой работает пользователь
        """
        # Ожидаю, что в представлении будет одна пара скобок. Она содержит имя компании.
        try:
            company = re.findall(r'\(.+\)', message_author)[0]
            username = message_author.replace(company, '')
        except IndexError:
            username = message_author
            company = '_Unparsed_'

        return {
            'username': username.strip(),
            'company': company[1:-1]
        }
