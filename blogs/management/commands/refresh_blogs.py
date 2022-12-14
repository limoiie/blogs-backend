import logging

from django.core.management import BaseCommand

from blogs.apis.refresh_blogs import refresh_blogs

logger = logging.getLogger(__file__)


class Command(BaseCommand):
    help = 'Update blogs from git repository, and store them into local db.'

    def add_arguments(self, parser):
        parser.add_argument('url', type=str, help='Url to remote blog repo.')
        parser.add_argument('force', type=bool, default=False,
                            help='Force to refresh all the blogs.')
        parser.add_argument('no_pull', type=bool, default=False,
                            help='Re-process blogs without pulling repo.')

    def handle(self, url, force, no_pull, *args, **options):
        logger.info(f'Refresh blogs from {url}...')
        refresh_blogs(force, no_pull)
