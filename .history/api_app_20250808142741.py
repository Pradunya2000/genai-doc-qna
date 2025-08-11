import streamlit as st
import requests

API_URL = "http://localhost:8000"  # Change if your FastAPI runs elsewhere

st.set_page_config(page_title="Advanced Document Q&A", layout="wide")

st.title("🗂️ Advanced GenAI Document Q&A")

tab1, tab2, tab3 = st.tabs(["📤 Upload Files", "❓ Q&A", "📁 Uploaded Files"])


def upload_files_ui():
    st.write("### Upload multiple files (PDF, TXT, DOCX/DOC)")

    # Initialize session state for upload slots
    if "upload_slots" not in st.session_state:
        st.session_state.upload_slots = [None]

    # Show upload slots
    uploaded_files = []
    for i in range(len(st.session_state.upload_slots)):
        file = st.file_uploader(f"Select file #{i+1}", key=f"upload_{i}")
        uploaded_files.append(file)

    # Button to add more upload slots
    if st.button("➕ Add another file upload slot"):
        st.session_state.upload_slots.append(None)
        st.experimental_rerun()

    # Upload button
    if st.button("⬆️ Upload files"):
        # Filter out None files
        files_to_upload = [f for f in uploaded_files if f is not None]

        if not files_to_upload:
            st.warning("Please select at least one file to upload.")
            return

        # Prepare files for requests
        files_payload = []
        for f in files_to_upload:
            files_payload.append(("files", (f.name, f.getvalue(), f.type)))

        with st.spinner("Uploading files..."):
            try:
                resp = requests.post(f"{API_URL}/upload/", files=files_payload)
                resp.raise_for_status()
                data = resp.json()
                st.success(data.get("message", "Files uploaded successfully!"))
                st.info(f"Uploaded files: {', '.join(data.get('files', []))}")

                # Reset upload slots after success
                st.session_state.upload_slots = [None]
                st.experimental_rerun()

            except Exception as e:
                st.error(f"Upload failed: {e}")


def qa_ui():
    st.write("### Ask Questions")

    # Fetch uploaded files for dropdown
    try:
        resp = requests.get(f"{API_URL}/files/")
        resp.raise_for_status()
        files_data = resp.json()
        file_names = [f["file"] for f in files_data]
        file_names.insert(0, "All files")  # option for no filtering
    except Exception:
        file_names = ["All files"]

    # Select source file filter
    source_file = st.selectbox("Select source file for Q&A (or All files)", options=file_names)

    # Initialize session state for questions list
    if "questions" not in st.session_state:
        st.session_state.questions = [""]

    # Display question inputs
    for i, q in enumerate(st.session_state.questions):
        st.session_state.questions[i] = st.text_input(f"Question #{i+1}", value=q, key=f"q_{i}")

    # Add more question button
    if st.button("➕ Add another question"):
        st.session_state.questions.append("")
        st.experimental_rerun()

    # Ask button
    if st.button("❓ Ask"):
        questions = [q.strip() for q in st.session_state.questions if q.strip()]
        if not questions:
            st.warning("Please enter at least one question.")
            return

        # Prepare payload
        payload = {"questions": questions}

        # If user selected "All files", pass None to API query param, else the filename
        query_params = {}
        if source_file != "All files":
            query_params["source_file"] = source_file

        with st.spinner("Getting answers..."):
            try:
                resp = requests.post(f"{API_URL}/ask/", json=payload, params=query_params)
                resp.raise_for_status()
                results = resp.json()
                responses = results.get("responses", [])

                for res in responses:
                    st.markdown(f"**Q:** {res['question']}")
                    st.markdown(f"**A:** {res['answer']}")
                    st.write("---")

            except Exception as e:
                st.error(f"Q&A failed: {e}")


def uploaded_files_ui():
    st.write("### Uploaded Files History")

    try:
        resp = requests.get(f"{API_URL}/files/")
        resp.raise_for_status()
        files_data = resp.json()

        if not files_data:
            st.info("No files uploaded yet.")
        else:
            import pandas as pd
            df = pd.DataFrame(files_data)
            df.columns = ["File Name", "Upload Date"]
            st.dataframe(df)

    except Exception as e:
        st.error(f"Failed to load uploaded files: {e}")

    st.write("### Clear All Uploaded Files and Embeddings")

    if st.button("🗑️ Clear All Files and Embeddings"):
        if st.confirm("Are you sure you want to delete all uploaded files and clear embeddings?"):
            try:
                resp = requests.delete(f"{API_URL}/clear/")
                resp.raise_for_status()
                st.success(resp.json().get("message", "Cleared successfully!"))

                # Refresh uploaded files UI
                st.experimental_rerun()
            except Exception as e:
                st.error(f"Clear operation failed: {e}")


with tab1:
    upload_files_ui()

with tab2:
    qa_ui()

with tab3:
    uploaded_files_ui()
