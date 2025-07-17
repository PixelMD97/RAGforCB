import streamlit as st
import os
from datetime import datetime
from rag_pipeline import load_or_build_qa_chain
import requests

# Webhook for Google Sheets
GOOGLE_SHEET_WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbwDkEQESqtxHU0C7N5-i_3755l7Pc2oht76N-o7YS9SczMODl3Mg1u6jhzRv6EOLbwo/exec"

def log_feedback_to_google_sheets(question, answer, thumbs_up):
    payload = {
        "timestamp": datetime.now().isoformat(),
        "question": question,
        "answer": answer,
        "thumbs_up": "Yes" if thumbs_up else "No"
    }
    try:
        requests.post(GOOGLE_SHEET_WEBHOOK_URL, json=payload, timeout=10)
    except Exception as e:
        print(" Logging error:", e)

#  Load RAG pipeline once
@st.cache_resource
def get_chain():
    return load_or_build_qa_chain()

#  Layout
st.set_page_config(page_title="Crystal Brain – Clinical Study Chatbot", layout="centered")

# Title
st.markdown(
    "<h1 style='text-align: center; color: #2c3e50;'>🧠 Crystal Brain – Clinical Study Chatbot (RAG)</h1>",
    unsafe_allow_html=True
)

st.markdown("<b>Stelle eine Frage zu den Studiendokumenten (Deutsch oder Englisch):</b>", unsafe_allow_html=True)

# 💬 Input
query = st.text_input(" ", placeholder="e.g. What are the exclusion criteria?")

# 🔍 Examples
with st.expander("🔍 Beispiel-Fragen anzeigen"):
    st.markdown(
        "- Was ist die Definition von Kreislaufversagen?\n"
        "- Welche Patienteninfo wird benötigt aus EPIC?\n"
        "- Wer ist der PI der Studie?\n"
        "- Welche Assessments werden erhoben?\n"
        "- How many tablets are available?\n"
        "- What inclusion criteria apply?\n"
        "- What are the exclusion criteria?"
    )

# 🔄 Chat logic
if query:
    result = get_chain()({"query": query})
    answer = result["result"]
    sources = result.get("source_documents", [])

    # Display Q
    st.markdown(
        f"""
        <div style='display: flex; justify-content: flex-start; margin-top: 2rem;'>
            <div style='background-color: #f0f0f0; padding: 0.8rem 1rem; border-radius: 8px; max-width: 90%;'>
                <b>Du:</b><br>{query}
            </div>
        </div>
        """, unsafe_allow_html=True
    )

    # Display A
    st.markdown(
        f"""
        <div style='display: flex; justify-content: flex-start; margin-top: 1rem;'>
            <div style='background-color: #d6eaf8; padding: 0.8rem 1rem; border-radius: 8px; max-width: 90%;'>
                <b>RAG-Bot:</b><br>{answer}
            </div>
        </div>
        """, unsafe_allow_html=True
    )

    # 📚 Sources
    if sources:
        with st.expander("📚 Quellen anzeigen"):
            for doc in sources:
                metadata = doc.metadata
                source = metadata.get("source", "Unbekannt")
                page = metadata.get("page", "?") + 1
                filename = os.path.basename(source).replace(".pdf", "").replace("-", " ").title()
                st.markdown(f"📄 **{filename}**, Seite {page}")

    # ✅ Feedback
    st.markdown("#### War die Antwort hilfreich?")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("👍 Ja"):
            st.success("Danke für dein Feedback!")
            log_feedback_to_google_sheets(query, answer, True)
    with col2:
        if st.button("👎 Nein"):
            st.warning("Wir arbeiten daran, es zu verbessern.")
            log_feedback_to_google_sheets(query, answer, False)

# Footer
st.markdown("<hr><small>⚠️ Diese Anwendung ist ein Prototyp und dient nur Demonstrationszwecken. Fragen und Antworten basieren auf bereitgestellten Dokumenten.</small>", unsafe_allow_html=True)
