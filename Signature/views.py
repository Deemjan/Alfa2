import json
import os

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.files.storage import default_storage
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

from Signature.cryptography import isValid, generateKey, serializePrivateKey, add_signed_doc, dateIsValid
from Signature.models import KeyTable, SignedDocument, TestVdDocument
from Signature.permissions import IsAuthenticatedAndKeyOwner
from Signature.serialize import KeyTableSerializer, SignedDocumentSerializer, UserSerializer, KeyFieldSerializer
from loguru import logger

from Signature.services import set_document_db

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
                'user_documents': users.testvddocument_set.all(), ### добавил для вывода всех загруженных документов пользователем
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
        set_document_db(filename, file_obj_data, request.user, PATH)
        return JsonResponse({'success': True, 'message': 'Файл загружен'})
    except Exception:
        return JsonResponse({'success': False, 'message': 'Документ не загружен'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@login_required(login_url='login-page')
@logger.catch
def test_sing_document_view(request):
    """Подписать выбранный файл"""
    try:
        print(request.POST)
        print(request.POST['documents_name'])
        document_id = request.POST['documents_name']
        sing_document(document_id, request.user)
        return JsonResponse({'success': True, 'message': 'OK'})
    except Exception:
        queryset = {
            'is_success': False,
            'msg_success': 'Документ не загружен',
            'user_keys': KeyTable.objects.filter(user=request.user),
            'docs': get_signed_docs_by_user(request)
        }
        return Response(queryset)


def sing_document(file_id: int, user: object) -> bool:
        document = TestVdDocument.objects.filter(document_id=file_id)

        # with default_storage.open(document.document_file.path, 'wb+') as destination:
        #     for chunk in file_obj_data.chunks():
        #         destination.write(chunk)
            # Generate key
        # success = add_signed_doc(file_name=filename, key_id=key_id, PATH=PATH)
        return True


class TestVSignDocumentView(APIView):
    parser_classes = (JSONParser, FormParser, MultiPartParser,)
    permission_classes = [IsAuthenticated]

    def sing_document(self, filename, file_obj_data, key_id, PATH) -> bool:
        with default_storage.open(PATH, 'wb+') as destination:
            for chunk in file_obj_data.chunks():
                destination.write(chunk)
            # Generate key
        success = add_signed_doc(file_name=filename, key_id=key_id, PATH=PATH)
        return success

    @staticmethod
    def post(self,request, format=None):
        try:

            queryset = {}
            docs = "dsads" #get_signed_docs_by_user(request)
            # post_data = json.loads(request.body.decode("utf-8"))
            # print(post_data)
            queryset['docs'] = docs
            queryset['info'] = request.user
            if request.method == 'POST':
                print(request.data.get('usert'))
                print(str(request.data.get('file')))
                print(str(request.FILES))
                return HttpResponse(request.data.get('usert'), request.FILES) #Response(queryset, status=status.HTTP_201_CREATED)
                # print(str(request.FILES))
                # print(request.FILES)
                # filename = str(request.FILES.get('file'))  # received file name
                # file_obj_data = request.FILES.get('file') #request.data['file']
                # # key_id = request.POST['key']
                # PATH = 'static/file_storage/' + filename
                #
                # success = self.sing_document(docs, filename, file_obj_data, 1, PATH)

                # if success:
                #     if os.path.exists(PATH):
                #         os.remove(PATH)
                #     queryset['is_success'] = success
                return Response(queryset)

            # if os.path.exists(PATH):
            #     os.remove(PATH)
            queryset['is_success'] = False
            queryset['msg_success'] = 'Что-то пошло не так'
            queryset['user_keys'] = KeyTable.objects.filter(user=request.user)
            return Response(queryset)
        except Exception:
            queryset = {
                            'is_success': False,
                            'msg_success': 'Документ не загружен',
                            'user_keys': KeyTable.objects.filter(user=request.user),
                            'docs': get_signed_docs_by_user(request)
                        }
            return Response(queryset)



