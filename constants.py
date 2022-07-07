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

USER_AGENT = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:102.0) '
              'Gecko/20100101 Firefox/102.0')

LOG_TEMPLATE = 'HTTP {}, Size {} bytes, Request: {}'
