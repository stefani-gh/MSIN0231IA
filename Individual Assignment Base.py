import streamlit as st
import os
from langchain_community.retrievers import WikipediaRetriever

# Load from Streamlit Secrets (Streamlit Cloud)
os.environ["LANGSMITH_API_KEY"] = st.secrets["LANGSMITH_API_KEY"]
os.environ["LANGSMITH_TRACING"] = "true"

# =============================================================================
# Your Market Research Tool on Wikipedia 
# =============================================================================
st.header("Your Market Research Tool on Wikipedia")

retriever = WikipediaRetriever(top_k_results=5)

query = st.text_input("Search Wikipedia", placeholder="Type your input here")

if st.button("Search"):
    if query:
        try:
            with st.spinner("Searching Wikipedia..."):
                st.session_state.wiki_results = retriever.invoke(query)
                st.session_state.wiki_query = query
        except Exception:
            st.error("Failed to fetch Wikipedia results. Please try again in a moment.")
    else:
        st.warning("Please enter a search term first!")

# Display results from session state (persists across reruns without duplicating)
if "wiki_results" in st.session_state:
    docs = st.session_state.wiki_results
    if docs:
        st.write(f"### Results for: *{st.session_state.wiki_query}*")
        for i, doc in enumerate(docs, 1):
            with st.expander(f"Result {i}: {doc.metadata.get('title', 'No title')}"):
                st.write(doc.page_content)
    else:
        st.info("No results found. Try a different search term.")

# Sidebar for settings
st.sidebar.header("Chatbot Settings")
temperature = st.sidebar.slider("Temperature", 0.0, 1.0, 0.7)
model = st.sidebar.selectbox("Model", ["gpt-4", "claude-3"])
api_key = st.sidebar.text_input("Please enter your OpenAI API key", type="password")