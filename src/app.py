import os
import streamlit as st
from rag import RagPipeline

st.set_page_config(page_title="NL Expat Guide", page_icon="🇳🇱")

INDEX_PATH = os.path.join(os.path.dirname(__file__), "..", "index", "faiss.index")
if not os.path.exists(INDEX_PATH):
   with st.spinner("First run: building the search index from source documents..."):
      from ingest import build_index
      build_index()

st.title("🇳🇱 NL Expat Guide")
st.caption(
    "Ask a question about immigrating to or settling in the Netherlands. "
    "Answers are grounded in a small curated set of official and reputable sources, "
    "with links so you can verify anything important yourself."
)

st.warning(
    "This is a demo project, not legal or tax advice. For anything binding, "
    "always confirm with the IND (immigration) or the Belastingdienst (tax)."
)


@st.cache_resource
def load_pipeline():
    return RagPipeline()


pipeline = load_pipeline()

question = st.text_input(
    "Your question",
    placeholder="e.g. Do I need a BSN before I can open a bank account?",
)

if st.button("Ask") and question:
    with st.spinner("Looking this up in the source documents..."):
        result = pipeline.answer(question)

    st.markdown("### Answer")
    st.write(result["answer"])

    if result["sources"]:
        st.markdown("### Sources")
        for s in result["sources"]:
            st.markdown(f"- [{s['title']}]({s['url']})")

st.divider()
st.caption(
    "Currently covers: highly skilled migrant permits, BSN registration, 30% ruling, bank accounts and insurance. "
    "Built with Streamlit + sentence-transformers + FAISS + Groq."
)
