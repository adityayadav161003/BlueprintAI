from typing import Generator
from backend.agents import BaseAgent


class Synthesis(BaseAgent):
    def __init__(self):
        super().__init__("syn")

    def run(
        self,
        groq_client,
        ba_output: str,       # BUG FIX 1: ba_output was missing from run() entirely in old version
        pm_output: str,
        qa_output: str,
        user_idea: str,
        industry: str,
    ) -> Generator[str, None, None]:
        """
        Final editor — assembles all three agent outputs into the complete 12-section PRD.

        Bug fixes applied:
        1. ba_output param was missing from run() — Synthesis had no access to BA content
        2. Truncation limits were too aggressive (2000/2000/1200 chars) causing massive
           data loss. Raised to 4000/3500/2500 to preserve personas, FRs, and risk table.
        3. Mermaid template was hardcoded inside the prompt — LLM was copying the generic
           node labels instead of replacing them. Replaced with description-only instruction.
        4. Sections 1–5 were meta-instructions ("Synthesize from BA output") with no actual
           BA content in context. Now the full ba_trimmed block is injected and sections
           instruct the LLM to USE it, not imagine it.
        5. Old prompt told LLM to write 14 sections but only gave context for 9.
           Prompt now matches exactly what agent data covers.
        """

        # BUG FIX 2: Truncation limits raised significantly.
        # Old limits: ba=2000, pm=2000, qa=1200 → ~1300 tokens total, most content lost.
        # New limits: ba=4000, pm=3500, qa=2500 → ~2500 tokens, preserves key sections.
        # If you switch to a model with larger context (Llama 3.1 70B supports 131k),
        # remove the truncation entirely and pass raw outputs.
        ba_trimmed = ba_output[:12000] if len(ba_output) > 12000 else ba_output
        pm_trimmed = pm_output[:12000] if len(pm_output) > 12000 else pm_output
        qa_trimmed = qa_output[:10000] if len(qa_output) > 10000 else qa_output

        system_prompt = (
            f'You are the final editor producing the complete Product Requirements Document'
            f' for: "{user_idea}"\n\n'
            f'ABSOLUTE RULES — violate any and the document is rejected:\n'
            f'1. Every sentence is about "{user_idea}" specifically. Not a template.\n'
            f'2. Never write "[insert here]", "[describe feature]", or any placeholder. Write the actual content.\n'
            f'3. Never use fake competitor names. Only real companies that exist.\n'
            f'4. Never mention ChromaDB, SSE, Ollama, vector databases, or AI pipeline infrastructure.\n'
            f'5. Every KPI must have a real number — not "X%" or "TBD".\n'
            f'6. Every acceptance criterion must be testable with a yes/no answer.\n'
            f'7. Every section must have the content detailed, with all fields populated.\n'
            f'8. Write like a senior PM at a funded startup. Specific, confident, no buzzwords.\n'
            f'9. A new engineer joining the team must understand the full product from this document alone.\n\n'
            f'CONSISTENCY GATE — check before finalizing:\n'
            f'- Does every persona reflect a real user of "{user_idea}"?\n'
            f'- Are all competitor names real companies?\n'
            f'- Do all functional requirements describe features of "{user_idea}"?\n'
            f'- Do all KPIs have specific target numbers?'
        )

        prompt = (
            f'Write the complete, final Product Requirements Document for:\n\n'
            f'PRODUCT: {user_idea}\n'
            f'INDUSTRY: {industry}\n\n'
            f'You have three agent reports below. Read all three before writing a single word.\n'
            f'Every section of the PRD must be grounded in these reports — do not invent content.\n\n'
            f'{"=" * 60}\n'
            f'BUSINESS ANALYST REPORT\n'
            f'(Source for Executive Summary, Sections 1 and 2)\n'
            f'{"=" * 60}\n'
            f'{ba_trimmed}\n\n'
            f'{"=" * 60}\n'
            f'PRODUCT MANAGER REPORT\n'
            f'(Source for Sections 3, 4, 5, 6, 7, and 11)\n'
            f'{"=" * 60}\n'
            f'{pm_trimmed}\n\n'
            f'{"=" * 60}\n'
            f'QA CRITIC REPORT\n'
            f'(Source for Sections 8, 9, 10, 12, and the Appendix)\n'
            f'{"=" * 60}\n'
            f'{qa_trimmed}\n\n'
            f'{"=" * 60}\n'
            f'Now write the PRD. The exact layout must be followed. The document must contain exactly these headings and structures:\n'
            f'{"=" * 60}\n\n'
            f'# {user_idea}\n'
            f'## Product Requirements Document\n\n'
            f'**Version:** 1.0 | **Status:** Final | **Industry:** {industry}\n\n'
            f'---\n\n'
            f'## Executive Summary\n\n'
            f'Provide a high-level summary of the product blueprint using the following bullet points:\n'
            f'- **Product Vision:** [The long-term vision of this product]\n'
            f'- **Core Problem:** [The primary pain point or inefficiency in the market today]\n'
            f'- **Our Solution:** [How this product solves this problem uniquely]\n'
            f'- **Target Customer:** [The ideal user or customer segment]\n'
            f'- **Business Model:** [How this product will generate revenue]\n'
            f'- **MVP Launch Target:** [Timeline target for the MVP]\n'
            f'- **Success Definition:** [Core quantitative goals for launch]\n\n'
            f'---\n\n'
            f'## 1. Problem Statement & Opportunity\n\n'
            f'Write the problem statement and opportunity context using the BA report. Detail the specific problem, existing workarounds/competitors, market size, and timing.\n\n'
            f'---\n\n'
            f'## 2. Target User Personas\n\n'
            f'Include 3 complete user persona profiles matching the structure generated by the BA. For each persona, include details for:\n'
            f'- **Demographics**\n'
            f'- **Daily Workflow**\n'
            f'- **Pain Points**\n'
            f'- **Goals**\n'
            f'- **Tech Stack**\n'
            f'- **Budget Authority**\n'
            f'- **Success Metrics**\n'
            f'- **Quote**\n'
            f'- **Usage Pattern**\n\n'
            f'---\n\n'
            f'## 3. Prioritized User Stories\n\n'
            f'Include user stories prioritized using MoSCoW (Must-Have, Should-Have, Could-Have, Won\'t-Have) with Acceptance Criteria for each story, matching the PM report.\n\n'
            f'---\n\n'
            f'## 4. Functional Requirements\n\n'
            f'Include the functional requirements table from the PM report:\n'
            f'| ID | FEATURE | USER STORY REF | DETAILED DESCRIPTION | ACCEPTANCE CRITERIA | PRIORITY | EST. EFFORT |\n'
            f'|---|---|---|---|---|---|---|\n\n'
            f'---\n\n'
            f'## 5. Non-Functional Requirements\n\n'
            f'Include the following from the PM report:\n'
            f'- **Performance SLAs** (Table: METRIC, REQUIREMENT, MEASUREMENT METHOD)\n'
            f'- **Security & Compliance** (Table: REQUIREMENT, STANDARD, IMPLEMENTATION)\n'
            f'- **Scalability Plan** (Phased strategy for users and database growth)\n\n'
            f'---\n\n'
            f'## 6. Technical Architecture\n\n'
            f'Include the following from the PM report:\n'
            f'- **Recommended Tech Stack** (Table: LAYER, TECHNOLOGY, JUSTIFICATION)\n'
            f'- **System Architecture Overview** (Text description and ASCII or Mermaid diagram)\n'
            f'- **Data Model (Key Entities)** (Key database tables and fields)\n'
            f'- **API Design (Key Endpoints)** (Table: METHOD, ENDPOINT, DESCRIPTION, REQUEST BODY, RESPONSE)\n\n'
            f'---\n\n'
            f'## 7. UI/UX Specifications\n\n'
            f'Include the following from the PM report:\n'
            f'- **Screen Inventory** (List of core pages/screens)\n'
            f'- **Design System Requirements** (Typography, Color Palette, Spacing)\n'
            f'- **Critical User Flows** (Step-by-step description of top 2-3 interactive flows)\n\n'
            f'---\n\n'
            f'## 8. QA & Testing Strategy\n\n'
            f'Include the testing strategy and coverage details from the QA report (Unit, Integration, E2E, Performance, UAT).\n\n'
            f'---\n\n'
            f'## 9. Risk Register & Mitigation Plan\n\n'
            f'Include the risk register table from the QA report:\n'
            f'| RISK | CATEGORY | LIKELIHOOD | IMPACT | MITIGATION STRATEGY | OWNER |\n'
            f'|------|----------|------------|--------|---------------------|-------|\n\n'
            f'---\n\n'
            f'## 10. Project Build Plan & Roadmap\n\n'
            f'Include the project roadmap and team requirements from the QA report, including the week-by-week Month 1 targets.\n\n'
            f'---\n\n'
            f'## 11. Success Metrics & KPIs\n\n'
            f'Include the following from the PM report:\n'
            f'- **North Star Metric**\n'
            f'- **Metric Framework** (Table: METRIC, BASELINE, MONTH 1, MONTH 3, MONTH 6, MONTH 12)\n'
            f'- **Analytics Implementation** (Events to track, funnel definitions, dashboard)\n\n'
            f'---\n\n'
            f'## 12. Launch Checklist\n\n'
            f'Include the Pre-Launch, Launch Week, and Post-Launch checklists from the QA report.\n\n'
            f'---\n\n'
            f'## Appendix: Open Questions & Decisions Log\n\n'
            f'Include the open questions log table from the QA report:\n'
            f'| QUESTION | DECISION MADE | RATIONALE | DATE |\n'
            f'|----------|---------------|-----------|------|\n\n'
            f'---\n\n'
            f'*PRD Version 1.0 — {user_idea} | {industry} | Generated by BlueprintAI*'
        )

        for chunk in groq_client.generate_stream(
            prompt=prompt,
            system_prompt=system_prompt,
            agent_type="syn",
            user_idea=user_idea,
            industry=industry,
        ):
            yield chunk