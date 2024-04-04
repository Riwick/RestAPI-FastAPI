import os

from dotenv import load_dotenv

load_dotenv()

"""Файл с получением данные из .env файла"""

SMTP_USER = os.environ.get('SMTP_USER')
SMTP_PASS = os.environ.get('STMP_PASS')
