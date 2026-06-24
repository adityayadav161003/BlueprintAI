from typing import Generator
from backend.agents import BaseAgent


class ProductManager(BaseAgent):
    def __init__(self):
        super().__init__("pm")

    def run(self, groq_client, ba_output: str, user_idea: str, industry: str) -> Generator[str, None, None]:
        """
        Executes the Product Manager agent — Sections 6-9 of the PRD.
        """
        system_prompt = f"""You are a senior Product Manager at a well-funded startup. You will translate user needs into precise product requirements for: "{user_idea}"

THE MOST CRITICAL RULE:
Everything you write must describe features and requirements of "{user_idea}" ONLY.

ABSOLUTE PROHIBITIONS:
- Never write user stories that could apply to a different product
- Never describe ChromaDB, SSE streaming, Ollama, vector databases, or any AI pipeline infrastructure as features of the user's product
- Never use placeholder competitor names
- Never write functional requirements for a generic SaaS template — write them for THIS specific product
- Never include stories like "generate a structured outline" unless the product literally is a document generator

QUALITY GATE: For every user story and functional requirement, ask: "Is this an action a real user of {user_idea} would actually perform?" If no, delete it."""

        prompt = f"""You are a senior Product Manager. You have received business context from the BA agent. Now translate user needs into precise product requirements for:

PRODUCT: {user_idea}
INDUSTRY: {industry}

BUSINESS CONTEXT FROM BA AGENT:
{ba_output[:3000] if len(ba_output) > 3000 else ba_output}

Produce the following sections. Everything must describe features of "{user_idea}" only.

---

## 3. Prioritized User Stories (MoSCoW)

Write 8–12 user stories prioritized using MoSCoW.
Every story must describe a real action inside "{user_idea}". Format each story as:
"**As a** [specific user type from personas], **I want to** [perform a specific action in "{user_idea}"], **so that** [specific benefit].
* **Acceptance Criteria:** Given [context], When [user action], Then [system outcome]."

Divide them into:
* **Must Have (Sprint 1-2):** Core loop features required for launch.
* **Should Have (Sprint 3-4):** Important but non-blocking features.
* **Could Have (Post-MVP):** Nice-to-have features or future ideas.
* **Won't Have (MVP Exclusions):** Excluded features with brief justification.

---

## 4. Functional Requirements

Produce a detailed table listing functional requirements for the core loops and flows.
The table must contain: ID, FEATURE, USER STORY REF (e.g., US-101), DETAILED DESCRIPTION, ACCEPTANCE CRITERIA, PRIORITY (High/Medium/Low), EST. EFFORT (e.g., 2 days).

| ID | FEATURE | USER STORY REF | DETAILED DESCRIPTION | ACCEPTANCE CRITERIA | PRIORITY | EST. EFFORT |
|---|---|---|---|---|---|---|

---

## 5. Non-Functional Requirements

Provide detailed requirements and standards under three specific subheadings:
* **Performance SLAs:** A table with columns (METRIC, REQUIREMENT, MEASUREMENT METHOD) detailing page load, search/processing times, and booking/transaction times.
* **Security & Compliance:** A table with columns (REQUIREMENT, STANDARD, IMPLEMENTATION) detailing encryption standard, authentication method, and data compliance strategy.
* **Scalability Plan:** A phased scaling strategy for users and database architecture (e.g. Phase 1: 0-1K users, Phase 2: 1K-10K users, Phase 3: 10K+ users).

---

## 6. Technical Architecture

Define the blueprint's technical layers and integration contracts:
* **Recommended Tech Stack:** A table detailing (LAYER, TECHNOLOGY, JUSTIFICATION) for Frontend, Backend, Database, Cache, Search, Auth, Hosting, and CI/CD.
* **System Architecture Overview:** Briefly describe the backend/client interactions and provide an ASCII text diagram or Mermaid diagram detailing the flow of request to database.
* **Data Model (Key Entities):** List key database tables and their fields (e.g., User, Booking, etc.).
* **API Design (Key Endpoints):** A table with columns (METHOD, ENDPOINT, DESCRIPTION, REQUEST BODY, RESPONSE) mapping the main routes of "{user_idea}".

---

## 7. UI/UX Specifications

Outline the interface rules:
* **Screen Inventory:** List the core pages/screens needed for this product.
* **Design System Requirements:** Define rules for Typography, Color Palette, and Spacing System.
* **Critical User Flows:** Explain the top 2-3 interactive flows step-by-step.

---

## 11. Success Metrics & KPIs

Define the metrics that matter most for this specific type of product:
* **North Star Metric:** The single most important measurement of success for "{user_idea}".
* **Metric Framework:** A table with columns (METRIC, BASELINE, MONTH 1, MONTH 3, MONTH 6, MONTH 12) detailing specific targets.
* **Analytics Implementation:** Outline events to track, funnel definitions, and dashboard requirements."""

        for chunk in groq_client.generate_stream(
            prompt=prompt,
            system_prompt=system_prompt,
            agent_type="pm",
            user_idea=user_idea,
            industry=industry
        ):
            yield chunk
