from datetime import datetime, timedelta

from django.contrib.auth.models import User
from django.db import models


# Create your models here.

class KeyTable(models.Model):
    key_id = models.AutoField(primary_key=True)
    key_name = models.CharField(max_length=100, default='Имя ключа', verbose_name='Название подписи')
    key = models.TextField(unique=True)
    dateOfCreation = models.DateTimeField(default=datetime.now())
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    dateOfExpiration = models.DateTimeField(default=datetime.now() + timedelta(days=30),
                                            verbose_name='Срок действия подписи')

    def __str__(self):
        return f"Таблица Ключей {self.key_id}"


class SignedDocument(models.Model):
    document_id = models.AutoField(primary_key=True)
    document_title = models.CharField(max_length=100)
    document_hash = models.TextField()
    public_key = models.TextField()
    signature = models.BinaryField()

    def __str__(self):
        return f"Документ {self.document_title}"
