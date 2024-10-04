import os
from django.core.management.base import BaseCommand, CommandError
from ai_agents.models import AIAgent
from channels.models import Channel
from config.settings import SYSTEM_PROMPT

class Command(BaseCommand):
    help = 'Seed local AI agents'

    def handle(self, *args, **options):
        try:
          AIAgent.objects.create(
              name='beta',
              description=SYSTEM_PROMPT,
              is_active=True,
              application_id=os.getenv('DISCORD_APP_ID'),
              bot_token=os.getenv('BOT_RUN_TOKEN_2'),
          )
          channel = Channel.objects.create(
              channel_name='Beta REPL',
              channel_type='Terminal',
              channel_id='beta_repl',
          )
          
          self.stdout.write(self.style.SUCCESS('AI Agent created'))
        except Exception as e:
            raise CommandError('An error occurred: %s' % str(e))
        