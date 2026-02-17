import streamlit as st
import os
from langchain_community.retrievers import WikipediaRetriever

# Load from Streamlit Secrets (Streamlit Cloud)
os.environ["LANGSMITH_API_KEY"] = st.secrets["LANGSMITH_API_KEY"]
os.environ["LANGSMITH_TRACING"] = "true"

# =============================================================================
# Settings of the Market Reserach Tool
# =============================================================================
# Sidebar for settings
st.sidebar.header("LLM Settings")
model = st.sidebar.selectbox("Model", ["ChatGPT5.2", "Gemini", "Copilot"])
gemini_api_key = st.sidebar.text_input("Please enter your  API key", type="password")

# =============================================================================
# Your Market Research Tool on Wikipedia 
# =============================================================================
st.header("Your Market Research Tool on Wikipedia")

retriever = WikipediaRetriever()

query = st.text_input("Search Wikipedia", placeholder="Type your input here")

if st.button("Search"):
    if query:
        try:
            with st.spinner("Searching Wikipedia..."):
                st.session_state.wiki_results = retriever.invoke(query)
                st.session_state.wiki_query = query
        except Exception as e:
            st.error(f"Error: {str(e)}")
    else:
        st.warning("Please enter a search term first!")

if "wiki_results" in st.session_state:
    docs = st.session_state.wiki_results
    if docs:
        st.write(f"### Results for: *{st.session_state.wiki_query}*")
        if len(docs) < 5:
            st.info(f"Only {len(docs)} result(s) found. Please try another term for more results.")
        for i, doc in enumerate(docs, 1):
            title = doc.metadata.get('title', 'No title')
            url = doc.metadata.get('source', '')
            if url:
                st.markdown(f"**{i}. [{title}]({url})**")
            else:
                st.write(f"**{i}. {title}** — URL not available")
    else:
        st.info("No results found. Try a different search term.")

# =============================================================================
# Industry Report 
# =============================================================================
st.header("Industry Report")

if "wiki_results" in st.session_state and st.session_state.wiki_results:
    if st.button("Summarize as Market Research"):
        if not gemini_api_key:
            st.warning("Please enter your Gemini API key in the sidebar first!")
        else:
            try:
                from langchain_google_genai import ChatGoogleGenerativeAI
                from langchain.schema import HumanMessage, SystemMessage

                combined_text = "\n\n".join(
                    [doc.page_content for doc in st.session_state.wiki_results]
                )

                llm = ChatGoogleGenerativeAI(
                    model="gemini-1.5-flash",
                    google_api_key=gemini_api_key
                )

                messages = [
                    SystemMessage(content=(
                        "You are a professional market research analyst. "
                        "Summarize the provided content into a concise market research report "
                        "of no more than 500 words. Focus on key insights, trends, and relevant facts."
                    )),
                    HumanMessage(content=f"Summarize this into a market research report:\n\n{combined_text}")
                ]

                with st.spinner("Generating market research report with Gemini..."):
                    response = llm.invoke(messages)
                    st.session_state.summary = response.content

            except Exception as e:
                st.error(f"Failed to generate report: {str(e)}")

# Display summary
if "summary" in st.session_state:
    st.write("### 📊 Market Research Summary")
    st.write(st.session_state.summary)
    st.caption(f"Word count: {len(st.session_state.summary.split())} | Powered by Gemini 1.5 Flash")
