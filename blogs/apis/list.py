from django.http import JsonResponse

from blogs.models import BlogWrapper, Blog


def _response_count(count):
    return JsonResponse(data={
        'data': count
    })


def _response_list(state, msg, data):
    return JsonResponse(data={
        'state': state,
        'message': msg,
        'data': data
    })


def count_blogs(_request):
    return _response_count(Blog.objects.count())


def list_blogs(_request, page_num, page_size):
    offset = page_num * page_size

    blogs = Blog.objects.order_by('-create_time')
    blogs = blogs[offset:offset+page_size]
    data = [BlogWrapper.blog2json(blog) for blog in blogs]
    return _response_list(True, 'successful', {
        'page': data,
        'count': Blog.objects.count()
    })
