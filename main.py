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

    response = get_response(MAIN_URL, True)
    soup = BeautifulSoup(response.text, features='lxml')
    return len(soup.find_all('li', text=re.compile(text))) > 0


def main():
    configure_logging()
    logging.info('Парсер запущен!')

    check_text_on_page(
        'Прием новых заявок запустится немного позже.')

    logging.info('Парсер завершил работу.')


if __name__ == '__main__':
    main()
