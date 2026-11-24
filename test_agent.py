import json
from google import genai
from google.genai import types

client = genai.Client()

def create_ticket(data):
    # In real life, this is where you'd POST to a CRM API!
    print("Sending to CRM -> Topic:", data["topic"], "| Urgency:", data["urgency"])

response = client.models.generate_content(
    model="models/gemini-4-hydrogen",
    contents="Partner needs urgent VMware VCF help before Friday",
    config=types.GenerateContentConfig(
        response_mime_type="application/json",
        system_instruction=(
            'Reply in JSON with keys: "topic" (string) and '
            '"urgency" ("Low", "Medium", or "High").'
        ),
    ),
)

ticket_data = json.loads(response.text)
create_ticket(ticket_data)