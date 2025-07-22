from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from pinecone import Pinecone
from embedder import embed_texts
import google.generativeai as genai
import os

# === CONFIG ===
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")
PINECONE_ENV = os.getenv("PINECONE_ENV")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

genai.configure(api_key=GEMINI_API_KEY)
gemini = genai.GenerativeModel(model_name="models/gemini-2.0-flash")

pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(PINECONE_INDEX_NAME)

TOP_K = 8
CORE_FIELDS = ["Scheme Name", "Ministry/Department", "Target Beneficiaries", "Tags", "Description"]

class QueryRequest(BaseModel):
    query: str

def detect_relevant_field(query):
    q = query.lower()
    if any(word in q for word in ["apply", "application", "register", "procedure", "how to avail"]):
        return "Application Process"
    elif "benefit" in q or "advantages" in q:
        return "Benefits"
    elif "eligibility" in q or "eligible" in q or "who can apply" in q:
        return "Eligibility Criteria"
    elif "document" in q or "paperwork" in q:
        return "Documents Required"
    else:
        return None

def retrieve_context(user_query: str) -> str:
    relevant_field = detect_relevant_field(user_query)
    query_vector = embed_texts([user_query])[0]
    response = index.query(vector=query_vector, top_k=TOP_K, include_metadata=True)
    matches = response["matches"]

    scheme_order = []
    for match in matches:
        pid = match["metadata"]["parent_doc_id"]
        if pid not in scheme_order:
            scheme_order.append(pid)
        if len(scheme_order) == 2:
            break

    final_context = []
    for idx, pid in enumerate(scheme_order):
        full_scheme = index.query(
            vector=query_vector,
            top_k=100,
            include_metadata=True,
            filter={"parent_doc_id": {"$eq": pid}}
        )["matches"]

        scheme_name = ""
        section = []

        for match in full_scheme:
            meta = match["metadata"]
            text = meta["chunk_text"]
            field = meta["field"]

            if field == "Scheme Name" and not scheme_name:
                scheme_name = text.split(":", 1)[1].strip()
                section.append(f"Scheme Name: {scheme_name}")
            if field in CORE_FIELDS:
                section.append(f"{field}: {text.split(':', 1)[1].strip()}")

        if idx == 0 and relevant_field:
            for match in full_scheme:
                meta = match["metadata"]
                if meta["field"] == relevant_field:
                    section.append(f"{relevant_field}: {meta['chunk_text'].split(':',1)[1].strip()}")

        final_context.append("\n".join(section))

    return "\n\n---\n\n".join(final_context)

def generate_answer(query: str, context: str) -> str:
    prompt = f"""
You are an intelligent and helpful assistant specializing in Indian government schemes.
Your goal is to provide clear, concise, and actionable information based *only* on the provided context.
If the context does not contain enough information to fully answer the question, clearly state that you cannot provide a complete answer with the available information. Do not invent information.

---
Contextual Information about Indian Government Schemes:

{context}

---
User's Query: "{query}"

---
Instructions for your response:
1.  **Prioritize the user's explicit question.** If the user asks for "eligibility criteria", focus on that section from the relevant scheme(s).
2.  **Provide a direct answer first.** Start with the most relevant information without preamble.
3.  **Structure your answer clearly.** Use headings, bullet points, or numbered lists where appropriate for readability.
4.  **Mention the scheme name(s) explicitly.** Always include the "Scheme Name" when providing information about it.
5.  **Be concise but comprehensive.** Include all necessary details from the context, but avoid verbose language.
6.  **If multiple schemes are relevant, compare and contrast them briefly** if it makes sense for the query, or present information for each clearly separated.
7.  **Do NOT include disclaimers or conversational filler** like "Based on the information provided..." or "I hope this helps!". Just present the answer directly.
8.  **If the query asks about a specific aspect (e.g., "application process") and the context for a relevant scheme does NOT have that specific field, state that the information is not available.** For example: "The application process for [Scheme Name] is not detailed in the provided information."

Answer:
"""
    response = gemini.generate_content(prompt)
    return response.text

@app.get("/")
async def root():
    return {"status": "✅ GenAI RAG backend is running."}

@app.post("/ask")
async def ask(query_request: QueryRequest):
    query = query_request.query
    context = retrieve_context(query)
    answer = generate_answer(query, context)
    return {"query": query, "answer": answer}
