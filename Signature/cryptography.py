from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from loguru import logger

from Signature.models import TestVSignedForDocument

logger.add("debug_signature_cryptography.json", format="{time} {level} {message}",
           level="DEBUG", rotation="1 week", compression="zip", serialize=True)


@logger.catch
def generate_key():
    return rsa.generate_private_key(public_exponent=65537, key_size=2048)


@logger.catch
def serialize_private_key(key):
    return key.private_bytes(encoding=serialization.Encoding.PEM,
                             format=serialization.PrivateFormat.PKCS8,
                             encryption_algorithm=serialization.NoEncryption())


@logger.catch
def _add_signed_doc(file: object, key_obj: object):
    """Определяем публичный и приватные ключи, подписываем документ и делаем запись в БД"""
    # key = _load_key(key_obj.key.encode('ascii'))
    key = _load_key(key_obj.key)
    public_key = _serialize_public_key(key.public_key())
    signature, doc_hash = _sign_document(file.document_file.path, key)
    print('asfasfas', type(file), type(doc_hash), type(public_key), type(signature), type(key_obj))
    print(public_key, signature)
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


@logger.catch
def _set_signed_doc_DB(file, doc_hash, public_key, signature, key_table):
    """Запись в таблицу TestVSignedForDocument информации"""
    sig = TestVSignedForDocument.objects.create(public_key=public_key, document_hash=doc_hash,
                                                signature=signature, signed=file, key_table_id=key_table)
    sig.save()
