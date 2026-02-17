import json
import os
from rag_engine import RAGEngine

def ingest_data():
    # Load corpus
    with open("data/legal_corpus.json", "r") as f:
        corpus = json.load(f)

    rag = RAGEngine()

    documents = []
    metadatas = []
    ids = []

    for idx, item in enumerate(corpus):
        # Create a rich text representation for embedding
        doc_text = f"{item['act']} Section {item['section']}: {item['text']}"
        documents.append(doc_text)
        
        # Metadata for retrieval
        metadatas.append({
            "act": item["act"],
            "section": item["section"]
        })
        
        # Unique ID
        ids.append(f"doc_{idx}")

    print(f"Ingesting {len(documents)} documents...")
    rag.add_documents(documents, metadatas, ids)
    print("Ingestion complete.")

if __name__ == "__main__":
    ingest_data()
