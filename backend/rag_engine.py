import chromadb
from chromadb.utils import embedding_functions
import google.generativeai as genai
import os
import time
from google.api_core import exceptions
from dotenv import load_dotenv

load_dotenv()
from typing import List

# Configure Gemini API
# Assumes GOOGLE_API_KEY is set in environment environment variable
if "GOOGLE_API_KEY" in os.environ:
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

class RAGEngine:
    def __init__(self, collection_name="samvidhan_legal"):
        self.client = chromadb.PersistentClient(path="./chroma_db")
        
        # Use Google Generative AI Embeddings if key is present, otherwise fallback to default
        # For simplicity in this demo, we'll strive to use Gemini embeddings.
        # If API key is missing, this might fail or we can use default sentence-transformers.
        if "GOOGLE_API_KEY" in os.environ:
            self.embedding_fn = embedding_functions.GoogleGenerativeAiEmbeddingFunction(
                api_key=os.environ["GOOGLE_API_KEY"],
                model_name="models/gemini-embedding-001"
            )
        else:
             # Fallback or error
             print("Warning: GOOGLE_API_KEY not found. Using default embeddings (sentence-transformers).")
             self.embedding_fn = embedding_functions.DefaultEmbeddingFunction()

        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embedding_fn
        )

    def add_documents(self, documents: List[str], metadatas: List[dict], ids: List[str]):
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )

    def query(self, query_text: str, n_results: int = 3):
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
        return results

    def generate_response(self, query: str, context: List[str], language: str = "en"):
        # Check if context is empty or very limited, trigger external search
        from external_search import search_indian_kanoon
        
        external_context = ""
        external_citations = []
        
        # Heuristic: If context is empty or explicitly requested, search online
        if not context or "latest" in query.lower() or "case law" in query.lower():
            print("Triggering external search...")
            search_results = search_indian_kanoon(query)
            if search_results:
                external_context = "\nExternal Search Results (Indian Kanoon):\n"
                for res in search_results:
                    external_context += f"- Title: {res['title']}\n  Summary: {res['summary']}\n  Source: {res['url']}\n"
                    external_citations.append({
                        "act": "Indian Kanoon (External)",
                        "section": "Case Law / Article",
                        "summary": res['title'],
                        "url": res['url'] # We will need to handle this in frontend
                    })
        
        full_context = ' '.join(context) + "\n" + external_context

        system_prompt = f"""You are Samvidhan.ai, an Indian legal information assistant.
You provide general legal guidance based on the provided statutory context and external search results.
Language: {language}

Usage Guidelines:
1. Identify the legal domain.
2. Mention relevant Act names and Section numbers.
3. If external search results are used, explicitly mention "According to online sources..."
4. Explain in simple language.
5. Provide a disclaimer that this is not legal advice.

Context:
{full_context}

User Query: {query}

Output JSON format:
{{
"domain": "...",
"relevant_laws": ["..."],
"explanation": "...",
"general_guidance": "...",
"confidence": "High/Medium/Low",
"disclaimer": "This is not legal advice.",
"external_citations": {external_citations} 
}}
"""
        # Note: We inject pre-formatted external_citations into the prompt instruction 
        # but actually we should just ask the LLM to structure the response and we merge citations later.
        # Better approach: Let LLM generate the text, and we append the external citations to the final response object in main.py
        # For now, to keep it simple, we will instruct the LLM to include them or just merge them in the backend return.
        
        # REVISED PROMPT for cleaner JSON handling
        system_prompt = f"""You are Samvidhan.ai, an Indian legal information assistant.
You provide general legal guidance based on the provided statutory context and external search results.
Language: {language}

Context:
{full_context}

User Query: {query}

Output JSON format:
{{
"domain": "Criminal/Civil/Constitutional...",
"relevant_laws": ["IPC Section 302", "Constitution Art 21"...],
"explanation": "Detailed explanation...",
"general_guidance": "Actionable steps...",
"confidence": "High/Medium/Low",
"disclaimer": "This is not legal advice."
}}
"""
        
        
        # Use currently available Gemini models (verified via list_models)
        models_to_try = [
            'models/gemini-2.5-flash',
            'models/gemini-2.0-flash',
            'models/gemini-2.5-pro'
        ]

        last_exception = None
        response_text = ""

        for model_name in models_to_try:
            try:
                print(f"Trying generation with model: {model_name}")
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(
                    system_prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.3,
                        response_mime_type="application/json"
                    )
                )
                print(f"Success with {model_name}")
                response_text = response.text
                break
                
            except Exception as e:
                print(f"Failed with {model_name}: {e}")
                last_exception = e
                time.sleep(1)
                continue
        
        if not response_text:
            if last_exception:
                raise last_exception
            raise Exception("All models failed")

        return response_text, external_citations


