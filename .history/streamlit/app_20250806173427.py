import streamlit as st
import requests

# FastAPI backend URL
API_URL = "http://localhost:8000"

st.set_page_config(page_title="📄 Private PDF Q&A App", layout="centered")

st.title("📄 Private PDF Q&A App")

# ---------- 1. FILE UPLOAD SECTION ----------
st.header("📤 Upload Documents (.pdf, .txt, .docx)")

uploaded_file = st.file_uploader("Choose a file", type=["pdf", "txt", "docx"])

if st.button("🚀 Upload and Process"):
    if uploaded_file is not None:
        files = {
            "files": (uploaded_file.name, uploaded_file.read(), uploaded_file.type)
        }
        with st.spinner("Uploading and processing..."):
            res = requests.post(f"{API_URL}/upload/", files=files)
        if res.status_code == 200:
            st.success("✅ File uploaded and processed successfully!")
            st.write("File name:", res.json()["files"])
        else:
            st.error("❌ Upload failed. Please check your backend.")
    else:
        st.warning("Please choose a file to upload.")

# ---------- 2. FILE SELECTION (OPTIONAL) ----------
st.markdown("---")
st.header("📁 Select a File to Query (Optional)")

with st.spinner("Loading uploaded file list..."):
    try:
        files_response = requests.get(f"{API_URL}/files/")
        files_response.raise_for_status()
        file_metadata = files_response.json()
        file_list = [item['source'] for item in file_metadata]
    except:
        file_list = []

selected_file = st.selectbox("Select a file (optional filter):", [""] + file_list)
source_param = selected_file if selected_file else None

# ---------- 3. QUESTION ASKING ----------
st.markdown("---")
st.header("❓ Ask Your Questions")
question_input = st.text_area("Enter one or more questions (each on a new line):", height=200)

if st.button("🔍 Get Answers"):
    if question_input.strip():
        questions = [q.strip() for q in question_input.strip().split('\n') if q.strip()]
        payload = {"questions": questions}
        params = {"source_file": source_param} if source_param else {}

        with st.spinner("Getting answers..."):
            response = requests.post(f"{API_URL}/ask/", json=payload, params=params)

        if response.status_code == 200:
            for qa in response.json()["responses"]:
                st.markdown(f"**🟡 Question:** {qa['question']}")
                st.markdown(f"**🟢 Answer:** {qa['answer']}")
                st.markdown("---")
        else:
            st.error("❌ Failed to get answers. Please try again.")
    else:
        st.warning("Please enter at least one question.")
