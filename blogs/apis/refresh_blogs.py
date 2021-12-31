import datetime
import logging
import os
import pathlib
import subprocess
from functools import reduce

import pytz
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

from blogs.models import Blog, get_author

BLOG_EXTENSIONS = ['.md', '.org']

BLOG_REPO_LOCAL_REL_PATH = 'blogs-repo'
BLOG_REPO_URL = 'https://github.com/limoiie/notes.git'

TZ = pytz.timezone('Asia/Shanghai')

logger = logging.getLogger(__file__)


class BaseProcessWrapper:
    def pre_process(self, content: bytes):
        pass

    def post_process(self, md: bytes):
        pass


class OrgProcessWrapper(BaseProcessWrapper):
    def __init__(self):
        self.escaped_underscore = b'UND3RSC0R3'

    def pre_process(self, content: bytes):
        content = self.__escape_underscore(content)
        return content

    def post_process(self, md: bytes):
        md = md.replace(self.escaped_underscore, b'_')
        return md

    def __escape_underscore(self, content):
        def is_blank(b):
            return b in b' \t\r\n'

        def f(acc: bytes, next_token: bytes):
            if acc.endswith(b'#+begin') or \
                    acc.endswith(b'#+end') or \
                    is_blank(acc[-1]) or \
                    is_blank(next_token[0]):
                return acc + b'_' + next_token
            return acc + self.escaped_underscore + next_token
        content = reduce(f, content.split(b'_'))
        return content


wrappers = {
    'org': OrgProcessWrapper()
}


def fetch_blog_repo(try_times=3):
    """
    Fetch blogs from repository.
    :return: The path to fetched blogs
    """
    blog_repo = default_storage.path(BLOG_REPO_LOCAL_REL_PATH)
    return blog_repo
    # while True:
    #     try:
    #         if default_storage.exists(blog_repo):
    #             logger.info(f'git pull...')
    #             subprocess.check_call(
    #                 ['git', 'pull', '--no-rebase'], cwd=blog_repo)
    #         else:
    #             logger.info(f'git clone {BLOG_REPO_URL}')
    #             subprocess.check_call(
    #                 ['git', 'clone', BLOG_REPO_URL, blog_repo])
    #         logger.info(f'fetch repo, done')
    #         return blog_repo
    #     except subprocess.CalledProcessError as e:
    #         if try_times <= 0:
    #             raise e
    #         try_times -= 1


def convert_to_md(fp: pathlib.Path):
    import subprocess
    with open(fp, 'br') as f:
        content = f.read()

    fmt = fp.suffix[1:]
    if fmt == 'md':
        return content

    content = wrappers[fmt].pre_process(content)
    md = subprocess.check_output(['pandoc', '-f', fmt, '-t', 'markdown'],
                                 input=content)
    md = wrappers[fmt].post_process(md)
    return md


def iterate_files(repo):
    for root, folders, files in os.walk(repo):
        for f in files:
            p = pathlib.Path(root, f)
            yield p


def extract_title_from(fp):
    with open(fp, 'r') as f:
        return f.readline().strip('#* ')


def extract_abstract_from_md(content):
    return content.split(b'\n', 1)[1].strip()[:200].decode(encoding='utf-8')


def extract_tags_from_md(_content):
    return []


def convert_blogs_and_store_into_db(blog_repo):
    """
    Convert blogs into markdown files and store them into database.
    """
    modified_blog_id_list = set()
    for fp in iterate_files(blog_repo):
        if fp.suffix not in BLOG_EXTENSIONS:
            continue

        ctime = datetime.datetime.fromtimestamp(fp.stat().st_ctime, tz=TZ)
        mtime = datetime.datetime.fromtimestamp(fp.stat().st_mtime, tz=TZ)

        title = extract_title_from(fp)
        blog_obj, created = Blog.objects.get_or_create(
            title=title, author=get_author('limo'), defaults={
                'create_time': ctime,
                'edit_time': mtime,
            })

        if created or blog_obj.edit_time < mtime:
            # when created or modified
            logger.info(f'Update {title} ({fp.name})...')

            md_content = convert_to_md(fp)
            blog_obj.create_time = ctime
            blog_obj.edit_time = mtime
            blog_obj.folder = fp.parent.relative_to(blog_repo)
            blog_obj.abstract = extract_abstract_from_md(md_content)
            blog_obj.md_doc.delete()
            blog_obj.md_doc.save(f'{title}.md', ContentFile(md_content))
            blog_obj.tags.set(extract_tags_from_md(md_content))
            blog_obj.save()

            if not created:
                modified_blog_id_list.add(blog_obj.id)
        else:
            # not modified, keep the same
            pass
    return modified_blog_id_list


def refresh_blogs():
    try:
        blog_repo = fetch_blog_repo()
        outdated = set(Blog.objects.values_list('id', flat=True))
        modified = convert_blogs_and_store_into_db(blog_repo)
    except subprocess.CalledProcessError as e:
        logger.error(f'Failed to refresh blogs: {e}')
        return

    for old_blog_id in outdated - modified:
        Blog.objects.get(id=old_blog_id).delete()
