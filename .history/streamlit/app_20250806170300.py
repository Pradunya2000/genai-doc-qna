import streamlit as st
import requests

API_BASE_URL = "http://localhost:8000"  # Update if deploying externally

st.set_page_config(page_title="📚 Private PDF Q&A", layout="wide")

st.title("📚 Private PDF Q&A App")
st.markdown("Upload PDF/DOCX/TXT files and ask questions based on their content.")

# 1️⃣ Tabs for navigation
tabs = st.tabs(["📤 Upload Files", "❓ Ask a Question", "🗂 View Uploaded Files"])

# ---------------------------------------------------------
# 📤 Upload Tab
with tabs[0]:  # Upload Documents Tab
    st.header("📄 Upload Documents One by One")

    # Initialize session state for uploaders
    if "file_upload_count" not in st.session_state:
        st.session_state.file_upload_count = 1  # start with 1 uploader
    if "uploaded_files" not in st.session_state:
        st.session_state.uploaded_files = []

    st.subheader("📂 Select Files to Upload")

    # Dynamically create file uploaders
    for i in range(st.session_state.file_upload_count):
        uploaded_file = st.file_uploader(f"Select File #{i + 1}", type=["pdf", "txt", "docx"], key=f"uploader_{i}")
        if uploaded_file is not None:
            # Prevent duplicates
            if uploaded_file.name not in [f.name for f in st.session_state.uploaded_files]:
                st.session_state.uploaded_files.append(uploaded_file)

    # Add another file uploader
    if st.button("➕ Add Another File"):
        st.session_state.file_upload_count += 1

    # Show uploaded file list
    if st.session_state.uploaded_files:
        st.markdown("### ✅ Files Ready to Upload:")
        for file in st.session_state.uploaded_files:
            st.write(f"📄 {file.name}")

        # Upload to backend
        if st.button("🚀 Upload All Files"):
            files = [("files", (f.name, f, f.type)) for f in st.session_state.uploaded_files]

            with st.spinner("Uploading..."):
                response = requests.post("http://localhost:8000/upload-doc", files=files)

            if response.status_code == 200:
                st.success("✅ Files uploaded and ingested successfully!")
                # Reset after upload
                st.session_state.file_upload_count = 1
                st.session_state.uploaded_files = []
            else:
                st.error("❌ Upload failed.")
    else:
        st.info("📭 No files uploaded yet.")


# ---------------------------------------------------------
# ❓ Ask a Question Tab
with tabs[1]:
    st.header("❓ Ask Questions")

    # Optional: Filter by source file
    with st.expander("🗂 Optional: Select a specific document to query"):
        file_list_res = requests.get(f"{API_BASE_URL}/files/")
        file_options = [f["file"] for f in file_list_res.json()] if file_list_res.status_code == 200 else []
        selected_file = st.selectbox("Filter by file", options=["All"] + file_options)
        file_param = None if selected_file == "All" else selected_file

    question_input = st.text_area("📝 Enter your question(s):", height=150, placeholder="One per line...")
    if st.button("🎯 Ask"):
        if question_input.strip():
            questions = [q.strip() for q in question_input.strip().split("\n") if q.strip()]

            with st.spinner("Thinking..."):
                res = requests.post(
                    f"{API_BASE_URL}/ask/",
                    json={"questions": questions},
                    params={"source_file": file_param} if file_param else None
                )

            if res.status_code == 200:
                for item in res.json()["responses"]:
                    with st.expander(f"❓ {item['question']}"):
                        st.write(f"🤖 {item['answer']}")
            else:
                st.error("❌ Failed to get answer.")
        else:
            st.warning("⚠️ Please enter at least one question.")

# ---------------------------------------------------------
# 🗂 View Files Tab
with tabs[2]:
    st.header("📁 Uploaded Documents")

    res = requests.get(f"{API_BASE_URL}/files/")
    if res.status_code == 200:
        files = res.json()
        if not files:
            st.info("📭 No documents uploaded yet.")
        else:
            for file in files:
                st.markdown(f"🔹 **{file['file']}** — 🕒 Uploaded on: `{file['upload_date']}`")
    else:
        st.error("❌ Unable to fetch uploaded file list.")
