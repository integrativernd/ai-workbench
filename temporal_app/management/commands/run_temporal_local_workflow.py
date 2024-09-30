import asyncio
from temporalio.client import Client
from temporal_app.workflows import SayHello
from django.core.management.base import BaseCommand, CommandError



async def run_workflow():
    # Create client connected to server at the given address
    client = await Client.connect("localhost:7233")

    # Execute a workflow
    result = await client.execute_workflow(
        SayHello.run, "Temporal", id="hello-workflow", task_queue="hello-task-queue"
    )

    print(f"Result: {result}")

class Command(BaseCommand):
    help = 'Test response types'

    def handle(self, *args, **options):
        try:
           asyncio.run(run_workflow())
        except Exception as e:
            raise CommandError('An error occurred: %s' % str(e))