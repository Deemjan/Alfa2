import os

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view
from rest_framework.parsers import FileUploadParser, MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from Signature.models import KeyTable
from Signature.serialize import KeyTableSerializer, SignedDocumentSerializer

from Signature.cryptography import isValid, generateKey, serializePrivateKey, add_signed_doc


class KeyTableViewSet(ModelViewSet):
    queryset = KeyTable.objects.all()
    serializer_class = KeyTableSerializer


class SignedDocumentViewSet(ModelViewSet):
    queryset = KeyTable.objects.all()
    serializer_class = SignedDocumentSerializer


def uploadCheckView(request):
    return render(request, 'test.html')


class VerifyDocumentView(APIView):
    parser_classes = (MultiPartParser,)

    def post(self, request, format=None):
        filename = str(request.FILES['file'])  # received file name
        file_obj_data = request.data['file']

        PATH = 'file_storage/' + filename

        with default_storage.open(PATH, 'wb+') as destination:
            for chunk in file_obj_data.chunks():
                destination.write(chunk)
            doc_hash = hash(destination)

        # Generate key
        success = isValid(PATH, filename)

        if os.path.exists(PATH):
            os.remove(PATH)

        if success:
            return Response(status=200)
        return Response(status=404)


class SignDocumentView(APIView):
    parser_classes = (JSONParser, FormParser, MultiPartParser,)

    def post(self, request, format=None):
        filename = str(request.FILES['file'])  # received file name
        file_obj_data = request.data['file']
        key_id = request.POST['keys']
        print(key_id)

        PATH = 'file_storage/' + filename

        with default_storage.open(PATH, 'wb+') as destination:
            for chunk in file_obj_data.chunks():
                destination.write(chunk)

        # Generate key
        success = add_signed_doc(file_name=filename, key_id=key_id, PATH=PATH)

        if os.path.exists(PATH):
            os.remove(PATH)

        if success:
            return Response(status=200)
        return Response(status=404)


class GenerateKeyView(APIView):
    parser_classes = (JSONParser, FormParser, MultiPartParser,)

    def post(self, request, format=None):

        try:
            user = request.user
            key = generateKey()
            key_name = request.data['Название подписи']
            private_key = serializePrivateKey(key)
            date_of_expiration = request.data['Дата']

            keyTable = KeyTable.objects.create(user=user, key=private_key.decode('ascii'), key_name=key_name,
                                               dateOfExpiration=date_of_expiration)
            keyTable.save()

            return Response(200)
        except:
            return Response(404)
