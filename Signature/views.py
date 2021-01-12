from datetime import datetime
import json
import os

import requests
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.shortcuts import render, redirect

# Create your views here.
from django.utils.dateparse import parse_date
from django.views.generic import TemplateView
from rest_framework import status
from rest_framework.parsers import FileUploadParser, MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import api_view, permission_classes

from Signature.models import KeyTable, SignedDocument
from Signature.permissions import IsAuthenticatedAndKeyOwner
from Signature.serialize import KeyTableSerializer, SignedDocumentSerializer, UserSerializer, KeyFieldSerializer

from Signature.cryptography import isValid, generateKey, serializePrivateKey, add_signed_doc, dateIsValid


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
# @login_required(login_url='login-page')
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
    queryset = {
        'user_keys': KeyTable.objects.filter(user=request.user),
        'create_key': '',
    }
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
            print(request.data)
            filename = str(request.FILES['file'])  # received file name
            file_obj_data = request.data['file']

            PATH = 'static/file_storage/' + filename

            with default_storage.open(PATH, 'wb+') as destination:
                for chunk in file_obj_data.chunks():
                    destination.write(chunk)

            success = isValid(PATH, filename)

            remove_document(PATH)

            if success:
                queryset['succ_or_err'] = 'Документ подлинный'
                queryset['user_keys'] = KeyTable.objects.filter(user=request.user)
                return render(request, 'Signature/private_page.html', queryset)
            queryset['succ_or_err'] = 'Документ не прошёл проверку'
            queryset['user_keys'] = KeyTable.objects.filter(user=request.user)
            return render(request, 'Signature/private_page.html', queryset)
        except Exception:
            queryset = {'succ_or_err': 'Документ не загружен',
                        'user_keys': KeyTable.objects.filter(user=request.user)}
            return render(request, 'Signature/private_page.html', queryset)


def remove_document(PATH):
    if os.path.exists(PATH):
        os.remove(PATH)


class SignDocumentView(APIView):
    parser_classes = (JSONParser, FormParser, MultiPartParser,)
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        try:
            queryset = {}
            print(request.data)
            filename = str(request.FILES['file'])  # received file name
            file_obj_data = request.data['file']
            key_id = request.POST['keys']
            print(request.data)
            PATH = 'static/file_storage/' + filename

            with default_storage.open(PATH, 'wb+') as destination:
                for chunk in file_obj_data.chunks():
                    destination.write(chunk)

            # Generate key
            success = add_signed_doc(file_name=filename, key_id=key_id, PATH=PATH)

            remove_document(PATH)

            if success:
                queryset['succ_or_err'] = 'Документ подписан'
                queryset['user_keys'] = KeyTable.objects.filter(user=request.user)
                return render(request, 'Signature/private_page.html', queryset)
            queryset['succ_or_err'] = 'Что-то пошло не так'
            queryset['user_keys'] = KeyTable.objects.filter(user=request.user)
            return render(request, 'Signature/private_page.html', queryset)
        except Exception:
            queryset = {'succ_or_err': 'Документ не загружен',
                        'user_keys': KeyTable.objects.filter(user=request.user)}
            return render(request, 'Signature/private_page.html', queryset)


class GenerateKeyView(APIView):
    parser_classes = (JSONParser, FormParser, MultiPartParser,)
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        try:
            queryset = {}
            user = request.user
            key = generateKey()
            key_name = request.data['Название подписи']
            private_key = serializePrivateKey(key)
            date_of_expiration = request.data['Дата']

            if dateIsValid(date_of_expiration):
                keyTable = KeyTable.objects.create(user=user, key=private_key.decode('ascii'), key_name=key_name,
                                                   dateOfExpiration=date_of_expiration)
                keyTable.save()
                queryset['succ_or_err'] = 'Ключ создан'
                queryset['user_keys'] = KeyTable.objects.filter(user=request.user)
                return render(request, 'Signature/private_page.html', queryset)
            else:
                queryset['succ_or_err'] = 'Некорректная дата'
                queryset['user_keys'] = KeyTable.objects.filter(user=request.user)
                return render(request, 'Signature/private_page.html', queryset)
        except Exception:
            queryset['succ_or_err'] = 'Что-то пошло не так'
            queryset['user_keys'] = KeyTable.objects.filter(user=request.user)
            return render(request, 'Signature/private_page.html', queryset)
