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
from constants import LOG_TEMPLATE, MAIN_URL, USER_AGENT

load_dotenv()

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')


def get_response(session, url, use_cache=False):
    headers = {
        'User-Agent': USER_AGENT,
    }

    if not use_cache:
        response = requests.get(url, headers=headers)
    else:
        response = session.get(url, headers=headers)

    status_code = response.status_code

    if status_code == 200:
        logging.info(
            LOG_TEMPLATE.format(status_code, len(response.content), url))
    else:
        logging.warning(
            LOG_TEMPLATE.format(status_code, len(response.content), url))

    return response


class ResponseStatusChanged(Exception):
    def __init__(self, status_code):
        self.status_code = status_code

    def __str__(self):
        return repr(self.status_code)


class CustomException(Exception):
    pass


# global last_status, current_status, bot_found_something

last_status = 200
current_status = 200
bot_found_something = None
size_unavailable = None
form_unavailable = None


def check_text_on_page(session, text):
    """Парсер текста."""
    global bot_found_something
    global last_status
    global current_status

    response = get_response(session, MAIN_URL, True)

    current_status = response.status_code
    # current_status = 403

    if current_status != last_status and current_status != 200:
        raise ResponseStatusChanged(status_code=current_status)

    soup = BeautifulSoup(response.text, features='lxml')
    result = len(soup.find_all(text=re.compile(text))) > 0

    print(soup.find_all(text=re.compile(text)))

    if result:
        logging.info(f'Текст "{text}" найден')
        return True

    logging.info(f'Текст "{text}" не найден')
    return False


async def action(bot, first_call):
    global bot_found_something
    global last_status
    global current_status
    global size_unavailable
    global form_unavailable

    try:
        session = CachedSession()

        if first_call:
            logging.info('Бот запущен')
            await bot.send_message(
                chat_id=CHAT_ID, text='Бот запущен',
                disable_notification=True)

        response = check_text_on_page(
            session, 'Наш сайт сейчас испытывает большую нагрузку')

        if response:
            if not size_unavailable:
                await bot.send_message(
                    chat_id=CHAT_ID,
                    text=f'HTTP {current_status} Сайт недоступен. Жалуется, '
                         f'что "Наш сайт сейчас испытывает большую нагрузку"')

                logging.warning('Сайт недоступен')
                size_unavailable = True

            raise CustomException

        response = check_text_on_page(
            session, 'Прием новых заявок запустится немного позже.')

        session.cache.clear()

        if response:
            if not form_unavailable:
                await bot.send_message(
                    chat_id=CHAT_ID,
                    text=f'HTTP {current_status} Форма недоступна')

                logging.warning('Форма недоступна')
                form_unavailable = True

            raise CustomException

        bot_found_something = True

        await bot.send_message(
            chat_id=CHAT_ID,
            text=f'У ИКЕА, кажется, что-то поменялось. Возможно, открыта '
                 f'форма - {MAIN_URL} [{current_status}]')
        logging.info('Бот что-то нашел! Возможно, это форма')

    except ResponseStatusChanged as status_code:
        await bot.send_message(
            chat_id=CHAT_ID,
            text=f'Что-то не так! Парсер вернулся с кодом {status_code}')
    except CustomException:
        pass
    finally:
        last_status = current_status


# async def action_ping(bot):
#     await bot.send_message(
#         chat_id=CHAT_ID, text='Просто пингуюсь', disable_notification=True)


class Timer:
    def __init__(self, interval, bot, callback):
        self._interval = interval
        self._bot = bot
        self._callback = callback
        self._is_first_call = True
        self._ok = True
        self._task = asyncio.ensure_future(self._job())

    async def _job(self):
        try:
            while self._ok:
                if not self._is_first_call:
                    await asyncio.sleep(self._interval)

                await self._callback(self._bot, self._is_first_call)

                self._is_first_call = False
        except Exception as ex:
            print(ex)

    def cancel(self):
        self._ok = False
        self._task.cancel()


if __name__ == '__main__':
    configure_logging()

    bot = Bot(token=TELEGRAM_TOKEN, parse_mode=types.ParseMode.HTML)

    timer1 = Timer(interval=180, bot=bot, callback=action)
    # timer2 = Timer(interval=3600, bot=bot, callback=action_ping)

    try:
        loop = asyncio.get_event_loop()
        loop.run_forever()
    except KeyboardInterrupt:
        timer1.cancel()
        # timer2.cancel()
