import datetime
import logging
import os
import pathlib
import subprocess

import pytz
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

from blogs.models import Blog, get_author

BLOG_EXTENSIONS = ['.md', '.org', '.html']

BLOG_REPO_LOCAL_REL_PATH = 'blogs-repo'
BLOG_REPO_URL = 'https://github.com/limoiie/notes.git'

TZ = pytz.timezone('Asia/Shanghai')

logger = logging.getLogger(__file__)


def fix_html(html: bytes):
    import re

    def make_header_as_link(content):
        new_content = b''
        prev_pos = 0
        for m in re.finditer(r'<h[2-9] id="(.*)">(.*)<'.encode(), content):
            header_id, header_name = m.group(1).decode(), m.group(2).decode()
            name_begin, name_end = m.span(2)
            # wrap name into a link
            link = f'<a href="#{header_id}">{header_name}</a>'.encode()
            new_content += content[prev_pos:name_begin] + link
            prev_pos = name_end
        return new_content + content[prev_pos:]

    html = make_header_as_link(html)
    return html


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


def to_pandoc_format(fmt):
    if fmt == 'md':
        return 'markdown'
    return fmt


def convert_to_html(fp: pathlib.Path):
    import subprocess
    with open(fp, 'br') as f:
        content = f.read()

    fmt = to_pandoc_format(fp.suffix[1:])
    if fmt == 'html':
        return content

    html = subprocess.check_output(['pandoc', '-f', fmt, '-t', 'html'],
                                   input=content)
    html = fix_html(html)
    return html


def iterate_files(repo):
    for root, folders, files in os.walk(repo):
        for f in files:
            p = pathlib.Path(root, f)
            yield p


def extract_title_from(fp):
    with open(fp, 'r') as f:
        return f.readline().strip('#* ')


def extract_abstract_from_html(content):
    return content.split(b'\n', 1)[1].strip()[:400].decode(encoding='utf-8')


def extract_tags_from_html(_content):
    return []


def convert_blogs_and_store_into_db(blog_repo, force):
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

        if force or created or blog_obj.edit_time < mtime:
            # when created or modified
            logger.info(f'Update {title} ({fp.name})...')

            html = convert_to_html(fp)
            blog_obj.create_time = ctime
            blog_obj.edit_time = mtime
            blog_obj.folder = fp.parent.relative_to(blog_repo)
            blog_obj.abstract = extract_abstract_from_html(html)
            blog_obj.html_doc.delete()
            blog_obj.html_doc.save(f'{title}.html', ContentFile(html))
            blog_obj.tags.set(extract_tags_from_html(html))
            blog_obj.save()

            if not created:
                modified_blog_id_list.add(blog_obj.id)
        else:
            # not modified, keep the same
            pass
    return modified_blog_id_list


def refresh_blogs(force):
    try:
        blog_repo = fetch_blog_repo()
        outdated = set(Blog.objects.values_list('id', flat=True))
        modified = convert_blogs_and_store_into_db(blog_repo, force)
    except subprocess.CalledProcessError as e:
        logger.error(f'Failed to refresh blogs: {e}')
        return

    for old_blog_id in outdated - modified:
        b = Blog.objects.get(id=old_blog_id)
        b.md_doc.delete()
        b.html_doc.delete()
        b.delete()
