from tortoise import models, fields


"""Файл с моделями для базы данных"""


class Category(models.Model):
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=50, unique=True, null=False)

    class Meta:
        table = 'Category'
