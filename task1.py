from langchain_groq import ChatGroq
import pandas as pd
from dotenv import load_dotenv
import os
from pydantic import BaseModel
import docs
from tabulate import tabulate

load_dotenv()
api_key=os.getenv("GROQ_API_KEY")

class Observation(BaseModel):
    type: str
    extracted_value: str
    derivation_method: str
    confidence: float
    evidence_span: str

class ObservationList(BaseModel):
    observations: list[Observation]

model=ChatGroq(
    model="openai/gpt-oss-20b",
    groq_api_key=api_key,
    temperature=0
)

structured_model=model.with_structured_output(ObservationList)

def validate_function(observation,source_text):
    evidence=observation.evidence_span in source_text
    return evidence


rows=[]

for document in docs.docs:
    print("Document ID:", document["id"])
    print("Source Type:", document["source_type"])
    print("Text:", document["text"])
    print("-" * 50)


    prompt=f"""
Extract every meaningful fact from the document.

For each fact:
- identify its type
- give the extracted value
- provide an evidence_span
- evidence_span MUST be copied exactly from the source text
- do not paraphrase evidence_span
- do not reformat evidence_span

Document:
{document["text"]}
"""

    try:
        result=structured_model.invoke(prompt)
        for observation in result.observations:
            passed=validate_function(
                observation,
                document['text']
            )

            rows.append({
                "doc_id": document["id"],
                "type": observation.type,
                "value": observation.extracted_value,
                "evidence_span": observation.evidence_span,
                "pass/fail": "PASS" if passed else "FAIL"
            })

            print("Type:", observation.type)
            print("Value:", observation.extracted_value)
            print("Evidence:", observation.evidence_span)
            print(
                "Validation:",
                "PASS" if passed else "FAIL"
            )
            print("-" * 30)


    except Exception as e:
        print(
            f"ERROR processing document {document['id']}: {e}"
        )

        print("Continuing to next document...")
        print("-" * 50)

print(tabulate(
    rows,
    headers="keys",
    tablefmt="grid"
))