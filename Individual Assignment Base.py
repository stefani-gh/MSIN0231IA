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
""" if "wiki_results" in st.session_state:
    docs = st.session_state.wiki_results
    if docs:
        st.write(f"### Results for: *{st.session_state.wiki_query}*")
        if len(docs) < 5:
            st.info(f"Only {len(docs)} result(s) found. Try other terms for more results.")
        for i, doc in enumerate(docs, 1):
            with st.expander(f"Result {i}: {doc.metadata.get('title', 'No title')}"):
                st.write(doc.page_content)
    else:
        st.info("No results found. Try a different search term.") """

# =============================================================================
# Industry Report
# =============================================================================

st.header("Industry Report")

if "wiki_results" in st.session_state and st.session_state.wiki_results:
    if st.button("Summarize as Market Research"):
        if not api_key:
            st.warning("Please enter your OpenAI API key in the sidebar first!")
        else:
            try:
                from langchain_openai import ChatOpenAI
                from langchain.schema import HumanMessage, SystemMessage

                # Combine all Wikipedia results into one text
                combined_text = "\n\n".join(
                    [doc.page_content for doc in st.session_state.wiki_results]
                )

                llm = ChatOpenAI(
                    model=model,
                    temperature=temperature,
                    api_key=api_key
                )

                messages = [
                    SystemMessage(content=(
                        "You are a professional market research analyst. "
                        "Summarize the provided content into a concise market research report "
                        "of no more than 500 words. Focus on key insights, trends, and relevant facts."
                    )),
                    HumanMessage(content=f"Summarize this into a market research report:\n\n{combined_text}")
                ]

                with st.spinner("Generating market research summary..."):
                    response = llm.invoke(messages)
                    st.session_state.summary = response.content

            except Exception as e:
                st.error(f"Failed to generate summary: {str(e)}")

# Display summary
if "summary" in st.session_state:
    st.write("### 📊 Market Research Summary")
    st.write(st.session_state.summary)
    word_count = len(st.session_state.summary.split())
    st.caption(f"Word count: {word_count}")

# Sidebar for settings
st.sidebar.header("LLM Settings")
model = st.sidebar.selectbox("Model", ["ChatGPT5.2", "Gemini", "Copilot"])
api_key = st.sidebar.text_input("Please enter your OpenAI API key", type="password")