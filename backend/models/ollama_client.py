import os
import json
import time
import urllib.request
import urllib.error
from typing import Generator

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")
ENABLE_MOCK_FALLBACK = os.getenv("ENABLE_MOCK_FALLBACK", "true").lower() == "true"

class OllamaClient:
    def __init__(self, base_url: str = None, default_model: str = None):
        # Read from environment directly to ensure latest config is picked up
        self.base_url = (base_url or os.getenv("OLLAMA_BASE_URL", OLLAMA_BASE_URL)).rstrip("/")
        self.default_model = default_model or os.getenv("OLLAMA_MODEL", OLLAMA_MODEL)

    def check_connection(self) -> bool:
        """
        Checks if Ollama is running and accessible using built-in urllib.
        """
        try:
            url = f"{self.base_url}/api/tags"
            # Set a low timeout to fail fast
            with urllib.request.urlopen(url, timeout=1.0) as response:
                if response.status == 200:
                    return True
        except Exception:
            pass
        return False

    def generate_stream(
        self,
        prompt: str,
        system_prompt: str,
        agent_type: str = "ba",
        user_idea: str = "",
        industry: str = ""
    ) -> Generator[str, None, None]:
        """
        Streams responses from local Ollama or falls back to mock simulation.
        """
        if self.check_connection():
            try:
                url = f"{self.base_url}/api/generate"
                payload = {
                    "model": self.default_model,
                    "prompt": prompt,
                    "system": system_prompt,
                    "stream": True,
                    "options": {
                        "temperature": 0.7
                    }
                }
                
                req = urllib.request.Request(
                    url,
                    data=json.dumps(payload).encode('utf-8'),
                    headers={'Content-Type': 'application/json'},
                    method='POST'
                )
                
                with urllib.request.urlopen(req, timeout=30.0) as response:
                    for line in response:
                        if not line:
                            continue
                        try:
                            data = json.loads(line.decode('utf-8'))
                            chunk = data.get("response", "")
                            if chunk:
                                yield chunk
                        except json.JSONDecodeError:
                            continue
                return  # Success
            except Exception as e:
                print(f"Ollama stream error: {e}. Falling back to mock generator...")

        # Fallback to simulated high-quality product metrics
        global ENABLE_MOCK_FALLBACK
        enable_mock = os.getenv("ENABLE_MOCK_FALLBACK", "true").lower() == "true"
        if enable_mock:
            for chunk in self._generate_mock_stream(agent_type, user_idea, industry):
                yield chunk
        else:
            raise RuntimeError("Ollama is offline and mock fallback is disabled.")

    def _generate_mock_stream(self, agent_type: str, user_idea: str, industry: str) -> Generator[str, None, None]:
        """
        Simulates high-quality, product-specific agent outputs for the frontend.
        """
        idea = user_idea or "Selected Product Idea"
        ind = industry or "General Tech"

        if agent_type == "ba":
            mock_data = self._get_mock_ba(idea, ind)
        elif agent_type == "pm":
            mock_data = self._get_mock_pm(idea, ind)
        elif agent_type == "qa":
            mock_data = self._get_mock_qa(idea, ind)
        else:
            mock_data = self._get_mock_syn(idea, ind)

        words = mock_data.split(" ")
        chunk_size = 3
        for i in range(0, len(words), chunk_size):
            chunk = " ".join(words[i:i+chunk_size]) + " "
            yield chunk
            # Typing animation speed control
            time.sleep(0.015)

    def _get_mock_ba(self, idea: str, industry: str) -> str:
        data = {
            "problem_statement": {
                "pain_point": f"Users face severe inefficiencies when trying to solve tasks related to {idea}. The current landscape lacks real-time automation and relies on fragmented, manual tooling.",
                "target_audience": f"Professionals, developers, and enterprises operating in the {industry} sector who require seamless coordination and data processing.",
                "current_workarounds": "Manual tracking using Excel spreadsheets, disjointed chat apps, and legacy systems that require constant context-switching."
            },
            "market_size": {
                "tam": "$15 Billion. Calculated as the global addressable spend of enterprises adopting digital transformation tools.",
                "sam": "$4.5 Billion. Representing the target segment of mid-market to enterprise companies in the region.",
                "som": "$250 Million. The realistic target share within the first 3 years of launching our optimized solution."
            },
            "success_metrics": [
                {
                    "metric": "User Retention Rate (D30)",
                    "target": "> 45%",
                    "justification": "Ensures the solution creates high daily utility and sticky habits for professionals."
                },
                {
                    "metric": "Task Completion Velocity",
                    "target": "3x reduction in time",
                    "justification": "Demonstrates clear efficiency gains over legacy manual workarounds."
                },
                {
                    "metric": "Net Promoter Score (NPS)",
                    "target": "> 60",
                    "justification": "Indicates high user satisfaction and organic viral loops."
                }
            ],
            "competitors": [
                {
                    "name": "LegacyCorp Solutions",
                    "strengths": ["Deep market penetration", "Robust offline infrastructure"],
                    "weaknesses": ["Extremely high licensing costs", "Outdated mobile UI/UX", "No AI integrations"]
                },
                {
                    "name": "ModernSync Inc",
                    "strengths": ["Clean modern design", "Fast sync speeds"],
                    "weaknesses": ["Lacks custom integrations", "Poor scalability for enterprise clients"]
                }
            ],
            "revenue_model": {
                "model_type": "B2B SaaS / Tiered Subscription",
                "pricing_strategy": "Starter: $15/user/month (basic features), Growth: $49/user/month (advanced automations, history), Enterprise: Custom (SLA, dedicated support)."
            },
            "key_assumptions": [
                "Target users are willing to connect their local work data to a secure cloud platform.",
                "FastAPI and local/hybrid AI models can process client requests in under 2 seconds.",
                "The industry is seeing an active shift toward AI-assisted productivity platforms."
            ]
        }
        return json.dumps(data, indent=2)

    def _get_mock_pm(self, idea: str, industry: str) -> str:
        return f"""# Product Requirements Document (PRD) Draft: {idea}

## 1. User Personas

### Persona 1: Alex the High-Performer
- **Demographics**: 32 years old, Lead Project Coordinator at a mid-sized firm.
- **Goals**: Automate status reports, eliminate manual tracking, save 5+ hours weekly.
- **Frustrations**: Tired of writing updates, copy-pasting spreadsheet data.
- **Tech Comfort**: High. Uses multiple SaaS tools daily.

### Persona 2: Sam the Operational Manager
- **Demographics**: 45 years old, Operations Lead.
- **Goals**: Streamline team workflows, view real-time pipeline performance metrics.
- **Frustrations**: Fragmented communication, out-of-date status reporting.
- **Tech Comfort**: Medium. Prefers simple, consolidated dashboards.

### Persona 3: Jordan the Independent Contractor
- **Demographics**: 28 years old, Freelance Developer.
- **Goals**: Manage multiple clients, create automated specs without overhead.
- **Frustrations**: Unclear scopes from clients, excessive time spent on administrative overhead.
- **Tech Comfort**: Very High. Active terminal and API user.

## 2. User Stories
*MoSCoW Prioritized*

### Must Have:
1. **US-101**: As a team coordinator, I want to type a raw idea and generate a structured outline, so that I don't start with a blank page.
2. **US-102**: As an operations manager, I want real-time streaming updates, so that I can see the system working immediately.
3. **US-103**: As a contractor, I want to download my generated document, so that I can share it with external partners.
4. **US-104**: As a user, I want a secure history tab, so that I can retrieve past generations without starting over.

### Should Have:
5. **US-105**: As a coordinator, I want to see a visual diagram of the AI process, so that I understand which agent is active.
6. **US-106**: As an editor, I want my output rendered in beautiful markdown, so that I can easily scan headers and bullet points.
7. **US-107**: As a manager, I want to export my PRD to PDF directly, so that I can print or present it at board meetings.

### Could Have:
8. **US-108**: As a developer, I want a voice input option, so that I can dictate product ideas on my mobile device.
9. **US-109**: As an international user, I want multi-language generation, so that I can support localized teams.

### Won't Have (For MVP):
10. **US-110**: Real-time collaborative editing in a shared canvas by multiple active web clients.

## 3. Functional Requirements

| ID | Description | Acceptance Criteria |
|---|---|---|
| **FR-001** | Prompt Input Handling | Accept text inputs up to 1000 characters. Validate inputs against injection. |
| **FR-002** | Multi-Agent Generation | Process prompt through 4-stage pipeline sequentially (BA -> PM -> QA -> Synthesis). |
| **FR-003** | SSE Streaming | Stream outputs token-by-token. Support visual step status transitions. |
| **FR-004** | Document Caching | Save generated drafts and finals in ChromaDB indexed by project ID. |
| **FR-005** | Markdown Rendering | Correctly parse Markdown, rendering headers, tables, lists, and bold text. |
| **FR-006** | Export Actions | Download as `.md` file. Format print layouts for clean browser PDF export. |
| **FR-007** | Pipeline Interruption | Support cancellation of active generations via backend API connections. |
| **FR-008** | Local Vector Storage | Store and query metadata tags. Retrieve history by prompt content. |

## 4. Non-Functional Requirements
- **Performance**: SSE stream connection must establish in < 500ms. Response tokens must stream at > 15 tokens/sec.
- **Security**: Prompt input sanitization. Secure database connection. SQLite vector storage encrypted on rest.
- **Scalability**: Backend must run in multi-threaded loop to handle concurrent sessions.
- **Accessibility**: WCAG 2.1 AA compliant. High contrast mode. Screen-reader friendly DOM structure.

## 5. UI/UX Notes
- **Key Screens**: 
  1. Main Dashboard: Input panel + visual flow pipeline map.
  2. Tabbed Results Pane: Switching between Active streaming panels (Analysis, Draft, QA, Final PRD).
  3. History Drawer: Left-aligned collapsible sidebar showing stored sessions.
- **Design Principles**: Dark tech-minimalist theme. Neon active-glow accents. Clear glassmorphism panels. Responsive grid scaling down to mobile viewports.
"""

    def _get_mock_qa(self, idea: str, industry: str) -> str:
        return f"""# QA Critic Report: Critical Evaluation for {idea}

## 1. Logical Gaps
- **Gap 1: Missing Core API Definitions**: The PRD draft mentions "database integration" and "sync actions" but does not define the format of the payloads or what database engines are officially supported.
- **Gap 2: History Conflict Behavior**: When a user retrieves a past document from ChromaDB and runs a new generation, there is no explanation of whether the previous entry is overwritten or versioned.
- **Gap 3: Token Limit Overflow**: For very complex prompts, the PM prompt does not detail how the agent prevents exceeding Ollama context limits.

## 2. Technical Risks
- **Risk 1: Vector Store Scaling (ChromaDB)**: In-memory ChromaDB databases will leak memory and lose history on restart. Persistent storage paths must be explicitly configured to prevent total data loss.
- **Risk 2: SSE Network Timeouts**: Web browsers will automatically drop and retry EventSource connections that stay idle for too long without keep-alive pings.

## 3. Missing Requirements
- **Missing Requirement 1**: Active cancellation mechanism. A user clicking "Stop" must notify the backend to cancel the active LLM process, otherwise resources are wasted.
- **Missing Requirement 2**: Session recovery on network failure. If connection drops, the frontend should be able to reconnect to the active backend session using the unique session ID.

## 4. Section Ratings

| Section | Rating (1-10) | Justification |
|---|---|---|
| User Personas | 8/10 | Well-developed and covers all main profiles, but could include more metrics on tech comfort. |
| User Stories | 9/10 | Excellent MoSCoW prioritization, highly detailed. |
| Functional Specs | 6/10 | Contains core criteria, but lacks clear error-handling scenarios. |
| Non-Functional Specs | 7/10 | Good SLA metrics, but security parameters are too generic. |
| UI/UX Notes | 8/10 | Clean structure, matches modern theme guidelines. |

## 5. Priority Fixes
1. Configure ChromaDB to use **persistent directory storage** instead of volatile in-memory storage.
2. Implement an **SSE Keep-Alive Heartbeat** (pings every 15 seconds) to prevent browser-side client timeouts.
3. Explicitly document **version controls** for past generations when re-triggering prompt runs.
"""

    def _get_mock_syn(self, idea: str, industry: str) -> str:
        return f"""# Final Product Requirements Document: {idea}

## Executive Summary
- **Vision**: Establish the premier automation platform for {idea} within the {industry} space, utilizing an advanced multi-agent orchestrator.
- **Target Audience**: Mid-market operations leads and freelance professionals looking to save 5+ hours weekly by automating administrative tasks.
- **Strategic Impact**: Eliminate fragmented tool ecosystems and provide a single, offline-first dashboard that operates with zero API costs using local AI models.

---

## 1. Detailed User Personas

### Persona 1: Alex the High-Performer
- **Profile**: 32 years old, Lead Project Coordinator.
- **Goals**: Automate status reports, eliminate manual tracking, save 5+ hours weekly.
- **Frustrations**: Tired of writing updates, copy-pasting spreadsheet data.
- **Tech Comfort**: High. Uses multiple SaaS tools daily.

### Persona 2: Sam the Operational Manager
- **Profile**: 45 years old, Operations Lead.
- **Goals**: Streamline team workflows, view real-time pipeline performance metrics.
- **Frustrations**: Fragmented communication, out-of-date status reporting.
- **Tech Comfort**: Medium. Prefers simple, consolidated dashboards.

### Persona 3: Jordan the Independent Contractor
- **Profile**: 28 years old, Freelance Developer.
- **Goals**: Manage multiple clients, create automated specs without overhead.
- **Frustrations**: Unclear scopes from clients, excessive time spent on administrative overhead.
- **Tech Comfort**: Very High. Active terminal and API user.

---

## 2. Competitive Positioning
Our solution dominates the competitors identified by our market research:
- **Vs. LegacyCorp Solutions**: Our tool offers a sleek, glassmorphic UI, modern mobile support, and built-in local AI workflows. It avoids LegacyCorp's steep enterprise pricing by leveraging local Ollama installations.
- **Vs. ModernSync Inc**: Unlike ModernSync, which has a rigid data structure, our platform supports custom AI integrations, persistence via ChromaDB, and exports documents to Markdown/PDF out-of-the-box.

---

## 3. Prioritized User Stories

### Must-Have
- **US-101**: As a coordinator, I want to type a raw idea and generate a structured outline, so that I don't start with a blank page.
- **US-102**: As an operations manager, I want real-time streaming updates, so that I can see the system working immediately.
- **US-103**: As a contractor, I want to download my generated document, so that I can share it with external partners.
- **US-104**: As a user, I want a secure history tab, so that I can retrieve past generations without starting over.

### Should-Have
- **US-105**: As a coordinator, I want to see a visual diagram of the AI process, so that I understand which agent is active.
- **US-106**: As an editor, I want my output rendered in beautiful markdown, so that I can easily scan headers and bullet points.
- **US-107**: As a manager, I want to export my PRD to PDF directly, so that I can print or present it at board meetings.

### Could-Have & Stretch
- **US-108**: Voice Input integration using Web Speech API for dictation.
- **US-109**: Support for multi-language PRD translation (Hindi, Spanish, French).

---

## 4. Functional Requirements & QA Enhancements

| ID | Description | Acceptance Criteria |
|---|---|---|
| **FR-001** | Prompt Input Handling | Accept text inputs up to 1000 characters. Validate inputs against injection. |
| **FR-002** | Multi-Agent Generation | Process prompt through 4-stage pipeline sequentially (BA -> PM -> QA -> Synthesis). |
| **FR-003** | SSE Streaming | Stream outputs token-by-token. Support visual step status transitions. |
| **FR-004** | Document Versioning | Store all generations in ChromaDB. If prompt is re-run, append timestamp version tag (`v1.0`, `v1.1`) rather than overwriting. |
| **FR-005** | Markdown Rendering | Correctly parse Markdown, rendering headers, tables, lists, and bold text. |
| **FR-006** | Export Actions | Download as `.md` file. Format print layouts for clean browser PDF export. |
| **FR-007** | Pipeline Interruption | Allow user to cancel active streams, firing a cancellation hook to backend to release LLM threads. |
| **FR-008** | Persistent Storage | ChromaDB must write directly to local file directory (`backend/memory/chroma_db`) to guarantee data integrity across restarts. |

---

## 5. Risk Mitigation Plan

- **Risk 1: In-Memory Data Loss**: 
  - *Mitigation*: Configured ChromaDB to use the persistent client storing vectors on the disk under `backend/memory/chroma_db`.
- **Risk 2: SSE Network Timeout**:
  - *Mitigation*: Backend sends empty comments (`: keep-alive\\n\\n`) every 15 seconds to keep the connection alive in standard browsers.
- **Risk 3: Complex Prompt Processing**:
  - *Mitigation*: Agent prompts enforce role play and clear structural delimiters to prevent context leakage or formatting breakdown.

---

## 6. 3-Month MVP Roadmap

```
Phase 1: Foundation (Weeks 1-4)
├── W1: Setup FastAPI app and Ollama Client wrapper (with local mock fallbacks)
├── W2: Define prompt templates & agent modules (BA, PM, QA)
├── W3: Integrate local ChromaDB storage and persistence
└── W4: Deploy SSE endpoint and test streaming payloads

Phase 2: Core Features (Weeks 5-8)
├── W5: Build Lumina Nexus glassmorphic frontend structure
├── W6: Implement agent visualizer animations and status logs
├── W7: Integrate marked.js markdown parsing & tab switcher
└── W8: Create export controllers for Markdown/PDF

Phase 3: Integration & Testing (Weeks 9-12)
├── W9: Write automated testing scripts (verify_setup.py)
├── W10: Perform stress-tests on concurrent sessions
├── W11: Optimize rendering speeds and styling layout fixes
└── W12: Final release and documentation wrap-up
```

---

## 7. Stretch Goals (6-Month Plan)
1. **Side-by-Side Compare Mode**: Compare differences between two different ideas in a dual-column layout.
2. **Template Library**: Pre-built starting configurations for healthcare, SaaS, fintech, and game development.
3. **Voice Command Dictation**: Speak prompt inputs using browser audio streaming.
"""
