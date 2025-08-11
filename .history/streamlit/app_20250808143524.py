import streamlit as st
import requests

API_BASE_URL = "http://localhost:8000"  # Change to your FastAPI backend URL

st.set_page_config(page_title="Advanced GenAI Docs Q&A", layout="wide")

def upload_files_tab():
    st.header("Upload Files")

    if "file_slots" not in st.session_state:
        st.session_state.file_slots = [None]

    def add_file_slot():
        st.session_state.file_slots.append(None)

    # Show file uploaders dynamically
    for i in range(len(st.session_state.file_slots)):
        st.session_state.file_slots[i] = st.file_uploader(
            f"Upload file #{i+1}", key=f"file_uploader_{i}", type=["pdf", "txt", "docx", "doc"]
        )

    st.button("Add File", on_click=add_file_slot)

    if st.button("Upload and Process"):
        files_to_upload = [f for f in st.session_state.file_slots if f is not None]
        if not files_to_upload:
            st.warning("Please upload at least one file before submitting.")
            return

        # Prepare multipart/form-data files payload
        files_payload = [("files", (file.name, file, file.type)) for file in files_to_upload]

        with st.spinner("Uploading files and processing..."):
            response = requests.post(f"{API_BASE_URL}/upload/", files=files_payload)
        
        if response.status_code == 200:
            st.success("Files uploaded and processed successfully!")
            # Reset file slots after upload
            st.session_state.file_slots = [None]
        else:
            st.error(f"Upload failed: {response.text}")

def qa_tab():
    st.header("Ask Questions")

    # Fetch uploaded files from backend for selection
    response = requests.get(f"{API_BASE_URL}/files/")
    files_data = []
    if response.status_code == 200:
        files_data = response.json()
    else:
        st.error("Failed to fetch uploaded files list from backend.")
        return

    file_options = ["All Files"] + [f["file"] for f in files_data]

    source_file = st.selectbox("Select Source File (for Q&A)", options=file_options)

    if "questions" not in st.session_state:
        st.session_state.questions = [""]

    def add_question():
        st.session_state.questions.append("")

    # Dynamic question input boxes
    for i in range(len(st.session_state.questions)):
        st.session_state.questions[i] = st.text_input(f"Question #{i+1}", value=st.session_state.questions[i], key=f"question_{i}")

    st.button("Add More Question", on_click=add_question)

    if st.button("Get Answers"):
        # Prepare payload
        filtered_source = None if source_file == "All Files" else source_file
        questions_filtered = [q.strip() for q in st.session_state.questions if q.strip()]

        if not questions_filtered:
            st.warning("Please enter at least one question.")
            return

        payload = {"questions": questions_filtered}

        with st.spinner("Getting answers..."):
            params = {}
            if filtered_source:
                params["source_file"] = filtered_source

            response = requests.post(f"{API_BASE_URL}/ask/", json=payload, params=params)
        
        if response.status_code == 200:
            results = response.json().get("responses", [])
            for res in results:
                st.markdown(f"**Q:** {res['question']}")
                st.markdown(f"**A:** {res['answer']}")
                st.markdown("---")
        else:
            st.error(f"Failed to get answers: {response.text}")

def uploaded_files_tab():
    st.header("Uploaded Files History")

    response = requests.get(f"{API_BASE_URL}/files/")
    if response.status_code == 200:
        files_data = response.json()
        if not files_data:
            st.info("No files uploaded yet.")
        else:
            for file in files_data:
                st.write(f"**File:** {file['file']} | **Uploaded on:** {file['upload_date']}")
    else:
        st.error("Failed to fetch uploaded files from backend.")

    if st.button("Clear All Files and Embeddings"):
        confirm = st.confirm("Are you sure you want to clear all uploaded files and embeddings? This action cannot be undone.")
        if confirm:
            resp = requests.delete(f"{API_BASE_URL}/clear/")
            if resp.status_code == 200:
                st.success("All files and embeddings cleared successfully.")
            else:
                st.error(f"Failed to clear files: {resp.text}")

def main():
    st.title("Advanced GenAI Documents Q&A")

    tab = st.tabs(["Upload Files", "Q&A", "Uploaded Files History"])

    with tab[0]:
        upload_files_tab()

    with tab[1]:
        qa_tab()

    with tab[2]:
        uploaded_files_tab()

if __name__ == "__main__":
    main()
