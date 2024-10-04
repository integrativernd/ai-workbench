import os
import logging
from uuid import uuid4

from temporalio.client import Client
from temporalio.client import TLSConfig

from temporal_app.workflows import AIAgentWorkflow, AIAgentWorkflowInput

from config.settings import PRODUCTION



async def get_temporal_client():
    if PRODUCTION:
        # Read TLS certificate and key from environment variables
        with open(os.getenv("TEMPORAL_MTLS_TLS_CERT"), "rb") as f:
            client_cert = f.read()
        # Read TLS certificate and key from environment variables
        with open(os.getenv("TEMPORAL_MTLS_TLS_KEY"), "rb") as f:
            client_key = f.read()
        # Connect to Temporal server with TLS configuration
        return await Client.connect(
            os.getenv("TEMPORAL_HOST_URL"),
            namespace=os.getenv("TEMPORAL_NAMESPACE"),
            tls=TLSConfig(
                client_cert=client_cert,
                client_private_key=client_key,
            ),
        )
    else:
        # Connect to local Temporal server
        return await Client.connect("localhost:7233")


# Function to run workflow in local environment
async def run_workflow(ai_agent, user_message):
    # Configure logging (uncomment to enable)
    logging.basicConfig(level=logging.INFO)
    # Connect to local Temporal server
    client = await get_temporal_client()
    # Start the AIAgentWorkflow
    result = await client.start_workflow(
        AIAgentWorkflow.run,
        AIAgentWorkflowInput(
            ai_agent.token,
            user_message.content,
            str(user_message.author),
            str(user_message.channel.id),
        ),
        id=f"ai-agent-workflow-{uuid4()}",  # Generate unique workflow ID
        task_queue="ai-agent-task-queue",
    )
    return result
