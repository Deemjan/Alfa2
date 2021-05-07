#
# def loadPublicKey(key):
#     public_key = serialization.load_pem_public_key(key, backend=None)
#     return public_key
#
#
# def getPublicKey(key):
#     return key.public_key()

#
# def serializePublicKey(key):
#     return key.public_bytes(encoding=serialization.Encoding.PEM,
#                             format=serialization.PublicFormat.SubjectPublicKeyInfo)
#
#
# def loadKey(key):
#     private_key = serialization.load_pem_private_key(
#         key, password=None, backend=None)
#     return private_key
#
#
# def get_private_key(pk):
#     return KeyTable.objects.get(pk=pk)
#
#
# def set_signed_doc_DB(file_name, doc_hash, public_key, signature, key_table):
#     signed_doc = SignedDocument.objects.create(document_title=file_name,
#                                                document_hash=doc_hash, public_key=public_key.decode('ascii'),
#                                                signature=signature, key_table_id=key_table)
#     signed_doc.save()
#
#
# def add_signed_doc(file_name, key_id, PATH):
#     try:
#         key_table = get_private_key(key_id)
#         key = loadKey(key_table.key.encode('ascii'))
#         public_key = serializePublicKey(key.public_key())
#         signature, doc_hash = signDocument(PATH, key)
#         set_signed_doc_DB(file_name, doc_hash, public_key, signature, key_table)
#
#         return True
#     except IntegrityError:
#         return False
#
#
# def signDocument(document, private_key):
#     with open(document, 'rb') as file:
#         message = file.read()
#         signature = private_key.sign(
#             message,
#             padding.PSS(
#                 mgf=padding.MGF1(hashes.SHA256()),
#                 salt_length=padding.PSS.MAX_LENGTH),
#             hashes.SHA256())
#         doc_hash = hash(file)
#     return signature, doc_hash
#
#
# def verifyDocument(document, public_key, signature):
#     public_key = serialization.load_pem_public_key(public_key.encode('ascii'), backend=None)
#     # public_key = serialization.load_pem_public_key(public_key.encode('ascii'), backend=default_backend())
#     with open(document, 'rb') as file:
#         try:
#             message = file.read()
#             public_key.verify(
#                 signature,
#                 message,
#                 padding.PSS(
#                     mgf=padding.MGF1(hashes.SHA256()),
#                     salt_length=padding.PSS.MAX_LENGTH),
#                 hashes.SHA256())
#             return True
#         except InvalidSignature:
#             return False
#
#
# def isValid(PATH, doc_title):
#     try:
#         document = SignedDocument.objects.get(document_title=doc_title)
#
#         if not dateIsValid(document.key_table_id.dateOfExpiration):
#             if os.path.exists(PATH):
#                 os.remove(PATH)
#             raise serializers.ValidationError({"validation error": "Signature has expired."})
#
#         return [verifyDocument(PATH, document.public_key, document.signature), document.key_table_id.user]
#     except SignedDocument.DoesNotExist:
#         if os.path.exists(PATH):
#             os.remove(PATH)
#         raise serializers.ValidationError({"validation error": "Document does not exist."})
#
#
# def dateIsValid(expiration_date):
#     if isinstance(expiration_date, str):
#         expiration_date = parse_date(expiration_date)
#     return datetime.datetime.now().date() <= expiration_date
