import json, os, re, time
from google import genai
from google.genai import types
from google.genai.errors import ServerError

client = genai.Client()

# Load RAG Portfolio
with open("thinksystem_portfolio.txt", encoding="utf-8") as f:
    CHUNKS = [c.strip() for c in f.read().split("\n\n") if c.strip()]

# Load Approved Backend Topics
with open("topics_list.txt", encoding="utf-8") as f:
    TOPICS_LIST = f.read().strip()

def search_faq(query):
    words = [w for w in re.findall(r"\w+", query.lower()) if len(w) > 1]
    scored = [(sum(w in c.lower() for w in words), c) for c in CHUNKS]
    top = [c for s, c in sorted(scored, key=lambda x: x[0], reverse=True) if s > 0][:3]
    return "\n\n".join(top) if top else "None"

def create_ticket(ticket):
    tickets = []
    if os.path.exists("tickets.json"):
        with open("tickets.json", encoding="utf-8") as f:
            tickets = json.load(f)
    tickets.append(ticket)
    with open("tickets.json", "w", encoding="utf-8") as f:
        json.dump(tickets, f, indent=2)
    print("\n[SUCCESS] Ticket saved to tickets.json ->", ticket)

chat = client.chats.create(
    model="models/gemini-3.5-flash-lite",
    config=types.GenerateContentConfig(
        response_mime_type="application/json",
        system_instruction=(
            "You are a Lenovo LETS conversational presales intake agent. Your goal is to collect 6 items through natural conversation: "
            "1) Requester Name & Email, 2) Country/Geo, 3) Topic Area, 4) Opportunity ID, 5) Customer Name (optional), and 6) Technical Details/Requirements.\n\n"
            f"APPROVED BACKEND TOPICS & SUBTOPICS REFERENCE:\n{TOPICS_LIST}\n\n"
            "CRITICAL CONVERSATION & CLASSIFICATION RULES:\n"
            "- Never interrogate the user or ask for multiple things upfront. Open the first message with a simple greeting: 'Hello, how can I help you today?'\n"
            "- STRICT RULE: Never list categories, menus, or options to the user, and never ask the user to 'choose' a topic. You must silently deduce the correct topic and subtopic from their natural description using the reference list.\n"
            "- Once all required info is gathered, set 'status' to 'review', and present a clear summary back to the user, asking: 'Do these details look correct? Reply yes to submit or let me know if anything needs changing.'\n"
            "- INTELLIGENT CORRECTIONS: During the review state, if the user asks to change or update a field, analyze their intent: if they say 'add' or 'also include', keep existing values and append the new ones. If they say 'replace' or state a direct correction, update appropriately.\n"
            "- Maintain a professional, direct, and concise technical tone. No overly cheerful filler.\n\n"
            "BEHIND THE SCENES PROCESSING: Silently generate a clean, one-line 'title' and a detailed factual 'description' (summarizing background and requirements without suggesting solutions) for the final JSON payload.\n"
            "BUSINESS RULE: If no Opportunity ID is provided, priority MUST be set to 'Low'.\n"
            "Always reply in JSON with keys: 'reply' (professional response), 'status' ('collecting', 'review', or 'submitted'), "
            "and 'ticket' (null while collecting, but a full JSON dictionary including title, description, requester_name, requester_email, country, topic, subtopic, opportunity_id, priority, customer_name when status is review or submitted)."
        ),
    ),
)

while True:
    user_msg = input("\nYou: ")
    facts = search_faq(user_msg)
    prompt = f"REFERENCE FACTS:\n{facts}\n\nUSER MESSAGE:\n{user_msg}"

    # Auto-retry block for temporary 503 high demand errors
    response_text = None
    for attempt in range(3):
        try:
            response_text = chat.send_message(prompt).text
            break
        except ServerError as e:
            if "503" in str(e) and attempt < 2:
                print("[API busy, retrying in 2 seconds...]")
                time.sleep(2)
            else:
                raise e

    data = json.loads(response_text)
    print("Agent:", data["reply"])

    if data.get("status") == "submitted":
        create_ticket(data["ticket"])
        break