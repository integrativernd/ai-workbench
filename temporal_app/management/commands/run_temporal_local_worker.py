import asyncio

from temporalio import activity, workflow
from temporalio.client import Client
from temporalio.worker import Worker

from temporal_app.activities import say_hello
from temporal_app.workflows import SayHello

async def run_worker():
    client = await Client.connect("localhost:7233", namespace="default")
    worker = Worker(
        client, task_queue="hello-task-queue", workflows=[SayHello], activities=[say_hello]
    )
    await worker.run()


# if __name__ == "__main__":
#     asyncio.run(main())

from django.core.management.base import BaseCommand, CommandError
from llm.response_types import get_response_type_for_message

class Command(BaseCommand):
    help = 'Test response types'

    def handle(self, *args, **options):
        try:
           asyncio.run(run_worker())
        except Exception as e:
            raise CommandError('An error occurred: %s' % str(e))