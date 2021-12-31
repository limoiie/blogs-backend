from django.urls import path

from .apis import publish, list, detail, login, csrftoken
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('auth/', login.login, name='login'),
    path('publish/', publish.publish_blog, name='publish'),
    path('list/<int:page_num>/<int:page_size>', list.list_blogs, name='list'),
    path('count/', list.count_blogs, name='count'),
    path('<int:blog_id>/', detail.detail_blog, name='details'),
    path('csrftoken/', csrftoken.csrf_token, name='csrf')
]
