import json

from django.contrib.auth import authenticate
from django.shortcuts import render
from django.http import Http404, JsonResponse

from blogs.models import Blog


def index(request):
    """Show a list of newest blogs"""
    blogs = Blog.objects.order_by('-createTime')[:5]
    context = {
        'latest_blogs': blogs
    }
    return render(request, 'blogs/index.html', context)
