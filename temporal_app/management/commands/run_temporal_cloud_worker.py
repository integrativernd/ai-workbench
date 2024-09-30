import os
import asyncio

from temporalio import activity, workflow
from temporalio.client import Client
from temporalio.worker import Worker

from temporal_app.activities import say_hello
from temporal_app.workflows import SayHello
from temporalio.client import Client, TLSConfig

from django.core.management.base import BaseCommand, CommandError
# from llm.response_types import get_response_type_for_message



async def run_worker():
    with open(os.getenv("TEMPORAL_MTLS_TLS_CERT"), "rb") as f:
        client_cert = f.read()

    with open(os.getenv("TEMPORAL_MTLS_TLS_KEY"), "rb") as f:
        client_key = f.read()

    client: Client = await Client.connect(
        os.getenv("TEMPORAL_HOST_URL"),
        namespace=os.getenv("TEMPORAL_NAMESPACE"),
        tls=TLSConfig(
            client_cert=client_cert,
            client_private_key=client_key,
        ),
    )

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