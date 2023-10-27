import os

import openai
import streamlit as st
from dotenv import load_dotenv, find_dotenv

from utils import query_agent

_ = load_dotenv(find_dotenv()) # read local .env file
openai.api_key = os.environ['OPENAI_API_KEY']

st.title("Let's do some analysis on your CSV data!")
st.header("Upload your CSV file")

data = st.file_uploader("Upload a CSV file", type=["csv"])

query = st.text_area("What do you want to know about your data?")
button = st.button("Generate")

if button:
    answer = query_agent(data, query)
    st.write(answer)