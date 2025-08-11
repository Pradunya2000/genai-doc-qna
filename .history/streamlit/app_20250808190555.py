import streamlit as st
import os
import requests
import json

# --- CONFIGURATION ---
# Ensure your FastAPI application is running on this address.
API_URL = "http://localhost:8000"

# --- HELPER FUNCTIONS ---
# Functions to interact with your FastAPI backend
@st.cache_data(show_spinner=False)
def get_uploaded_files():
    """Fetches the list of uploaded files and their metadata from the API."""
    try:
        response = requests.get(f"{API_URL}/files/")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to fetch file history from backend: {e}")
        return []

def upload_files(uploaded_files):
    """Sends uploaded files to the backend for processing."""
    if not uploaded_files:
        st.warning("Please select files to upload.")
        return

    files_to_upload = [("files", (file.name, file.getvalue(), file.type)) for file in uploaded_files]
    try:
        with st.spinner("🚀 Uploading and processing documents..."):
            response = requests.post(f"{API_URL}/upload/", files=files_to_upload)
            response.raise_for_status()
            st.success(response.json().get("message", "✅ Files uploaded successfully!"))
            st.cache_data.clear()  # Clear cache to refresh file history
            st.rerun()
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Error uploading files: {e}")

def ask_questions(questions, selected_file):
    """Sends multiple questions to the backend and displays the answers."""
    if not questions:
        st.warning("Please enter at least one question.")
        return

    payload = {"questions": questions}
    params = {"source_file": selected_file} if selected_file else {}
    
    try:
        with st.spinner("🤔 Getting answers..."):
            response = requests.post(
                f"{API_URL}/ask/",
                json=payload,
                params=params,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            return response.json()["responses"]
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Error asking questions: {e}")
        return None

def clear_all_data():
    """Clears all uploaded files and vector store data from the backend."""
    try:
        with st.spinner("🗑️ Clearing all files and embeddings..."):
            response = requests.delete(f"{API_URL}/clear/")
            response.raise_for_status()
            st.success(response.json().get("message", "✅ All files and embeddings cleared!"))
            st.session_state.questions = [""]  # Reset Q&A input fields
            st.cache_data.clear() # Clear cache
            st.rerun()
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Error clearing data: {e}")

# --- STREAMLIT UI LAYOUT ---

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
    
    # List to hold the uploaded file objects
    all_uploaded_files = []
    
    # Create dynamic file upload slots
    for i in range(st.session_state.num_files):
        uploaded_file = st.file_uploader(
            f"File {i+1}", 
            type=["pdf", "txt", "docx"],
            accept_multiple_files=False,
            key=f"file_uploader_{i}"
        )
        if uploaded_file:
            all_uploaded_files.append(uploaded_file)
            
    # Buttons for dynamic slots and processing
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("➕ Add Another File", type="secondary"):
            st.session_state.num_files += 1
            st.rerun()
    with col2:
        st.markdown("*Click to add a new slot for another file.*")

    st.markdown("---")
    
    if st.button("📤 Process All Files", type="primary"):
        upload_files(all_uploaded_files)

# --- TAB 2: Q&A SESSION ---
with tab2:
    st.header("Ask Questions about Your Documents")
    
    file_history = get_uploaded_files()
    if not file_history:
        st.warning("⚠️ No files uploaded yet. Please upload documents in the 'File Uploader' tab to begin.")
    else:
        st.info("Choose a source file to narrow down your query, or select 'All Documents' to search across your entire library.")
        
        # Source file selection with a more descriptive label
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

        # Dynamic question input windows
        for i in range(len(st.session_state.questions)):
            st.session_state.questions[i] = st.text_area(
                f"Question {i+1}", 
                value=st.session_state.questions[i], 
                height=10, 
                key=f"question_input_{i}"
            )
        
        if st.button("➕ Add More Question", type="secondary"):
            st.session_state.questions.append("")
            st.rerun()

        st.markdown("---")

        # Submit button and displaying answers
        if st.button("🚀 Get Answers", type="primary"):
            questions_to_ask = [q for q in st.session_state.questions if q.strip()]
            
            source = selected_file if selected_file != "All Documents" else None
            responses = ask_questions(questions_to_ask, source)

            if responses:
                st.subheader("📌 Answers:")
                for res in responses:
                    with st.expander(f"**Q:** {res['question']}", expanded=True):
                        st.success(f"**A:** {res['answer']}")

# --- TAB 3: FILE HISTORY ---
with tab3:
    st.header("Uploaded Documents History")
    
    file_history = get_uploaded_files()
    if file_history:
        st.info("Here is a list of all documents currently in the knowledge base, along with their upload dates.")
        st.dataframe(file_history, use_container_width=True)
        st.markdown("---")
        
        st.subheader("🧹 Clear All Data")
        st.warning("⚠️ **Warning:** Clicking this button will permanently delete all uploaded files and their embeddings from the system.")
        if st.button("🗑️ Clear All Data", type="secondary"):
            clear_all_data()
    else:
        st.info("No files have been uploaded yet.")