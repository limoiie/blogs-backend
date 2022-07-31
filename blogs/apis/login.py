import json

from django.contrib.auth import authenticate

from blogs.apis.quick_response import quick_json_response
from blogs.models import UserWrapper


def login(request):
    if request.method != 'POST':
        return quick_json_response(code=-1,
                                   message=f'Bap request method, you should use '
                                           f'`POST` instead of `{request.method}`')

    data = json.loads(request.body)
    username = data['username']
    password = data['password']
    user = authenticate(username=username, password=password)

    if user is None:
        return quick_json_response(code=-1,
                                   message='Error username or password')

    return quick_json_response(code=0, data=UserWrapper.user2json(user))
