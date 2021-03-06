# Generated by Django 3.1.2 on 2021-01-09 20:06

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('Signature', '0005_auto_20210106_2057'),
    ]

    operations = [
        migrations.AlterField(
            model_name='keytable',
            name='dateOfCreation',
            field=models.DateField(default=datetime.datetime(2021, 1, 9, 20, 6, 12, 675917, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='keytable',
            name='dateOfExpiration',
            field=models.DateField(default=datetime.datetime(2021, 2, 8, 20, 6, 12, 675917, tzinfo=utc), verbose_name='Срок действия подписи'),
        ),
    ]
