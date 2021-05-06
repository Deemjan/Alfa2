from django.conf.urls import url
from django.urls import path,include
from rest_framework.routers import SimpleRouter

from Signature import views

router = SimpleRouter()

urlpatterns = [
    path('', views.first_page_view, name='first-page'),
    path('uploadCheck', views.uploadCheckView),

    path('testUploadDoc', views.test_upload_document_view, name='testUploadDoc'),
    path('testSingDoc', views.test_sing_document_view, name='testSingDoc'),
    path('testVerifyDoc', views.test_verify_document_view, name='testVerifyDoc'),
    path('testGetUsersDocs', views.test_get_users_signed_documents_view, name='testGetUsersDocs'),

    path('admin-page', views.testView, name='admin-page'),
    path('dedicated-page', views.dedicated_page_view, name='dedicated-page'),
    path('private-page', views.private_page_view, name='private-page'),
]

urlpatterns += router.urls
