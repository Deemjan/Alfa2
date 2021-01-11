from django.urls import path
from authentication.views import register_page, login_page, logout_page
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView

urlpatterns = [
    path('register/', register_page, name='registration-page'),
    path('login-page/', login_page, name='login-page'),
    path('logout-page/', logout_page, name='logout-page')
]



# path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
# path('login2/', Login.as_view(), name='login'),
#     path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
#     path('register/', RegisterView.as_view(), name='auth_register'),
#     path('change_password/<int:pk>/', ChangePasswordView.as_view(), name='auth_change_password'),
#     path('update_profile/<int:pk>/', UpdateProfileView.as_view(), name='auth_update_profile'),
#     path('logout/', LogoutView.as_view(), name='auth_logout'),