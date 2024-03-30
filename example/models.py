from tortoise import models, fields
from tortoise.validators import MinValueValidator


class Category(models.Model):
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=50, unique=True, null=False)

    examples: fields.ReverseRelation['ExampleModel']

    class Meta:
        table = 'Category'
        ordering = ['title']


class ExampleModel(models.Model):
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=255, null=False)
    age = fields.IntField(default=1, validators=[MinValueValidator(0)])
    price = fields.DecimalField(max_digits=10, decimal_places=2, default=1.00, validators=[MinValueValidator(0)])
    description = fields.CharField(max_length=2000, null=True)
    category: fields.ForeignKeyRelation[Category] = fields.ForeignKeyField(
        'models.Category', on_delete=fields.OnDelete.CASCADE)

    class Meta:
        table = 'Example'

