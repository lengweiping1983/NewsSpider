# -*- coding: utf-8 -*-
import logging
from datetime import datetime


current_time = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')

construction_formatter_fill = '[%(asctime)s](%(levelname)5s)(%(processName)s)' \
                              '(%(process)d):%(message)s'
formatter = logging.Formatter(construction_formatter_fill)

logger = logging.getLogger()
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)
