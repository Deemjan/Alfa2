import json
import datetime
import os

from cryptography.hazmat.backends import default_backend
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db.models import QuerySet
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
# Create your views here.
from django.utils.dateparse import parse_date
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from cryptography.hazmat.primitives.asymmetric import rsa, padding, utils
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization, hashes
from Signature.cryptography import isValid, generateKey, serializePrivateKey, add_signed_doc, dateIsValid
from Signature.models import KeyTable, SignedDocument, TestVdDocument, TestVKeyTable, TestVSignedForDocument
from Signature.permissions import IsAuthenticatedAndKeyOwner
from Signature.serialize import KeyTableSerializer, SignedDocumentSerializer, UserSerializer, KeyFieldSerializer
from loguru import logger

from Signature.services import set_document_db, sing_document

logger.add("debug_signature_views.json", format="{time} {level} {message}",
           level="DEBUG", rotation="1 week", compression="zip", serialize=True)


class KeyTableViewSet(ModelViewSet):
    queryset = KeyTable.objects.all()
    serializer_class = KeyTableSerializer
    permission_classes = [IsAuthenticatedAndKeyOwner]


class KeyOwnerViewSet(ModelViewSet):
    serializer_class = KeyTableSerializer

    # permission_classes = [IsAuthenticatedAndKeyOwner]

    @login_required(login_url='login-page')
    def get_queryset(self):
        return KeyTable.objects.filter(user=self.request.user)


class SignedDocumentViewSet(ModelViewSet):
    queryset = SignedDocument.objects.all()
    serializer_class = SignedDocumentSerializer
    permission_classes = [IsAuthenticated]


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]


class KeyFieldViewSet(ModelViewSet):
    queryset = KeyTable.objects.all()
    serializer_class = KeyFieldSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return KeyTable.objects.filter(user_id=self.request.query_params['user'])


def get_signed_docs_by_user(request, user=None):
    user = user if user is not None else request.user
    try:
        key_table = KeyTable.objects.get(user=user)
        signed_docs = SignedDocument.objects.filter(key_table_id=key_table)
        return signed_docs
    except KeyTable.DoesNotExist:
        return KeyTable.objects.none()


@login_required(login_url='login-page')
def uploadCheckView(request):
    return render(request, 'test.html', {'user': request.user})


@login_required(login_url='login-page')
def testView(request):
    queryset = {'users': User.objects.all()}
    return render(request, 'Signature/admin.html', queryset)


# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
def firstPageView(request):
    return render(request, 'Signature/first_page.html')


@api_view(['GET', 'POST'])
# @permission_classes([IsAuthenticated])
@login_required(login_url='login-page')
def dedicatedPageView(request):
    try:
        queryset = {}
        if request.method == 'POST':
            print(request.data)
            n = int(request.POST.get('sel'))
            date = parse_date(request.POST.get('date'))
            key = KeyTable.objects.get(key_id=n)
            key.dateOfExpiration = date
            key.save()

            # key2 = TestVKeyTable.objects.get(key_id=n)
            # key2.dateOfExpiration = date
            # key2.save()

            queryset['succ_or_err'] = 'Изменения сохранены'

        queryset['user_keys'] = KeyTable.objects.filter(user_id=request.query_params['user'])
        queryset['docs'] = get_signed_docs_by_user(request, user=request.query_params['user'])

        return render(request, 'Signature/dedicated_page.html', queryset)
    except Exception:
        queryset = {'user_keys': KeyTable.objects.filter(user_id=request.query_params['user'])}
        return render(request, 'Signature/dedicated_page.html', queryset)


# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @login_required(login_url='login-page')
# def loginPageView(request):
#     return render(request, 'Signature/login_page.html')


# @api_view(['GET', 'POST'])
# @permission_classes([IsAuthenticated])
@login_required(login_url='login-page')
def privatePageView(request):
    docs = get_signed_docs_by_user(request)
    users = User.objects.get(username=request.user)
    queryset = {'user_keys': KeyTable.objects.filter(user=request.user),
                'create_key': '',
                'docs': docs,
                'user_documents': users.testvddocument_set.all(),
                ### добавил для вывода всех загруженных документов пользователем
                'succ_or_err': ''}
    return render(request, 'Signature/private_page.html', queryset)


# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def registrationPageView(request):
#     return render(request, 'Signature/registration_page.html')


class VerifyDocumentView(APIView):
    parser_classes = (MultiPartParser,)
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        try:
            queryset = {}

            docs = get_signed_docs_by_user(request)
            # remove_document()
            filename = str(request.FILES['file'])  # received file name
            file_obj_data = request.data['file']
            print(file_obj_data)

            PATH = 'static/file_storage/' + filename

            with default_storage.open(PATH, 'wb+') as destination:
                for chunk in file_obj_data.chunks():
                    destination.write(chunk)

            success, info_user = isValid(PATH, filename)
            queryset['info'] = info_user
            queryset['docs'] = docs
            queryset['succ_or_err'] = ''
            if success:
                queryset['succ_or_err'] = 'Документ подлинный'
                queryset['user_keys'] = KeyTable.objects.filter(user=request.user)
                queryset['info'] = info_user
                if os.path.exists(PATH):
                    os.remove(PATH)
                return render(request, 'Signature/private_page.html', queryset)
            queryset['succ_or_err'] = 'Документ не прошёл проверку'

            queryset['user_keys'] = KeyTable.objects.filter(user=request.user)
            return render(request, 'Signature/private_page.html', queryset)
        except ValidationError:
            if os.path.exists(PATH):
                os.remove(PATH)
            queryset = {'succ_or_err': 'Документ не был подписан',
                        'user_keys': KeyTable.objects.filter(user=request.user),
                        'docs': get_signed_docs_by_user(request)}
            return render(request, 'Signature/private_page.html', queryset)
        except Exception as e:
            queryset = {'succ_or_err': 'Документ не загружен',
                        'user_keys': KeyTable.objects.filter(user=request.user),
                        'docs': get_signed_docs_by_user(request)}
            return render(request, 'Signature/private_page.html', queryset)


def remove_document():
    files = os.listdir('static/file_storage')
    files.remove('.keep')
    for file in files:
        if os.path.exists(file):
            os.remove(file)


class SignDocumentView(APIView):
    parser_classes = (JSONParser, FormParser, MultiPartParser,)
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        try:
            # remove_document()
            queryset = {}

            docs = get_signed_docs_by_user(request)
            queryset['docs'] = docs
            queryset['succ_or_err'] = ''
            queryset['info'] = request.user
            filename = str(request.FILES['file'])  # received file name
            file_obj_data = request.data['file']
            key_id = request.POST['keys']
            PATH = 'static/file_storage/' + filename
            with default_storage.open(PATH, 'wb+') as destination:
                for chunk in file_obj_data.chunks():
                    destination.write(chunk)

            # Generate key
            success = add_signed_doc(file_name=filename, key_id=key_id, PATH=PATH)

            if success:
                queryset['succ_or_err'] = 'Документ подписан'
                queryset['user_keys'] = KeyTable.objects.filter(user=request.user)
                # return download(request, PATH, filename)
                # remove_document(PATH)
                if os.path.exists(PATH):
                    os.remove(PATH)
                return render(request, 'Signature/private_page.html', queryset)

            if os.path.exists(PATH):
                os.remove(PATH)

            queryset['succ_or_err'] = 'Что-то пошло не так'
            queryset['user_keys'] = KeyTable.objects.filter(user=request.user)
            return render(request, 'Signature/private_page.html', queryset)
        except Exception:
            queryset = {'succ_or_err': 'Документ не загружен',
                        'user_keys': KeyTable.objects.filter(user=request.user),
                        'docs': get_signed_docs_by_user(request)}
            return render(request, 'Signature/private_page.html', queryset)


def download(request, PATH, filename):
    with open(PATH, 'rb') as fh:
        response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
        response['Content-Disposition'] = 'inline; filename=' + filename
        return response


# Не нужен так как нет необходимости в из вне создавать ключ
class GenerateKeyView(APIView):
    parser_classes = (JSONParser, FormParser, MultiPartParser,)
    permission_classes = [IsAuthenticated]


#################

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@login_required(login_url='login-page')
@logger.catch
def test_upload_document_view(request):
    """"Загрузка документа на сервер и в БД"""
    try:
        filename = str(request.FILES['file'])
        file_obj_data = request.data['file']
        PATH = 'static/file_storage/' + filename
        signed_docs_by_user = _get_signed_docs_by_user(request.user, filename, file_obj_data)
        # set_document_db(filename, file_obj_data, request.user, PATH)
        return JsonResponse({'success': True, 'message': 'Файл загружен'})
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


@logger.catch
def _verify_document(document: InMemoryUploadedFile, public_key: object, signature: object) -> bool:
    try:
        public_key = serialization.load_pem_public_key(public_key, backend=None)
        # public_key = serialization.load_pem_public_key(public_key.encode('ascii'), backend=default_backend())
        # with open(document.path, 'rb') as file:
        # print(document, type(document))
        # print(document, type(document.file))
        # print(document, type(document.file.read()))
        message = document.open().read()
        # print(f'PUBLIC KEY : {public_key} ############# SIGNATURE : {signature}')
        # print('dfsdfdsfds', message)
        public_key.verify(
            signature,
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
        sing_document(document_id, request.user)
        return JsonResponse({'success': True, 'message': 'Документ подписан'})
    except Exception:
        return JsonResponse({'success': False, 'message': 'Ошибка. Документ не подписан'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@login_required(login_url='login-page')
@logger.catch
def test_verify_document_view(request):
    """Проверить документ на подлинность"""
    print(request.POST)
    # docs = _get_signed_docs_by_user(request.user, request.POST['documents_name_verify'])

    # success, info_user = isValid(PATH, filename)
    return JsonResponse({'success': True, 'message': 'Документ подлинный'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@login_required(login_url='login-page')
@logger.catch
def test_get_users_signed_documents(request):
    """Возвращает название документа, кем и когда документ был подписан"""
    docs = test_get_signed_docs_by_user(request)
    print(f"docs : {docs}")
    user = User.objects.get(username=request.user)
    # user_keys = KeyTable.objects.filter(user=request.user).values()
    # user_documents = user.testvddocument_set.all()
    # print(f"user_documents : {user_documents}")
    # print(f"user_keys: {user_keys}")
    print(f"user: {user}")
    return JsonResponse({'success': True,
                         'docs': docs})

    # except Exception:
    #     return JsonResponse({'success': False,
    #                          'docs':[],
    #                          'user_keys':[],
    #                          'user_documents':[]})

    # <td> {{doc.document_title}}</td>
    # <td>{{doc.key_table_id.user.first_name}} {{doc.key_table_id.user.last_name}}</td>
    # <td>{{doc.date_for_logs|date:"d-m-Y H:i"}}</td>


def test_get_signed_docs_by_user(request, user=None):
    user = user if user is not None else request.user
    try:
        key_table = TestVKeyTable.objects.get(user=user)
        signed_docs = TestVSignedForDocument.objects.filter(key_table_id=key_table)
        docs = []
        for doc in signed_docs:
            docs.append(dict(title=f"{doc.signed.document_title}",
                             date=f"{doc.date_signed}",
                             user=f"{user.first_name} {user.last_name}"))
        return docs
    except TestVKeyTable.DoesNotExist:
        return TestVKeyTable.objects.none()

#### Нужно сгенирировать ключ +
###Подписать документ +
# Рефактор проверки на подлиность
