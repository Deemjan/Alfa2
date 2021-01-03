from django.shortcuts import render

# Create your views here.
from rest_framework.viewsets import ModelViewSet

from Signature.models import KeyTable
from Signature.serialize import KeyTableSerializer, SignedDocumentSerializer


class KeyTableViewSet(ModelViewSet):
    queryset = KeyTable.objects.all()
    serializer_class = KeyTableSerializer


class SignedDocumentViewSet(ModelViewSet):
    queryset = KeyTable.objects.all()
    serializer_class = SignedDocumentSerializer
