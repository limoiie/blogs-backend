from django.shortcuts import render


def csrf_token(request):
    return render(request, 'blogs/csrf_token.html')
