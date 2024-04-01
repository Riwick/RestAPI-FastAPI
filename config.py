import os

from dotenv import load_dotenv

load_dotenv()

SMTP_USER = os.environ.get('SMTP_USER')
SMTP_PASS = os.environ.get('STMP_PASS')
