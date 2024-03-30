from tortoise import models, fields


class Category(models.Model):
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=50, unique=True, null=False)

    class Meta:
        table = 'Category'
