import smtplib
from email.message import EmailMessage

from config import SMTP_USER, SMTP_PASS


"""Файл с настройками для отправки подтверждения почты пользователя по почте"""


SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 465


def get_email_template(email_addr: str, token: str):

    """В этой функции происходит создание самого письма, который отправляется пользователю"""

    email = EmailMessage()
    email['Subject'] = 'RestAPI-FastAPI'  # Заголовок
    email['From'] = SMTP_USER  # От кого
    email['To'] = email_addr  # Кому

    email.set_content(  # Само тело письма с токеном
        '<div>'
        f'<h1>Здравствуйте, {email_addr}, вот ваш токен:</h1>'
        f'<h2>{token}</h2>'
        '</div>',
        subtype='html'
    )
    return email


def send_email(email_addr: str, token: str):

    """Эта функция отвечает за отправку письма"""

    email = get_email_template(email_addr, token)

    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:  # Создание соединения
        server.login(user=SMTP_USER, password=SMTP_PASS)  # Авторизация для отправки сообщения
        server.send_message(email)  # Сама отправка

