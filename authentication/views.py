from django.http import HttpResponse
from django.shortcuts import render, redirect

from django.contrib.auth import authenticate, login, logout

from django.contrib import messages

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from rest_framework import generics
from rest_framework.authentication import BaseAuthentication
from rest_framework.permissions import IsAuthenticated

from authentication.forms import CreateUserForm
from .serializers import RegisterSerializer, ChangePasswordSerializer, UpdateUserSerializer

from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import status

from rest_framework import status, exceptions
from django.http import HttpResponse
from rest_framework.authentication import get_authorization_header, BaseAuthentication
import jwt
import json
# Create your views here.


from .serializers import MyTokenObtainPairSerializer
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView


def register_page(request):
    context = {}
    form = CreateUserForm()

    if request.method == 'POST':
        form = CreateUserForm(request.POST)

        if form.is_valid():
            form.save()
            user = form.cleaned_data.get('username')
            print('regestr_page:', user, form.cleaned_data.get('password'))
            messages.success(request, 'Успешная регистрация' + user)
            return redirect('private-page')

    context = {'form': form}
    return render(request, 'authentication/registration_page.html', context)


def login_page(request):
    context = {}
    # if request.user.is_authenticated:
    #     return redirect('private-page')
    # else:
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        print('login_page :', username, password)
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('private-page')
        else:
            messages.info(request, 'Логин или пароль не верен')
    return render(request, 'authentication/login_page.html', context)


def logout_page(request):
    logout(request)
    return redirect('first-page')



# Use with rest_framework
# class MyObtainTokenPairView(TokenObtainPairView):
#     permission_classes = (AllowAny,)
#     serializer_class = MyTokenObtainPairSerializer
#
#
# class RegisterView(generics.CreateAPIView):
#     queryset = User.objects.all()
#     permission_classes = (AllowAny,)
#     serializer_class = RegisterSerializer
#
#     def post(self, request, *args, **kwargs):
#         super().post(request=request, *args, **kwargs)
#         return redirect('/login-page')
#
#
# class ChangePasswordView(generics.UpdateAPIView):
#     queryset = User.objects.all()
#     permission_classes = (IsAuthenticated,)
#     serializer_class = ChangePasswordSerializer
#
#
# class UpdateProfileView(generics.UpdateAPIView):
#     queryset = User.objects.all()
#     permission_classes = (IsAuthenticated,)
#     serializer_class = UpdateUserSerializer
#
#
# class Login(APIView):
#
#     def post(self, request, *args, **kwargs):
#         if not request.data:
#             return Response({'Error': "Please provide username/password"}, status="400")
#
#         username = request.data['username']
#         password = request.data['password']
#
#         print(request)
#         print(username)
#         print(password)
#         try:
#             user = User.objects.get(username=username)
#         except User.DoesNotExist:
#             return Response({'Error': "Invalid username/password"}, status="400")
#         if user:
#             payload = {
#                 'id': user.id,
#                 'email': user.email,
#             }
#             jwt_token = {'token': jwt.encode(payload, "SECRET_KEY")}
#
#             return HttpResponse(
#                 json.dumps(jwt_token),
#                 status=200,
#                 content_type="application/json" )
#         else:
#             return Response(
#                 json.dumps({'Error': "Invalid credentials"}),
#                 status=400,
#                 content_type="application/json" )
#
#
# class TokenAuthentication(BaseAuthentication):
#     model = None
#
#     def get_model(self):
#         return User
#
#     def authenticate(self, request):
#         auth = get_authorization_header(request).split()
#         if not auth or auth[0].lower() != b'token':
#             return None
#
#         if len(auth) == 1:
#             msg = 'Invalid token header. No credentials provided.'
#             raise exceptions.AuthenticationFailed(msg)
#         elif len(auth) > 2:
#             msg = 'Invalid token header'
#             raise exceptions.AuthenticationFailed(msg)
#
#         try:
#             token = auth[1]
#             if token == "null":
#                 msg = 'Null token not allowed'
#                 raise exceptions.AuthenticationFailed(msg)
#         except UnicodeError:
#             msg = 'Invalid token header. Token string should not contain invalid characters.'
#             raise exceptions.AuthenticationFailed(msg)
#
#         return self.authenticate_credentials(token)
#
#     def authenticate_credentials(self, token):
#         model = self.get_model()
#         payload = jwt.decode(token, "SECRET_KEY")
#         email = payload['email']
#         userid = payload['id']
#         msg = {'Error': "Token mismatch", 'status': "401"}
#         try:
#
#             user = User.objects.get(
#                 email=email,
#                 id=userid,
#                 is_active=True
#             )
#
#             if not user.token['token'] == token:
#                 raise exceptions.AuthenticationFailed(msg)
#
#         except jwt.ExpiredSignature or jwt.DecodeError or jwt.InvalidTokenError:
#             return HttpResponse({'Error': "Token is invalid"}, status="403")
#         except User.DoesNotExist:
#             return HttpResponse({'Error': "Internal server error"}, status="500")
#
#         return user, token
#
#     def authenticate_header(self, request):
#         return 'Token'
#
#
# class LogoutView(APIView):
#     permission_classes = (IsAuthenticated,)
#
#     def post(self, request):
#         try:
#             refresh_token = request.data["refresh_token"]
#             print(refresh_token)
#             token = RefreshToken(refresh_token)
#             token.blacklist()
#
#             return redirect('/login-page')
#         except Exception as e:
#             return Response(status=status.HTTP_400_BAD_REQUEST)
