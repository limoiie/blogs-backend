import json

from django.contrib.auth import authenticate
from django.http import JsonResponse

from blogs.models import UserWrapper


def _response_login(state, msg, user=None):
    if user is None:
        user = {}
    return JsonResponse(data={
        'state': state,
        'message': msg,
        'data': user
    })


def login(request):
    if request.method != 'POST':
        msg = f'Bap request method, you should use `POST` instead of `{request.method}`'
        return _response_login(False, msg)

    data = json.loads(request.body)
    username = data['username']
    password = data['password']
    user = authenticate(username=username, password=password)

    if user is None:
        return _response_login(False, 'Error username or password')
    else:
        return _response_login(True, 'success', UserWrapper.user2json(user))
