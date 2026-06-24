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

## 8. QA & Testing Strategy

Outline a targeted testing approach for "{user_idea}"'s core user flows:
* **Testing Types:** Brief strategy for Unit Testing, Integration Testing, E2E Testing, Performance Testing, and User Acceptance Testing (UAT) specific to this product.
* **Flow Coverage:** Detail test coverage targets (e.g. 80% coverage using Jest, 50% integration testing).

---

## 9. Risk Register & Mitigation Plan

Identify 3–5 risks that are SPECIFIC to "{user_idea}" and its operating context. Include owners for each mitigation.

| RISK | CATEGORY | LIKELIHOOD (High/Medium/Low) | IMPACT (High/Medium/Low) | MITIGATION STRATEGY | OWNER |
|------|----------|------------|--------|---------------------|-------|

---

## 10. Project Build Plan & Roadmap

Define a phased timeline for building the MVP:
* **Phased Roadmap:** Divide the plan into 4 clear phases (e.g. Phase 1: Foundation (W1-4), Phase 2: Core Features (W5-8), Phase 3: Beta & Polish (W9-12), Phase 4: Launch & Growth (W13-16)).
* **Week-by-Week Month 1:** List targets for Week 1, 2, 3, and 4.
* **Team Requirements:** List the suggested staff (e.g. 2 frontend developers, 2 backend developers, 1 QA engineer, 1 PM).

---

## 12. Launch Checklist

List specific tasks divided by launch timeline:
* **Pre-Launch (T-4 weeks):** Tasks like code freeze, user testing, and marketing setups.
* **Launch Week:** Deployment checks and live monitoring.
* **Post-Launch (Week 1-4):** Feedback gathering and analytics checks.

---

## Appendix: Open Questions & Decisions Log

List open questions or assumptions in a tabular log:

| QUESTION | DECISION MADE | RATIONALE | DATE |
|----------|---------------|-----------|------|"""

        for chunk in groq_client.generate_stream(
            prompt=prompt,
            system_prompt=system_prompt,
            agent_type="qa",
            user_idea=user_idea,
            industry=industry
        ):
            yield chunk
