import datetime

from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization, hashes
from django.contrib.auth.models import User
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db.models import QuerySet
from django.utils.dateparse import parse_date
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
    print(f'sing_document {user}  {user.pk} {user.username} ')
    key = TestVKeyTable.objects.get(user=user)
    print(key)

    _add_signed_doc(file=document, key_obj=key)


@logger.catch
def get_signed_docs_by_user(user: object, document_title: str, document_file) -> object:
    """
    Проверка документа на подлиность:
        1. Проверить существование такого документа в БД
        2. Проверить есть ли у него подписи
        3. Вернуть ответ
    """
    information_about_signed = []
    document_in_db = TestVdDocument.objects.filter(document_title=document_title)
    print(f'document_in_db = {document_in_db} document_title= {document_title}')
    if document_in_db.exists():
        print('документ существует')
        document_in_db = TestVdDocument.objects.get(document_title=document_title)
        signed = document_in_db.testvsignedfordocument_set.all()
        if signed.exists():
            print(f'Есть хотя бы одна подпись')
            for sign in signed:
                first_name = sign.key_table_id.user.first_name
                last_name = sign.key_table_id.user.last_name
                print(document_file.file)
                print(f'странное условие равно {_is_valid(document_file, document_title, sign)}')
                if _is_valid(document_file, document_title, sign):
                    print(f'подпись валидна ?_is_valid= {signed}')
                    msg = f'{first_name} {last_name} подписал документ {sign.date_signed}. Документ подлиный'
                    print(msg)
                    information_about_signed.append(msg)
                else:
                    msg = f'{first_name} {last_name} подписал документ {sign.date_signed}. Документ не прошел ' \
                          f'проверку на подлиность'
                    print(msg)
                    information_about_signed.append(msg)
        else:
            print(f'add user to document= {signed}')
            print(f'нет подписей')
            _add_user_to_document_db(filename=document_title, file_obj_data=document_file, user=user)
    else:
        set_document_db(filename=document_title, file_obj_data=document_file, user=user)
    return information_about_signed


@logger.catch
def _add_user_to_document_db(filename: str, file_obj_data: object, user: object) -> None:
    """"Запрос на добавление пользователя к документу в БД"""
    users = User.objects.get(username=user)
    document = TestVdDocument.objects.get(document_title=filename)
    document.user.add(users)
    document.save()
    # users.testvddocument_set.add(document_title=filename, document_file=file_obj_data)


@logger.catch
def _is_valid(document_file: object, document_title: str, signed: QuerySet) -> bool:
    print(f'data is {_date_is_valid(signed.date_signed)}')
    if not _date_is_valid(signed.date_signed):
        return False
    print(f'{document_file} {signed.public_key} {signed.signature}')
    verif = _verify_document(document_file, signed.public_key, signed.signature)
    print(f'verify is {verif}')
    return verif


@logger.catch
def _date_is_valid(expiration_date) -> bool:
    if isinstance(expiration_date, str):
        expiration_date = parse_date(expiration_date)
    return datetime.datetime.now().date() <= expiration_date


@logger.catch
def _verify_document(document: InMemoryUploadedFile, public_key: bytes, signature: bytes) -> bool:
    try:
        public_key = serialization.load_pem_public_key(public_key, backend=None)
        message = document.open().read()
        public_key.verify(
            bytes(signature),
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256())
        return True
    except InvalidSignature as exception:
        print(exception)


def _get_signed_docs_by_user(request, user=None):
    user = user if user is not None else request.user
    try:
        key_table = TestVKeyTable.objects.get(user=user)
        signed_docs = TestVSignedForDocument.objects.filter(key_table_id=key_table)
        return signed_docs
    except TestVKeyTable.DoesNotExist:
        return TestVKeyTable.objects.none()


def _test_get_signed_docs_by_user(request, user=None):
    user = user if user is not None else request.user
    try:
        key_table = TestVKeyTable.objects.get(user=user)
        signed_docs = TestVSignedForDocument.objects.filter(key_table_id=key_table)
        docs = []

        for doc in signed_docs:
            users = doc.signed.user.all()
            users_list = []
            for user_name in users.values("first_name", "last_name"):
                users_list.append(f"{user_name['first_name']} {user_name['last_name']}")

            docs.append(dict(title=f"{doc.signed.document_title}",
                             date=f"{doc.date_signed}",
                             users=users_list))
        return docs
    except TestVKeyTable.DoesNotExist:
        return TestVKeyTable.objects.none()