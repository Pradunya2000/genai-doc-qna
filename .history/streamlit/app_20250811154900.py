# streamlit_app.py
import streamlit as st
import os
import shutil
from typing import List
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# ✅ Import backend logic directly
from document_loader import load_documents_from_folder, split_documents
from embedding_store import store_embeddings, get_vectorstore
from qa_chain import get_qa_chain
from retriever import get_all_metadata

UPLOAD_FOLDER = "docs"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# -----------------
# Backend-equivalent functions
# -----------------

def process_uploaded_files(uploaded_files):
    """Process and store embeddings for uploaded files."""
    if not uploaded_files:
        st.warning("Please select files to upload.")
        return

    for file in uploaded_files:
        file_path = os.path.join(UPLOAD_FOLDER, file.name)
        with open(file_path, "wb") as buffer:
            buffer.write(file.getbuffer())

    # Ingest docs
    docs = load_documents_from_folder(UPLOAD_FOLDER)
    chunks = split_documents(docs)
    store_embeddings(chunks)
    st.success("✅ Files uploaded and processed successfully!")

def answer_questions(questions: List[str], source_file: str = None):
    """Ask one or more questions using QA chain."""
    chain = get_qa_chain(source_file)
    responses = []
    for q in questions:
        result = chain({"query": q})
        responses.append({"question": q, "answer": result["result"]})
    return responses

def clear_all_data():
    """Delete docs and clear embeddings."""
    for filename in os.listdir(UPLOAD_FOLDER):
        os.remove(os.path.join(UPLOAD_FOLDER, filename))
    db = get_vectorstore()
    db.delete_collection()
    st.success("🗑️ All files and embeddings cleared successfully.")

# -----------------
# Streamlit UI
# -----------------

st.set_page_config(page_title="Gen AI Document Q&A", page_icon="📚", layout="wide")
st.title("📚 Advanced Gen AI Document Q&A")
st.markdown("---")

tab1, tab2, tab3 = st.tabs(["**📂 File Uploader**", "**💬 Q&A Session**", "**📜 File History**"])

# --- TAB 1: FILE UPLOADER ---
with tab1:
    st.header("Upload Documents to the Knowledge Base")
    if "num_files" not in st.session_state:
        st.session_state.num_files = 1

    all_uploaded_files = []
    for i in range(st.session_state.num_files):
        uploaded_file = st.file_uploader(
            f"File {i+1}",
            type=["pdf", "txt", "docx"],
            accept_multiple_files=False,
            key=f"file_uploader_{i}"
        )
        if uploaded_file:
            all_uploaded_files.append(uploaded_file)

    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("➕ Add Another File", type="secondary"):
            st.session_state.num_files += 1
            st.rerun()

    if st.button("📤 Process All Files", type="primary"):
        process_uploaded_files(all_uploaded_files)

# --- TAB 2: Q&A SESSION ---
with tab2:
    st.header("Ask Questions about Your Documents")

    file_history = get_all_metadata()
    if not file_history:
        st.warning("⚠️ No files uploaded yet.")
    else:
        file_options = ["All Documents"] + [f['file'] for f in file_history]
        selected_file = st.selectbox("🔍 Select Source File:", file_options)
        source_file = None if selected_file == "All Documents" else selected_file

        if "questions" not in st.session_state:
            st.session_state.questions = [""]

        for i in range(len(st.session_state.questions)):
            st.session_state.questions[i] = st.text_area(
                f"Question {i+1}",
                value=st.session_state.questions[i],
                height=35,
                key=f"question_input_{i}"
            )

        if st.button("➕ Add More Question", type="secondary"):
            st.session_state.questions.append("")
            st.rerun()

        if st.button("🚀 Get Answers", type="primary"):
            questions_to_ask = [q for q in st.session_state.questions if q.strip()]
            responses = answer_questions(questions_to_ask, source_file)
            for res in responses:
                with st.expander(f"**Q:** {res['question']}", expanded=True):
                    st.success(f"**A:** {res['answer']}")

# --- TAB 3: FILE HISTORY ---
with tab3:
    st.header("Uploaded Documents History")
    file_history = get_all_metadata()
    if file_history:
        st.dataframe(file_history, use_container_width=True)
        st.subheader("🧹 Clear All Data")
        st.warning("⚠️ **Warning:** Clicking this button will permanently delete all uploaded files and their embeddings from the system.")
        if st.button("🗑️ Clear All Data", type="secondary"):
            clear_all_data()
    else:
        st.info("No files uploaded yet.")
