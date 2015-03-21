from optparse import make_option
from django.core.management.base import BaseCommand, CommandError

from live_updates import run

class Command(BaseCommand):
    help = 'Run comet server'
    option_list = BaseCommand.option_list + (
        make_option('--port',
            action='store_true',
            dest='port',
            default=8001,
            help='Choose port to run on'),
    )

    def handle(self, *args, **options):
        port = options['port']
        run(port)