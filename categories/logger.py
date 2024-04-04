import logging
import sys


"""Конфигурация логгера"""


category_logger = logging.Logger(name='example_logger')
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter(
    fmt="%(asctime)s - %(name)s:%(lineno)d - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

handler.setFormatter(formatter)
category_logger.addHandler(handler)
category_logger.setLevel(logging.DEBUG)