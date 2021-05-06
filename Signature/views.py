from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.dateparse import parse_date
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from Signature.models import TestVKeyTable
from loguru import logger
from Signature.services import sing_document, _test_get_signed_docs_by_user, _get_signed_docs_by_user

logger.add("debug_signature_views.json", format="{time} {level} {message}",
           level="DEBUG", rotation="1 week", compression="zip", serialize=True)


@login_required(login_url='login-page')
def uploadCheckView(request):
    return render(request, 'test.html', {'user': request.user})


@login_required(login_url='login-page')
def testView(request):
    queryset = {'users': User.objects.all()}
    return render(request, 'Signature/admin.html', queryset)


def first_page_view(request):
    return render(request, 'Signature/first_page.html')


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@login_required(login_url='login-page')
def dedicated_page_view(request):
    try:
        queryset = {}
        if request.method == 'POST':
            print(request.data)
            n = int(request.POST.get('sel'))
            date = parse_date(request.POST.get('date'))
            key = TestVKeyTable.objects.get(key_id=n)
            key.dateOfExpiration = date
            key.save()
            queryset['succ_or_err'] = 'Изменения сохранены'
        queryset['user_keys'] = TestVKeyTable.objects.filter(user_id=request.query_params['user'])
        queryset['docs'] = _get_signed_docs_by_user(request, user=request.query_params['user'])

        return render(request, 'Signature/dedicated_page.html', queryset)
    except Exception:
        queryset = {'user_keys': TestVKeyTable.objects.filter(user_id=request.query_params['user'])}
        return render(request, 'Signature/dedicated_page.html', queryset)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@login_required(login_url='login-page')
def private_page_view(request):
    docs = _get_signed_docs_by_user(request)
    users = User.objects.get(username=request.user)
    queryset = {'user_keys': TestVKeyTable.objects.filter(user=request.user),
                'create_key': '',
                'docs': docs,
                'user_documents': users.testvddocument_set.all(),# добавил для вывода всех загруженных документов пользователем
                'succ_or_err': ''}
    return render(request, 'Signature/private_page.html', queryset)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@login_required(login_url='login-page')
@logger.catch
def test_upload_document_view(request):
    """"Загрузка документа на сервер и в БД"""
    try:
        filename = str(request.FILES['file'])
        file_obj_data = request.data['file']
        signed_docs_by_user = _get_signed_docs_by_user(request.user, filename, file_obj_data)
        return JsonResponse({'success': True, 'message': 'Файл загружен', 'info': signed_docs_by_user})
    except Exception:
        return JsonResponse({'success': False, 'message': 'Документ не загружен'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@login_required(login_url='login-page')
@logger.catch
def test_sing_document_view(request):
    """Подписать выбранный файл"""
    try:
        print(request.POST)
        document_id = request.POST['documents_name_sing']
        sing_document(document_id, request.user)
        return JsonResponse({'success': True, 'message': 'Документ подписан'})
    except Exception:
        return JsonResponse({'success': False, 'message': 'Ошибка. Документ не подписан'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@login_required(login_url='login-page')
@logger.catch
def test_verify_document_view(request):
    """Проверить документ на подлинность"""
    print(request.POST)
    return JsonResponse({'success': True, 'message': 'Документ подлинный'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@login_required(login_url='login-page')
@logger.catch
def test_get_users_signed_documents_view(request):
    """Возвращает название документа, кем и когда документ был подписан"""
    try:
        docs = _test_get_signed_docs_by_user(request)
        if len(docs) == 0:
            return JsonResponse({'success': False})
        print(f"docs : {docs}")
        user = User.objects.get(username=request.user)
        print(f"user: {user}")
        return JsonResponse({'success': True,
                             'docs': docs})
    except Exception:
        return JsonResponse({'success': False,
                             'docs': [],
                             'user_keys': [],
                             'user_documents': []})



#### Нужно сгенирировать ключ +
###Подписать документ +
# Рефактор проверки на подлиность
