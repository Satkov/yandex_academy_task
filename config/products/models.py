import uuid

from django.db import models


class Product(models.Model):
    TYPE_CHOICES = [
        ('OFFER', 'Товар'),
        ('CATEGORY', 'Категория')
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField('Название категории/товара', max_length=100, null=False)
    date = models.DateTimeField(auto_now=True)
    parentId = models.ForeignKey('self', null=True, blank=True, related_name='children', on_delete=models.CASCADE)
    type = models.CharField('Тип', max_length=10, choices=TYPE_CHOICES, null=False)
    price = models.BigIntegerField(null=True, blank=True)

    class Meta:
        indexes = [models.Index(fields=['id'], name='product_id_idx')]
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'

    def __str__(self):
        return f'{self.name}'
