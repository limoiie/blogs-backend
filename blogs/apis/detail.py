from django.http import JsonResponse

from blogs.models import Blog, BlogWrapper


def _response_detail(state, msg, data=None):
    return JsonResponse(data={
        'state': state,
        'message': msg,
        'data': data
    })


def detail_blog(_request, blog_id):
    blog_id = int(blog_id)
    print('blog id: ', blog_id)
    print('blog id: ', type(blog_id))

    try:
        blog = Blog.objects.get(pk=blog_id)
    except Blog.DoesNotExist:
        msg = 'Failed to fetch blog: does not exist!'
        return _response_detail(False, msg)

    data = BlogWrapper.blog2json_detail(blog)
    return _response_detail(True, 'successful', data)
