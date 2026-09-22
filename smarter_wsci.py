from pathlib import Path
from ollama import chat
import json



question = """
I changed my university password this morning.
Now my Windows laptop won't connect to campus Wi-Fi,
but my phone still works.
"""

## WRITE ##
service_status = {
    "wifi": "operational"
}

state = {
    "problem": question,
    "wi_fi status": "operational",
    "wi-fi_check": True
}

with open("state.json", "w") as file:
    json.dump(
        state,
        file,
        indent=2
    )

with open("state.json", "r") as file:
    state = json.load(file)

print(state)


## SELECT CONTEXT FILES BASED ON QUESTION
## Create the function that takes the student's question, takes some keywords and chooses the relevant files from the knowledge base. Return a list of the selected files.
## For example, if the question has the kyeword "print" or "printer", then the function should return the file "knowledge/printer_setup.txt" in a list.
def select_context(question):
    keyword_files = {
        "wifi": "knowledge/wifi_setup.txt",
        "wi-fi": "knowledge/wifi_setup.txt",
        "eduroam": "knowledge/wifi_setup.txt",
        "network": "knowledge/wifi_setup.txt",
        "connect": "knowledge/wifi_setup.txt",
        "password": "knowledge/password_changes.txt",
        "credential": "knowledge/password_changes.txt",
        "account": "knowledge/password_changes.txt",
        "email": "knowledge/email_setup.txt",
        "mail": "knowledge/email_setup.txt",
        "vpn": "knowledge/vpn.txt",
        "print": "knowledge/printing.txt",
        "printer": "knowledge/printing.txt",
        "projector": "knowledge/classroom_projectors.txt",
        "display": "knowledge/classroom_projectors.txt",
        "university": "knowledge/service_status.txt",
        "status": "knowledge/service_status.txt",
    }
    lowered = question.lower()
    selected = set()
    for keyword, file_path in keyword_files.items():
        if keyword in lowered:
            selected.add(file_path)
    return sorted(selected)


selected_files = select_context(question)

## READ SELECTED FILES and add their contents to the context variable.
context = ""

for file_path in selected_files:
    context += Path(file_path).read_text()
    context += "\n\n"


## 
## COMPRESS CONTEXT
## Add logic to compress the context from above by calling Qwen with "context" and the "question" as the parameter
## The response from Qwen should be the compressed context. Store it in a variable called "compressed_context" 

def compress_context(context, question):
    response = chat(
        model="qwen3:8b",
        messages=[
            {
                "role": "user",
                "content": (
                    "Compress the following context so that it only contains "
                    "the information relevant to the question.\n\n"
                    f"Question:\n{question}\n\n"
                    f"Context:\n{context}"
                ),
            },
        ],
    )
    return response.message.content


compressed_context = compress_context(context, question)

## Print the length of the compressed context
print(len(compressed_context))

## Now, call Qwen again with the compressed context and the student's question. Store the response in a variable called "response" and print the response from Qwen.
## Ensure the model produces a structured output 
response = chat(
    model="qwen3:8b",
    messages=[
        {
            "role": "user",
            "content": (
                f"Context:\n{compressed_context}\n\n"
                f"Student question:\n{question}\n\n"
                "Respond with JSON containing the keys 'diagnosis' and 'recommended_steps'."
            ),
        },
    ],
    format="json",
)




print(response.message.content)

## WRITE the above output in an artifact called "state"
state["diagnosis"] = json.loads(response.message.content)

with open("state.json", "w") as file:
    json.dump(
        state,
        file,
        indent=2
    )

## Update the rest of the code so that it uses the "state" artifact as part of the context. 
## It is important to ensure that the model uses only the relevant parts from the "state" artifact and not the entire artifact.
## For this, you may have to think of a good structure for the "state" artifact and how to use it in the context.
with open("state.json", "r") as file:
    state = json.load(file)

relevant_context = {
    "problem": state["problem"],
    "wi_fi status": state["wi_fi status"],
    "diagnosis": state["diagnosis"],
}

response = chat(
    model="qwen3:8b",
    messages=[
        {
            "role": "user",
            "content": (
                f"Context:\n{json.dumps(relevant_context, indent=2)}\n\n"
                f"Student question:\n{question}\n\n"
                "Give the student the final answer using only the relevant parts of the context."
            ),
        },
    ],
)

print(response.message.content)
