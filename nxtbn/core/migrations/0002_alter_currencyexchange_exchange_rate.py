# Generated by Django 4.2.11 on 2024-05-25 06:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='currencyexchange',
            name='exchange_rate',
            field=models.IntegerField(default=0),
        ),
    ]