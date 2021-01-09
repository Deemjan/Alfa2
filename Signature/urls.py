from django.urls import path
from rest_framework.routers import SimpleRouter

from Signature import views
from Signature.views import KeyTableViewSet, SignedDocumentViewSet

router = SimpleRouter()
router.register(r'keys', KeyTableViewSet)
router.register(r'docs', SignedDocumentViewSet)
router.register(r'getKeyOwnerViewSet', views.KeyOwnerViewSet, basename='test')
router.register(r'get_users_key_table', views.KeyFieldViewSet)

urlpatterns = [
    path('uploadCheck', views.uploadCheckView),
    path('uploadHandler', views.VerifyDocumentView.as_view()),
    path('generateKey', views.GenerateKeyView.as_view()),
    path('signDocHandler', views.SignDocumentView.as_view()),
    path('admin-page', views.testView, name='admin-page'),
    path('front-page', views.firstPageView, name='front-page'),
    path('dedicated-page', views.dedicatedPageView, name='dedicated-page'),
    path('login-page', views.loginPageView, name='login-page'),
    path('private-page', views.privatePageView, name='private-page'),
    path('registration-page', views.registrationPageView, name='registration-page'),
    path('first-page', views.firstPageView, name='first-page'),
    #path('', views.openUserPage)
]

urlpatterns += router.urls
