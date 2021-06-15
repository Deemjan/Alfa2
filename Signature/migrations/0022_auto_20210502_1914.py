# Generated by Django 3.1.2 on 2021-05-02 14:14

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('Signature', '0021_auto_20210429_1228'),
    ]

    operations = [
        migrations.AlterField(
            model_name='keytable',
            name='dateOfCreation',
            field=models.DateField(default=datetime.datetime(2021, 5, 2, 14, 14, 6, 241443, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='keytable',
            name='dateOfExpiration',
            field=models.DateField(default=datetime.datetime(2021, 6, 1, 14, 14, 6, 241443, tzinfo=utc), verbose_name='Срок действия подписи'),
        ),
        migrations.AlterField(
            model_name='signeddocument',
            name='date_for_logs',
            field=models.DateTimeField(default=datetime.datetime(2021, 5, 2, 14, 14, 6, 241443, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='signeddocument',
            name='date_of_creation',
            field=models.DateField(default=datetime.datetime(2021, 5, 2, 14, 14, 6, 241443, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='testvddocument',
            name='date_for_logs',
            field=models.DateTimeField(default=datetime.datetime(2021, 5, 2, 14, 14, 6, 241443, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='testvddocument',
            name='date_of_creation',
            field=models.DateField(default=datetime.datetime(2021, 5, 2, 14, 14, 6, 241443, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='testvkeytable',
            name='dateOfCreation',
            field=models.DateField(default=datetime.datetime(2021, 5, 2, 14, 14, 6, 241443, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='testvkeytable',
            name='dateOfExpiration',
            field=models.DateField(default=datetime.datetime(2021, 6, 1, 14, 14, 6, 241443, tzinfo=utc), verbose_name='Срок действия подписи'),
        ),
        migrations.AlterField(
            model_name='testvkeytable',
            name='key',
            field=models.BinaryField(unique=True),
        ),
        migrations.AlterField(
            model_name='testvsignedfordocument',
            name='date_signed',
            field=models.DateField(default=datetime.datetime(2021, 5, 2, 14, 14, 6, 241443, tzinfo=utc)),
        ),
    ]
