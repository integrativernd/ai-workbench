from django.core.management.base import BaseCommand, CommandError
from tools.code.search import list_files_to_change

class Command(BaseCommand):
    help = 'List files that need to be changed'

    def add_arguments(self, parser):
        parser.add_argument('description', type=str, help='Description of the changes')

    def handle(self, *args, **options):
        description = options['description']
        self.stdout.write(f"Files to change: {description}\n")
        try:
            self.stdout.write(list_files_to_change(description))
            self.stdout.write(self.style.SUCCESS('Command completed successfully'))
        except Exception as e:
            raise CommandError('An error occurred: %s' % str(e))