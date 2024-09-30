import asyncio

from temporalio.client import Client
from temporalio.worker import Worker

from temporal_app.activities import say_hello
from temporal_app.workflows import SayHello
from django.core.management.base import BaseCommand, CommandError

async def run_worker():
    client = await Client.connect("localhost:7233", namespace="default")
    worker = Worker(
        client, task_queue="hello-task-queue", workflows=[SayHello], activities=[say_hello]
    )
    await worker.run()


class Command(BaseCommand):
    help = 'Test response types'

    def handle(self, *args, **options):
        try:
           asyncio.run(run_worker())
        except Exception as e:
            raise CommandError('An error occurred: %s' % str(e))