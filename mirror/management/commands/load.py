from django.core.management.base import BaseCommand
from mirror.models import load
import sys


class Command(BaseCommand):
    args = '<folder folder ...>'
    help = 'Create entry for corresponding DEF 14A document'

    def handle(self, *args, **options):
        n = len(args)
        for i, folder in enumerate(args):
            f = load(folder)
            path = f.local_path()
            counter = i + 1
            message = '\r[%(counter)d / %(n)d] %(path)s' % locals()
            sys.stdout.write(message)
            sys.stdout.flush()
