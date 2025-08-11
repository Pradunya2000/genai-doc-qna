# streamlit/app.py

import streamlit as st
import os
import shutil
from typing import List

# === Backend-equivalent functions ===

UPLOAD_FOLDER = "docs"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

from document_loader import load_documents_from_folder, split_documents
from embedding_store import store_embeddings, get_vectorstore
from qa_chain import get_qa_chain
from retriever import get_all_metadata

def process_uploaded_files(uploaded_files):
    if not uploaded_files:
        st.warning("Please select files to upload.")
        return

    for file in uploaded_files:
        file_path = os.path.join(UPLOAD_FOLDER, file.name)
        with open(file_path, "wb") as buffer:
            buffer.write(file.getbuffer())

    docs = load_documents_from_folder(UPLOAD_FOLDER)
    chunks = split_documents(docs)
    store_embeddings(chunks)
    st.success("✅ Files uploaded and processed successfully!")

def direct_get_uploaded_files():
    return get_all_metadata()

def answer_questions(questions: List[str], selected_file: str):
    source_file = None if selected_file == "All Documents" else selected_file
    chain = get_qa_chain(source_file)
    responses = []
    for q in questions:
        result = chain({"query": q})
        responses.append({"question": q, "answer": result["result"]})
    return responses

def clear_all_data():
    for filename in os.listdir(UPLOAD_FOLDER):
        os.remove(os.path.join(UPLOAD_FOLDER, filename))
    db = get_vectorstore()
    db.delete_collection()
    st.success("✅ All files and embeddings cleared successfully.")

# === Original Streamlit UI code, unchanged ===

st.set_page_config(page_title="Gen AI Document Q&A", page_icon="📚", layout="wide")
st.title("📚 Advanced Gen AI Document Q&A")
st.markdown("---")

tab1, tab2, tab3 = st.tabs(["**📂 File Uploader**", "**💬 Q&A Session**", "**📜 File History**"])

# --- TAB 1: FILE UPLOADER ---
with tab1:
    st.header("Upload Documents to the Knowledge Base")
    st.info("💡 Add one or more files to ingest them into the system. The processed files will be used for answering your questions.")
    
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
    with col2:
        st.markdown("*Click to add a new slot for another file.*")

    st.markdown("---")
    
    if st.button("📤 Process All Files", type="primary"):
        process_uploaded_files(all_uploaded_files)  # <-- replaced API call with direct function

# --- TAB 2: Q&A SESSION ---
with tab2:
    st.header("Ask Questions about Your Documents")
    
    file_history = direct_get_uploaded_files()  # <-- replaced API call with direct function
    if not file_history:
        st.warning("⚠️ No files uploaded yet. Please upload documents in the 'File Uploader' tab to begin.")
    else:
        st.info("Choose a source file to narrow down your query, or select 'All Documents' to search across your entire library.")
        
        file_options = ["All Documents"] + [file['file'] for file in file_history]
        selected_file = st.selectbox(
            "**🔍 Select Source File:**",
            options=file_options,
            help="This feature allows you to perform Q&A on a single, specific document."
        )

        st.markdown("---")
        st.subheader("📝 Enter Your Questions")
        
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

        st.markdown("---")

        if st.button("🚀 Get Answers", type="primary"):
            questions_to_ask = [q for q in st.session_state.questions if q.strip()]
            responses = answer_questions(questions_to_ask, selected_file)  # <-- replaced API call

            if responses:
                st.subheader("📌 Answers:")
                for res in responses:
                    with st.expander(f"**Q:** {res['question']}", expanded=True):
                        st.success(f"**A:** {res['answer']}")

# --- TAB 3: FILE HISTORY ---
with tab3:
    st.header("Uploaded Documents History")
    
    file_history = direct_get_uploaded_files()  # <-- replaced API call
    if file_history:
        st.info("Here is a list of all documents currently in the knowledge base, along with their upload dates.")
        st.dataframe(file_history, use_container_width=True)
        st.markdown("---")
        
        st.subheader("🧹 Clear All Data")
        st.warning("⚠️ **Warning:** Clicking this button will permanently delete all uploaded files and their embeddings from the system.")
        if st.button("🗑️ Clear All Data", type="secondary"):
            clear_all_data()  # <-- replaced API call
    else:
        st.info("No files have been uploaded yet.")
