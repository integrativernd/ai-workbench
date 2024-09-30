from django.core.management.base import BaseCommand, CommandError
from tools.code.file_navigation import list_files

class Command(BaseCommand):
    help = 'List changes filed'

    def handle(self, *args, **options):
        # Your command logic goes here
        try:
            for file_path in list_files():
                print(file_path)
            self.stdout.write(self.style.SUCCESS('Command completed successfully'))
        except Exception as e:
            raise CommandError('An error occurred: %s' % str(e))