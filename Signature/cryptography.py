import os

from cryptography.hazmat.primitives.asymmetric import rsa, padding, utils
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.exceptions import InvalidSignature
from django.db import IntegrityError
from django.utils import timezone
from rest_framework import serializers

from Signature.models import SignedDocument, KeyTable


def generateKey():
    return rsa.generate_private_key(public_exponent=65537, key_size=2048)


# def saveKey(fileName, private_key):
#     with open(rf'keys\\{fileName}.pem', 'wb') as key_file:
#         key_file.write(serializePrivateKey(private_key))
#
#
# def saveSignature(fileName, signature):
#     with open(rf'signatures\\{fileName}.txt', 'wb') as key_file:
#         key_file.write(signature)
#
#
# def loadSignature(fileName):
#     with open(rf'signatures\\{fileName}.txt', "rb") as key_file:
#         return key_file.read()


# def loadKey(fileName):
#     with open(rf'keys\\{fileName}.pem', "rb") as key_file:
#         private_key = serialization.load_pem_private_key(
#             key_file.read(), password=None, backend=None)
#         return private_key


# def loadKey(key):
#     private_key = serialization.load_pem_private_key(
#         key, password=None, backend=None)
#     return private_key


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
    # print(key.encode('ascii'))
    private_key = serialization.load_pem_private_key(
        key, password=None, backend=None)
    return private_key


def get_private_key(pk):
    return KeyTable.objects.get(pk=pk)


def add_signed_doc(file_name, key_id, PATH):
    try:
        # print(get_private_key(key_id).key)
        key_table = get_private_key(key_id)
        key = loadKey(key_table.key.encode('ascii'))
        public_key = serializePublicKey(key.public_key())
        signature, doc_hash = signDocument(PATH, key)

        signedDoc = SignedDocument.objects.create(document_title=file_name,
                                                  document_hash=doc_hash, public_key=public_key.decode('ascii'),
                                                  signature=signature, key_table_id=key_table)
        signedDoc.save()
        return True
    except IntegrityError:
        return False



def signDocument(document, private_key):
    # chosen_hash = hashes.SHA256()
    # hasher = hashes.Hash(chosen_hash)
    # hasher.update(b"data & ")
    # hasher.update(b"more data")
    # digest = hasher.finalize()
    # sig = private_key.sign(
    #     digest,
    #     padding.PSS(
    #         mgf=padding.MGF1(hashes.SHA256()),
    #         salt_length=padding.PSS.MAX_LENGTH),
    #     utils.Prehashed(chosen_hash))

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


# def verify_doc(file_name):
#     PATH = f'Digital_signature/files/{file_name}'
#     doc_hash = ''
#     with open(PATH, 'rb') as file:
#         doc_hash = hash(file)
#
#     document = pull_document_from_database(doc_hash)
#     return verifyDocument(PATH, document.public_key, document.signature)


def isValid(PATH, doc_title):
    try:
        document = SignedDocument.objects.get(document_title=doc_title)

        if not dateIsValid(document.key_table_id.dateOfExpiration):
            if os.path.exists(PATH):
                os.remove(PATH)
            raise serializers.ValidationError({"validation error": "Signature has expired."})

        return verifyDocument(PATH, document.public_key, document.signature)
    except SignedDocument.DoesNotExist:
        if os.path.exists(PATH):
            os.remove(PATH)
        raise serializers.ValidationError({"validation error": "Document does not exist."})



def dateIsValid(expiration_date):
    return timezone.now() <= expiration_date

# def test():
#     key = generateKey()
#     PATH = r'C:\Users\orda1\PycharmProjects\aua\a.docx'
#     signature = signDocument(PATH, key)
#     saveKey('key', key)
#     saveSignature('signature', signature)
