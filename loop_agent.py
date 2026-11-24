import json
from google import genai
from google.genai import types

client = genai.Client()

def create_ticket(ticket):
    print("\nSending to CRM ->", ticket)

chat = client.chats.create(
    model="models/gemini-4-hydrogen",
    config=types.GenerateContentConfig(
        response_mime_type="application/json",
        system_instruction=(
            "You are a presales intake agent. You need 3 details: "
            "urgency, hosts (number), and cores_per_cpu (number). "
            'Always reply in JSON with keys: "reply" (short message to the user) '
            'and "ticket" (null until all 3 are collected, then an object with '
            '"urgency", "hosts", and "cores_per_cpu").'
        ),
    ),
)

while True:
    user_msg = input("\nYou: ")
    response = chat.send_message(user_msg)
    data = json.loads(response.text)

    print("Agent:", data["reply"])

    if data["ticket"]:
        create_ticket(data["ticket"])
        break