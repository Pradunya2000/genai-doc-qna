📄 GenAI Multi-Document Q&A System
💡 Project Overview
This is an advanced Retrieval-Augmented Generation (RAG) application designed to provide secure, natural-language querying over private, multi-format documents. 
The system enables users to upload multiple files, intelligently query them, and receive context-aware answers grounded in the document content. This project 
demonstrates proficiency in building a complete end-to-end Generative AI solution.

--------------------------------------------------------------------------------------------------------------------------------------------------------------

🚀 Key Features

This project highlights a solid understanding of modern AI development by implementing the following core features:

📂 Multi-File & Multi-Format Ingestion: The system supports a powerful ingestion pipeline that can process multiple PDF, TXT, and DOCX files in a single request, demonstrating robust file handling and data processing skills.
🔍 Advanced RAG Querying: I've implemented a flexible Q&A system that can query across all uploaded documents or be filtered to a specific file. This showcases an understanding of fine-tuning retrieval logic to meet user needs.
📜 Document History & Management: The application includes a dedicated feature to fetch and display a history of all uploaded documents, providing a clear audit trail and demonstrating skills in data management.
🗑️ Comprehensive Data Clearing: A one-click solution is provided to remove all documents and their vector embeddings, which is a crucial feature for data privacy and storage management.
⚡ Real-Time User Experience: The system is designed for a fast, responsive user experience with Streamlit for the frontend, allowing for rapid prototyping and interactive data applications.

--------------------------------------------------------------------------------------------------------------------------------------------------------------

🏗️ Technical Stack

This project was built using a well-defined and modern tech stack:

Frontend: Streamlit for building a rich, interactive web application with pure Python, demonstrating my ability to deliver user-friendly interfaces.
Backend: FastAPI for creating a high-performance, asynchronous API. This highlights my skills in designing scalable and well-documented web services.
LLM Framework: LangChain was used to orchestrate the entire RAG pipeline, from document loading to final answer generation, showcasing my expertise in leveraging industry-standard AI frameworks.
Embeddings: sentence-transformers/all-MiniLM-L6-v2 from HuggingFace was chosen for its balance of performance and efficiency, a key consideration for practical applications.
Vector Database: ChromaDB serves as the persistent knowledge base, proving my experience in working with vector databases for semantic search.
LLM API: The system connects to an OpenAI-compatible endpoint, showcasing a flexible and modular design that can be adapted to different LLM providers.
--------------------------------------------------------------------------------------------------------------------------------------------------------------

📂 Project Structure

genai-doc-qa/
│── app/                  # Backend (FastAPI)
│── frontend/             # Streamlit app
│── test_files/           # Diagnostic & smoke test scripts
│── docs/                 # Example documents
│── requirements.txt      # Python dependencies
│── Dockerfile            # Deployment setup
│── README.md             # Project documentation

--------------------------------------------------------------------------------------------------------------------------------------------------------------

⚙️ Installation & Setup

1️⃣ Clone the repo
git clone https://github.com/yourusername/genai-doc-qa.git
cd genai-doc-qa


2️⃣ Install dependencies
pip install -r requirements.txt


3️⃣ Set environment variables
Create a .env file:

env
A4F_API_KEY=your_api_key
A4F_BASE_URL=https://api.a4f.ai/v1
LLM_MODEL_NAME=gpt-3.5-turbo

4️⃣ Run backend (FastAPI)
uvicorn app.main:app --reload

5️⃣ Run frontend (Streamlit)
streamlit run frontend/app.py

--------------------------------------------------------------------------------------------------------------------------------------------------------------

🧪 Running Tests

Example:
python test_files/app.py           # Ingest documents
python test_files/inspect_db.py    # Inspect vector DB contents
python test_files/model.py         # Test LLM connectivity
python test_files/test_query.py    # Run sample Q&A query

--------------------------------------------------------------------------------------------------------------------------------------------------------------

📦 Deployment

With Docker:
docker build -t genai-doc-qa .
docker run -p 8000:8000 genai-doc-qa

Or deploy to Streamlit Cloud, Hugging Face Spaces, or AWS.

--------------------------------------------------------------------------------------------------------------------------------------------------------------

🗂 Example Usage Flow

1. Upload Documents → Add files one by one in PDF, TXT, or DOCX format.

2. Ask Questions → Query across all documents, or select a specific file for targeted answers.

3. View History → Check the list of all uploaded documents in the interface.

4. Clear History → Remove all stored files and embeddings with one click.

--------------------------------------------------------------------------------------------------------------------------------------------------------------

📌 Roadmap
 Add support for batch file upload.

 Implement streaming responses for faster UX.

 Add hybrid search (BM25 + embeddings) for better retrieval.

 Integrate authentication for multi-user support.

--------------------------------------------------------------------------------------------------------------------------------------------------------------

👨‍💻 Author
Your Name — Pradunya Rajendra SArode