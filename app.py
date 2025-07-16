import streamlit as st
from rag_pipeline import load_or_build_qa_chain
from datetime import datetime
import os
import requests

# --- Page Setup ---
st.set_page_config(page_title="Crystal Brain – Clinical Chatbot", layout="wide")

# --- Google Sheets Logging ---
GOOGLE_SHEET_WEBHOOK_URL = "https://your-google-webhook-url"  # Replace with your own

def log_to_sheets(question, answer, feedback):
    payload = {
        "timestamp": datetime.now().isoformat(),
        "question": question,
        "answer": answer,
        "feedback": feedback
    }
    try:
        requests.post(GOOGLE_SHEET_WEBHOOK_URL, json=payload)
    except Exception as e:
        st.warning(f"⚠️ Fehler beim Loggen: {e}")

# --- Session State ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- Header ---
st.markdown(
    "<h1 style='text-align: center; color: #2c3e50;'>🧠 Crystal Brain – Clinical Study Chatbot (RAG)</h1>",
    unsafe_allow_html=True
)
st.markdown("💬 **Stelle eine Frage zu den Studiendokumenten (Deutsch oder Englisch):**")

# --- Example Prompts ---
with st.expander("🔍 Beispiel-Fragen anzeigen"):
    st.markdown(
        "- Was ist die Definition von Kreislaufversagen?\n"
        "- Welche Patienteninfo wird benötigt aus EPIC?\n"
        "- Wer ist der PI der Studie?\n"
        "- Welche Assessments werden erhoben?\n"
        "- How many tablets are available?\n"
        "- What inclusion criteria apply?"
    )

# --- Query Input ---
query = st.text_input(" ", placeholder="Frage eingeben…")

# --- Handle Query ---
if query:
    qa_chain = load_or_build_qa_chain()
    result = qa_chain({"query": query})
    st.session_state.chat_history.append({
        "timestamp": datetime.now().strftime("%H:%M"),
        "question": query,
        "answer": result["result"],
        "sources": result.get("source_documents", []),
        "feedback": None
    })

# --- Display Chat History ---
for i, entry in enumerate(reversed(st.session_state.chat_history)):
    ts = entry.get("timestamp", "--:--")

    st.markdown(
        f"""
        <div style='display: flex; align-items: flex-start; margin-bottom: 1rem;'>
            <div style='font-size: 1.5rem; margin-right: 0.5rem;'>🧑‍⚕️</div>
            <div style='background-color: #ecf0f1; padding: 0.6rem 1rem; border-radius: 0.5rem; max-width: 80%;'>
                <b>Du ({ts}):</b><br>{entry["question"]}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div style='display: flex; align-items: flex-start; margin-bottom: 1rem;'>
            <div style='font-size: 1.5rem; margin-right: 0.5rem;'>🤖</div>
            <div style='background-color: #d6eaf8; padding: 0.6rem 1rem; border-radius: 0.5rem; max-width: 80%;'>
                <b>RAG-Bot:</b><br>{entry["answer"]}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    if entry["sources"]:
        with st.expander("📚 Quellen anzeigen"):
            for doc in entry["sources"]:
                metadata = doc.metadata
                source = metadata.get("source", "Unbekannt")
                page = metadata.get("page", "?") + 1
                filename = os.path.basename(source).replace(".pdf", "").replace("-", " ").title()
                st.markdown(f"📄 **{filename}**, Seite {page}")

    # --- Feedback Buttons ---
    if entry["feedback"] is None:
        st.markdown("#### War die Antwort hilfreich?")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("👍 Ja", key=f"yes_{i}"):
                st.session_state.chat_history[-(i + 1)]["feedback"] = "👍"
                log_to_sheets(entry["question"], entry["answer"], "👍")
                st.success("Danke für dein Feedback!")
        with col2:
            if st.button("👎 Nein", key=f"no_{i}"):
                st.session_state.chat_history[-(i + 1)]["feedback"] = "👎"
                log_to_sheets(entry["question"], entry["answer"], "👎")
                st.warning("Wir arbeiten daran, es zu verbessern.")


