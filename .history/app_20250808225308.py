# app.py

from document_loader import load_documents_from_folder, split_documents
from embedding_store import store_embeddings
from qa_chain import get_qa_chain

def ingest_documents(folder_path):
    print("📄 Loading documents...")
    docs = load_documents_from_folder(folder_path)
    print(f"✅ {len(docs)} documents loaded.")

    print("🔪 Splitting documents...")
    chunks = split_documents(docs)
    print(f"✅ {len(chunks)} chunks created.")

    print("📦 Generating & storing embeddings...")
    store_embeddings(chunks)
    print("✅ Embeddings stored in ChromaDB.")


def ask_question(question):
    chain = get_qa_chain()
    result = chain({"query": question})
    return result["result"]


if __name__ == "__main__":
    folder_path = "docs"  # Replace with your folder path containing PDFs/TXT/DOCX
    ingest_documents(folder_path)

    while True:
        query = input("\nAsk a question (or type 'exit'): ")
        if query.lower() == "exit":
            break
        answer = ask_question(query)
        print("\n🤖 Answer:", answer)
