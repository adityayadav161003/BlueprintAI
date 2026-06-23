from typing import Generator
from backend.agents import BaseAgent


class BusinessAnalyst(BaseAgent):
    def __init__(self):
        super().__init__("ba")

    def run(self, groq_client, user_idea: str, industry: str) -> Generator[str, None, None]:
        """
        Executes the Business Analyst agent — generates deep, investor-grade market analysis.
        """
        system_prompt = """You are a Senior Business Analyst who has worked at McKinsey, BCG, and Sequoia Capital.

Your deliverables have directly secured Series A and Series B funding rounds. You combine rigorous market research with startup pragmatism.

IRON RULES — violate any of these and the output is rejected:
1. TAM/SAM/SOM must use BOTTOMS-UP methodology (not top-down guesses). Show the math.
2. SOM (Year 1) must be conservative and defensible. No startup captures $1B in Year 1 — ever.
3. Every market size figure must have a source methodology (e.g., "15M target users × $10/month avg. spend = $1.8B SAM").
4. Competitor analysis must include REAL companies, their actual pricing, and honest differentiation gaps.
5. Revenue model must include unit economics: Customer Acquisition Cost (CAC), Lifetime Value (LTV), LTV:CAC ratio, Payback Period.
6. Business workflow section is MANDATORY — describe how value flows from the business to the customer step by step.
7. Identify ALL regulatory, compliance, and legal requirements for this industry explicitly.
8. Format in clean, professional markdown. Tables for comparisons. No bullet-point-only sections.
9. Do NOT use vague phrases: "leverage AI", "improve UX", "increase revenue", "disrupt the industry".
10. Every risk must have a specific mitigation with a timeline and owner role."""

        prompt = f"""Conduct a rigorous, investor-grade Business Analysis for the following product:

PRODUCT IDEA: {user_idea}
INDUSTRY: {industry}

Output a comprehensive Business Analysis Report in markdown. Be specific, realistic, and data-grounded. Use the exact structure below — do NOT skip any section.

---

# Business Analysis Report: {user_idea}

## 1. Problem Statement & Market Gap
- Describe the exact real-world pain point in 2-3 sentences with specificity.
- Quantify the inefficiency: hours wasted per week, money lost per transaction, error rates, etc.
- Identify the primary sufferers: specific job roles, demographics, or situations.
- Explain WHY existing solutions fail to solve this (not just that they "lack features").

## 2. End-to-End Business Workflow
Map how the product creates and delivers value step by step. Example for a delivery app:
```
Step 1: Customer registers and uploads prescription
Step 2: System routes to licensed pharmacy for verification  
Step 3: Pharmacist confirms availability and price
Step 4: Customer approves order and completes payment
Step 5: Delivery partner assigned and dispatched
Step 6: Real-time tracking until delivery confirmed
Step 7: Digital receipt + refill reminder scheduled
```
Adapt this pattern to the actual product. Be specific — developers will use this to define their data model.

## 3. All User Roles (Complete Role Inventory)
List EVERY role that will interact with the system (not just end-users):
| Role | Description | Primary Actions | Permissions Level |
This is critical — many PRDs forget admin, operator, and compliance roles.

## 4. Target Market Analysis
- **Primary Segment**: demographics, psychographics, specific behavior patterns
- **Secondary Segments**: who else benefits
- **Geographic Focus**: specific countries/cities for launch, expansion sequence
- **Market Timing**: why this product is viable NOW (regulatory shifts, tech readiness, behavior change)

## 5. Market Sizing — Bottoms-Up Methodology

### TAM (Total Addressable Market)
Show the calculation:
- Number of potential users globally × average annual spend per user = TAM
- Cross-validate with any known industry report figures.

### SAM (Serviceable Addressable Market)  
- Restrict to your realistic geography and segment
- Show: [addressable users in target region] × [realistic price point] = SAM

### SOM (Serviceable Obtainable Market) — Year 1 to Year 3
Be CONSERVATIVE and REALISTIC:
- Year 1 SOM: Show assumed market share % (typically 0.01%–0.1% of SAM) × SAM
- Year 2 SOM: Apply realistic growth multiplier
- Year 3 SOM: Show with assumptions about team size and GTM execution

## 6. Competitive Landscape
| Competitor | Type | Pricing | Key Strengths | Key Weaknesses | Our Advantage Over Them |
Include 4–5 real or representative competitors. Be honest about where they beat us.

## 7. Regulatory & Compliance Requirements
This section is NON-NEGOTIABLE for industries like healthcare, fintech, legal, and edtech.
List EVERY compliance requirement:
- Applicable laws and standards (HIPAA, GDPR, PCI-DSS, FDA, etc.)
- Licensing requirements (pharmacy license, financial license, etc.)
- Data handling obligations (retention period, encryption, audit logs)
- User consent requirements
- Reporting obligations

## 8. Revenue Model & Unit Economics
- **Primary Revenue Stream**: pricing model, price points, billing frequency
- **Secondary Revenue Streams**: upsells, commissions, white-label, API
- **Unit Economics**:
  - Estimated CAC (Customer Acquisition Cost): $X via [channel]
  - Estimated LTV (Lifetime Value): $Y based on [retention assumption]
  - LTV:CAC Ratio: (must be ≥ 3:1 to be viable)
  - Payback Period: [months]
  - Gross Margin: X%

## 9. Go-To-Market Strategy
### Phase 1: Launch (Months 1-3)
- Primary channels, partnerships, and tactics
- Target: X customers/users

### Phase 2: Growth (Months 4-9)
- Scaling channels, referral programs
- Target: Y customers/users

### Phase 3: Expansion (Months 10-18)
- Geographic or segment expansion
- Target: Z customers/users

## 10. Key Success Metrics (KPIs)
| Metric | Definition | Target Month 3 | Target Month 6 | Target Year 1 | Target Year 3 |
Must include: activation rate, D30 retention, NPS, CAC, LTV, MRR, churn rate, and product-specific metrics.

## 11. Risk Register
| Risk | Category | Likelihood | Impact | Mitigation Strategy | Owner |
Include: regulatory risk, technical risk, market adoption risk, competitive risk, and funding risk.

## 12. Investment Thesis
- Why this product must be built NOW (market timing argument)
- Competitive window before the market matures
- Team and resource requirements to execute
- Comparable successful companies (analogous market comps)
- Realistic exit scenarios (acqui-hire, strategic acquisition, IPO path)

---
Be specific, data-rich, and investor-grade. Every number must be defensible."""

        for chunk in groq_client.generate_stream(
            prompt=prompt,
            system_prompt=system_prompt,
            agent_type="ba",
            user_idea=user_idea,
            industry=industry
        ):
            yield chunk
