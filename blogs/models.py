import datetime
import posixpath

from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

TIME_FMT = '%Y/%m/%d %H:%M:%S'


def upload_to(ins, category, filename):
    dirname = ins.create_time.date().strftime(
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
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
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

    abstract = models.TextField()

    md_doc = models.FileField(upload_to=upload_to_markdown)
    html_doc = models.FileField(upload_to=upload_to_html)

    create_time = models.DateTimeField('date published')
    edit_time = models.DateTimeField('date edited')


def get_author(key):
    is_id = type(key) == int
    author = User.objects.get(pk=key) if is_id else \
        User.objects.get(username=key)

    if author is None:
        raise ValueError(f'Author `{key}` is not found')
    return author


def get_tags(tags):
    objs = []
    for tag in tags:
        obj_created = Tag.objects.get_or_create(name=tag)
        objs.append(obj_created[0])
    return objs


def str2time(str_time):
    return datetime.datetime.strptime(str_time, TIME_FMT)


def time2str(time):
    return time.strftime(TIME_FMT)


def store_file(blog, filename, ext, content):
    f = ContentFile(content)
    blog.md_doc.save(filename + ext, f)


def store_blog(data):
    title = data['title']
    author = get_author(data['author'])

    folder = data['folder']
    tags = get_tags(data['tags'])

    abstract = data['abstract']

    md_doc = data['mdDocument']
    html_doc = data['htmlDocument']

    create_time = str2time(data['createTime'])
    edit_time = str2time(data['editTime'])

    blog = Blog(title=title, author=author, folder=folder, abstract=abstract,
                create_time=create_time, edit_time=edit_time)

    blog.md_doc.save(f'{title}.md', ContentFile(md_doc))
    blog.html_doc.save(f'{title}.html', ContentFile(html_doc))

    blog.save()

    blog.tags.set(tags)

    return blog


def list_tags(tags):
    return [tag.name for tag in tags]


class BlogWrapper:
    """
    This is a wrapper class between the interface of front-end
    and the interface of django model
    """
    @staticmethod
    def json2blog(json):
        return store_blog(json)

    @staticmethod
    def blog2json(blog):
        data = {
            'id': blog.id,
            'title': blog.title,
            'author': blog.author.username,
            'folder': blog.folder,
            'tags': list_tags(blog.tags.all()),
            'abstract': blog.abstract,
            'createTime': time2str(blog.create_time),
            'editTime': time2str(blog.edit_time),
            'mdDocument': None,
            'htmlDocument': None
        }

        return data

    @staticmethod
    def blog2json_detail(blog):
        data = BlogWrapper.blog2json(blog)

        try:
            doc = blog.html_doc.read()
            data['htmlDocument'] = doc.decode('utf-8')
            blog.html_doc.close()
        except ValueError:
            doc = blog.md_doc.read()
            data['mdDocument'] = doc.decode('utf-8')
            blog.md_doc.close()
        return data


class UserWrapper:
    @staticmethod
    def user2json(user):
        # be consistent with angular:app/services/auth.service.ts
        return {
            'id': user.id,
            'name': user.username,
            'email': user.email,
            'slogan': '#todo slogan',
            'avater': '#todo avater',
            'token': '#todo token',
        }
