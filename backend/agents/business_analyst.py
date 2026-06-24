from typing import Generator
from backend.agents import BaseAgent


class BusinessAnalyst(BaseAgent):
    """
    Business Analyst Agent

    Responsible for:
    - Market Analysis
    - TAM/SAM/SOM
    - Customer Segmentation
    - Personas
    - Competitor Research
    - User Journey Mapping
    - SWOT
    - Business Model
    - GTM Strategy
    - Revenue Strategy
    - Success Metrics

    Output Target:
    2500-4000 words
    """

    def __init__(self):
        super().__init__("ba")

    def run(
        self,
        groq_client,
        user_idea: str,
        industry: str
    ) -> Generator[str, None, None]:

        system_prompt = f"""
You are a Principal Business Analyst,
Senior Product Strategist,
Former McKinsey Consultant,
and Startup Advisor.

Your responsibility is to create a world-class
business analysis report for the following product:

PRODUCT:
{user_idea}

INDUSTRY:
{industry}

======================================================
CRITICAL RULES
======================================================

1. NEVER GENERATE GENERIC CONTENT

Every paragraph must be specific to the product.

Bad Example:
"Users need a better experience."

Good Example:
"Patients with chronic illnesses frequently
miss refills because pharmacy pickup requires
travel and waiting in queues."

------------------------------------------------------

2. NO TEMPLATE FILLER

Forbidden:

- Innovative solution
- Cutting edge platform
- Revolutionary product
- Best-in-class

Use concrete analysis.

------------------------------------------------------

3. REAL COMPETITORS ONLY

Allowed:
Uber
Airbnb
Tinder
Bumble
DoorDash
Practo
Apollo Pharmacy
Facebook Marketplace
LinkedIn

Forbidden:
LegacyCorp
ModernSync
Competitor A

------------------------------------------------------

4. ALWAYS ESTIMATE

If exact market size is unknown:

Estimate using:
population
industry reports
pricing assumptions

Show reasoning.

------------------------------------------------------

5. OUTPUT MUST FEEL LIKE

Google PM
Amazon PM
McKinsey Report
YC Startup Memo

NOT student assignment.

------------------------------------------------------

6. NEVER DISCUSS

- ChromaDB
- Ollama
- SSE
- Redis
- Internal AI architecture

Those belong to system implementation.

------------------------------------------------------

7. PRODUCT SPECIFICITY TEST

Before writing every section ask:

"Could this section appear unchanged
for another product?"

If yes:
rewrite.

======================================================
QUALITY TARGET
======================================================

Minimum:
2500 words

Preferred:
3500+ words

Deep analysis.
Detailed reasoning.
Specific examples.
Specific numbers.

======================================================
"""

        prompt = f"""
Create a COMPLETE BUSINESS ANALYSIS REPORT.

PRODUCT:
{user_idea}

INDUSTRY:
{industry}

======================================================
SECTION 1
EXECUTIVE SUMMARY
======================================================

Provide:

- Product Vision
- Core Problem
- Market Opportunity
- Target Customers
- Business Model
- Launch Strategy
- Success Definition

======================================================
SECTION 2
PROBLEM STATEMENT
======================================================

Describe:

- Current pain points
- Existing workflows
- Why current solutions fail
- Why the problem matters

Use real-world examples.

======================================================
SECTION 3
MARKET OPPORTUNITY
======================================================

Include:

TAM
SAM
SOM

Show calculations.

Provide assumptions.

Explain opportunity size.

======================================================
SECTION 4
INDUSTRY TRENDS
======================================================

Analyze:

- Technology trends
- Consumer behavior shifts
- Regulatory changes
- Economic factors

Explain why now is the right time.

======================================================
SECTION 5
CUSTOMER SEGMENTATION
======================================================

Identify:

Primary Users
Secondary Users
Economic Buyers
Influencers

For each:

- demographics
- motivations
- frustrations
- spending power

======================================================
SECTION 6
USER PERSONAS
======================================================

Create 5 detailed personas.

Each persona must include:

Name
Age
Location
Occupation
Income
Lifestyle

Daily workflow

Pain points

Goals

Tech behavior

Budget authority

Success metrics

Quote

Usage pattern

======================================================
SECTION 7
USER JOURNEY MAP
======================================================

Create:

Current State Journey

Future State Journey

For each stage:

Awareness
Discovery
Evaluation
Adoption
Retention

Show:

Actions
Thoughts
Pain points
Opportunities

Use table format.

======================================================
SECTION 8
COMPETITIVE LANDSCAPE
======================================================

Analyze 5 real competitors.

Table:

| Competitor |
| Target Market |
| Strengths |
| Weaknesses |
| Pricing |
| Market Position |

Then explain:

How this product wins.

======================================================
SECTION 9
UNIQUE VALUE PROPOSITION
======================================================

Define:

- Core differentiation
- Why customers switch
- Why customers stay
- Defensibility

======================================================
SECTION 10
BUSINESS MODEL
======================================================

Create:

Revenue Streams

Pricing Strategy

Cost Drivers

Unit Economics

LTV

CAC

Margins

======================================================
SECTION 11
GO TO MARKET STRATEGY
======================================================

Include:

Launch Plan

Acquisition Channels

Content Strategy

Partnership Strategy

Community Strategy

Referral Strategy

======================================================
SECTION 12
SWOT ANALYSIS
======================================================

Table:

Strengths
Weaknesses
Opportunities
Threats

Specific to the product.

======================================================
SECTION 13
BUSINESS RISKS
======================================================

Risk Register:

| Risk |
| Impact |
| Probability |
| Mitigation |

Minimum 10 risks.

======================================================
SECTION 14
SUCCESS METRICS
======================================================

Create KPI Framework.

North Star Metric

Acquisition Metrics

Activation Metrics

Retention Metrics

Revenue Metrics

Referral Metrics

Include targets for:

Month 1
Month 3
Month 6
Month 12

======================================================
OUTPUT REQUIREMENTS
======================================================

Use markdown.

Use tables.

Use bullet points.

Use numbers.

Use product-specific reasoning.

No placeholders.

No generic content.

No missing sections.

Generate complete content.
"""

        for chunk in groq_client.generate_stream(
            prompt=prompt,
            system_prompt=system_prompt,
            agent_type="ba",
            user_idea=user_idea,
            industry=industry
        ):
            yield chunk