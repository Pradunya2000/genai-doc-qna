import streamlit as st
import requests

# Base URL of your FastAPI backend
API_URL = "http://localhost:8000"

st.set_page_config(page_title="📄 Private PDF Q&A", layout="centered")

st.title("📄 Private PDF Q&A App")

# 1. Upload documents section
st.header("📤 Upload PDF or TXT Documents")
uploaded_files = st.file_uploader("Select files", type=["pdf", "txt"], accept_multiple_files=True)

if st.button("🚀 Upload and Process"):
    if uploaded_files:
        files = [("files", (f.name, f.read(), f.type)) for f in uploaded_files]
        with st.spinner("Uploading and processing documents..."):
            res = requests.post(f"{API_URL}/upload/", files=files)
        if res.status_code == 200:
            st.success("✅ Documents uploaded and processed successfully!")
            st.write("Files:", res.json()["files"])
        else:
            st.error("❌ Failed to upload files.")
    else:
        st.warning("Please upload at least one file.")

# Divider
st.markdown("---")

# 2. File selection (for filtering Q&A)
st.header("📁 Select File to Query (Optional)")
with st.spinner("Fetching uploaded file list..."):
    file_list = requests.get(f"{API_URL}/files/").json()

file_names = [f["source"] for f in file_list]
selected_file = st.selectbox("Choose a file (or leave empty to search all):", [""] + file_names)
source_param = selected_file if selected_file else None

# 3. Ask questions section
st.header("❓ Ask Questions")
question_input = st.text_area("Enter your question(s) (one per line):")

if st.button("🔍 Get Answers"):
    if question_input.strip():
        questions = [q.strip() for q in question_input.strip().split('\n') if q.strip()]
        payload = {"questions": questions}
        params = {"source_file": source_param} if source_param else {}

        with st.spinner("Thinking..."):
            res = requests.post(f"{API_URL}/ask/", json=payload, params=params)

        if res.status_code == 200:
            responses = res.json()["responses"]
            for r in responses:
                st.markdown(f"**🟡 Question:** {r['question']}")
                st.markdown(f"**🟢 Answer:** {r['answer']}")
                st.markdown("---")
        else:
            st.error("❌ Failed to get answers from the backend.")
    else:
        st.warning("Please enter at least one question.")
