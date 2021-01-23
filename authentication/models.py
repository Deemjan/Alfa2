from django.contrib.auth.models import User
from django.db import models

# Create your models here.
# from django.utils import timezone
#
# NOW = timezone.now()
#
#
# class Logs(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
#     record = models.TextField()
#     date_of_creation = models.DateField(default=NOW)
#
#     def __str__(self):
#         return f"Запись"