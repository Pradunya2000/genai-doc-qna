import streamlit as st
import requests
import time
import json
import os

# --- Configuration ---
# Set this to the URL where your FastAPI backend is running
# If running locally, this is usually http://127.0.0.1:8000
API_URL = "http://127.0.0.1:8000"

# Set up the Streamlit page configuration
st.set_page_config(
    page_title="GEN AI Documents Q&A",
    page_icon="📚",
    layout="wide",
)

# --- Session State and Initial Setup ---
# Initialize session state variables if they don't exist
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "uploaded_files_meta" not in st.session_state:
    st.session_state.uploaded_files_meta = []
if "selected_source" not in st.session_state:
    st.session_state.selected_source = "All Uploaded Files"

# Function to fetch the list of uploaded files from the API
def fetch_uploaded_files():
    try:
        response = requests.get(f"{API_URL}/files/")
        response.raise_for_status() # Raise an exception for bad status codes
        st.session_state.uploaded_files_meta = response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to connect to the backend API: {e}. Is the server running?")
        st.session_state.uploaded_files_meta = []

# --- Sidebar for File Management ---
with st.sidebar:
    st.header("File Management 📁")

    st.markdown("---")
    
    # Multiuploader for files
    uploaded_files = st.file_uploader(
        "Upload your documents (multiple formats allowed)",
        accept_multiple_files=True,
        type=['pdf', 'docx', 'txt', 'md']
    )

    if uploaded_files:
        files = [('files', (file.name, file.getvalue(), file.type)) for file in uploaded_files]
        with st.spinner("Uploading and processing documents..."):
            try:
                response = requests.post(f"{API_URL}/upload/", files=files)
                response.raise_for_status()
                st.success(response.json()["message"])
                # Refresh the file history after a successful upload
                fetch_uploaded_files()
            except requests.exceptions.RequestException as e:
                st.error(f"Error uploading files: {e}")
            
    st.subheader("Uploaded Documents History")
    
    # Fetch and display the file history
    if not st.session_state.uploaded_files_meta:
        fetch_uploaded_files()

    if st.session_state.uploaded_files_meta:
        file_names = ["All Uploaded Files"] + [f["file"] for f in st.session_state.uploaded_files_meta]
        
        # Source file selector
        st.session_state.selected_source = st.selectbox(
            "Select a file for Q&A (optional)",
            options=file_names,
            key="source_selector"
        )
        
        # Display the list of files
        for file_meta in st.session_state.uploaded_files_meta:
            st.write(f"- **{file_meta['file']}** (Uploaded: {file_meta['upload_date']})")
        
        st.markdown("---")
        
        # Clear all files button
        if st.button("Clear All History", type="secondary"):
            with st.spinner("Clearing files and embeddings..."):
                try:
                    response = requests.delete(f"{API_URL}/clear/")
                    response.raise_for_status()
                    st.success(response.json()["message"])
                    st.session_state.uploaded_files_meta = []
                    st.session_state.chat_history = []
                    st.session_state.selected_source = "All Uploaded Files"
                    st.rerun() # Rerun to clear the interface
                except requests.exceptions.RequestException as e:
                    st.error(f"Error clearing files: {e}")
    else:
        st.info("No files uploaded yet.")

# --- Main App Content ---
st.title("GEN AI Documents Q&A")
st.markdown(
    """
    **Upload your documents on the left to get started!**
    
    You can ask questions about the documents and even limit the Q&A to a specific file using the source file selector.
    """
)

# --- Function to handle Q&A via the API ---
def query_documents(query: str, source_file: str):
    """Sends a query to the backend API and returns the AI's response."""
    
    payload = {"questions": [query]}
    
    params = {}
    if source_file != "All Uploaded Files":
        params["source_file"] = source_file

    with st.spinner("Thinking..."):
        try:
            response = requests.post(
                f"{API_URL}/ask/",
                json=payload,
                params=params
            )
            response.raise_for_status()
            return response.json()["responses"][0]["answer"]
        except requests.exceptions.RequestException as e:
            st.error(f"Error querying documents: {e}")
            return "An error occurred while fetching the answer."

# --- Chat Interface ---
# Display chat messages from history on app rerun
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Ask a question about your documents..."):
    # Add user message to chat history
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        # Call the Q&A function with the current state
        response = query_documents(
            query=prompt,
            source_file=st.session_state.selected_source
        )
        st.markdown(response)
    
    # Add assistant response to chat history
    st.session_state.chat_history.append({"role": "assistant", "content": response})

