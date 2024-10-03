import os
from temporalio.client import Client
from config.settings import PRODUCTION
from temporalio.client import TLSConfig



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