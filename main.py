import asyncio
import logging
import os
import re

import requests
from aiogram import Bot, types
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from requests_cache import CachedSession

import constants
from configs import configure_logging

load_dotenv()

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')


def get_response(session, url, use_cache=False):
    response = {True: session, False: requests}[
        use_cache].get(url, headers={'User-Agent': constants.USER_AGENT})

    status_code = response.status_code

    getattr(
        logging, {200: 'info', None: 'warning'}.get(status_code, None))(
        constants.LOG_TEMPLATE.format(status_code, len(response.content), url))

    return response


class ResponseStatusChanged(Exception):
    def __init__(self, status_code):
        self.status_code = status_code

    def __str__(self):
        return repr(self.status_code)


class CustomException(Exception):
    pass


last_status = 200
current_status = 200
bot_found_something = None
site_unavailable = None
form_unavailable = None


def check_text_on_page(session, text):
    """Парсер текста."""

    global bot_found_something
    global last_status
    global current_status

    response = get_response(session, constants.MAIN_URL, True)

    current_status = response.status_code

    if current_status != last_status and current_status != 200:
        raise ResponseStatusChanged(status_code=current_status)

    soup = BeautifulSoup(response.text, features='lxml')
    result = len(soup.find_all(text=re.compile(text))) > 0

    if result:
        logging.info(constants.MSG_LOG_TEXT_FOUND.format(text))
        return True

    logging.info(constants.MSG_LOG_TEXT_NOT_FOUND.format(text))
    return False


async def action(bot, first_call):
    global bot_found_something
    global last_status
    global current_status
    global site_unavailable
    global form_unavailable

    texts = {
        'site_unavailable': 'Наш сайт сейчас испытывает большую нагрузку',
        'form_unavailable': 'Прием новых заявок запустится немного позже.'
    }

    try:
        session = CachedSession()

        if first_call:
            logging.info(constants.MSG_BOT_STARTED)
            await bot.send_message(
                chat_id=CHAT_ID, text=constants.MSG_BOT_STARTED,
                disable_notification=True)

        response = check_text_on_page(session, texts['site_unavailable'])

        if response:
            if not site_unavailable:
                await bot.send_message(
                    chat_id=CHAT_ID,
                    text=constants.MSG_NO_SITE.format(
                        current_status, texts['site_unavailable']))

                logging.warning(constants.MSG_LOG_NO_SITE)
                site_unavailable = True

            raise CustomException

        response = check_text_on_page(session, texts['form_unavailable'])

        session.cache.clear()

        if response:
            if not form_unavailable:
                await bot.send_message(
                    chat_id=CHAT_ID,
                    text=constants.MSG_NO_FORM.format(current_status))

                logging.warning(constants.MSG_LOG_NO_FORM)
                form_unavailable = True

            raise CustomException

        bot_found_something = True

        await bot.send_message(
            chat_id=CHAT_ID,
            text=constants.MSG_FORM.format(current_status))
        logging.info(constants.MSG_LOG_FORM)

    except ResponseStatusChanged as status_code:
        await bot.send_message(
            chat_id=CHAT_ID, text=constants.MSG_LOG_ERROR.format(status_code))
    except CustomException:
        pass
    finally:
        last_status = current_status


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

    try:
        loop = asyncio.get_event_loop()
        loop.run_forever()
    except KeyboardInterrupt:
        timer1.cancel()
