from blogs.apis.quick_response import quick_json_response
from blogs.models import Blog, BlogWrapper


def detail_blog(_request, blog_id):
    blog_id = int(blog_id)
    try:
        blog = Blog.objects.get(pk=blog_id)
    except Blog.DoesNotExist:
        return quick_json_response(
            code=-1, message='Failed to fetch blog: does not exist!')

    data = BlogWrapper.blog2json_detail(blog)
    return quick_json_response(code=0, data=data)
