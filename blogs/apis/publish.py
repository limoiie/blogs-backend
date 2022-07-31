import json

from blogs.apis.quick_response import quick_json_response
from blogs.models import BlogWrapper


def publish_blog(request):
    if request.method != 'POST':
        return quick_json_response(
            code=-1, message=f'Bap request method, you should use `POST` '
                             'instead of `{request.method}`')

    data = json.loads(request.body)
    if 'id' not in data:
        data['fromOrg'] = False

    try:
        blog, _created = BlogWrapper.dic2blog(data)
    except Exception as e:
        return quick_json_response(code=-1,
                                   message=f'Failed to parse form data: {e}')
    return quick_json_response(code=0, data=blog.id)
