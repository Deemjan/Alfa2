from datetime import datetime, timedelta

import django
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


# Create your models here.

class KeyTable(models.Model):
    now = timezone.now()
    key_id = models.AutoField(primary_key=True)
    key_name = models.CharField(max_length=100, default='Имя ключа', verbose_name='Название подписи', unique=True)
    key = models.TextField(unique=True)
    dateOfCreation = models.DateField(default=now)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    dateOfExpiration = models.DateField(default=now + timezone.timedelta(days=30),
                                            verbose_name='Срок действия подписи')

    def __str__(self):
        return f"Таблица Ключей - {self.key_id}, название подписи - {self.key_name}, срок действия до - " \
               f"{self.dateOfExpiration} "


class SignedDocument(models.Model):
    document_id = models.AutoField(primary_key=True)
    document_title = models.CharField(max_length=100, unique=True)
    document_hash = models.TextField()
    public_key = models.TextField()
    signature = models.BinaryField()
    key_table_id = models.ForeignKey(KeyTable, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"Документ {self.document_title}"
