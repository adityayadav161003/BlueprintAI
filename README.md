---
title: BlueprintAI
emoji: 🏗️
colorFrom: gray
colorTo: black
sdk: docker
app_port: 7860
pinned: false
---

# BlueprintAI — Premium Multi-Agent PRD Generator

BlueprintAI is a state-of-the-art, premium AI-powered software design tool that automates the generation of highly detailed Product Requirements Documents (PRDs). Built specifically for developers, product managers, and software architects, BlueprintAI simulates a full-cycle product design team using a multi-agent pipeline. 

The application features a gorgeous, high-contrast, premium monochrome (black-and-white) UI styled with elegant glassmorphism, micro-animations, and grain overlays, presenting a polished look that matches modern developer-focused platforms.

---

## 🚀 Key Features

*   **Sequential Multi-Agent Pipeline**: Simulates a collaborative product team consisting of a Business Analyst, Product Manager, QA Critic, and Synthesis Agent.
*   **Premium Monochrome Design**: High-contrast matte blacks, rich dark greys, crisp white accents, and subtle glowing feedback animations.
*   **Structured Technical Blueprints**: Mandates technical database schemas, endpoint routing trees, API contracts, MoSCoW features, and structured directory layouts in the final PRD.
*   **Live Stream Visualizer**: Real-time streaming status of agent processes (top-to-bottom pipeline progress) using Server-Sent Events (SSE).
*   **Local Session History**: Fully local persistence of generated documents in a collapsible sidebar menu.
*   **Markdown & PDF Export**: Instant downloads of generated PRDs styled with clean formatting for sharing or presentation.
*   **Flexible Model Fallbacks**: Fully integrated with high-speed Groq API endpoints (`llama-3.3-70b-versatile`) while supporting automated local Ollama connection checks and simulated mock generation fallbacks for offline testing.

---

## 🏗️ Project Architecture

```
BlueprintAI/
├── 📁 backend/
│   ├── main.py                     ← Threading HTTP & API server with SSE support
│   ├── .env                        ← Local credentials & configurations (ignored in git)
│   ├── requirements.txt            ← Minimal backend dependencies
│   ├── 📁 agents/                  ← Agentic logic & prompting layers
│   │   ├── __init__.py
│   │   ├── business_analyst.py     ← BA Agent: Market size & competitor matrices
│   │   ├── product_manager.py      ← PM Agent: High-level requirements draft
│   │   ├── qa_critic.py            ← QA Agent: Gap finder & risk critic
│   │   └── synthesis.py            ← Synthesis Agent: Combines PM draft + QA corrections
│   ├── 📁 models/                  ← Model connections
│   │   ├── groq_client.py          ← Groq API wrapper (supports streaming)
│   │   └── ollama_client.py        ← Ollama API wrapper
│   ├── 📁 memory/                  ← Session & local vector/history store
│   │   └── conversation_store.py   ← History management & JSON store
│   └── 📁 prompts/                 ← Isolated text prompts for individual agents
│       ├── ba_prompt.txt
│       ├── pm_prompt.txt
│       ├── qa_prompt.txt
│       └── syn_prompt.txt
│
├── 📁 frontend/                    ← Modern, high-performance web interface
│   ├── index.html                  ← 3-Page Website (Landing -> App -> Docs)
│   ├── 📁 css/
│   │   ├── landing.css             ← Premium black & white homepage styling
│   │   └── lumina-theme.css        ← Main workspace theme stylesheet
│   └── 📁 js/
│       ├── landing.js              ← Homepage visual transitions & navigation
│       ├── app.js                  ← Main workspace event controller
│       ├── agent-visualizer.js     ← Animated top-to-bottom agent nodes
│       ├── markdown-renderer.js    ← Rich text renderer for raw agent streams
│       └── export-handler.js       ← PDF & markdown download handlers
│
└── 📁 docs/                        ← Explanatory guides & developer resources
    ├── prompt-design.md            ← Guide to Prompting Engineering patterns
    └── evaluation-rubric.md        ← Checklist for evaluating PRD quality
```

---

## 🛠️ Step-by-Step Installation & Setup

Follow these instructions to run BlueprintAI locally.

### 1. Clone & Set Up Directory
Navigate to the project root directory.

### 2. Configure Environment
1. In the `backend/` directory, create a `.env` file (or copy the template).
2. Add your Groq API key:
   ```env
   GROQ_API_KEY=gsk_your_groq_api_key_here
   ENABLE_MOCK_FALLBACK=true
   ```
   *Note: If `ENABLE_MOCK_FALLBACK` is `true`, BlueprintAI will run even without an active Groq API key by providing high-quality simulated multi-agent outputs.*

### 3. Install Python Dependencies
Create a virtual environment and install the required libraries:
```bash
cd backend
python -m venv .venv

# Activate on Windows:
.venv\Scripts\activate

# Activate on macOS/Linux:
source .venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### 4. Run the Server
Launch the backend server:
```bash
python main.py
```
The server runs on **`http://localhost:8000`**.

### 5. Launch the UI
Open your web browser and navigate to:
👉 **[http://localhost:8000](http://localhost:8000)**

Explore the multi-page marketing homepage, click **Get Started**, enter your product idea, and watch the collaborative agent pipeline build your technical architecture.
