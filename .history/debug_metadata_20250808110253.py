# debug_metadata.py
from retriever import get_all_metadata

if __name__ == "__main__":
    all_meta = get_all_metadata()
    for m in all_meta:
        print(f"File in DB: '{m['file']}' | Upload Date: {m['upload_date']}'")
