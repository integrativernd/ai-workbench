from django.core.management.base import BaseCommand, CommandError
# from discord_server.chatbot_manager import run_chatbot_manager

class Command(BaseCommand):
    help = 'Start local chatbot manager'

    def handle(self, *args, **options):
        try:
            from discord_server.chatbot_manager import run_chatbot_manager
            self.stdout.write(self.style.SUCCESS('Starting chatbot manager'))
            run_chatbot_manager()
        except Exception as e:
            raise CommandError('An error occurred: %s' % str(e))