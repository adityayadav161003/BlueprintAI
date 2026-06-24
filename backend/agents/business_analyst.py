from typing import Generator
from backend.agents import BaseAgent


class BusinessAnalyst(BaseAgent):
    def __init__(self):
        super().__init__("ba")

    def run(self, groq_client, user_idea: str, industry: str) -> Generator[str, None, None]:
        """
        Executes the Business Analyst agent — Sections 1-5 of the PRD.
        """
        system_prompt = f"""You are a world-class product strategist and senior Business Analyst.

THE MOST CRITICAL RULE:
Every single section you generate must be 100% grounded in the user's product: "{user_idea}"

You are NOT generating analysis for a generic product. You are generating analysis for the EXACT product described above.

ABSOLUTE PROHIBITIONS:
- Never use placeholder competitor names like "LegacyCorp" or "ModernSync"
- Never generate generic personas that could apply to any product
- Never write sentences that could apply unchanged to a different product
- Never describe ChromaDB, SSE streaming, Ollama, or any AI pipeline infrastructure
- Never produce output that would be identical regardless of the product input

QUALITY GATE: Before writing each section, ask yourself: "Could this sentence appear unchanged in a PRD for a completely different product?" If yes, rewrite it until it cannot."""

        prompt = f"""You are a senior Business Analyst. Deeply research and define the business context for this product:

PRODUCT: {user_idea}
INDUSTRY: {industry}

Produce the following sections. Every section must be entirely specific to "{user_idea}". If you find yourself writing something that could apply to a different product, stop and rewrite it.

---

## Executive Summary

Write 3–4 sentences summarizing what "{user_idea}" is, who it is for, the specific problem it solves, and why now is the right time.

---

## 1. Problem Statement & Market Opportunity

Answer all of the following specifically for "{user_idea}":
- What specific problem does this product solve? Describe it in concrete terms with real examples.
- Who currently has this problem and how do they cope today? Name the actual methods or platforms they use right now.
- What is the realistic market size or opportunity? Show your reasoning with numbers (even if estimated).
- Why does this problem need a dedicated product right now — what has changed recently (behavior, technology, regulation) that makes this viable?

---

## 2. Target Audience

In one focused paragraph, describe the primary population of people who would use "{user_idea}". Be specific: their age range, lifestyle, situation, geography (city/country), and what characteristic makes them the right audience for this product. This must be a description of real people who would actually use this specific product.

---

## 3. User Personas

Write 3–5 user personas. Each persona must be a realistic, specific user of "{user_idea}" — not a generic business user.

For each persona provide:
- **Name, Age, Occupation, City, Monthly Income**
- **Their daily workflow related to this product's problem** — what do they actually do today, step by step, when they encounter the problem this product solves?
- **Exact pain points** — name the real platforms, apps, or methods they currently use and what frustrates them about those
- **Goals they want to achieve using {user_idea} specifically** — what does success look like for them?
- **Technology comfort level** and their preferred devices
- **A representative quote** in their own voice — how would they describe their frustration in casual conversation?
- **Usage pattern** — how often and in what context would they use this product?

---

## 4. Competitive Analysis

Identify 3–5 REAL, named competitors or substitutes in the market for "{user_idea}".

For each competitor, provide:
- Their actual product name and company (no invented names)
- Their key strengths
- Their key weaknesses or gaps
- How "{user_idea}" wins against them specifically

If you are uncertain of exact names, describe the category with real examples (e.g., "existing marketplace apps like OLX, Quikr, and Facebook Marketplace").

Do NOT invent fake competitor names under any circumstances.

| Competitor | Strengths | Weaknesses | Our Advantage |
|-----------|-----------|------------|---------------|

---

## 5. Unique Value Proposition

In 2–3 sentences, state exactly what makes "{user_idea}" different and why users would choose it over the alternatives listed above. Be specific — reference the actual competitors and the actual gap this product fills. Do not use generic phrases like "best in class" or "seamless experience"."""

        for chunk in groq_client.generate_stream(
            prompt=prompt,
            system_prompt=system_prompt,
            agent_type="ba",
            user_idea=user_idea,
            industry=industry
        ):
            yield chunk
