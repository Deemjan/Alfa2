import os

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.parsers import FileUploadParser, MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import api_view, permission_classes
from Signature.models import KeyTable, SignedDocument
from Signature.permissions import IsAuthenticatedAndKeyOwner
from Signature.serialize import KeyTableSerializer, SignedDocumentSerializer

from Signature.cryptography import isValid, generateKey, serializePrivateKey, add_signed_doc


class KeyTableViewSet(ModelViewSet):
    queryset = KeyTable.objects.all()
    serializer_class = KeyTableSerializer
    # permission_classes = [IsAuthenticatedAndKeyOwner]


class KeyOwnerViewSet(ModelViewSet):
    serializer_class = KeyTableSerializer
    permission_classes = [IsAuthenticatedAndKeyOwner]

    def get_queryset(self):
        return KeyTable.objects.filter(user=self.request.user)


class SignedDocumentViewSet(ModelViewSet):
    queryset = SignedDocument.objects.all()
    serializer_class = SignedDocumentSerializer
    permission_classes = [IsAuthenticated]


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def uploadCheckView(request):
    return render(request, 'test.html', {'user': request.user})


def testView(request):
    return render(request, 'test2.html')


class VerifyDocumentView(APIView):
    parser_classes = (MultiPartParser,)
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        filename = str(request.FILES['file'])  # received file name
        file_obj_data = request.data['file']

        PATH = 'static/file_storage/' + filename

        with default_storage.open(PATH, 'wb+') as destination:
            for chunk in file_obj_data.chunks():
                destination.write(chunk)

        success = isValid(PATH, filename)

        remove_document(PATH)

        if success:
            return Response(status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST, headers={
            "validation error": "Document didn't pass validation."})


def remove_document(PATH):
    if os.path.exists(PATH):
        os.remove(PATH)


class SignDocumentView(APIView):
    parser_classes = (JSONParser, FormParser, MultiPartParser,)
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        filename = str(request.FILES['file'])  # received file name
        file_obj_data = request.data['file']
        key_id = request.POST['keys']

        PATH = 'static/file_storage/' + filename

        with default_storage.open(PATH, 'wb+') as destination:
            for chunk in file_obj_data.chunks():
                destination.write(chunk)

        # Generate key
        success = add_signed_doc(file_name=filename, key_id=key_id, PATH=PATH)

        remove_document(PATH)

        if success:
            return Response(status.HTTP_200_OK)
        return Response(status.HTTP_400_BAD_REQUEST, headers={"error": "Document already signed."})


class GenerateKeyView(APIView):
    parser_classes = (JSONParser, FormParser, MultiPartParser,)
    permission_classes = [IsAuthenticated]

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

            return Response(status.HTTP_201_CREATED)
        except Exception:
            return Response(status.HTTP_400_BAD_REQUEST)
