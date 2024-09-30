from django.core.management.base import BaseCommand, CommandError
from tools.code.file_navigation import list_changed_files

class Command(BaseCommand):
    help = 'List changes filed'

    # def add_arguments(self, parser):
    #     # Optional: Add command line arguments
    #     parser.add_argument('sample_argument', nargs='+', type=int)

    def handle(self, *args, **options):
        # Your command logic goes here
        try:
            # Access arguments like this:
            # for item in options['sample_argument']:
            #     self.stdout.write(f'Processing item {item}')

            # Your main logic
            for file_path in list_changed_files():
                print(file_path)
            self.stdout.write(self.style.SUCCESS('Command completed successfully'))
        except Exception as e:
            raise CommandError('An error occurred: %s' % str(e))