# Generated by Django 3.2.13 on 2022-06-20 18:59

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100, verbose_name='Название категории/товара')),
                ('date', models.DateTimeField()),
                ('type', models.CharField(choices=[('OFFER', 'Товар'), ('CATEGORY', 'Категория')], max_length=10, verbose_name='Тип')),
                ('price', models.BigIntegerField(blank=True, null=True)),
                ('parentId', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='products.product')),
            ],
            options={
                'verbose_name': 'Продукт',
                'verbose_name_plural': 'Продукты',
            },
        ),
        migrations.CreateModel(
            name='ProductHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_id', models.UUIDField()),
                ('name', models.CharField(max_length=100, verbose_name='Название категории/товара')),
                ('date', models.DateTimeField()),
                ('type', models.CharField(choices=[('OFFER', 'Товар'), ('CATEGORY', 'Категория')], max_length=10, verbose_name='Тип')),
                ('price', models.BigIntegerField(blank=True, null=True)),
                ('price_changed', models.BooleanField(default=False)),
                ('parentId', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='products.product')),
            ],
            options={
                'verbose_name': 'История изменений модели Product',
            },
        ),
        migrations.AddIndex(
            model_name='producthistory',
            index=models.Index(fields=['product_id'], name='product_history_product_id_idx'),
        ),
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['id'], name='product_id_idx'),
        ),
    ]
