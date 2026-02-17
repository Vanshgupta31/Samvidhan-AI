from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import QueryRequest, QueryResponse, Citation
from rag_engine import RAGEngine
import os
from dotenv import load_dotenv
import json
import re

load_dotenv()

app = FastAPI(title="Samvidhan.ai API")

# Initialize RAG Engine
# Use a global instance to keep the connection open
rag_engine = RAGEngine()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Samvidhan.ai API is running"}

@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    try:
        # Retrieve context
        results = rag_engine.query(request.query)
        documents = results['documents'][0]
        metadatas = results['metadatas'][0]
        
        # Generate response using LLM
        # This returns a JSON string and external citations list
        response_text, external_citations = rag_engine.generate_response(request.query, documents, request.language)
        
        # Parse JSON response from LLM
        # Remove potential markdown code blocks
        clean_json = re.sub(r"```json\n|```", "", response_text).strip()
        data = json.loads(clean_json)
        
        citations = []
        # Add local citations
        for i, doc in enumerate(documents):
            meta = metadatas[i]
            citations.append(Citation(
                act=meta.get("act", "Unknown Act"),
                section=meta.get("section", "Unknown Section"),
                summary=doc[:150] + "..." # Truncate for summary
            ))
        
        # Add external citations
        for ext in external_citations:
            citations.append(Citation(
                act=ext.get("act", "External Source"),
                section=ext.get("section", "General"),
                summary=ext.get("summary", "")[:150] + "...",
                url=ext.get("url")
            ))
            
        return QueryResponse(
            domain=data.get("domain", "General Legal"),
            relevant_laws=data.get("relevant_laws", []),
            explanation=data.get("explanation", "Could not generate explanation."),
            general_guidance=data.get("general_guidance", "Please consult a lawyer."),
            confidence=data.get("confidence", "Low"),
            disclaimer=data.get("disclaimer", "Not legal advice."),
            citations=citations
        )
        
    except Exception as e:
        print(f"Error processing query: {e}")
        # In case of error, return a fallback response or raise HTTP exception
        # For demo purposes, let's return a safe error response
        return QueryResponse(
            domain="Error",
            relevant_laws=[],
            explanation="An error occurred while processing your query.",
            general_guidance="Please try again later.",
            confidence="Low",
            disclaimer="System Error",
            citations=[]
        )
