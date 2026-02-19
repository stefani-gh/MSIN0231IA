import streamlit as st
import os
import re
from langchain_community.retrievers import WikipediaRetriever

# Load from Streamlit Secrets (Streamlit Cloud)
langsmith_api_key = st.secrets.get("LANGSMITH_API_KEY")
if langsmith_api_key:
    os.environ["LANGSMITH_API_KEY"] = langsmith_api_key
    os.environ["LANGSMITH_TRACING"] = "true"

# =============================================================================
# Settings of the Market Reserach Tool
# =============================================================================
# Sidebar for settings
st.sidebar.header("⚙️ LLM Setting")
model = st.sidebar.selectbox("Model", ["OpenAI", "Gemini", "Copilot"])
gemini_api_key = st.sidebar.text_input("Please enter your  API key", type="password")
default_gemini_api_key = st.secrets.get("GOOGLE_API_KEY", "")

if model != "Gemini":
    st.sidebar.info("Only Gemini is currently implemented. Please select Gemini to generate a report.")

# =============================================================================
# Market Research Tool on Wikipedia 
# =============================================================================
st.header("📃 Market Research Tool on Wikipedia")
st.markdown("""
            How to use this tool?
            1. Search an industry you are interested in in the textbox below and click "Search".
            2. After the search results are done, you can click the results to view the related Wikipedia links.
            3. If you want a summarised market reserach report, click the "Generate Industry Report." 
            """)

retriever = WikipediaRetriever(
    top_k_results = 5
)

if "search_submitted" not in st.session_state:
    st.session_state.search_submitted = False

def submit_search():
    st.session_state.search_submitted = True

query = st.text_input(
    "Search Wikipedia",
    placeholder="Type your industry here",
    on_change=submit_search
)
search_clicked = st.button("Search")

if search_clicked or st.session_state.search_submitted:
    st.session_state.search_submitted = False
    if query:
        try:
            with st.spinner("🔍 Searching Wikipedia..."):
                st.session_state.wiki_results = retriever.invoke(query)
                st.session_state.wiki_query = query
                st.session_state.pop("summary", None)
                st.session_state.pop("references", None)
        except Exception as e:
            st.error(f"Error: {str(e)}")
    else:
        st.warning("⚠️ Please enter a search term first!")

if "wiki_results" in st.session_state:
    docs = st.session_state.wiki_results
    if docs:
        st.write(f"### Results for: *{st.session_state.wiki_query}*")
        for i, doc in enumerate(docs, 1):
            title = doc.metadata.get('title', 'No title')
            url = doc.metadata.get('source', '')
            if url:
                st.markdown(f"**{i}. [{title}]({url})**")
            else:
                st.write(f"**{i}. {title}** — URL not available")
        if len(docs) < 5:
            st.info(f"⚠️ Only {len(docs)} result(s) found. Please try another term for more results.")
    else:
        st.info("⚠️ No results found. Try a different search term.")

# =============================================================================
# Industry Report 
# =============================================================================
st.header("📚 Industry Report")

if "wiki_results" in st.session_state and st.session_state.wiki_results:
    if st.button("Generate Industry Report"):
        api_key_to_use = gemini_api_key.strip() or default_gemini_api_key
        if model != "Gemini":
            st.warning("⚠️ Please select Gemini in the sidebar before generating the report.")
        elif not api_key_to_use:
            st.warning("⚠️ Please enter your API key in the setting first!")
        else:
            try:
                from langchain_google_genai import ChatGoogleGenerativeAI
                from langchain_core.messages import HumanMessage, SystemMessage

                combined_text = "\n\n".join(
                    [doc.page_content for doc in st.session_state.wiki_results]
                )

                llm = ChatGoogleGenerativeAI(
                    model="gemini-2.0-flash",
                    google_api_key=api_key_to_use
                )

                messages = [
                    SystemMessage(content=(
                        "You are a professional market researcher."
                        "Summarize the provided content from the wikipedia links generated above into a concise market research report"
                        "No more than 500 words. The report should include Definition and Scope, SWOT analysis of the market, "
                        "current market trends and insights, key players, relevant facts, conclusions."
                    )),
                    HumanMessage(content=f"Summarize this into a market research report:\n\n{combined_text}")
                ]

                with st.spinner("Generating market research report with Gemini..."):
                    response = llm.invoke(messages)
                    st.session_state.summary = response.content
                    references = []
                    seen_urls = set()
                    for doc in st.session_state.wiki_results:
                        title = doc.metadata.get("title", "Untitled")
                        url = doc.metadata.get("source", "").strip()
                        if url and url not in seen_urls:
                            references.append((title, url))
                            seen_urls.add(url)
                    st.session_state.references = references

            except Exception as e:
                error_text = str(e)
                if "RESOURCE_EXHAUSTED" in error_text or "429" in error_text:
                    retry_match = re.search(r"retry in ([0-9.]+)s", error_text, re.IGNORECASE)
                    retry_msg = f" Retry after about {retry_match.group(1)} seconds." if retry_match else ""
                    st.error(
                        "Gemini API quota/rate limit reached (429 RESOURCE_EXHAUSTED)."
                        f"{retry_msg}"
                    )
                    st.info(
                        "This usually means the API key has no available quota or billing is not enabled. "
                        "Check Gemini API usage limits and billing for this key, or use another key/project."
                    )
                else:
                    st.error(f"Failed to generate report: {error_text}")

# Display summary
if "summary" in st.session_state:
    st.write("### 📊 Market Research Summary")
    if st.session_state.get("references"):
        footnote_links = " ".join(
            [f"[{idx}]({url})" for idx, (_, url) in enumerate(st.session_state.references, 1)]
        )
        st.markdown(f"{st.session_state.summary}\n\nSources: {footnote_links}")
    else:
        st.write(st.session_state.summary)
    if st.session_state.get("references"):
        st.markdown("### References")
        for idx, (title, url) in enumerate(st.session_state.references, 1):
            st.markdown(f"{idx}. [{title}]({url})")
    st.caption(f"Word count: {len(st.session_state.summary.split())} | Powered by Gemini 2.0 Flash")
