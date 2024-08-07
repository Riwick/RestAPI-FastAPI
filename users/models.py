from tortoise import models, fields


"""Файл с моделями для базы данных"""


class User(models.Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=50, unique=True, null=False)
    password = fields.CharField(max_length=100)
    email = fields.CharField(max_length=100, unique=True)
    is_superuser = fields.BooleanField(default=False)
    date_joined = fields.DatetimeField(auto_now_add=True)
    is_active = fields.BooleanField(default=True)  # Активен ли его аккаунт(можно ли на него зайти)

    confirm_code = fields.TextField()
    confirmed = fields.BooleanField(default=False)  # Подтвердил ли пользователь почту

    class Meta:
        table = 'User'
