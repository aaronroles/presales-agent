import json
import os
import re
import time
import streamlit as st
from google import genai
from google.genai import types
from google.genai.errors import ServerError

# Page config
st.set_page_config(page_title="Lenovo LETS Presales Agent", page_icon="💻")
st.title("Lenovo LETS Presales Intake Agent")

# Load Knowledge Base
@st.cache_data
def load_data():
    with open("thinksystem_portfolio.txt", encoding="utf-8") as f:
        chunks = [c.strip() for c in f.read().split("\n\n") if c.strip()]
    with open("topics_list.txt", encoding="utf-8") as f:
        topics = f.read().strip()
    return chunks, topics

CHUNKS, TOPICS_LIST = load_data()

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

# System instruction definition
SYSTEM_INSTRUCTION = (
    "You are a Lenovo LETS conversational presales intake agent. Your goal is to collect 6 items through natural conversation: "
    "1) Requester Name & Email, 2) Country/Geo, 3) Topic & Subtopic Area, 4) Opportunity ID, 5) Customer Name (optional), and 6) Technical Details/Requirements.\n\n"
    f"APPROVED BACKEND TOPICS & SUBTOPICS REFERENCE:\n{TOPICS_LIST}\n\n"
    "CRITICAL CONVERSATION & CLASSIFICATION RULES:\n"
    "- Never interrogate the user or ask for multiple things upfront. Open the first message with a simple greeting: 'Hello, how can I help you today?'\n"
    "- STRICT RULE: Never list categories, menus, or options to the user, and never ask the user to 'choose' a topic. You must silently deduce the correct topic and subtopic from their natural description using the reference list.\n"
    "- Once all required info is gathered, set 'status' to 'review', and present a clear summary back to the user, asking: 'Do these details look correct? Reply yes to submit or let me know if anything needs changing.'\n"
    "- If the user confirms with 'yes', set 'status' to 'submitted'.\n"
    "- INTELLIGENT CORRECTIONS: During the review state, if the user asks to change or update a field, analyze their intent: if they say 'add' or 'also include', keep existing values and append the new ones. If they say 'replace' or state a direct correction, update appropriately.\n"
    "- Maintain a professional, direct, and concise technical tone. No overly cheerful filler.\n\n"
    "BEHIND THE SCENES PROCESSING: Silently generate a clean, one-line 'title' and a detailed factual 'description' (summarizing background and requirements without suggesting solutions) for the final JSON payload.\n"
    "BUSINESS RULE: If no Opportunity ID is provided, priority MUST be set to 'Low'.\n"
    "Always reply in JSON with keys: 'reply' (professional response), 'status' ('collecting', 'review', or 'submitted'), "
    "and 'ticket' (null while collecting, but a full JSON dictionary including title, description, requester_name, requester_email, country, topic, subtopic, opportunity_id, priority, customer_name when status is review or submitted)."
)

# Initialize messages list in session state
if "messages" not in st.session_state:
    st.session_state.messages = []
    
    # Prime with initial greeting using a fresh client
    client = genai.Client()
    init_chat = client.chats.create(
        model="models/gemini-3.5-flash-lite", 
        config=types.GenerateContentConfig(response_mime_type="application/json", system_instruction=SYSTEM_INSTRUCTION)
    )
    for attempt in range(3):
        try:
            init_resp = init_chat.send_message("Hello")
            init_data = json.loads(init_resp.text)
            st.session_state.messages.append({"role": "assistant", "content": init_data["reply"]})
            break
        except ServerError:
            if attempt < 2:
                time.sleep(2)
            else:
                st.session_state.messages.append({"role": "assistant", "content": "Hello, how can I help you today?"})

# Display chat history on rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if user_input := st.chat_input("Type your message here..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Build clean conversation history string directly from session state (1 single API call)
    conversation_history = ""
    for m in st.session_state.messages[:-1]: # exclude the brand new message since user_input has it
        role = "User" if m["role"] == "user" else "Agent"
        conversation_history += f"{role}: {m['content']}\n"

    facts = search_faq(user_input)
    prompt = f"REFERENCE FACTS:\n{facts}\n\nCONVERSATION HISTORY SO FAR:\n{conversation_history}\n\nCURRENT USER MESSAGE:\n{user_input}"
    
    response_text = None
    for attempt in range(3):
        try:
            client = genai.Client()
            chat = client.chats.create(
                model="models/gemini-3.5-flash-lite",
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    system_instruction=SYSTEM_INSTRUCTION
                ),
            )
            
            resp = chat.send_message(prompt)
            response_text = resp.text
            break
        except ServerError as e:
            if "503" in str(e) and attempt < 2:
                time.sleep(2)
            else:
                st.error("API is busy (503 error). Please try sending your message again in a moment.")
                st.stop()
        except Exception as e:
            if attempt < 2:
                time.sleep(1)
            else:
                st.error(f"Error: {e}")
                st.stop()

    data = json.loads(response_text)
    agent_reply = data["reply"]
    st.session_state.messages.append({"role": "assistant", "content": agent_reply})
    with st.chat_message("assistant"):
        st.markdown(agent_reply)

    # Check if submitted
    if data.get("status") == "submitted":
        create_ticket(data["ticket"])
        st.success("Ticket successfully submitted and saved to `tickets.json`!")
        st.balloons()