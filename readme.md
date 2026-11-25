# Lenovo LETS Presales RAG & Conversational Intake Agent

An intelligent, multi-turn technical presales assistant featuring a **Streamlit Web UI**, **Retrieval-Augmented Generation (RAG)**, and an **agentic intake workflow** built with Python and the Google GenAI SDK.

This project bridges traditional enterprise presales operations with modern applied AI—acting as a conversational alternative to rigid web request forms (such as Lenovo's *Ask LETS*).

---

## Business Context & Motivation

In high-volume enterprise hardware sales environments, technical presales teams receive thousands of unstructured requests annually. Common challenges include:
- Incomplete sizing inputs submitted by users, requiring manual back-and-forth communication.
- Repetitive lookups across complex hardware specs, configurations, and software licensing rules.
- Manual re-entry of request parameters into enterprise CRM platforms (e.g., Microsoft Dynamics 365).

This prototype addresses these challenges by acting as a front-line conversational agent that answers technical questions from grounded documentation, dynamically collects required CRM metadata, enforces business rules (e.g., missing Opportunity ID = Low priority), and provides a final review screen before dispatching structured JSON payloads.

---

## Architectural Workflow

```text
[ User Query / Chat Input (Streamlit UI) ]
                   │
                   ▼
┌──────────────────────────────────────────────┐
│        Local Knowledge Base (RAG)            │
│  - Parses thinksystem_portfolio.txt          │
│  - Parses approved topics_list.txt           │
└──────────────────────┬───────────────────────┘
                       │ Matched Facts & Context
                       ▼
┌──────────────────────────────────────────────┐
│           Gemini Agentic Runtime             │
│  - System Prompt Governance & Tone Rules     │
│  - Multi-Turn Conversation History           │
│  - Silent Topic/Subtopic Mapping             │
│  - Dynamic Slot-Filling (6 Required Fields)  │
└──────────────────────┬───────────────────────┘
                       │ Complete & Verified Data
                       ▼
┌──────────────────────────────────────────────┐
│             Review & Confirm State           │
│  - Presents structured summary to user       │
│  - Waits for explicit "yes" confirmation     │
└──────────────────────┬───────────────────────┘
                       │ User Confirmed ("yes")
                       ▼
┌──────────────────────────────────────────────┐
│          Backend Dispatch Action             │
│  - Appends record to local `tickets.json`    │
│  - Simulates Dynamics 365 / REST API handoff │
└──────────────────────────────────────────────┘
```

---

## Key Capabilities

1. **Conversational Front-End (Streamlit Web UI):**
   - Provides a clean, browser-based chat interface (`app.py`) for interactive user testing and demonstrations.
2. **Grounded Domain Knowledge (RAG):**
   - Retrieves relevant hardware specifications across Lenovo ThinkSystem rack servers, edge platforms, GPU/AI workload servers, and licensing rules strictly from local text files.
3. **Conversational Slot-Filling & State Retention:**
   - Guides users naturally through 6 core intake items (Requester, Country, Topic, Opp ID, Customer Name, Tech Details) without robotic interrogation.
4. **Smart Validation & Business Rules:**
   - Automatically enforces business logic—such as restricting requests missing an Opportunity ID to `Low` priority.
5. **Interactive Review & Confirm State:**
   - Summarizes all collected details back to the user before submission, supporting intelligent typo corrections or additions before hitting the CRM.
6. **Robust API Error Handling:**
   - Includes automatic retry blocks for temporary server-side high demand (503 errors).

---

## Tech Stack

- **Language:** Python 3.10+
- **Frontend / UI:** Streamlit
- **LLM Engine:** Google Gemini (`models/gemini-3.5-flash-lite`)
- **SDK:** `google-genai`
- **Data Exchange:** JSON (`tickets.json`)
- **Interface:** Web UI (`app.py`) & Command-Line Interface (`thinksystem_agent.py`)

---

## Project Structure

```text
presales-agent/
│
├── app.py                      # Streamlit web chat interface and runtime
├── thinksystem_agent.py        # Core CLI agent loop, RAG retrieval logic, and action handler
├── thinksystem_portfolio.txt   # Enterprise hardware and licensing knowledge base
├── topics_list.txt             # Approved backend product taxonomy reference
├── tickets.json                # Local JSON store simulating CRM submissions
├── .gitignore                  # Excludes virtual environments and sensitive keys
└── README.md                   # Project documentation
```

---

## Getting Started

### 1. Prerequisites
- Python installed on your machine
- A valid Gemini API key from Google AI Studio

### 2. Environment Setup
Navigate to your project folder in CMD:
```cmd
cd presales-agent
```

Set your API key in your terminal session:
```cmd
set GEMINI_API_KEY=your_api_key_here
```

Install the required libraries:
```cmd
pip install google-genai streamlit
```

### 3. Running the Web App
Launch the Streamlit web interface:
```cmd
python -m streamlit run app.py
```
*(This will automatically open the interactive chat app in your default browser).*

---

## Future Enhancements (Roadmap)

- [ ] **Semantic Vector Embeddings:** Replace keyword matching with vector embeddings (using `gemini-embedding-001` or ChromaDB) for semantic retrieval.
- [ ] **Native Function Calling:** Migrate from JSON prompting to native Gemini Tool / Function Calling definitions.
- [ ] **Direct API Integration:** Connect the output hook directly to the Microsoft Dynamics 365 Web API.