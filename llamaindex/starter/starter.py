import os
import sys
import logging

from llama_index import VectorStoreIndex, SimpleDirectoryReader, StorageContext, load_index_from_storage
from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv()) # read local .env file

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))


if (not os.path.exists('./storage')):
    # Load the documents and create the index
    documents = SimpleDirectoryReader(os.path.join(os.path.dirname(__file__), 'data')).load_data()
    index = VectorStoreIndex.from_documents(documents)
    # store it for later
    index.storage_context.persist()
else:
    storage_context = StorageContext.from_defaults(persist_dir='./storage')
    index = load_index_from_storage(storage_context)


query_engine = index.as_query_engine()
response = query_engine.query("What did the author do growing up?")
print(response)