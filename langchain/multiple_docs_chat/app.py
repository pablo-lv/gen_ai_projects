import os
import tempfile

from dotenv import load_dotenv, find_dotenv
import streamlit as st
from langchain.document_loaders import Docx2txtLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings, HuggingFaceInstructEmbeddings
from langchain.llms import HuggingFaceHub, OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.vectorstores import FAISS
from PyPDF2 import PdfReader

from htmlTemplates import user_template, bot_template, css

_ = load_dotenv(find_dotenv()) # read local .env file
embedding_model_name = os.environ.get("EMBEDDING_MODEL_NAME")
repo = os.environ.get("GOOGLE_FLAN_T5_XXL")

def get_vector_store(text_chunks):
    embeddings = HuggingFaceInstructEmbeddings(model_name=embedding_model_name)
    vectorstore = FAISS.from_texts(text_chunks, embedding=embeddings)
    return vectorstore

def get_conversation_chain(vector_store):
    llm = HuggingFaceHub(repo_id=repo, model_kwargs={"temperature":0.5, "max_length": 1024})
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    conversation_chain = ConversationalRetrievalChain.from_llm(llm=OpenAI(), retriever=vector_store.as_retriever(), memory=memory)

    return conversation_chain

def get_documents_text(docs) -> str:
    documents_text = []
    for doc in docs:
        filetype, upload_file = get_file_details(doc)
        if filetype == ".docx":
            temp_file_path = save_tmp_file(upload_file)
            loader = Docx2txtLoader(temp_file_path)
            documents_text.append(loader.load())
        elif filetype == ".pdf":
            pdf_reader = PdfReader(doc)
            for page in pdf_reader.pages:
                documents_text.append(page.extract_text())
    raw_text = [page.page_content for pages in documents_text for page in pages]
    raw_text = '\n'.join(raw_text)
    return raw_text.replace('\n\n\n', '\n')


def get_file_details(doc):
    filetype = os.path.splitext(doc.name)[1].lower() if doc else None
    upload_file = doc.read() if doc else None
    return filetype, upload_file


def save_tmp_file(upload_file) -> str:
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file.write(upload_file)
    temp_file_path = temp_file.name
    return temp_file_path


def get_text_chunks(text):
    text_splitter = CharacterTextSplitter(separator="\n", chunk_size=1000, chunk_overlap=200, length_function=len)
    return text_splitter.split_text(text)

def handle_user_input(user_question):
    response = st.session_state.conversation({'question': user_question})
    st.session_state['chat_history'] = response['chat_history']
    for i, message in enumerate(st.session_state.chat_history):
        if i % 2 == 0:
            st.write(user_template.replace("{{MSG}}", message.content), unsafe_allow_html=True)
        else:
            st.write(bot_template.replace("{{MSG}}", message.content), unsafe_allow_html=True)

def init_session_state():
    if 'conversation' not in st.session_state:
        st.session_state['conversation'] = None
    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = None

def main():
    st.set_page_config("Chat with multiple documents", page_icon=":books:")
    st.write(css, unsafe_allow_html=True)
    st.header("Chat with multiple documents :books:")

    user_question = st.text_input("Ask a question from your documents")
    init_session_state()

    with st.sidebar:
        st.subheader("Chat with Document")
        st.text("LLM chatapp using langchain")
        st.subheader("Your Documents")
        docs = st.file_uploader("Upload your documents", type=["docx", "pdf"], accept_multiple_files=True)

        if st.button("Process"):
            with st.spinner("Processing..."):
                # Extract text from documents
                raw_text = get_documents_text(docs)
                # Split text into chunks
                text_chunks = get_text_chunks(raw_text)
                # Create vector store FAISS
                vector_store = get_vector_store(text_chunks)
                # Create conversation chain
                conversation_chain = get_conversation_chain(vector_store)
                st.session_state['conversation'] = conversation_chain
                st.success("Done!")

    if user_question and st.session_state.conversation:
        handle_user_input(user_question)


if __name__ == "__main__":
    main()