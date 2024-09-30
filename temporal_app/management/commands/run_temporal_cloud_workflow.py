import os
import asyncio
from temporalio.client import Client
from temporal_app.workflows import SayHello
from temporalio.client import Client, TLSConfig
from django.core.management.base import BaseCommand, CommandError

async def run_workflow():
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