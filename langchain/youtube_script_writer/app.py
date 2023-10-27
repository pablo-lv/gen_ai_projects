import os
import streamlit as st

from utils import generate_script

st.markdown("""
<style>
div.stButton > button:first-child {
    background-color: #0099ff;
    color: #ffffff;
}
div.stButton > button:hover {
    background-color: #00ff00;
    color: #FFFFFF;
}
</style>""", unsafe_allow_html=True)

if 'API_KEY' not in st.session_state:
    st.session_state['API_KEY'] = ''

st.title("Youtube Script Writer")

st.sidebar.title("Settings")
st.session_state['API_KEY'] = st.sidebar.text_input("API Key", type="password")
st.sidebar.image(os.path.join(os.path.dirname(__file__), 'Youtube.jpg'), width=300, use_column_width=True)


prompt = st.text_input("Please provide the topic of the video", key="prompt")
video_length = st.text_input("Expected Video length in minutes", key="video_length")
creativity = st.slider("Creativity", min_value=0.0, max_value=1.0, value=0.2, step=0.1, key="creativity")

submit = st.button("Generate script")

if submit:
    if st.session_state['API_KEY']:
        search_result,title,script = generate_script(prompt,video_length,creativity,st.session_state['API_KEY'])

        st.success("Hope you like this script!")
        st.subheader("Title:")
        st.write(title)
        st.subheader("Your Video Script:")
        st.write(script)
        st.subheader("Check out the video here:")

        with st.expander("Show me "):
            st.info(search_result)
    else:
        st.error("Please provide an API Key")

