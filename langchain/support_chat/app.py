import os

import streamlit as st
import openai
from dotenv import load_dotenv, find_dotenv
from utils import *
from constants import WEBSITE_URL, PINECONE_ENVIRONMENT, PINECONE_INDEX

import constants

_ = load_dotenv(find_dotenv()) # read local .env file
openai.api_key = os.environ['OPENAI_API_KEY']

if 'HUGGINGFACE_API_KEY' not in st.session_state:
    st.session_state['HUGGINGFACE_API_KEY'] = ''
if 'PINECONE_API_KEY' not in st.session_state:
    st.session_state['PINECONE_API_KEY'] = ''


st.title("AI Assistance for WEB")

st.sidebar.title("Settings")
st.session_state['HUGGINGFACE_API_KEY'] = st.sidebar.text_input("HuggingFace API Key", type="password")
st.session_state['PINECONE_API_KEY'] = st.sidebar.text_input("Pinecone API Key", type="password")

load_button = st.sidebar.button("Load Data to Pinecone", key="load_button")


#If the bove button is clicked, pushing the data to Pinecone...
if load_button:
    #Proceed only if API keys are provided
    if st.session_state['HUGGINGFACE_API_KEY'] !="" and st.session_state['PINECONE_API_KEY']!="" :

        #Fetch data from site
        site_data=get_website_data(constants.WEBSITE_URL)
        st.write("Data pull done...")

        #Split data into chunks
        chunks_data=split_data(site_data)
        st.write("Splitting data done...")

        #Creating embeddings instance
        embeddings=create_embeddings()
        st.write("Embeddings instance creation done...")

        #Push data to Pinecone
        push_to_pinecone(st.session_state['PINECONE_API_KEY'],constants.PINECONE_ENVIRONMENT,constants.PINECONE_INDEX,embeddings,chunks_data)
        st.write("Pushing data to Pinecone done...")

        st.sidebar.success("Data pushed to Pinecone successfully!")
    else:
        st.sidebar.error("Ooopssss!!! Please provide API keys.....")

#********SIDE BAR Funtionality ended*******

# Captures User Inputs
prompt = st.text_input('How can I help you my friend ❓', key="prompt")  # The box for the text prompt
document_count = st.slider('No.Of links to return 🔗 - (0 LOW || 5 HIGH)', 0, 5, 2, step=1)

submit = st.button("Search")

if submit:
    # Proceed only if API keys are provided
    if st.session_state['HUGGINGFACE_API_KEY'] != "" and st.session_state['PINECONE_API_KEY'] != "":

        # Creating embeddings instance
        embeddings = create_embeddings()
        st.write("Embeddings instance creation done...")

        # Pull index data from Pinecone
        index = pull_from_pinecone(st.session_state['PINECONE_API_KEY'], constants.PINECONE_ENVIRONMENT,
                                   constants.PINECONE_INDEX, embeddings)
        st.write("Pinecone index retrieval done...")

        # Fetch relevant documents from Pinecone index
        relevant_docs = get_similar_docs(index, prompt, document_count)
        st.write(relevant_docs)

        # Displaying search results
        st.success("Please find the search results :")
        # Displaying search results
        st.write("search results list....")
        for document in relevant_docs:
            st.write("👉**Result : " + str(relevant_docs.index(document) + 1) + "**")
            st.write("**Info**: " + document.page_content)
            st.write("**Link**: " + document.metadata['source'])



    else:
        st.sidebar.error("Ooopssss!!! Please provide API keys.....")