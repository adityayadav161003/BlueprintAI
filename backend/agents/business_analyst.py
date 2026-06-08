from typing import Generator
from backend.agents import BaseAgent
from backend.models.groq_client import GroqClient

class BusinessAnalyst(BaseAgent):
    def __init__(self):
        super().__init__("ba")

    def run(self, groq_client: GroqClient, user_idea: str, industry: str) -> Generator[str, None, None]:
        """
        Executes the Business Analyst agent to generate a comprehensive market analysis.
        """
        system_prompt = """You are a senior business analyst with 15 years of experience at McKinsey, BCG, and Bain & Company.

Your expertise:
- Market sizing using bottoms-up and top-down methodologies (TAM/SAM/SOM)
- Competitive landscape mapping with Porter's Five Forces
- Revenue model design and unit economics
- Go-to-market strategy and channel analysis
- Investment opportunity evaluation with IRR/NPV thinking
- Customer discovery and Jobs-to-be-Done framework

CRITICAL RULES:
- Never use vague phrases like "improve user experience", "leverage AI", or "increase revenue"
- Always cite specific numbers, percentages, and timeframes
- Every claim must be grounded in realistic market data
- Output must be structured, professional, and investor-grade
- Write in clean markdown with headers, tables, and bullet points
- Be concise but comprehensive — executives read this document"""

        prompt = f"""Conduct a comprehensive business analysis for the following product idea:

PRODUCT IDEA: {user_idea}
INDUSTRY: {industry}

Produce a structured Business Analysis Report in markdown format covering:

## 1. Problem Statement & Market Gap
- Define the exact pain point with specificity
- Quantify the inefficiency (time lost, money wasted, etc.)
- Identify who suffers most from this problem

## 2. Target Market Analysis
- Primary user segment (demographics, psychographics, behavior)
- Secondary user segments
- Geographic focus and expansion plan

## 3. Market Sizing (TAM/SAM/SOM)
- TAM: Total Addressable Market with calculation methodology
- SAM: Serviceable Addressable Market (realistic segment)
- SOM: Serviceable Obtainable Market (Year 1-3 targets)

## 4. Competitive Landscape
Create a comparison table of 3-4 real or representative competitors:
| Competitor | Strengths | Weaknesses | Pricing | Market Share |

## 5. Our Competitive Advantage
- Unique differentiators (what we do that no one else does)
- Defensible moats (network effects, data, switching costs, brand)

## 6. Revenue Model & Monetization
- Primary revenue stream with pricing strategy
- Secondary revenue streams
- Unit economics: CAC, LTV, Payback Period estimates

## 7. Go-To-Market Strategy
- Launch channels (Phase 1)
- Growth levers (Phase 2)
- Partnership opportunities

## 8. Key Success Metrics (KPIs)
Provide a table:
| Metric | Target (Month 6) | Target (Year 1) | Target (Year 3) |

## 9. Risks & Mitigations
Top 3 business risks with likelihood, impact, and mitigation strategy.

## 10. Investment Thesis
Why this product deserves to be built now — market timing, technology readiness, and team requirements.

Be specific, data-rich, and realistic. Do not pad with filler content."""

        for chunk in groq_client.generate_stream(
            prompt=prompt,
            system_prompt=system_prompt,
            agent_type="ba",
            user_idea=user_idea,
            industry=industry
        ):
            yield chunk
