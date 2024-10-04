import asyncio

from temporalio.worker import Worker

from temporal_app.activities import AIAgentActivityManager
from temporal_app.workflows import AIAgentWorkflow
from django.core.management.base import BaseCommand, CommandError
from temporal_app.client import get_temporal_client

async def main():
    client = await get_temporal_client()
    activity_manager = AIAgentActivityManager(client)
    worker = Worker(
        client,
        task_queue="ai-agent-task-queue",
        workflows=[AIAgentWorkflow],
        activities=[
            activity_manager.perform_activity,
            activity_manager.get_tools,
            activity_manager.call_tool,
        ],
    )
    await worker.run()

class Command(BaseCommand):
    help = 'Start Temporal Worker'

    def handle(self, *args, **options):
        print('Starting Temporal Worker')
        try:
           asyncio.run(main())
        except Exception as e:
            raise CommandError('An error occurred: %s' % str(e))