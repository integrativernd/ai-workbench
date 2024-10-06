
from llama_index.llms.anthropic import Anthropic
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.vector_stores.postgres import PGVectorStore
from llama_index.core import (
  Settings,
  get_response_synthesizer,
  VectorStoreIndex,
)

from django.core.management.base import BaseCommand

from ai_agents.models import CodeRepository


tokenizer = Anthropic().tokenizer

Settings.tokenizer = tokenizer

Settings.llm = Anthropic(
    model="claude-3-opus-20240229",
    # system_prompt=SYSTEM_PROMPT,
)

class Command(BaseCommand):
    help = 'Test response types'

    def add_arguments(self, parser):
        parser.add_argument('message', type=str, help='The message you want to send')

    def handle(self, *args, **options):
        message = options['message'] or "Describe your source code."

        vector_store = PGVectorStore.from_params(
            database="vector_db",
            host="localhost",
            password="password",
            port=5432,
            user="postgres",
            table_name="ai_workbench_vector_store",
            embed_dim=1536  # openai embedding dimension
        )

        vector_store_index = VectorStoreIndex.from_vector_store(vector_store=vector_store)

        retriever = VectorIndexRetriever(
            index=vector_store_index,
            similarity_top_k=100,
        )
        
        response_synthesizer = get_response_synthesizer(
            llm=Anthropic(model="claude-3-opus-20240229"),
            # response_mode="refine",
            streaming=True,
        )

        query_engine = RetrieverQueryEngine(
            retriever=retriever,
            response_synthesizer=response_synthesizer,
        )

        streaming_response = query_engine.query(message)
        streaming_response.print_response_stream()

        print(streaming_response)
