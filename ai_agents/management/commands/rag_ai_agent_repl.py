
from llama_index.llms.anthropic import Anthropic
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.vector_stores.postgres import PGVectorStore
from llama_index.core import (
  Settings,
  get_response_synthesizer,
  VectorStoreIndex,
  SimpleDirectoryReader,
  StorageContext,
)

from django.core.management.base import BaseCommand

from ai_agents.models import CodeRepository


tokenizer = Anthropic().tokenizer

Settings.tokenizer = tokenizer

Settings.llm = Anthropic(
    model="claude-3-opus-20240229",
    # system_prompt=SYSTEM_PROMPT,
)

# EMBED_MODEL = HuggingFaceEmbedding(
#     model_name="WhereIsAI/UAE-Large-V1",
#     embed_batch_size=10, # 24 # open-source embedding model
# )

# Settings.embed_model = EMBED_MODEL

class Command(BaseCommand):
    help = 'Test response types'

    def handle(self, *args, **options):
        print('RAG AI Agent REPL')
        vector_store = PGVectorStore.from_params(
            database="vector_db",
            host="localhost",
            password="password",
            port=5432,
            user="postgres",
            table_name="ai_workbench_vector_store",
            embed_dim=1536 # openai embedding dimension
        )

        vector_store_index = VectorStoreIndex.from_vector_store(vector_store=vector_store)

        chat_engine = vector_store_index.as_chat_engine(
            llm=Settings.llm,
            chat_mode="best",
        )
        streaming_response = chat_engine.stream_chat("""
           List all the code files you are aware of.
        """)
        for token in streaming_response.response_gen:
            print(token, end="")