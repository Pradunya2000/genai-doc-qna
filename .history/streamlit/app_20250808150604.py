import streamlit as st
import os
import requests
import json

# --- CONFIGURATION ---
# The URL where your FastAPI application is running.
API_URL = "http://localhost:8000"

# --- HELPER FUNCTIONS ---
@st.cache_data
def get_uploaded_files():
    """Fetches the list of uploaded files and their metadata from the API."""
    try:
        response = requests.get(f"{API_URL}/files/")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to fetch file history: {e}")
        return []

def upload_files(uploaded_files):
    """Sends uploaded files to the backend for processing."""
    files_to_upload = [("files", (file.name, file.getvalue(), file.type)) for file in uploaded_files]
    try:
        with st.spinner("Uploading and processing documents..."):
            response = requests.post(f"{API_URL}/upload/", files=files_to_upload)
            response.raise_for_status()
            st.success(response.json().get("message", "Files uploaded successfully!"))
            st.session_state.files_uploaded = True
    except requests.exceptions.RequestException as e:
        st.error(f"Error uploading files: {e}")

def ask_question(question, selected_file):
    """Sends a question to the backend and returns the answer."""
    payload = {"questions": [question]}
    params = {"source_file": selected_file} if selected_file else {}
    
    try:
        with st.spinner("Getting answer..."):
            response = requests.post(
                f"{API_URL}/ask/",
                json=payload,
                params=params,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            answers = response.json()["responses"]
            if answers:
                return answers[0]["answer"]
            return "No answer found."
    except requests.exceptions.RequestException as e:
        st.error(f"Error asking question: {e}")
        return "An error occurred while fetching the answer."

def clear_data():
    """Clears all uploaded files and vector store data from the backend."""
    try:
        if st.button("Clear All Data", type="secondary"):
            with st.spinner("Clearing all files and embeddings..."):
                response = requests.delete(f"{API_URL}/clear/")
                response.raise_for_status()
                st.success(response.json().get("message", "Data cleared successfully!"))
                st.session_state.files_uploaded = False
                st.session_state.conversation_history = []
                st.cache_data.clear()
                st.experimental_rerun()
    except requests.exceptions.RequestException as e:
        st.error(f"Error clearing data: {e}")

# --- STREAMLIT UI LAYOUT ---

st.set_page_config(page_title="Gen AI Document Q&A", page_icon="📚")
st.title("📚 Gen AI Document Q&A")
st.markdown("Upload your documents and ask questions about them. You can ask questions about all documents or filter by a specific file.")

if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []
if "files_uploaded" not in st.session_state:
    st.session_state.files_uploaded = False

# --- Sidebar for File Management ---
with st.sidebar:
    st.header("File Management")
    uploaded_files = st.file_uploader(
        "**1. Upload Documents**",
        type=["pdf", "txt", "docx"],
        accept_multiple_files=True,
        help="You can upload multiple files at once."
    )
    if uploaded_files:
        if st.button("Process Files", type="primary"):
            upload_files(uploaded_files)

    st.markdown("---")
    st.header("Uploaded File History")
    file_history = get_uploaded_files()
    if file_history:
        st.write("Files in Vector Store:")
        st.json(file_history)
    else:
        st.info("No files have been uploaded yet.")
    
    if st.session_state.files_uploaded or file_history:
        clear_data()

# --- Main Area for Q&A ---
# Display conversation history
for chat in st.session_state.conversation_history:
    with st.chat_message(chat["role"]):
        st.markdown(chat["content"])

# User input and Q&A logic
if file_history:
    st.markdown("---")
    st.header("Ask a Question")
    
    # 2. Optional Source File Selection
    file_options = ["All Documents"] + [file['file'] for file in file_history]
    selected_file = st.selectbox(
        "**2. Select a source file (optional)**",
        options=file_options,
        help="To restrict the Q&A to a specific document, select it from the dropdown. Otherwise, questions will be answered from all uploaded documents."
    )
    
    # User chat input
    user_question = st.chat_input("Ask a question about your documents...")
    if user_question:
        # Save user message to history
        st.session_state.conversation_history.append({"role": "user", "content": user_question})
        with st.chat_message("user"):
            st.markdown(user_question)

        # Get answer from backend
        source = selected_file if selected_file != "All Documents" else None
        answer = ask_question(user_question, source)
        
        # Save bot response to history
        st.session_state.conversation_history.append({"role": "assistant", "content": answer})
        with st.chat_message("assistant"):
            st.markdown(answer)

else:
    st.warning("Please upload documents in the sidebar to start asking questions.")