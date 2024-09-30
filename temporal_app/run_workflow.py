import os
from temporalio.client import Client
from temporal_app.workflows import SayHello
from temporalio.client import TLSConfig
import logging
from config.settings import PRODUCTION



async def run_production_workflow():
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
    return await client.execute_workflow(
        SayHello.run, "Temporal", id="hello-workflow", task_queue="hello-task-queue"
    )


async def run_local_workflow():
    # Uncomment the lines below to see logging output
    # import logging
    logging.basicConfig(level=logging.INFO)

    # Start client
    client = await Client.connect("localhost:7233")

    return await client.execute_workflow(
        SayHello.run, "Temporal", id="hello-workflow", task_queue="hello-task-queue"
    )


async def run_workflow():
    if PRODUCTION:
        return await run_production_workflow()
    else:
        return await run_local_workflow()