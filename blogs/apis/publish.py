import json

from django.http import JsonResponse

from blogs.models import BlogWrapper


def _response_publish(state, msg, blog_id=-1):
    return JsonResponse(data={
        'state': state,
        'message': msg,
        'blogId': blog_id
    })


def publish_blog(request):
    if request.method != 'POST':
        msg = f'Bap request method, you should use `POST` instead of `{request.method}`'
        return _response_publish(False, msg)

    data = json.loads(request.body)

    try:
        blog = BlogWrapper.json2blog(data)
    except Exception as e:
        msg = f'Failed to parse form data: {e}'
        return _response_publish(False, msg)

    blog.save()
    return _response_publish(True, 'successful', blog.id)
