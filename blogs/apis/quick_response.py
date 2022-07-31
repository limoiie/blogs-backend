from collections import namedtuple

from django.http import JsonResponse

QuickResponse = namedtuple('QuickResponse', 'code,message,data')


def quick_json_response(code=0, message=None, data=None):
    return JsonResponse(data={
        'code': code,
        'message': message,
        'data': data
    })
