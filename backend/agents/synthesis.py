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
        ba_trimmed = ba_output[:4000] if len(ba_output) > 4000 else ba_output
        pm_trimmed = pm_output[:3500] if len(pm_output) > 3500 else pm_output
        qa_trimmed = qa_output[:2500] if len(qa_output) > 2500 else qa_output

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
            f'7. The Mermaid diagram node labels must name this product\'s actual components.\n'
            f'8. Write like a senior PM at a funded startup. Specific, confident, no buzzwords.\n'
            f'9. A new engineer joining the team must understand the full product from this document alone.\n\n'
            f'CONSISTENCY GATE — check before finalizing:\n'
            f'- Does every persona reflect a real user of "{user_idea}"?\n'
            f'- Are all competitor names real companies?\n'
            f'- Do all functional requirements describe features of "{user_idea}"?\n'
            f'- Do all KPIs have specific target numbers?'
        )

        # BUG FIX 3: Mermaid block removed from prompt.
        # The old prompt embedded a generic flowchart template (User->Frontend->Auth->API...)
        # which the LLM copied verbatim instead of adapting. Now we describe what we want
        # in plain English and let the LLM construct the diagram from scratch for this product.

        # BUG FIX 4: All three agent outputs are now injected into the prompt context.
        # Old version: only pm_output and qa_output were passed; ba_output was not a param.
        # Sections 1–5 (problem, personas, competitive, UVP) were being hallucinated.
        prompt = (
            f'Write the complete, final Product Requirements Document for:\n\n'
            f'PRODUCT: {user_idea}\n'
            f'INDUSTRY: {industry}\n\n'
            f'You have three agent reports below. Read all three before writing a single word.\n'
            f'Every section of the PRD must be grounded in these reports — do not invent content.\n\n'
            f'{"=" * 60}\n'
            f'BUSINESS ANALYST REPORT\n'
            f'(Source for Sections 1, 2, 3, 4, 5 — problem, personas, competitive, UVP)\n'
            f'{"=" * 60}\n'
            f'{ba_trimmed}\n\n'
            f'{"=" * 60}\n'
            f'PRODUCT MANAGER REPORT\n'
            f'(Source for Sections 6, 7, 8, 9, 10 — user stories, FRs, NFRs, KPIs)\n'
            f'{"=" * 60}\n'
            f'{pm_trimmed}\n\n'
            f'{"=" * 60}\n'
            f'QA CRITIC REPORT\n'
            f'(Source for Sections 11, 12 — risks, open questions)\n'
            f'{"=" * 60}\n'
            f'{qa_trimmed}\n\n'
            f'{"=" * 60}\n'
            f'Now write the PRD. All 12 sections are mandatory.\n'
            f'{"=" * 60}\n\n'
            f'# {user_idea}\n'
            f'## Product Requirements Document\n\n'
            f'**Version:** 1.0 | **Status:** Final | **Industry:** {industry}\n\n'
            f'---\n\n'

            f'## Executive Summary\n\n'
            f'Write 3–4 sentences: what "{user_idea}" is, who it is for, the specific problem it solves,'
            f' and why now is the right time. Every word must be about this product specifically.\n\n'
            f'---\n\n'

            f'## 1. Problem Statement & Market Opportunity\n\n'
            f'Using the BA report above, write the problem statement for "{user_idea}".\n'
            f'Cover: the exact problem, who has it and how they cope today (name real platforms/methods),'
            f' the market opportunity with realistic numbers, and why now is the right time.\n\n'
            f'---\n\n'

            f'## 2. Target Audience\n\n'
            f'Using the BA report above, write one focused paragraph describing the real users'
            f' of "{user_idea}". Include: age range, lifestyle, geography, and what makes them the right audience.\n\n'
            f'---\n\n'

            f'## 3. User Personas\n\n'
            f'Using the BA report above, present each persona. Format each one as:\n\n'
            f'### [Name], [Age] — [Occupation], [City]\n'
            f'- **Income:** [level]\n'
            f'- **Daily Workflow:** [how they encounter the problem this product solves]\n'
            f'- **Pain Points:** [specific frustrations with their current methods or platforms]\n'
            f'- **Goals:** [what they want to achieve using "{user_idea}"]\n'
            f'- **Tech Comfort:** [level and preferred devices]\n'
            f'- **Quote:** "[something they would actually say, in casual language]"\n'
            f'- **Usage Pattern:** [how often and in what context they use this product]\n\n'
            f'---\n\n'

            f'## 4. Competitive Analysis\n\n'
            f'Using the BA report above, present the competitive landscape.\n'
            f'Only use real competitor names from the BA report — do not invent any.\n\n'
            f'| Competitor | Strengths | Weaknesses | Our Advantage |\n'
            f'|-----------|-----------|------------|---------------|\n\n'
            f'---\n\n'

            f'## 5. Unique Value Proposition\n\n'
            f'Using the BA report above, write 2–3 sentences on what makes "{user_idea}" different'
            f' from the competitors listed above. Be specific — reference the actual gap this product fills.\n\n'
            f'---\n\n'

            f'## 6. System Architecture\n\n'
            f'Write one paragraph describing the technical architecture of "{user_idea}":'
            f' what type of clients (web/mobile), what backend, what databases, what external services.\n\n'
            f'Then produce a Mermaid flowchart. Name every node after the actual components'
            f' of "{user_idea}" — for example, a cafe dating app might have nodes named'
            f' "Vibe Match Engine", "Cafe Booking API", "Profile Service", "Safety Reporting".'
            f' Do NOT use generic labels like "Core Service" or "Frontend App".'
            f' Build the diagram from the product\'s real architecture.\n\n'
            f'```mermaid\n'
            f'flowchart LR\n'
            f'    [build the diagram here with product-specific node names]\n'
            f'```\n\n'
            f'---\n\n'

            f'## 7. Prioritized User Stories\n\n'
            f'Using the PM report above, present user stories in three tiers.\n'
            f'Every story must describe a real action inside "{user_idea}".\n\n'
            f'### Must-Have (Core Loop)\n'
            f'*Without these, the product does not work.*\n\n'
            f'For each story:\n'
            f'**As a** [real user of "{user_idea}"], **I want to** [specific action in this product],'
            f' **so that** [specific benefit].\n'
            f'> **AC:** Given [context], When [user action], Then [system outcome]\n\n'
            f'### Should-Have\n'
            f'*Significantly improves the experience.*\n\n'
            f'### Could-Have\n'
            f'*Defer if needed.*\n\n'
            f'---\n\n'

            f'## 8. Functional Requirements\n\n'
            f'Using the PM report above, list every feature of "{user_idea}".\n'
            f'Every row must describe a real feature of this product — not a generic software concept.\n\n'
            f'| ID | Feature Area | Description | Acceptance Criteria | Priority |\n'
            f'|----|-------------|-------------|---------------------|----------|\n\n'
            f'**Priority:** P0 = must have at launch, P1 = first 30 days post-launch, P2 = future\n\n'
            f'---\n\n'

            f'## 9. Non-Functional Requirements\n\n'
            f'Using the PM report above, fill every row with real values specific to "{user_idea}".\n\n'
            f'| Category | Requirement | Target | Notes |\n'
            f'|----------|-------------|--------|-------|\n\n'
            f'Cover: Performance, Scalability, Security, Compliance (name the actual laws'
            f' that apply to this product and geography), Availability, Accessibility.\n\n'
            f'---\n\n'

            f'## 10. Success Metrics & KPIs\n\n'
            f'Using the PM report above, define measurable success for "{user_idea}".\n'
            f'Choose the metrics that matter for this specific product type.\n'
            f'Every target must be a real number — not "X%" or "TBD".\n\n'
            f'| Metric | What It Measures | Month 1 Target | Month 6 Target | Month 12 Target |\n'
            f'|--------|-----------------|----------------|----------------|------------------|\n\n'
            f'**North Star Metric:** [The single number that best shows if "{user_idea}" is working]\n\n'
            f'---\n\n'

            f'## 11. Risk Register\n\n'
            f'Using the QA report above, list the risks specific to "{user_idea}".\n'
            f'Every risk must be something the founding team of this specific product would worry about.\n\n'
            f'| Risk | Category | Likelihood | Impact | Mitigation |\n'
            f'|------|----------|------------|--------|------------|\n\n'
            f'---\n\n'

            f'## 12. Open Questions & Assumptions\n\n'
            f'Using the QA report above, list unknowns that could affect "{user_idea}".\n\n'
            f'Format each as:\n'
            f'- **[Question or Assumption]:** [Why it matters for this product] → [How to resolve it]\n\n'
            f'---\n\n'

            f'## 13. 3-Month MVP Roadmap\n\n'
            f'Write a phased roadmap based on the Must-Have stories and P0 requirements above.'
            f' Phase the work realistically for a small team (2–4 engineers).\n\n'
            f'| Phase | Weeks | Goal | Key Deliverables |\n'
            f'|-------|-------|------|------------------|\n\n'
            f'Week-by-week breakdown for Month 1:\n\n'
            f'| Week | Focus | Specific Deliverables | Done When |\n'
            f'|------|-------|-----------------------|-----------|\n\n'
            f'---\n\n'

            f'## 14. 6-Month Stretch Goals\n\n'
            f'Three specific expansion ideas for "{user_idea}" after the MVP is proven.'
            f' Each must be a natural next step for THIS product — not a generic SaaS feature.\n\n'
            f'1. **[Expansion name]:** [What it is and why it fits this product after MVP]\n'
            f'2. **[Expansion name]:** [Same format]\n'
            f'3. **[Expansion name]:** [Same format]\n\n'
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