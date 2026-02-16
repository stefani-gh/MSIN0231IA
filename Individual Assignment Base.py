import streamlit as st
import pickle #for saving and loading ML models
import time
import os

# Load from Streamlit Secrets (Streamlit Cloud)
os.environ["LANGSMITH_API_KEY"] = st.secrets["LANGSMITH_API_KEY"]
os.environ["LANGSMITH_TRACING"] = "true"

# =============================================================================
# Your Market Research Tool on Wikipedia 
# =============================================================================
st.header("Wikipedia Tool")
from langchain_community.retrievers import WikipediaRetriever

retriever = WikipediaRetriever(top_k_results=5)

# Text box for user input
query = st.text_input("Search Wikipedia", placeholder="Type your input here")

if query:
    with st.spinner("Searching Wikipedia..."):
        docs = retriever.invoke(query)
    
    st.write(f"### Results for: *{query}*")
    for i, doc in enumerate(docs, 1):
        with st.expander(f"Result {i}: {doc.metadata.get('title', 'No title')}"):
            st.write(doc.page_content)

# Search button
if st.button("Search") and query:
    with st.spinner("Searching Wikipedia..."):
        docs = retriever.invoke(query)
    
    st.write(f"### Results for: *{query}*")
    for i, doc in enumerate(docs, 1):
        with st.expander(f"Result {i}: {doc.metadata.get('title', 'No title')}"):
            st.write(doc.page_content)

elif st.button and not query:
    st.warning("Please enter a search term first!")


# Sidebar for settings
st.sidebar.header("Chatbot Settings")
temperature = st.sidebar.slider("Temperature", 0.0, 1.0, 0.7)
model = st.sidebar.selectbox("Model", ["gpt-4", "claude-3"])
api_key = st.sidebar.text_input("Please enter your OpenAI API key",
type = "password")
