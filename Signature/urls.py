from django.urls import path
from rest_framework.routers import SimpleRouter

from Signature import views
from Signature.views import KeyTableViewSet, SignedDocumentViewSet

router = SimpleRouter()
router.register(r'keys', KeyTableViewSet)
router.register(r'docs', SignedDocumentViewSet)
router.register(r'getKeyOwnerViewSet', views.KeyOwnerViewSet, basename='test')

urlpatterns = [
    path('uploadCheck', views.uploadCheckView),
    path('uploadHandler', views.VerifyDocumentView.as_view()),
    path('generateKey', views.GenerateKeyView.as_view()),
    path('signDocHandler', views.SignDocumentView.as_view()),
    path('test', views.testView),
    #path('', views.openUserPage)
]

urlpatterns += router.urls
