from django.core.management.base import BaseCommand, CommandError
from tools.github.issues import read_github_issue

class Command(BaseCommand):
    help = 'Create project overview'

    def handle(self, *args, **options):
        try:
            result = read_github_issue({ 'issue_number': 2 })
            # self.stdout.write(self.style.SUCCESS('Command completed successfully'))
            self.stdout.write(result[0])
            self.stdout.write(result[1])
        except Exception as e:
            raise CommandError('An error occurred: %s' % str(e))