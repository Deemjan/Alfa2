from django.contrib.auth.models import User
from loguru import logger


@logger.catch
def set_document_db(filename: str, file_obj_data: object, user: object, path: str) -> None:
    """"Запрос на сохранение документа в БД"""
    users = User.objects.get(username=user)
    users.testvddocument_set.get_or_create(document_title=filename, document_file=file_obj_data)

