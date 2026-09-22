import re
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os
import docs

load_dotenv()
api_key=os.getenv("GROQ_API_KEY")

model=ChatGroq(
    model="openai/gpt-oss-20b",
    groq_api_key=api_key,
    temperature=0
)

def deterministic_extract(text, field_type):

    if field_type == "date":
        pattern = r"\d{4}-\d{2}-\d{2}"

    elif field_type == "amount":
        pattern = r"\$[\d,]+\.\d{2}"

    elif field_type == "id":
        pattern = r"[A-Z]+-?\d+"

    elif field_type == "phone":
        pattern = r"\+91-\d{5}-\d{5}"

    else:
        return None

    match = re.search(pattern, text)
    if match:
        return match.group()

    return None

def heuristic_extract(text, field_type):

    prompt = f"""Extract only the {field_type} from this text.
Text:
{text}
Reply with just the value, nothing else."""

    response = model.invoke(prompt)
    return response.content.strip()

def semantic_extract(text):

    prompt = f"""
Extract every meaningful fact from this text.
Text:
{text}

Return each fact clearly.
"""
    response = model.invoke(prompt)
    return response.content.strip()


results = []
deterministic_count=0
heuristic_count=0
semantic_count=0

for doc in docs.docs:
    text=doc['text']
    lower_text = text.lower()
    found_field = False

    for field_type in ["date","amount","id","phone"]:
        result=deterministic_extract(text,field_type)

        if result:
            strategy = "deterministic"
            found_field = True

        elif field_type == "date" and "date" in lower_text:
            result = heuristic_extract(text, field_type)
            strategy = "heuristic"
            found_field = True

        elif field_type == "amount" and "amount" in lower_text:
            result = heuristic_extract(text, field_type)
            strategy = "heuristic"
            found_field = True

        elif field_type == "id" and "invoice" in lower_text:
            result = heuristic_extract(text, field_type)
            strategy = "heuristic"
            found_field = True

        elif field_type == "phone" and "phone" in lower_text:
            result = heuristic_extract(text, field_type)
            strategy = "heuristic"
            found_field = True

        else:
            continue

        result={
            "doc_id":doc['id'],
            "field_type": field_type,
            "value": result,
            "strategy_used":strategy
        }
        results.append(result)

        if strategy=="deterministic":
            deterministic_count+=1
        elif strategy=="heuristic":
            heuristic_count+=1
        else:
            semantic_count+=1

    if not found_field:
        result = semantic_extract(text)

        results.append({
            "doc_id": doc["id"],
            "field_type": "semantic",
            "value": result,
            "strategy_used": "semantic"
        })

        semantic_count += 1

total=deterministic_count+heuristic_count+semantic_count
print(deterministic_count,"deterministic,",heuristic_count,"heuristic,",semantic_count,"semantic cut of",total,"total fields")