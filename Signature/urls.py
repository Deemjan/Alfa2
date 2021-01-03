from django.urls import path
from rest_framework.routers import SimpleRouter

from Signature.views import KeyTableViewSet, SignedDocumentViewSet

router = SimpleRouter()
router.register(r'keys', KeyTableViewSet)
router.register(r'docs', SignedDocumentViewSet)

urlpatterns = [
    #path('', views.openUserPage)
]

urlpatterns += router.urls
