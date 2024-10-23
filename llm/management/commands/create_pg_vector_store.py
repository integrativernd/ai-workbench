from llama_index.llms.anthropic import Anthropic
from llama_index.vector_stores.postgres import PGVectorStore
from llama_index.core import (
  Settings,
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

class Command(BaseCommand):
    help = 'Create Llama Index PostgreSQL vector store'

    def handle(self, *args, **options):
        repository = CodeRepository.objects.get(title="ai-workbench")
        print(repository.title)
        documents = SimpleDirectoryReader(
            input_dir=".",
            recursive=True,
            filename_as_id=True,
            required_exts=[".py", '.pdf'],
            exclude=[
                ".env",
                ".venv",
                ".certs",
                ".pytest_cache",
                ".git",
                ".idea",
                ".vscode",
                "__pycache__",
                "__init__.py",
                "credentials,json"
            ],
        ).load_data()
        
        print(f"Found {len(documents)} documents")

        for document in documents:
            print(document.metadata['file_path'])

        vector_store = PGVectorStore.from_params(
            database="vector_db",
            host="localhost",
            password="password",
            port=5432,
            user="postgres",
            table_name="ai_workbench_vector_store",
            # openai embedding dimension
            embed_dim=1536
        )

        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        
        VectorStoreIndex.from_documents(
            documents,
            storage_context,
            show_progress=True,
        )
