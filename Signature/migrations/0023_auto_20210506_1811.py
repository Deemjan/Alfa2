# Generated by Django 3.1.2 on 2021-05-06 13:11

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('Signature', '0022_auto_20210502_1914'),
    ]

    operations = [
        migrations.AlterField(
            model_name='keytable',
            name='dateOfCreation',
            field=models.DateField(default=datetime.datetime(2021, 5, 6, 13, 11, 42, 274556, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='keytable',
            name='dateOfExpiration',
            field=models.DateField(default=datetime.datetime(2021, 6, 5, 13, 11, 42, 274556, tzinfo=utc), verbose_name='Срок действия подписи'),
        ),
        migrations.AlterField(
            model_name='signeddocument',
            name='date_for_logs',
            field=models.DateTimeField(default=datetime.datetime(2021, 5, 6, 13, 11, 42, 274556, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='signeddocument',
            name='date_of_creation',
            field=models.DateField(default=datetime.datetime(2021, 5, 6, 13, 11, 42, 274556, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='testvddocument',
            name='date_for_logs',
            field=models.DateTimeField(default=datetime.datetime(2021, 5, 6, 13, 11, 42, 274556, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='testvddocument',
            name='date_of_creation',
            field=models.DateField(default=datetime.datetime(2021, 5, 6, 13, 11, 42, 274556, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='testvkeytable',
            name='dateOfCreation',
            field=models.DateField(default=datetime.datetime(2021, 5, 6, 13, 11, 42, 274556, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='testvkeytable',
            name='dateOfExpiration',
            field=models.DateField(default=datetime.datetime(2021, 6, 5, 13, 11, 42, 274556, tzinfo=utc), verbose_name='Срок действия подписи'),
        ),
        migrations.AlterField(
            model_name='testvsignedfordocument',
            name='date_signed',
            field=models.DateField(default=datetime.datetime(2021, 5, 6, 13, 11, 42, 274556, tzinfo=utc)),
        ),
    ]
