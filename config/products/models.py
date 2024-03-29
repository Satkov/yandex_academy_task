import uuid

from django.db import models
from django.db.models.signals import pre_delete, pre_save
from django.dispatch import receiver
from django.shortcuts import get_object_or_404


class TypeChoices(models.TextChoices):
    OFFER = 'OFFER', 'Товар'
    CATEGORY = 'CATEGORY', 'Категория'


class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField('Название категории/товара', max_length=100, null=False)
    date = models.DateTimeField()
    parentId = models.ForeignKey('self', null=True, blank=True, related_name='children', on_delete=models.CASCADE)
    type = models.CharField('Тип', max_length=10, choices=TypeChoices.choices, null=False)
    price = models.BigIntegerField(null=True, blank=True)

    class Meta:
        indexes = [models.Index(fields=['id'], name='product_id_idx')]
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'

    def __str__(self):
        return f'{self.name}'


class ProductHistory(models.Model):
    product_id = models.UUIDField()
    name = models.CharField('Название категории/товара', max_length=100, null=False)
    date = models.DateTimeField()
    parentId = models.ForeignKey(Product, null=True, blank=True, on_delete=models.CASCADE)
    type = models.CharField('Тип', max_length=10, choices=TypeChoices.choices, null=False)
    price = models.BigIntegerField(null=True, blank=True)
    price_changed = models.BooleanField(default=False)

    class Meta:
        indexes = [models.Index(fields=['product_id'], name='product_history_product_id_idx')]
        verbose_name = 'История изменений модели Product'


@receiver(pre_save, sender=Product)
def pre_save_product_receiver(sender, instance, *args, **kwargs):
    obj = ProductHistory(
        product_id=instance.id,
        name=instance.name,
        date=instance.date,
        type=instance.type,
        price=instance.price
    )
    if Product.objects.filter(id=instance.id).exists() and obj.type == 'OFFER':
        obj.price_changed = get_object_or_404(Product, id=instance.id).price != instance.price
    if instance.parentId:
        obj.parentId = instance.parentId
    obj.save()


@receiver(pre_delete, sender=Product)
def pre_delete_product_receiver(sender, instance, *args, **kwargs):
    ProductHistory.objects.filter(product_id=instance.id).delete()

    if instance.type == 'CATEGORY':
        instance.children.all().delete()
