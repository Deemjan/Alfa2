from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


# Create your models here.

NOW = timezone.now()


class KeyTable(models.Model):

    key_id = models.AutoField(primary_key=True)
    key_name = models.CharField(max_length=100, default='Имя ключа', verbose_name='Название подписи', unique=True)
    key = models.TextField(unique=True)
    dateOfCreation = models.DateField(default=NOW)
    # user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    user = models.OneToOneField(User, on_delete=models.CASCADE, default=1)
    dateOfExpiration = models.DateField(default=NOW + timezone.timedelta(days=30),
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
    date_of_creation = models.DateField(default=NOW)
    date_for_logs = models.DateTimeField(default=NOW)

    def __str__(self):
        return f"Документ {self.document_title}"

########################################################################################################################


class TestVKeyTable(models.Model):
    key_name = models.CharField(max_length=100, default='Имя ключа', verbose_name='Название подписи', unique=True)
    key = models.BinaryField(unique=True)
    dateOfCreation = models.DateField(default=NOW)
    user = models.OneToOneField(User, on_delete=models.CASCADE, default=1)
    dateOfExpiration = models.DateField(default=NOW + timezone.timedelta(days=30),
                                        verbose_name='Срок действия подписи')

    def __str__(self):
        return f"Тестовая таблица ключей - {self.id}, название подписи - {self.key_name}, срок действия до - " \
               f"{self.dateOfExpiration} "


class TestVdDocument(models.Model):
    document_title = models.CharField(max_length=100, unique=True)
    document_file = models.FileField(upload_to='uploads/')
    # key_table_id = models.ForeignKey(KeyTable, on_delete=models.CASCADE, null=True)
    date_of_creation = models.DateField(default=NOW)
    date_for_logs = models.DateTimeField(default=NOW)
    user = models.ManyToManyField(User)

    def __str__(self):
        return f"Документ {self.document_title}"


class TestVSignedForDocument(models.Model):
    public_key = models.BinaryField()
    document_hash = models.TextField(blank=True)
    signature = models.BinaryField()
    signed = models.ForeignKey(TestVdDocument, on_delete=models.CASCADE)
    key_table_id = models.ForeignKey(TestVKeyTable, on_delete=models.CASCADE, null=True)
    date_signed = models.DateField(default=NOW)

    def __str__(self):
        return f"Подписи для документа {self.signed.document_title}"


