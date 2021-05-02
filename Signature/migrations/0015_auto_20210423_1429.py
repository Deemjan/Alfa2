# Generated by Django 3.1.2 on 2021-04-23 09:29

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('Signature', '0014_auto_20210415_1237'),
    ]

    operations = [
        migrations.AlterField(
            model_name='keytable',
            name='dateOfCreation',
            field=models.DateField(default=datetime.datetime(2021, 4, 23, 9, 29, 47, 211472, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='keytable',
            name='dateOfExpiration',
            field=models.DateField(default=datetime.datetime(2021, 5, 23, 9, 29, 47, 211472, tzinfo=utc), verbose_name='Срок действия подписи'),
        ),
        migrations.AlterField(
            model_name='signeddocument',
            name='date_for_logs',
            field=models.DateTimeField(default=datetime.datetime(2021, 4, 23, 9, 29, 47, 211472, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='signeddocument',
            name='date_of_creation',
            field=models.DateField(default=datetime.datetime(2021, 4, 23, 9, 29, 47, 211472, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='testvddocument',
            name='date_for_logs',
            field=models.DateTimeField(default=datetime.datetime(2021, 4, 23, 9, 29, 47, 211472, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='testvddocument',
            name='date_of_creation',
            field=models.DateField(default=datetime.datetime(2021, 4, 23, 9, 29, 47, 211472, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='testvddocument',
            name='document_hash',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='testvkeytable',
            name='dateOfCreation',
            field=models.DateField(default=datetime.datetime(2021, 4, 23, 9, 29, 47, 211472, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='testvkeytable',
            name='dateOfExpiration',
            field=models.DateField(default=datetime.datetime(2021, 5, 23, 9, 29, 47, 211472, tzinfo=utc), verbose_name='Срок действия подписи'),
        ),
    ]
