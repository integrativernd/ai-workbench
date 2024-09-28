from django.core.management.base import BaseCommand, CommandError
from tools.code.internal_tools import add_tool_responder

class Command(BaseCommand):
    help = 'Add tool response'

    # def add_arguments(self, parser):
    #     # Optional: Add command line arguments
    #     parser.add_argument('sample_argument', nargs='+', type=int)

    def handle(self, *args, **options):
        # Your command logic goes here
        try:
            add_tool_responder()
            self.stdout.write(self.style.SUCCESS('Command completed successfully'))
        except Exception as e:
            raise CommandError('An error occurred: %s' % str(e))