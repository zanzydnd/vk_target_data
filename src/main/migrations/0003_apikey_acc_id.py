# Generated by Django 3.1.7 on 2021-10-08 19:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_auto_20211008_2244'),
    ]

    operations = [
        migrations.AddField(
            model_name='apikey',
            name='acc_id',
            field=models.CharField(default='7960621', max_length=255),
        ),
    ]
