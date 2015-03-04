from django.core.management.base import BaseCommand
from mirror.models import File, load
import sys
import json


class Command(BaseCommand):
    args = '<folder folder ...>'
    help = 'Create entry for corresponding DEF 14A document'

    def handle(self, *args, **options):
        n = len(args)
        for i, folder in enumerate(args):
            try:
                f = load(folder)
            except:
                print folder
                sys.exit(255)
            path = (f.local_path() if type(f) == File else '')
            counter = i + 1
            message = '\r[%(counter)d / %(n)d] %(path)s' % locals()
            sys.stdout.write(message)
            sys.stdout.flush()
