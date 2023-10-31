import os
import sys
import logging

import chromadb
from llama_index import VectorStoreIndex, SimpleDirectoryReader, StorageContext, load_index_from_storage, ServiceContext
from llama_index.vectore_stores import ChromaVectorStore
from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv()) # read local .env file

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))






if (not os.path.exists('./storage')):
    # Load the documents and create the index
    documents = SimpleDirectoryReader(os.path.join(os.path.dirname(__file__), 'data')).load_data()
    service_context = ServiceContext.from_defaults(chunk_size=1000)
    index = VectorStoreIndex.from_documents(documents, service_context=service_context)
    # store it for later
    index.storage_context.persist()
else:
    chroma_client = chromadb.PersistentClient()
    chroma_collection = chroma_client.create_collaction('quickstart')
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

    storage_context = StorageContext.from_defaults(vector_store=vector_store, persist_dir='./storage')
    index = load_index_from_storage(storage_context)



query_engine = index.as_query_engine()
response = query_engine.query("What did the author do growing up?")
print(response)