import logging
import re

import requests
from requests_cache import CachedSession
from bs4 import BeautifulSoup

from configs import configure_logging
from constants import MAIN_URL, USER_AGENT


def get_response(url, use_cache=False):
    headers = {
        'User-Agent': USER_AGENT,
    }

    if not use_cache:
        return requests.get(url, headers=headers)

    session = CachedSession()
    return session.get(url, headers=headers)


def check_text_on_page(text):
    """Парсер текста."""

    response = get_response(MAIN_URL, False)
    soup = BeautifulSoup(response.text, features='lxml')
    result = len(soup.find_all('li', text=re.compile(text))) > 0

    if result:
        logging.info('Бот не видит изменений')
        return True

    logging.info('Бот что-то нашел')
    return False


def main():
    configure_logging()
    check_text_on_page('Прием новых заявок запустится немного позже.')


if __name__ == '__main__':
    main()
