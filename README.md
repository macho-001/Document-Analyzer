📄 Document Analyzer
📌 Overview

Document Analyzer is an agentic system designed to analyze DOCX and PDF documents automatically. It checks formatting, validates diagrams, summarizes content, and extracts headings using a combination of tools orchestrated by an intelligent agent.

The system eliminates the need for manual document review by providing structured insights and actionable feedback.

🎯 Problem Statement

Manual document analysis is time-consuming and prone to errors. Common tasks like verifying format compliance, detecting missing diagrams, summarizing content, or extracting headings often require multiple tools and human intervention.

Document Analyzer automates these tasks, instantly providing users with a full summary and validation of their documents.

🚀 Key Features

📄 Upload DOCX or PDF documents for analysis

🧩 Format validation and suggestions for missing elements

🔍 Diagram detection and verification

📝 Document summarization

🏷️ Heading extraction and search

🤖 Intelligent agent selects the appropriate tools based on user queries

💡 Collapsible section to display agent reasoning and decision-making

⚡ In-memory temporary storage until the document is removed or browser is closed

📊 Streamed results for real-time feedback

📋 Prerequisites
Before you begin, ensure you have the following installed:

Python 3.9 or higher (tested on Python 3.9, 3.10, 3.11)
pip (Python package manager)
Git (for cloning the repository)
Ollama (for local LLM serving)
Minimum 4GB RAM (8GB recommended for larger documents)

Operating System Support

✅ Linux (Ubuntu 20.04+, Debian 10+)
✅ macOS (10.15+)
✅ Windows 10/11

🧠 How It Works

User uploads a document (DOCX or PDF)

Document is stored temporarily in memory

The agent interprets user queries and selects the correct tools:

summarizer_tool – generates summaries

diagram_checker – verifies diagrams

format_checker – validates document format

searching_headings – extracts and searches headings

Tools are executed and results are streamed back to the UI

Internal agent reasoning is displayed in a collapsible section

User interacts iteratively until they are satisfied or close the browser (which clears the temporary session)

🛠️ Tech Stack
Core Technologies

Python

Flask (Backend & API)

LangChain (LLM orchestration)

LangGraph (Agentic workflow orchestration)

In-memory storage (temporary document holding)

Agent Tools

summarizer.py – Summarizes document content

diagram_checker.py – Checks diagrams and validates them

format_checker.py – Verifies document format

heading_search.py – Searches and lists document headings

critic.py – Validates agent reasoning and prevents loops

🔄 Agent Flow
┌─────────────┐
│   START     │
└──────┬──────┘
       │
       v
┌─────────────────────┐
│  Reasoning Node     │ ← Decides next action
│  • run_tool         │
│  • ask_user         │
│  • go_to_critic     │
└──────┬──────────────┘
       │
       v
┌─────────────────────┐
│  Tool Node          │ ← Executes tools
│  • Reads decision   │
│  • Runs tool        │
│  • Updates state    │
└──────┬──────────────┘
       │
       v
┌─────────────────────┐
│  Critic Node        │ ← Validates & routes
│  • Check completion │
│  • Detect loops     │
│  • Validate outputs │
└──────┬──────────────┘
       │
   ┌───┴───┐
   │       │
   v       v
┌──────┐ ┌──────────────┐
│ User │ │ Continue?    │
│Input │ │ • Yes → Loop │
└──────┘ │ • No → END   │
         └──────────────┘

📂 Project Structure
app/
├── tools/
│   ├── critic.py
│   ├── diagram_checker.py
│   ├── format_checker.py
│   ├── heading_search.py
│   └── summarizer.py
├── memory/
│   └── conversation.py
├── state/
│   └── agent_state.py
├── agents/
│   ├── actions.py
│   ├── graph.py
│   └── reasonings.py
├── main.py
└── config.py
└── app.py


⚙️ Configuration
app = Flask(__name__, 
            static_folder='static',
            template_folder='templates')
app.secret_key = 'your-secret-key-here-change-in-production'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config.update(
    SESSION_PERMANENT=False,  # cookie expires on browser close
    SESSION_TYPE='filesystem' # or your preferred session type
)

📦 Installation

Clone the repository

git clone <repository-url>
cd document-analyzer


Install dependencies

pip install -r requirements.txt

▶️ Running the Application
python app.py


The application will be available at:

http://localhost:5000

🧑‍💻 Usage

Upload a DOCX or PDF document

Ask queries via the agent chatbot:

“Summarize this document”

“Which diagrams are present?”

“Is the format valid?”

Streamed results appear in real-time

Expand the collapsible reasoning section to see how the agent made decisions

Temporary document storage is cleared when the session ends or the browser closes

🎥 Demo Video

https://www.loom.com/share/25ea3be08f9a4770a9adbe0886bef780

📜 License

This project is provided under the MIT License:

MIT License

🙏 Acknowledgments

LangChain team for the orchestration framework
LangGraph team for agentic workflow capabilities
Flask community for the web framework
All contributors and testers

📞 Contact

Project Maintainer: Muhammad Ahmed
Email: ahmedmuhammad.a326@gmail.com
GitHub: @macho_001

