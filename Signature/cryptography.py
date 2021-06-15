import datetime
import os

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa, padding, utils
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.exceptions import InvalidSignature
from django.db import IntegrityError
from django.utils import timezone
from django.utils.dateparse import parse_date
from loguru import logger
from rest_framework import serializers

from Signature.models import SignedDocument, KeyTable, TestVSignedForDocument


def generateKey():
    return rsa.generate_private_key(public_exponent=65537, key_size=2048)


def loadPublicKey(key):
    public_key = serialization.load_pem_public_key(key, backend=None)
    return public_key


def getPublicKey(key):
    return key.public_key()


def serializePrivateKey(key):
    return key.private_bytes(encoding=serialization.Encoding.PEM,
                             format=serialization.PrivateFormat.PKCS8,
                             encryption_algorithm=serialization.NoEncryption())


def serializePublicKey(key):
    return key.public_bytes(encoding=serialization.Encoding.PEM,
                            format=serialization.PublicFormat.SubjectPublicKeyInfo)


def loadKey(key):
    private_key = serialization.load_pem_private_key(
        key, password=None, backend=None)
    return private_key


def get_private_key(pk):
    return KeyTable.objects.get(pk=pk)


def set_signed_doc_DB(file_name, doc_hash, public_key, signature, key_table):
    signed_doc = SignedDocument.objects.create(document_title=file_name,
                                               document_hash=doc_hash, public_key=public_key.decode('ascii'),
                                               signature=signature, key_table_id=key_table)
    signed_doc.save()


def add_signed_doc(file_name, key_id, PATH):
    try:
        key_table = get_private_key(key_id)
        if not dateIsValid(key_table.dateOfExpiration):
            return False
        key = loadKey(key_table.key.encode('ascii'))
        public_key = serializePublicKey(key.public_key())
        signature, doc_hash = signDocument(PATH, key)
        set_signed_doc_DB(file_name, doc_hash, public_key, signature, key_table)

        return True
    except IntegrityError:
        return False


def signDocument(document, private_key):
    with open(document, 'rb') as file:
        message = file.read()
        signature = private_key.sign(
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256())
        doc_hash = hash(file)
    return signature, doc_hash


def verifyDocument(document, public_key, signature):
    public_key = serialization.load_pem_public_key(public_key.encode('ascii'), backend=None)
    # public_key = serialization.load_pem_public_key(public_key.encode('ascii'), backend=default_backend())
    with open(document, 'rb') as file:
        try:
            message = file.read()
            public_key.verify(
                signature,
                message,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH),
                hashes.SHA256())
            return True
        except InvalidSignature:
            return False


def isValid(PATH, doc_title):
    try:
        document = SignedDocument.objects.get(document_title=doc_title)

        if not dateIsValid(document.key_table_id.dateOfExpiration):
            if os.path.exists(PATH):
                os.remove(PATH)
            raise serializers.ValidationError({"validation error": "Signature has expired."})

        return [verifyDocument(PATH, document.public_key, document.signature), document.key_table_id.user]
    except SignedDocument.DoesNotExist:
        if os.path.exists(PATH):
            os.remove(PATH)
        raise serializers.ValidationError({"validation error": "Document does not exist."})


def dateIsValid(expiration_date):
    if isinstance(expiration_date, str):
        expiration_date = parse_date(expiration_date)
    return datetime.datetime.now().date() <= expiration_date


# ################################################
logger.add("debug_signature_cryptography.json", format="{time} {level} {message}",
           level="DEBUG", rotation="1 week", compression="zip", serialize=True)


@logger.catch
def _add_signed_doc(file: object, key_obj: object):
    """Определяем публичный и приватные ключи, подписываем документ и делаем запись в БД"""
    # key = _load_key(key_obj.key.encode('ascii'))
    key = _load_key(key_obj.key)
    public_key = _serialize_public_key(key.public_key())
    signature, doc_hash = _sign_document(file.document_file.path, key)
    _set_signed_doc_DB(file, doc_hash, public_key, signature, key_obj)


@logger.catch
def _load_key(key: object) -> object:
    """Загрузка ключа"""
    private_key = serialization.load_pem_private_key(
        key, password=None, backend=None)
    return private_key


@logger.catch
def _serialize_public_key(key: object) -> object:
    """Возвращаем публичный ключ"""
    return key.public_bytes(encoding=serialization.Encoding.PEM,
                            format=serialization.PublicFormat.SubjectPublicKeyInfo)


@logger.catch
def _set_signed_doc_DB(file, doc_hash, public_key, signature, key_table):
    """Запись в таблицу TestVSignedForDocument информации"""  # # вроде работает без  public_key=public_key.decode(
    # 'ascii')
    sig = TestVSignedForDocument.objects.create(public_key=public_key, document_hash=doc_hash,
                                                signature=signature, signed=file, key_table_id=key_table)
    sig.save()


@logger.catch
def _sign_document(document, private_key):
    """Открытия и подписание документа"""
    with open(document, 'rb') as file:
        message = file.read()
        signature = private_key.sign(
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256())
        doc_hash = hash(file)
    return signature, doc_hash
