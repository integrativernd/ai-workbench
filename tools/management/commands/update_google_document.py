from django.core.management.base import BaseCommand, CommandError
from tools.google.docs import append_text
from config.settings import DOCUMENT_ID

class Command(BaseCommand):
    help = 'Update primary google document'

    def handle(self, *args, **options):
        try:
            self.stdout.write('Reading google document...')
            append_text(DOCUMENT_ID, "Hello World!")
            # print(get_google_auth_url())
            self.stdout.write(self.style.SUCCESS('Command completed successfully'))
        except Exception as e:
            raise CommandError('An error occurred: %s' % str(e))