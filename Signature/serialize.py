from rest_framework.serializers import ModelSerializer
from .models import KeyTable, SignedDocument


class KeyTableSerializer(ModelSerializer):
    class Meta:
        model = KeyTable
        fields = '__all__'


class SignedDocumentSerializer(ModelSerializer):
    class Meta:
        model = SignedDocument
        fields = '__all__'
