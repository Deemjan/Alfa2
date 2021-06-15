from django.contrib.auth.models import User
from loguru import logger

from Signature.cryptography import _add_signed_doc
from Signature.models import TestVdDocument, TestVKeyTable, TestVSignedForDocument

logger.add("debug_signature_services.json", format="{time} {level} {message}",
           level="DEBUG", rotation="1 week", compression="zip", serialize=True)


@logger.catch
def set_document_db(filename: str, file_obj_data: object, user: object) -> None:
    """"Запрос на сохранение документа в БД"""
    users = User.objects.get(username=user)
    users.testvddocument_set.get_or_create(document_title=filename, document_file=file_obj_data)


@logger.catch
def sing_document(file_id: int, user: object):
    """Находим необходимые document и key, после добавляем подпись документу"""
    document = TestVdDocument.objects.get(pk=file_id)
    user = User.objects.get(username=user)
    key = TestVKeyTable.objects.get(user=user)
    try:
        signed = TestVSignedForDocument.objects.get(signed=document)
        if user == signed.key_table_id.user:
            return "Вы уже подписали этот документ"
        _add_signed_doc(file=document, key_obj=key)
        return "Документ успешно подписан"
    except TestVSignedForDocument.DoesNotExist:
        _add_signed_doc(file=document, key_obj=key)
        return "Документ успешно подписан"
