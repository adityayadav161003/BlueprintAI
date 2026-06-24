from typing import Generator
from backend.agents import BaseAgent


class QACritic(BaseAgent):
    def __init__(self):
        super().__init__("qa")

    def run(self, groq_client, pm_output: str, user_idea: str, industry: str) -> Generator[str, None, None]:
        """
        Executes the QA Critic agent — Sections 10-12 of the PRD.
        """
        system_prompt = f"""You are a senior QA Engineer and Risk Analyst reviewing requirements for: "{user_idea}"

THE MOST CRITICAL RULE:
Every risk, assumption, and test case you identify must be specific to "{user_idea}" and its real-world context.

ABSOLUTE PROHIBITIONS:
- Never list SSE timeout, ChromaDB, or Ollama as risks — those are internal tool risks, not product risks
- Never list generic software project risks that apply to every product equally
- Never invent fake competitor names
- A dating app has trust and safety risks. A used laptop marketplace has fraud and counterfeit risks. A food delivery app has logistics risks. Write risks specific to THIS product category.

QUALITY GATE: For every risk, ask: "Could this exact risk appear unchanged in a PRD for a completely different type of product?" If yes, make it specific to {user_idea}."""

        prompt = f"""You are a senior QA Engineer and Risk Analyst. Review the PM output and produce the following sections. Everything must describe features of "{user_idea}" only.

PRODUCT: {user_idea}
INDUSTRY: {industry}

PM OUTPUT TO REVIEW:
{pm_output[:3500] if len(pm_output) > 3500 else pm_output}

---

## 11. Risk Register

Identify 5–8 risks that are SPECIFIC to "{user_idea}" and its operating context.

| Risk | Category | Likelihood (H/M/L) | Impact (H/M/L) | Mitigation Strategy |
|------|----------|--------------------|----------------|---------------------|

Risk categories to consider for this specific product:
- Market risks (competition timing, adoption barriers specific to this product)
- Technical risks (specific to what this product needs to do — real-time features, data sensitivity, scale)
- Legal/compliance risks (specific to this product's domain and geography)
- Operational/safety risks (trust, fraud, safety concerns specific to this product type)
- Financial risks (pricing model viability, unit economics specific to this business model)

Every risk must be something a founder building "{user_idea}" would genuinely worry about. No generic project management risks.

---

## 12. Open Questions & Assumptions

List 5–8 things currently unknown or assumed that could significantly affect the direction of "{user_idea}".

Format each as:
**[Assumption or Question]:** [Why it matters for this product specifically] → [How to resolve it — specific action, not "do research"]

Cover areas relevant to this product:
- User behavior assumptions that need validation with real users
- Business model decisions not yet finalized
- Regulatory or legal questions specific to this product's market
- Technical feasibility unknowns for the key features
- Partnership or integration dependencies this product relies on
- Safety or trust mechanisms that need further design

---

## 13. 3-Month MVP Roadmap

Define a phased roadmap for a small engineering team (2-4 developers) to build the Must-Have user stories and functional requirements.

| Phase | Weeks | Goal | Key Deliverables |
|-------|-------|------|------------------|

Provide a detailed week-by-week breakdown for Month 1:

| Week | Focus | Specific Deliverables | Done When |
|------|-------|-----------------------|-----------|

---

## 14. 6-Month Stretch Goals

List three specific expansion ideas for "{user_idea}" after the MVP is proven. Each must be a natural next step for THIS product type.

1. **[Expansion name]:** [What it is and why it fits this product after MVP]
2. **[Expansion name]:** [Same format]
3. **[Expansion name]:** [Same format]"""

        for chunk in groq_client.generate_stream(
            prompt=prompt,
            system_prompt=system_prompt,
            agent_type="qa",
            user_idea=user_idea,
            industry=industry
        ):
            yield chunk
