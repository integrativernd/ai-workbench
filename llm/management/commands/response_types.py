from django.core.management.base import BaseCommand, CommandError
from llm.response_types import get_response_type_for_message

class Command(BaseCommand):
    help = 'Test response types'

    def add_arguments(self, parser):
        parser.add_argument('message', type=str, help='Description of the changes')

    def handle(self, *args, **options):
        message = options['message']
        try:
            self.stdout.write(self.style.SUCCESS('Checking response type'))
            result = get_response_type_for_message(message)
            print(result)
        except Exception as e:
            raise CommandError('An error occurred: %s' % str(e))