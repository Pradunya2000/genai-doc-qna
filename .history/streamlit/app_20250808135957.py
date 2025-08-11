"""
Streamlit Frontend for Private PDF/DOCX/TXT Q&A Application
-----------------------------------------------------------
This application provides three main functionalities:
1. Uploading PDF, DOCX, and TXT files to a backend (FastAPI) for ingestion.
2. Asking questions based on the uploaded documents, with optional file filtering.
3. Viewing and managing uploaded files.
"""

import streamlit as st
import requests

# -------------------------------
# 🔧 Configuration
# -------------------------------
API_BASE_URL = "http://localhost:8000"  # Change this if backend is deployed elsewhere

# -------------------------------
# 🎨 Page Setup
# -------------------------------
st.set_page_config(page_title="📚 Private PDF Q&A", layout="wide")
st.title("📚 Private PDF Q&A")
st.markdown("Upload PDF/DOCX/TXT files and ask questions based on their content.")

# -------------------------------
# 📑 Tabs for Navigation
# -------------------------------
tabs = st.tabs([
    "📤 Upload Files",
    "❓ Ask a Question",
    "🗂 View Uploaded Files"
])

with tabs[0]:
    st.header("📄 Upload Documents One by One")

    # Initialize state
    if "file_slots" not in st.session_state:
        st.session_state.file_slots = [0]  # slot IDs
    if "uploaded_files" not in st.session_state:
        st.session_state.uploaded_files = {}

    def add_file_slot():
        st.session_state.file_slots.append(max(st.session_state.file_slots) + 1)
        st.rerun()

    st.subheader("📂 Select Files to Upload")

    # Render file slots
    for slot_id in list(st.session_state.file_slots):
        col1, _ = st.columns([5, 1])  # no second column for remove button
        file = col1.file_uploader(
            f"Select File #{slot_id+1}",
            type=["pdf", "txt", "docx"],
            key=f"uploader_{slot_id}"
        )
        if file:
            st.session_state.uploaded_files[slot_id] = file

    # Add file slot
    if st.button("➕ Add Another File"):
        add_file_slot()

    selected_files = list(st.session_state.uploaded_files.values())

    if selected_files:
        st.markdown("### ✅ Files Ready to Upload:")
        for f in selected_files:
            st.write(f"📄 {f.name}")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("🚀 Upload Files"):
                files = [("files", (f.name, f, f.type)) for f in selected_files]
                with st.spinner("Uploading and processing files..."):
                    try:
                        response = requests.post(f"{API_BASE_URL}/upload/", files=files)
                        if response.status_code == 200:
                            st.success("✅ Files uploaded successfully!")
                            # No clear_all_files() here as function removed
                        else:
                            st.error("❌ Upload failed.")
                    except Exception as e:
                        st.error(f"🚫 Error: {e}")
        with col2:
            pass  # Removed Clear Files button, keep layout empty
    else:
        st.info("📭 No files selected yet.")

# =========================================================
# ❓ TAB 2: Ask Questions
# =========================================================
with tabs[1]:
    st.header("❓ Ask Questions")

    # -------------------------------
    # 📂 Optional File Filter
    # -------------------------------
    with st.expander("🗂 Optional: Select a specific document to query"):
        try:
            file_list_res = requests.get(f"{API_BASE_URL}/files/")
            file_options = [f["file"] for f in file_list_res.json()] if file_list_res.status_code == 200 else []
        except Exception:
            file_options = []

        if file_options:
            selected_file = st.selectbox("Filter by file", options=["All"] + file_options)
        else:
            selected_file = "All"

        file_param = None if selected_file == "All" else selected_file

    st.markdown("### 📝 Your Questions")

    # Initialize question boxes
    if "question_boxes" not in st.session_state:
        st.session_state.question_boxes = [""]

    # Function to add more question boxes
    def add_question_box():
        st.session_state.question_boxes.append("")

    st.button("➕ Add Question", on_click=add_question_box)

    # Collect questions
    updated_questions = []
    for i, q in enumerate(st.session_state.question_boxes):
        question = st.text_input(f"Question {i+1}", value=q, key=f"question_{i}")
        updated_questions.append(question)

    st.session_state.question_boxes = updated_questions

    # Submit all questions
    if st.button("🎯 Ask All"):
        questions = [q.strip() for q in st.session_state.question_boxes if q.strip()]
        if not questions:
            st.warning("⚠️ Please enter at least one question.")
        else:
            with st.spinner("Getting answers..."):
                res = requests.post(
                    f"{API_BASE_URL}/ask/",
                    json={"questions": questions},
                    params={"source_file": file_param} if file_param else None
                )

            if res.status_code == 200:
                for item in res.json()["responses"]:
                    with st.expander(f"❓ {item['question']}"):
                        st.markdown(f"**🤖 Answer:** {item['answer']}")
            else:
                st.error("❌ Failed to get answers.")

# =========================================================
# 🗂 TAB 3: View Uploaded Files
# =========================================================
with tabs[2]:
    st.header("📁 Uploaded Documents")

    col1, col2 = st.columns([3, 1])

    # Display uploaded files
    with col1:
        try:
            res = requests.get(f"{API_BASE_URL}/files/")
            if res.status_code == 200:
                files = res.json()
                if not files:
                    st.info("📭 No documents uploaded yet.")
                else:
                    for file in files:
                        st.markdown(f"🔹 **{file['file']}** — _Uploaded on {file['upload_date']}_")
            else:
                st.error("❌ Failed to fetch uploaded files.")
        except Exception:
            st.error("🚫 Could not connect to the backend.")

# Clear all files button
    with col2:
        if st.button("🧹 Clear All Files"):
            try:
                clear_res = requests.delete(f"{API_BASE_URL}/clear/")
                if clear_res.status_code == 200:
                    st.success("🧼 All uploaded files and embeddings cleared!")
                    st.rerun()  # 👈 Force UI refresh so the list updates immediately
                else:
                    st.error("❌ Failed to clear files.")
            except Exception as e:
                st.error(f"🚫 Error: {e}")
