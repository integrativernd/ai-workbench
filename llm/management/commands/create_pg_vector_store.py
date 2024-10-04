
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

    def add_arguments(self, parser):
        parser.add_argument('message', type=str, help='Description of the changes')
        parser.add_argument('--reindex', type=str, help='Reindex the documents')

    def handle(self, *args, **options):
        message = options['message'] or "Describe your source code."
        reindex = options['reindex']
        repository = CodeRepository.objects.get(title="ai-workbench")

        print(repository.title)

        documents = SimpleDirectoryReader(
            input_dir=".",
            recursive=True,
            filename_as_id=True,
            required_exts=[".py"],
            exclude=[
                ".env",
                ".venv",
                ".certs",
                ".pytest_cache",
                ".git", ".idea",
                ".vscode",
                "__pycache__",
                "__init__.py"
            ],
        ).load_data()

        vector_store = PGVectorStore.from_params(
            database="vector_db",
            host="localhost",
            password="password",
            port=5432,
            user="postgres",
            table_name="ai_workbench_vector_store",
            embed_dim=1536  # openai embedding dimension
        )

        if reindex:
            storage_context = StorageContext.from_defaults(vector_store=vector_store)
            vector_store_index = VectorStoreIndex.from_documents(
                documents,
                storage_context,
                show_progress=True,
            )
        else:
             vector_store_index = VectorStoreIndex.from_vector_store(vector_store=vector_store)

        retriever = VectorIndexRetriever(
            index=vector_store_index,
            similarity_top_k=3,
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

# References:
# https://christophergs.com/blog/production-rag-with-postgres-vector-store-open-source-models