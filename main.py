import asyncio
import logging
import os
import re

import requests
from aiogram import Bot, types
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from requests_cache import CachedSession

from configs import configure_logging
from constants import MAIN_URL, USER_AGENT

load_dotenv()

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
GROUP_ID = os.environ.get('GROUP_ID')


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


async def main():
    configure_logging()

    bot = Bot(token=TELEGRAM_TOKEN, parse_mode=types.ParseMode.HTML)

    result = check_text_on_page('Прием новых заявок запустится немного позже.')

    if not result:
        await bot.send_message(
            chat_id=GROUP_ID,
            text=f'У ИКЕА, кажется, что-то поменялось. Возможно, открыта форма'
                 f' - {MAIN_URL}')


if __name__ == '__main__':
    asyncio.run(main())
