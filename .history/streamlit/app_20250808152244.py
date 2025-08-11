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
        with st.spinner("Uploading and processing documents..."):
            response = requests.post(f"{API_URL}/upload/", files=files_to_upload)
            response.raise_for_status()
            st.success(response.json().get("message", "Files uploaded successfully!"))
            st.cache_data.clear()  # Clear cache to refresh file history
            st.rerun()  # Corrected function call
    except requests.exceptions.RequestException as e:
        st.error(f"Error uploading files: {e}")

def ask_questions(questions, selected_file):
    """Sends multiple questions to the backend and displays the answers."""
    if not questions:
        st.warning("Please enter at least one question.")
        return

    payload = {"questions": questions}
    params = {"source_file": selected_file} if selected_file else {}
    
    try:
        with st.spinner("Getting answers..."):
            response = requests.post(
                f"{API_URL}/ask/",
                json=payload,
                params=params,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            return response.json()["responses"]
    except requests.exceptions.RequestException as e:
        st.error(f"Error asking questions: {e}")
        return None

def clear_all_data():
    """Clears all uploaded files and vector store data from the backend."""
    try:
        with st.spinner("Clearing all files and embeddings..."):
            response = requests.delete(f"{API_URL}/clear/")
            response.raise_for_status()
            st.success(response.json().get("message", "Data cleared successfully!"))
            st.session_state.questions = [""]  # Reset Q&A input fields
            st.cache_data.clear() # Clear cache
            st.rerun() # Corrected function call
    except requests.exceptions.RequestException as e:
        st.error(f"Error clearing data: {e}")

# --- STREAMLIT UI LAYOUT ---

st.set_page_config(page_title="Gen AI Document Q&A", page_icon="📚", layout="wide")
st.title("📚 Gen AI Document Q&A")
st.markdown("---")

tab1, tab2, tab3 = st.tabs(["**Upload File**", "**Q&A**", "**File History**"])

# --- TAB 1: UPLOAD FILE ---
with tab1:
    st.header("Upload New Documents")
    st.markdown("Use the button below to add file upload slots one at a time.")
    
    if "num_files" not in st.session_state:
        st.session_state.num_files = 1
    
    # List to hold the uploaded file objects
    all_uploaded_files = []
    
    # Create dynamic file upload slots
    for i in range(st.session_state.num_files):
        uploaded_file = st.file_uploader(
            f"File {i+1}", 
            type=["pdf", "txt", "docx"],
            accept_multiple_files=False, # Now only accepts one file per slot
            key=f"file_uploader_{i}"
        )
        if uploaded_file:
            all_uploaded_files.append(uploaded_file)
            
    # Button to add another file slot
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("Add Another File", type="secondary"):
            st.session_state.num_files += 1
            st.rerun()
    with col2:
        st.markdown("*Click to add a new slot for another file.*")

    st.markdown("---")
    
    # Button to process all files
    if st.button("Process All Files", type="primary"):
        upload_files(all_uploaded_files)

# --- TAB 2: Q&A ---
with tab2:
    st.header("Ask Questions")
    
    # Check if files are uploaded before showing Q&A interface
    file_history = get_uploaded_files()
    if not file_history:
        st.warning("Please upload documents in the 'Upload File' tab to start asking questions.")
    else:
        # Source file selection
        file_options = ["All Documents"] + [file['file'] for file in file_history]
        selected_file = st.selectbox(
            "**Select a source file (optional):**",
            options=file_options,
            help="Choose a specific file to restrict the Q&A to that document. If 'All Documents' is selected, the answer will be based on all uploaded files."
        )

        st.markdown("---")
        st.markdown("**Enter your questions below:**")
        
        if "questions" not in st.session_state:
            st.session_state.questions = [""]

        # Dynamic question input windows
        for i in range(len(st.session_state.questions)):
            st.session_state.questions[i] = st.text_area(
                f"Question {i+1}", 
                value=st.session_state.questions[i], 
                height=50, 
                key=f"question_input_{i}"
            )
        
        # Add more question button
        if st.button("Add More Question", type="secondary"):
            st.session_state.questions.append("")
            st.rerun() # Corrected function call

        st.markdown("---")

        # Submit button and displaying answers
        if st.button("Get Answers", type="primary"):
            # Filter out empty questions
            questions_to_ask = [q for q in st.session_state.questions if q.strip()]
            
            source = selected_file if selected_file != "All Documents" else None
            responses = ask_questions(questions_to_ask, source)

            if responses:
                st.subheader("Answers:")
                for res in responses:
                    st.success(f"**Q:** {res['question']}")
                    st.info(f"**A:** {res['answer']}")

# --- TAB 3: FILE HISTORY ---
with tab3:
    st.header("Uploaded File History")
    
    file_history = get_uploaded_files()
    if file_history:
        st.info("Below is the list of documents currently stored in the knowledge base.")
        st.dataframe(file_history, use_container_width=True)
        st.markdown("---")
        
        if st.button("Clear All Data", type="secondary", help="This will permanently delete all uploaded files and their embeddings."):
            clear_all_data()
    else:
        st.info("No files have been uploaded yet.")