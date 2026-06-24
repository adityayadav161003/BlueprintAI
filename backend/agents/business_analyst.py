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

Provide a high-level summary of the product blueprint using the following bullet points:
- **Product Vision:** What is the long-term vision of "{user_idea}"?
- **Core Problem:** What is the primary pain point or inefficiency in the market today?
- **Our Solution:** How does "{user_idea}" solve this problem uniquely?
- **Target Customer:** Who is the ideal user or customer segment?
- **Business Model:** How will this product generate revenue (pricing model, transaction fees)?
- **MVP Launch Target:** Timeline target for the MVP (e.g., 12 weeks).
- **Success Definition:** Core quantitative goals for launch (e.g., user acquisition targets, bookings).

---

## 1. Problem Statement & Opportunity

Describe the business context and market opportunity specifically for "{user_idea}":
- What specific problem does this product solve? Describe it in concrete terms with real examples.
- Who currently has this problem and how do they cope today? Name the actual methods or platforms they use right now.
- What is the realistic market size or opportunity? Show your reasoning with numbers (even if estimated).
- Why does this problem need a dedicated product right now — what has changed recently (behavior, technology, regulation) that makes this viable?

---

## 2. User Personas (3 Complete Profiles)

Write 3 user personas. Each persona must be a realistic, specific user of "{user_idea}" (e.g., for a car-sharing app: Urban Millennial, Environmentally Conscious Gen Z, Urban Professional). 

For each persona provide:
- **Demographics:** Age, occupation, city, lifestyle.
- **Daily Workflow:** How do they commute, travel, or encounter the problem this product solves in their daily routine?
- **Pain Points:** Specific frustrations with current workarounds or competing products.
- **Goals:** What they want to accomplish using "{user_idea}" specifically.
- **Tech Stack:** Tech comfort level, preferred devices, and digital apps they use daily.
- **Budget Authority:** Transportation or product budget levels, price sensitivity.
- **Success Metrics:** What constitutes a successful usage session or outcome for them (e.g., time saved, cost reduced)?
- **Quote:** A representative quote in their own voice in casual, natural language.
- **Usage Pattern:** How often and in what context they use this product."""

        for chunk in groq_client.generate_stream(
            prompt=prompt,
            system_prompt=system_prompt,
            agent_type="ba",
            user_idea=user_idea,
            industry=industry
        ):
            yield chunk
