from llama_index.llms.anthropic import Anthropic
from llama_index.core import Settings

tokenizer = Anthropic().tokenizer
Settings.tokenizer = tokenizer


from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.query_engine import RetrieverQueryEngine


from django.core.management.base import BaseCommand
from llama_index.core import (
  get_response_synthesizer,
  SimpleDirectoryReader,
  load_index_from_storage,
  StorageContext
)
from llama_index.vector_stores.postgres import PGVectorStore



class Command(BaseCommand):
    help = 'Test response types'

    def add_arguments(self, parser):
        parser.add_argument('message', type=str, help='Description of the changes')

    def handle(self, *args, **options):
        message = options['message']

        documents = SimpleDirectoryReader(
            input_dir="llm",
            exclude=[
                ".env",
                ".venv",
                ".certs",
                ".pytest_cache",
                ".git", ".idea",
                ".vscode",
                "__pycache__"
            ],
        ).load_data()

        for doc in documents:
            print(doc.metadata['file_path'])

        vector_store = PGVectorStore.from_params(
            database="vector_db",
            host="localhost",
            password="password",
            port=5432,
            user="postgres",
            table_name="ai_workbench_vector_store",
            embed_dim=1536  # openai embedding dimension
        )

        persist_dir = "data"

        vector_store.persist(persist_dir)

        # loaded_vector_store = PGVectorStore.load(persist_dir)
      
        # index = VectorStoreIndex.from_documents(documents)
        # storage_context = StorageContext.from_defaults(persist_dir="data")
        # storage_context = StorageContext.from_defaults(vector_store=vector_store)

        storage_context = StorageContext.from_defaults(
            persist_dir=persist_dir,
            vector_store=vector_store
        )
                  
        index = load_index_from_storage(storage_context)

        # index = VectorStoreIndex.from_documents(
        #     documents,
        #     storage_context=storage_context,
        #     show_progress=True
        # )

        retriever = VectorIndexRetriever(
            index=index,
            similarity_top_k=10,
        )
        
        response_synthesizer = get_response_synthesizer(
            llm=Anthropic(model="claude-3-opus-20240229"),
            response_mode="simple_summarize",
        )

        query_engine = RetrieverQueryEngine(
            retriever=retriever,
            response_synthesizer=response_synthesizer,
        )

        # index.storage_context.persist(persist_dir=f"data")

        # query_engine = index.as_query_engine(
        #     llm=Anthropic(model="claude-3-opus-20240229")
        # )

        response = query_engine.query(message)

        print(response)