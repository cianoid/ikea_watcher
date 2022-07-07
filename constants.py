from pathlib import Path

BASE_DIR = Path(__file__).parent
MAIN_URL = 'https://www.ikea.com/ru/ru/campaigns/info-hub-pub38dba770'

LOG_DIR = BASE_DIR / 'logs'
LOG_FILE = LOG_DIR / 'parser.log'

DATETIME_FORMAT = '%Y-%m-%d_%H-%M-%S'

LOG_SIZE = 10 ** 6
LOG_COUNT = 5
LOG_FORMAT = '"%(asctime)s - [%(levelname)s] - %(message)s"'
LOG_DT_FORMAT = '%d.%m.%Y %H:%M:%S'
LOG_ENCODING = 'utf-8'

USER_AGENT = (
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:102.0) Gecko/20100101 '
    'Firefox/102.0')

LOG_TEMPLATE = 'HTTP {}, Size {} bytes, Request: {}'

MSG_BOT_STARTED = 'Бот запущен'
MSG_LOG_NO_SITE = 'Сайт недоступен'
MSG_NO_SITE = (
        'HTTP {} ' + MSG_LOG_NO_SITE + '. Жалуется, что "{}"')
MSG_LOG_NO_FORM = 'Форма недоступна'
MSG_NO_FORM = 'HTTP {} ' + MSG_LOG_NO_FORM
MSG_FORM = (
    'У ИКЕА, кажется, что-то поменялось. Возможно, открыта форма - '
    '' + MAIN_URL + ' [{}]')
MSG_LOG_FORM = 'Бот что-то нашел! Возможно, это форма'
MSG_LOG_ERROR = 'Что-то не так! Парсер вернулся с кодом {}'
MSG_LOG_TEXT_FOUND = 'Текст "{}" найден'
MSG_LOG_TEXT_NOT_FOUND = 'Текст "{}" не найден'
