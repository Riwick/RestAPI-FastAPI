from tortoise import models, fields
from tortoise.validators import MinValueValidator

from categories.models import Category


class ExampleModel(models.Model):
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=255, null=False)
    age = fields.IntField(validators=[MinValueValidator(1)], null=True, default=1)
    price = fields.DecimalField(max_digits=10, decimal_places=2, default=1.00, validators=[MinValueValidator(1)])
    description = fields.CharField(max_length=2000, null=True)
    category: fields.ForeignKeyRelation[Category] = fields.ForeignKeyField(
        'models.Category', on_delete=fields.OnDelete.CASCADE)

    class Meta:
        table = 'Example'
