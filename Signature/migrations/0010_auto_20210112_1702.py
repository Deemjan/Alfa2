# Generated by Django 3.1.2 on 2021-01-12 12:02

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('Signature', '0009_auto_20210110_1715'),
    ]

    operations = [
        migrations.AlterField(
            model_name='keytable',
            name='dateOfCreation',
            field=models.DateField(default=datetime.datetime(2021, 1, 12, 12, 2, 11, 857691, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='keytable',
            name='dateOfExpiration',
            field=models.DateField(default=datetime.datetime(2021, 2, 11, 12, 2, 11, 857691, tzinfo=utc), verbose_name='Срок действия подписи'),
        ),
    ]