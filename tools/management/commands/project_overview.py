from django.core.management.base import BaseCommand, CommandError
from tools.project_overview import create_project_overview

class Command(BaseCommand):
    help = 'Create project overview'

    def handle(self, *args, **options):
        try:
            create_project_overview()
            self.stdout.write(self.style.SUCCESS('Command completed successfully'))
        except Exception as e:
            raise CommandError('An error occurred: %s' % str(e))