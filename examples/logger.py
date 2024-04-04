import logging
import sys

"""Конфигурация логгера"""

example_model_logger = logging.Logger(name='example_logger')
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter(
    fmt="%(asctime)s - %(name)s:%(lineno)d - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

handler.setFormatter(formatter)
example_model_logger.addHandler(handler)
example_model_logger.setLevel(logging.DEBUG)
