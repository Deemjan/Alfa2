import datetime

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db.models import QuerySet
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.dateparse import parse_date
from loguru import logger
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from Signature.models import TestVdDocument, TestVKeyTable, TestVSignedForDocument
from Signature.services import set_document_db, sing_document

logger.add("debug_signature_views.json", format="{time} {level} {message}",
           level="DEBUG", rotation="1 week", compression="zip", serialize=True)


def get_signed_docs_by_user(request, user=None):
    user = user if user is not None else request.user
    try:
        key_table = TestVKeyTable.objects.get(user=user)
        signed_docs = TestVSignedForDocument.objects.filter(key_table_id=key_table)
        return signed_docs
    except TestVKeyTable.DoesNotExist:
        return TestVKeyTable.objects.none()


@login_required(login_url='login-page')
def uploadCheckView(request):
    return render(request, 'test.html', {'user': request.user})


@login_required(login_url='login-page')
def testView(request):
    queryset = {'users': User.objects.all()}
    return render(request, 'Signature/admin.html', queryset)


def first_page_view(request):
    return render(request, 'Signature/first_page.html')


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@login_required(login_url='login-page')
def dedicated_page_view(request):
    try:
        queryset = {}
        if request.method == 'POST':
            print(request.data)
            n = int(request.POST.get('sel'))
            date = parse_date(request.POST.get('date'))
            key = TestVKeyTable.objects.get(key_id=n)
            key.dateOfExpiration = date
            key.save()
            queryset['succ_or_err'] = 'Изменения сохранены'
        queryset['user_keys'] = TestVKeyTable.objects.filter(user_id=request.query_params['user'])
        queryset['docs'] = _get_signed_docs_by_user(request, user=request.query_params['user'])

        return render(request, 'Signature/dedicated_page.html', queryset)
    except Exception:
        queryset = {'user_keys': TestVKeyTable.objects.filter(user_id=request.query_params['user'])}
        return render(request, 'Signature/dedicated_page.html', queryset)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@login_required(login_url='login-page')
def private_page_view(request):
    users = User.objects.get(username=request.user)
    queryset = {'user_keys': TestVKeyTable.objects.filter(user=request.user),
                'create_key': '',
                'user_documents': users.testvddocument_set.all(),# добавил для вывода всех загруженных документов пользователем
                'succ_or_err': ''}
    return render(request, 'Signature/private_page.html', queryset)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@login_required(login_url='login-page')
@logger.catch
def test_upload_document_view(request):
    """"Загрузка документа на сервер и в БД"""
    try:
        filename = str(request.FILES['file'])
        file_obj_data = request.data['file']
        signed_docs_by_user = _get_signed_docs_by_user(request.user, filename, file_obj_data)
        return JsonResponse({'success': True, 'message': 'Файл загружен', 'info': signed_docs_by_user})
    except Exception:
        return JsonResponse({'success': False, 'message': 'Документ не загружен'})


@logger.catch
def _get_signed_docs_by_user(user: object, document_title: str, document_file) -> object:
    """
    Проверка документа на подлиность:
        1. Проверить существование такого документа в БД
        2. Проверить есть ли у него подписи
        3. Вернуть ответ
    """
    information_about_signed = []
    # Название документа : document_title
    # Кем подписан : [f'{first_name} {last_name}',...]
    # Когда подписан : sign.date_signed
    # Верифицирован? : signature_validated
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
                signature_validated = _is_valid(document_file, document_title, sign)
                information_about_signed.append(dict(document_title=document_title,
                                                     user=f'{first_name} {last_name}',
                                                     signed_date=sign.date_signed,
                                                     validated=signature_validated))
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
def _date_is_valid(expiration_date):
    if isinstance(expiration_date, str):
        expiration_date = parse_date(expiration_date)
    return datetime.datetime.now().date() <= expiration_date


############################################## TEST #########################################################
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


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@login_required(login_url='login-page')
@logger.catch
def test_sing_document_view(request):
    """Подписать выбранный файл"""
    try:
        print(request.POST)
        document_id = request.POST['documents_name_sing']
        message = sing_document(document_id, request.user)
        return JsonResponse({'success': True, 'message': message})
    except Exception:
        return JsonResponse({'success': False, 'message': 'Ошибка. Документ не подписан'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@login_required(login_url='login-page')
@logger.catch
def test_verify_document_view(request):
    """Проверить документ на подлинность"""
    document_id = request.POST['documents_name_verify']
    print(request.POST)
    return JsonResponse({'success': True, 'message': 'Документ подлинный'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@login_required(login_url='login-page')
@logger.catch
def test_get_users_signed_documents_view(request):
    """Возвращает название документа, кем и когда документ был подписан"""
    try:
        docs = test_get_signed_docs_by_user(request)
        if len(docs) == 0:
            return JsonResponse({'success': False})
        #print(f"docs : {docs}")
        user = User.objects.get(username=request.user)
        #print(f"user: {user}")
        return JsonResponse({'success': True,
                             'docs': docs})
    except Exception:
        return JsonResponse({'success': False,
                             'docs': [],
                             'user_keys': [],
                             'user_documents': []})


def test_get_signed_docs_by_user(request, user=None):
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


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@login_required(login_url='login-page')
@logger.catch
def test_get_user_uploaded_documents(request):
    try:
        users = User.objects.get(username=request.user)
        print(users)
        docs = users.testvddocument_set.all()
        print(docs)
        return JsonResponse({
            'success': True,
            'docs': list(docs.values())
        })
    except Exception:
        return JsonResponse({'success': False})

#### Нужно сгенирировать ключ +
###Подписать документ +
# Рефактор проверки на подлиность
