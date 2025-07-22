import spacy
nlp = spacy.load("en_core_web_sm")

def sent_tokenize(text):
    return [sent.text.strip() for sent in nlp(text).sents]

import json
import re
import uuid
from transformers import AutoTokenizer
import os

# === Model tokenizer with 512 max limit ===
tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
MODEL_MAX_TOKENS = 512

SMALL_FIELDS = ["Scheme Name", "Ministry/Department", "Target Beneficiaries", "Tags", "Description"]
MEDIUM_FIELDS = ["Benefits", "Eligibility Criteria", "Documents Required"]
LARGE_FIELD = "Application Process"

MAX_WORDS = 300
MAX_TOKENS = 450

CHUNK_OUTPUT_PATH = os.path.join("data", "chunked_output.json")

def clean_text(text):
    return re.sub(r'\n+', '\n', text).strip()

def create_chunk(content, field, scheme_name, unique_id):
    return {
        "chunk_id": str(uuid.uuid4()),
        "parent_doc_id": unique_id,
        "chunk_text": f"{field}: {content}",
        "scheme_name": scheme_name,
        "field": field
    }

def word_based_chunking(content, field, scheme_name, unique_id, chunks):
    sentences = sent_tokenize(content)
    temp_chunk = ""
    for sentence in sentences:
        if len((temp_chunk + " " + sentence).split()) <= MAX_WORDS:
            temp_chunk += " " + sentence
        else:
            chunks.append(create_chunk(temp_chunk.strip(), field, scheme_name, unique_id))
            temp_chunk = sentence
    if temp_chunk:
        chunks.append(create_chunk(temp_chunk.strip(), field, scheme_name, unique_id))

def token_based_chunking(content, field, scheme_name, unique_id, chunks):
    sentences = sent_tokenize(content)
    temp_chunk = ""
    for sentence in sentences:
        token_count = len(tokenizer.encode(temp_chunk + " " + sentence,
                                            add_special_tokens=False,
                                            truncation=True,
                                            max_length=MODEL_MAX_TOKENS))
        if token_count <= MAX_TOKENS:
            temp_chunk += " " + sentence
        else:
            chunks.append(create_chunk(temp_chunk.strip(), field, scheme_name, unique_id))
            temp_chunk = sentence
    if temp_chunk:
        chunks.append(create_chunk(temp_chunk.strip(), field, scheme_name, unique_id))

def run_chunking(input_json_path: str) -> list[dict]:
    with open(input_json_path, "r", encoding="utf-8") as f:
        schemes = json.load(f)

    chunks = []

    for scheme in schemes:
        scheme_name = scheme.get("Scheme Name", "Unknown Scheme").strip()
        unique_id = scheme.get("Unique-ID", str(uuid.uuid4()))

        for field in SMALL_FIELDS + MEDIUM_FIELDS + [LARGE_FIELD]:
            content = scheme.get(field, "")
            if not content or content.strip().lower() in ["not available", "n/a"]:
                continue

            content = clean_text(content)

            if field in SMALL_FIELDS:
                chunks.append(create_chunk(content, field, scheme_name, unique_id))
            elif field in MEDIUM_FIELDS:
                if len(content.split()) <= MAX_WORDS:
                    chunks.append(create_chunk(content, field, scheme_name, unique_id))
                else:
                    word_based_chunking(content, field, scheme_name, unique_id, chunks)
            elif field == LARGE_FIELD:
                token_len = len(tokenizer.encode(content, add_special_tokens=False, truncation=True, max_length=MODEL_MAX_TOKENS))
                if token_len <= MAX_TOKENS:
                    chunks.append(create_chunk(content, field, scheme_name, unique_id))
                else:
                    token_based_chunking(content, field, scheme_name, unique_id, chunks)

    with open(CHUNK_OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)

    print(f"✅ Chunking complete! Total chunks: {len(chunks)}")
    print(f"📄 Saved to: {CHUNK_OUTPUT_PATH}")
    return chunks
