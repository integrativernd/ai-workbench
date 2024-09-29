from django.core.management.base import BaseCommand, CommandError
from tools.google.auth import get_google_auth_url
from tools.google.docs import read_document
from config.settings import DOCUMENT_ID

class Command(BaseCommand):
    help = 'Read primary google document'

    def handle(self, *args, **options):
        # Your command logic goes here
        try:
            self.stdout.write('Reading google document...')
            self.stdout.write(read_document(DOCUMENT_ID))
            # print(get_google_auth_url())
            self.stdout.write(self.style.SUCCESS('Command completed successfully'))
        except Exception as e:
            raise CommandError('An error occurred: %s' % str(e))