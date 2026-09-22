import os
import re
import json
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from tabulate import tabulate
import docs


load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

with open("observations.json", "r") as f:
    observations = json.load(f)

print(observations)


def structure(type, evidence):

    type=type.lower()

    if "date" in type:
        pattern = r"\d{4}-\d{2}-\d{2}"

    elif "currency" ==  type:
        pattern = r"\$[\d,]+\.\d{2}"

    elif "invoice" in type or "ticket" in type:
        pattern = r"[A-Z]+-?\d+"

    else:
        return 0.0

    if re.fullmatch(pattern, evidence):
        return 1.0

    if re.search(pattern, evidence):
        return 0.5

    return 0.0

print(structure("date", "2026-03-02"))
print(structure("date", "last week"))
print(structure("currency", "$1,240.50"))
print(structure("invoice_id", "INV-4471"))


def find(text,evidence):

    sentences = re.split(r'(?<=[.!?])\s+', text.strip())

    for sentence in sentences:
        if evidence in sentence:
            return sentence

    return text

model = ChatGroq(
    model="openai/gpt-oss-20b",
    groq_api_key=api_key,
    temperature=0
)

def semantic_clarity(evidence, sentence):

    prompt = f"""
Evidence:
{evidence}

Sentence:
{sentence}

Give a score between 0 and 1 based on the context from the sentence.Return only the number."""

    response = model.invoke(prompt)

    return float(response.content.strip())

source_trust = {"invoice_pdf": 0.95, "email": 0.7, "support_ticket": 0.75, "crm_note": 0.6, "log": 0.9, "meeting_note": 0.5}

results=[]

for observation in observations:

    document_texts = {}
    document_types = {}

    for document in docs.docs:
        document_texts[document["id"]] = document["text"]
        document_types[document["id"]] = document["source_type"]
        doc_id=observation['doc_id']
        source_text=document_texts[doc_id]
        source_type = document_types[doc_id]

        structural=structure(observation['type'],observation['evidence_span'])
        sentence=find(source_text,observation['evidence_span'])
        semantic=semantic_clarity(observation['evidence_span'],sentence)
        trust=source_trust[source_type]
        confidence = 0.4*structural + 0.3*semantic + 0.3*trust


        result={
            "doc_id": doc_id,
            "type": observation["type"],
            "value": observation["value"],
            "evidence_span": observation["evidence_span"],
            "confidence": round(confidence, 2),
            "factors": {
                "structural_clarity": structural,
                "semantic_clarity": semantic,
                "source_trust": trust
            }
        }
results.append(result)