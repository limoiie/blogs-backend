from blogs.apis.quick_response import quick_json_response
from blogs.models import Blog, BlogWrapper


def count_blogs(_request):
    return quick_json_response(code=0, data=Blog.objects.count())


def list_blogs(_request, page_num, page_size):
    offset = page_num * page_size

    blogs = Blog.objects.order_by('-createTime')[offset:offset + page_size]
    data = [BlogWrapper.blog2dic(blog) for blog in blogs]
    return quick_json_response(code=0, data={
        'page': data,
        'count': Blog.objects.count()
    })
