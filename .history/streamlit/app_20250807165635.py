import streamlit as st
import requests

API_BASE_URL = "http://localhost:8000"  # Change if deployed

st.set_page_config(page_title="📚 Private PDF Q&A", layout="wide")
st.title("📚 Private PDF Q&A App")
st.markdown("Upload PDF/DOCX/TXT files and ask questions based on their content.")

# 1️⃣ Tabs for navigation
tabs = st.tabs(["📤 Upload Files", "❓ Ask a Question", "🗂 View Uploaded Files"])

# ---------------------------------------------------------
# 📤 Upload Tab
with tabs[0]:
    st.header("📄 Upload Documents One by One")

    # Session state to track upload slots
    if "file_upload_count" not in st.session_state:
        st.session_state.file_upload_count = 1
    if "uploaded_files" not in st.session_state:
        st.session_state.uploaded_files = []

    st.subheader("📂 Select Files to Upload")

    # Show upload slots
    for i in range(st.session_state.file_upload_count):
        uploaded_file = st.file_uploader(f"Select File #{i + 1}", type=["pdf", "txt", "docx"], key=f"uploader_{i}")
        if uploaded_file:
            if uploaded_file.name not in [f.name for f in st.session_state.uploaded_files]:
                st.session_state.uploaded_files.append(uploaded_file)

    # Add more upload slots
    if st.button("➕ Add Another File"):
        st.session_state.file_upload_count += 1

    # Show uploaded file list
    if st.session_state.uploaded_files:
        st.markdown("### ✅ Files Ready to Upload:")
        for file in st.session_state.uploaded_files:
            st.write(f"📄 {file.name}")

        # Upload to FastAPI backend
        if st.button("🚀 Upload Files"):
            files = [("files", (f.name, f, f.type)) for f in st.session_state.uploaded_files]

            with st.spinner("Uploading and processing files..."):
                response = requests.post(f"{API_BASE_URL}/upload/", files=files)

            if response.status_code == 200:
                st.success("✅ Files uploaded and ingested successfully!")
                st.session_state.uploaded_files.clear()
                st.session_state.file_upload_count = 1
            else:
                st.error("❌ Upload failed.")
    else:
        st.info("📭 No files selected yet.")

# ---------------------------------------------------------
# ---------------------------------------------------------
# ❓ Ask a Question Tab
with tabs[1]:
    st.header("❓ Ask Questions")

    # Optional file selector
    with st.expander("🗂 Optional: Select a specific document to query"):
        try:
            file_list_res = requests.get(f"{API_BASE_URL}/files/")
            if file_list_res.status_code == 200:
                file_options = [f["file"] for f in file_list_res.json()]
            else:
                file_options = []
        except:
            file_options = []

        if file_options:
            selected_file = st.selectbox("Filter by file", options=["All"] + file_options)
        else:
            selected_file = "All"

        file_param = None if selected_file == "All" else selected_file

    st.markdown("### 📝 Your Questions")

    # Initialize question list in session state
    if "question_boxes" not in st.session_state:
        st.session_state.question_boxes = [""]

    # Function to add a new empty question box
    def add_question_box():
        st.session_state.question_boxes.append("")

    # Button to add new question
    st.button("➕ Add Question", on_click=add_question_box)

    # Collect questions from user
    updated_questions = []
    for i, q in enumerate(st.session_state.question_boxes):
        question = st.text_input(f"Question {i+1}", value=q, key=f"question_{i}")
        updated_questions.append(question)

    # Update session state
    st.session_state.question_boxes = updated_questions

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

# ---------------------------------------------------------
# ---------------------------------------------------------
# 🗂 View Uploaded Files Tab
with tabs[2]:
    st.header("📁 Uploaded Documents")

    col1, col2 = st.columns([3, 1])

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
        except:
            st.error("🚫 Could not connect to the backend.")

    with col2:
        if st.button("🧹 Clear All Files"):
            try:
                clear_res = requests.delete(f"{API_BASE_URL}/clear/")
                if clear_res.status_code == 200:
                    st.success("🧼 All uploaded files and embeddings cleared!")
                else:
                    st.error("❌ Failed to clear files.")
            except Exception as e:
                st.error(f"🚫 Error: {e}")
