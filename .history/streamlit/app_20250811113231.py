# streamlit/app.py

import streamlit as st
from backend import (
    process_upload_files,
    ask_questions_local,
    get_uploaded_files_local,
    clear_all_data_local,
)

# --- STREAMLIT UI SETUP ---
st.set_page_config(page_title="Gen AI Document Q&A", page_icon="📚", layout="wide")
st.title("📚 Advanced Gen AI Document Q&A")
st.markdown("---")

tab1, tab2, tab3 = st.tabs(["**📂 File Uploader**", "**💬 Q&A Session**", "**📜 File History**"])

# --- TAB 1: FILE UPLOADER ---
with tab1:
    st.header("Upload Documents to the Knowledge Base")
    st.info("💡 Add one or more files to ingest them into the system. The processed files will be used for answering your questions.")

    if "num_files" not in st.session_state:
        st.session_state.num_files = 1

    all_uploaded_files = []

    for i in range(st.session_state.num_files):
        uploaded_file = st.file_uploader(
            f"File {i+1}",
            type=["pdf", "txt", "docx"],
            accept_multiple_files=False,
            key=f"file_uploader_{i}"
        )
        if uploaded_file:
            all_uploaded_files.append(uploaded_file)

    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("➕ Add Another File", type="secondary"):
            st.session_state.num_files += 1
            st.experimental_rerun()
    with col2:
        st.markdown("*Click to add a new slot for another file.*")

    st.markdown("---")

    if st.button("📤 Process All Files", type="primary"):
        if not all_uploaded_files:
            st.warning("Please select files to upload.")
        else:
            with st.spinner("🚀 Uploading and processing documents..."):
                response = process_upload_files(all_uploaded_files)
                st.success(response.get("message", "✅ Files uploaded successfully!"))
                st.experimental_rerun()

# --- TAB 2: Q&A SESSION ---
with tab2:
    st.header("Ask Questions about Your Documents")

    file_history = get_uploaded_files_local()
    if not file_history:
        st.warning("⚠️ No files uploaded yet. Please upload documents in the 'File Uploader' tab to begin.")
    else:
        st.info("Choose a source file to narrow down your query, or select 'All Documents' to search across your entire library.")

        file_options = ["All Documents"] + [file['file'] for file in file_history]
        selected_file = st.selectbox(
            "**🔍 Select Source File:**",
            options=file_options,
            help="This feature allows you to perform Q&A on a single, specific document."
        )

        st.markdown("---")
        st.subheader("📝 Enter Your Questions")

        if "questions" not in st.session_state:
            st.session_state.questions = [""]

        for i in range(len(st.session_state.questions)):
            st.session_state.questions[i] = st.text_area(
                f"Question {i+1}",
                value=st.session_state.questions[i],
                height=35,
                key=f"question_input_{i}"
            )

        if st.button("➕ Add More Question", type="secondary"):
            st.session_state.questions.append("")
            st.experimental_rerun()

        st.markdown("---")

        if st.button("🚀 Get Answers", type="primary"):
            questions_to_ask = [q for q in st.session_state.questions if q.strip()]
            source = selected_file if selected_file != "All Documents" else None

            with st.spinner("🤔 Getting answers..."):
                responses = ask_questions_local(questions_to_ask, source)

            if responses:
                st.subheader("📌 Answers:")
                for res in responses:
                    with st.expander(f"**Q:** {res['question']}", expanded=True):
                        st.success(f"**A:** {res['answer']}")

# --- TAB 3: FILE HISTORY ---
with tab3:
    st.header("Uploaded Documents History")

    file_history = get_uploaded_files_local()
    if file_history:
        st.info("Here is a list of all documents currently in the knowledge base, along with their upload dates.")
        st.dataframe(file_history, use_container_width=True)
        st.markdown("---")

        st.subheader("🧹 Clear All Data")
        st.warning("⚠️ **Warning:** Clicking this button will permanently delete all uploaded files and their embeddings from the system.")
        if st.button("🗑️ Clear All Data", type="secondary"):
            with st.spinner("🗑️ Clearing all files and embeddings..."):
                response = clear_all_data_local()
                st.success(response.get("message", "✅ All files and embeddings cleared!"))
                st.session_state.questions = [""]
                st.experimental_rerun()
    else:
        st.info("No files have been uploaded yet.")
