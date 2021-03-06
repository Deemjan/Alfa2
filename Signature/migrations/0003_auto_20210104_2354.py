# Generated by Django 3.1.2 on 2021-01-04 18:54

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('Signature', '0002_auto_20210103_2054'),
    ]

    operations = [
        migrations.AlterField(
            model_name='keytable',
            name='dateOfCreation',
            field=models.DateTimeField(default=datetime.datetime(2021, 1, 4, 18, 54, 5, 747351, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='keytable',
            name='dateOfExpiration',
            field=models.DateTimeField(default=datetime.datetime(2021, 2, 3, 18, 54, 5, 747351, tzinfo=utc), verbose_name='Срок действия подписи'),
        ),
        migrations.AlterField(
            model_name='signeddocument',
            name='document_title',
            field=models.CharField(max_length=100, unique=True),
        ),
    ]
