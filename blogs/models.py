import posixpath
from datetime import datetime

from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

TIME_FMT = '%Y/%m/%d %H:%M:%S'


def upload_to(ins, category, filename):
    dirname = ins.createTime.date().strftime(
        f'{ins.author.username}/{category}/%Y/%m/%d')
    return posixpath.join(dirname, filename)


def upload_to_markdown(ins, filename):
    return upload_to(ins, 'markdown', filename)


def upload_to_html(ins, filename):
    return upload_to(ins, 'html', filename)


# Extend to the User model
# https://simpleisbetterthancomplex.com/tutorial/2016/07/22/how-to-extend-django-user-model.html
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)


@receiver(post_save, sender=User)
def create_user_profile(_sender, instance, created, **_kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(_sender, instance, **_kwargs):
    instance.profile.save()


class Tag(models.Model):
    name = models.CharField(max_length=32)

    def __str__(self):
        return f'#{self.name}'


# Create your models here.
class Blog(models.Model):
    title = models.CharField(max_length=200)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    folder = models.CharField(max_length=200)
    tags = models.ManyToManyField(Tag)
    visibility = models.BooleanField(default=False)

    abstract = models.TextField()

    mdDocument = models.FileField(upload_to=upload_to_markdown)
    htmlDocument = models.FileField(upload_to=upload_to_html)

    createTime = models.DateTimeField('date published')
    editTime = models.DateTimeField('date edited')

    fromOrg = models.BooleanField(default=False)


class BlogWrapper:
    """
    This is a wrapper class between the interface of front-end
    and the interface of django model
    """

    @staticmethod
    def dic2blog(dic):
        def field(name):
            match name:
                case 'title': value = dic[name]
                case 'author': value = get_author(dic[name])
                case 'folder': value = dic[name]
                case 'tags': value = get_tags(dic[name])
                case 'visibility': value = dic[name]
                case 'abstract': value = dic[name]
                case 'createTime': value = from_timestamp(dic[name])
                case 'editTime': value = from_timestamp(dic[name])
                case 'fromOrg': value = dic[name]
                case _: raise ValueError(f'Unsupported field {name}')
            return value

        fields = ('title', 'author', 'folder', 'visibility', 'abstract',
                  'createTime', 'editTime', 'fromOrg')
        blog, created = Blog.objects.update_or_create(pk=dic['id'], defaults={
            key: field(key) for key in fields if key in dic and
                                                 dic[key] is not None
        })

        if 'tags' in dic and dic['tags'] is not None:
            blog.tags.set(get_tags(dic['tags']))
        if 'mdDocument' in dic and dic['mdDocument'] is not None:
            file = ContentFile(dic['mdDocument'])
            blog.mdDocument.save(f'{blog.title}.md', file)
        if 'htmlDocument' in dic and dic['htmlDocument'] is not None:
            file = ContentFile(dic['htmlDocument'])
            blog.htmlDocument.save(f'{blog.title}.html', file)

        return blog, created

    @staticmethod
    def blog2dic(blog: Blog):
        data = {
            'id': blog.id,
            'title': blog.title,
            'author': blog.author.username,
            'folder': blog.folder,
            'tags': [tag.name for tag in blog.tags.all()],
            'visibility': blog.visibility,
            'abstract': blog.abstract,
            'createTime': to_timestamp(blog.createTime),
            'editTime': to_timestamp(blog.editTime),
            'mdDocument': None,
            'htmlDocument': None
        }

        return data

    @staticmethod
    def blog2json_detail(blog: Blog):
        data = BlogWrapper.blog2dic(blog)

        try:
            doc = blog.htmlDocument.read()
            data['htmlDocument'] = doc.decode('utf-8')
            blog.htmlDocument.close()
        except ValueError:
            doc = blog.mdDocument.read()
            data['mdDocument'] = doc.decode('utf-8')
            blog.mdDocument.close()
        return data


class UserWrapper:
    @staticmethod
    def user2json(user: User):
        # be consistent with angular:app/services/auth.service.ts
        return {
            'id': user.id,
            'name': user.username,
            'email': user.email,
            'slogan': '#todo slogan',
            'avatar': '#todo avatar',
            'token': '#todo token',
        }


def get_author(key):
    is_id = type(key) == int
    author = User.objects.get(pk=key) if is_id else \
        User.objects.get(username=key)

    if author is None:
        raise ValueError(f'Author `{key}` is not found')
    return author


def get_tags(tags):
    tag_objs = []
    for tag in tags:
        tag_obj, _created = Tag.objects.get_or_create(name=tag)
        tag_objs.append(tag_obj)
    return tag_objs


def from_timestamp(milliseconds):
    return datetime.fromtimestamp(milliseconds / 1000)


def to_timestamp(date: datetime):
    return date.timestamp() * 1000
