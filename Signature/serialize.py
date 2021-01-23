from django.contrib.auth.models import User
from rest_framework.serializers import ModelSerializer
from .models import KeyTable, SignedDocument


class KeyTableSerializer(ModelSerializer):
    class Meta:
        model = KeyTable
        fields = '__all__'


class SignedDocumentSerializer(ModelSerializer):
    class Meta:
        model = SignedDocument
        fields = ["document_title", "key_table_id", "date_of_creation"]


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class KeyFieldSerializer(ModelSerializer):
    class Meta:
        model = KeyTable
        fields = ["key_id", "key_name", 'user', "dateOfExpiration"]
