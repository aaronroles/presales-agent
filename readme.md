\# Enterprise Presales RAG \& Intake Agent



An intelligent, multi-turn technical presales assistant built with Python and the Google GenAI SDK. 



This project bridges traditional enterprise presales operations with modern applied AI. It combines \*\*Retrieval-Augmented Generation (RAG)\*\* across enterprise data centre hardware documentation with an \*\*agentic intake workflow\*\* that extracts sizing parameters and triggers downstream CRM actions.



\---



\## Business Context \& Motivation



In high-volume enterprise hardware sales environments (such as Lenovo ISG), technical presales teams receive thousands of unstructured requests annually from internal sales reps and channel partners. Common challenges include:

\- Incomplete sizing inputs submitted by users, requiring manual back-and-forth communication.

\- Repetitive lookups across complex hardware specs, configurations, and software licensing rules (e.g., VMware VCF core minimums).

\- Manual re-entry of request parameters into enterprise CRM platforms (e.g., Microsoft Dynamics 365).



This prototype addresses these challenges by acting as an intelligent front-line assistant that can simultaneously answer domain-specific technical questions from grounded documentation and guide users through structured intake.



\---



\## Architectural Workflow



```text

\[ User Query / Request ]

&#x20;          │

&#x20;          ▼

┌──────────────────────────────────────────────┐

│        Local Knowledge Base (RAG)            │

│  - Parses thinksystem\_portfolio.txt          │

│  - Scores relevance via keyword indexing     │

└──────────────────────┬───────────────────────┘

&#x20;                      │ Top Matched Chunks

&#x20;                      ▼

┌──────────────────────────────────────────────┐

│           Gemini Agentic Runtime             │

│  - System Prompt Governance                  │

│  - Multi-Turn Conversation Memory            │

│  - Grounded Technical Q\&A                    │

│  - Slot-Filling (Urgency, Hosts, Cores/CPU)  │

└──────────────────────┬───────────────────────┘

&#x20;                      │ Validated Parameters

&#x20;                      ▼

┌──────────────────────────────────────────────┐

│          Structured JSON Output              │

│  - Enforces schema: {urgency, hosts, cores}  │

└──────────────────────┬───────────────────────┘

&#x20;                      │

&#x20;                      ▼

┌──────────────────────────────────────────────┐

│          Backend Dispatch Action             │

│  - Executes Python function create\_ticket()  │

│  - Simulates Dynamics 365 / REST API handoff │

└──────────────────────────────────────────────┘

```



\---



\## Key Capabilities



1\. \*\*Grounded Domain Knowledge (RAG):\*\*

&#x20;  - Retrieves relevant hardware specifications across Lenovo ThinkSystem rack servers (V3 and next-gen V4 platforms), edge platforms, GPU/AI workload servers, and VMware VCF core licensing rules.

&#x20;  - Prevents hallucinations by instructing the model to rely strictly on retrieved reference chunks.



2\. \*\*Conversational Slot-Filling \& State Retention:\*\*

&#x20;  - Maintains conversation history across multi-turn exchanges.

&#x20;  - Automatically detects missing criteria needed to size and log a presales ticket:

&#x20;    - Request urgency

&#x20;    - Number of host nodes

&#x20;    - Cores per CPU

&#x20;  - Converses naturally in plain English, asking only for the missing parameters.



3\. \*\*Schema Enforcement \& Automated Action Handoff:\*\*

&#x20;  - Once all criteria are met, the agent breaks the conversational loop and produces a structured JSON payload.

&#x20;  - The Python runtime parses the JSON and executes a local function (`create\_ticket()`), simulating a production webhook or REST API payload delivery to systems like Microsoft Dynamics 365.



\---



\## Tech Stack



\- \*\*Language:\*\* Python 3.10+

\- \*\*LLM Engine:\*\* Google Gemini (`models/gemini-3.5-flash-lite`)

\- \*\*SDK:\*\* `google-genai`

\- \*\*Data Exchange:\*\* JSON

\- \*\*Interface:\*\* Command-Line Interface (CLI / CMD)



\---



\## Project Structure



```text

presales-agent/

│

├── thinksystem\_agent.py        # Core agent loop, RAG retrieval logic, and action handler

├── thinksystem\_portfolio.txt   # Structured enterprise hardware and licensing knowledge base

├── test\_agent.py               # Initial prototype for single-turn JSON schema validation

├── loop\_agent.py               # Base interactive multi-turn intake script

└── README.md                   # Project documentation

```



\---



\## Getting Started



\### 1. Prerequisites

\- Python installed on your machine

\- A valid Gemini API key from Google AI Studio



\### 2. Environment Setup

Clone or navigate to the repository folder:

```cmd

cd presales-agent

```



Set your API key in your terminal session:

```cmd

set GEMINI\_API\_KEY=your\_api\_key\_here

```



Install the required library:

```cmd

pip install google-genai

```



\### 3. Running the Agent

Execute the agent script:

```cmd

python thinksystem\_agent.py

```



\---



\## Example Interaction Transcript



```text

You: hello

Agent: Hello! I am your Lenovo ThinkSystem presales RAG agent. How can I help you with hardware or licensing today?



You: which server is best for enterprise AI workload?

Agent: The ThinkSystem SR650 V3 supports multiple GPUs, making it ideal for mid-size AI inference. Additionally, the ThinkSystem SR650 V4 is built for AI-ready infrastructure with upgraded PCIe Gen5 and Neptune cooling options.



You: need help with logging a ticket for a partner urgent quote.

Agent: I can help you log a ticket. What is the urgency level for this quote?



You: this is need before close of business today

Agent: Thank you. How many hosts are required?



You: need 4 hosts

Agent: Got it, 4 hosts. Finally, how many cores per CPU are needed?



You: 32c per cpu

Agent: Thank you. Your ticket has been logged with urgency set to 'before close of business today', 4 hosts, and 32 cores per CPU.



Sending to CRM -> {'urgency': 'before close of business today', 'hosts': 4, 'cores\_per\_cpu': 32}

```



\---



\## Future Enhancements (Roadmap)



\- \[ ] \*\*Semantic Vector Embeddings:\*\* Replace keyword matching with vector embeddings (using `gemini-embedding-001` or ChromaDB) for semantic retrieval.

\- \[ ] \*\*Native Function Calling:\*\* Migrate from JSON prompting to native Gemini Tool / Function Calling definitions.

\- \[ ] \*\*Direct API Integration:\*\* Connect the output hook directly to Microsoft Dynamics 365 Web API or local SQLite/MySQL database storage.

\- \[ ] \*\*Web Interface:\*\* Wrap the CLI script in a lightweight Streamlit or web UI for interactive demonstrations.

