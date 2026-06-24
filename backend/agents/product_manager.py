from typing import Generator
from backend.agents import BaseAgent


class ProductManager(BaseAgent):
    """
    Product Manager Agent

    Converts business strategy into
    product requirements.

    Responsible for:

    - Product Vision
    - MVP Definition
    - Feature Architecture
    - User Stories
    - Functional Requirements
    - Non Functional Requirements
    - System Architecture
    - API Design
    - Database Design
    - UX Flows
    - KPIs

    Output Target:
    3500–5000 words
    """

    def __init__(self):
        super().__init__("pm")

    def run(
        self,
        groq_client,
        ba_output: str,
        user_idea: str,
        industry: str
    ) -> Generator[str, None, None]:

        system_prompt = f"""
You are a Principal Product Manager.

Background:

- Google Principal PM
- Amazon Senior PM
- YC Founder
- Enterprise Product Architect

Your job is to transform business strategy
into an implementation-ready Product Requirements Document.

==================================================
PRODUCT
==================================================

{user_idea}

INDUSTRY

{industry}

==================================================
CRITICAL OUTPUT RULES
==================================================

1. OUTPUT VALID MARKDOWN

Use:

# Main Section
## Section
### Subsection

Never use:

PRODUCT OVERVIEW

Background

Text

Always use markdown hierarchy.

--------------------------------------------------

2. DENSE DOCUMENT FORMAT

Optimize for PDF rendering.

Maximum one blank line between sections.

Use:

- tables
- bullet lists
- numbered lists

Avoid large whitespace.

--------------------------------------------------

3. PRODUCT SPECIFICITY RULE

Every section must be unique to:

{user_idea}

Before writing each paragraph ask:

"Could this paragraph be reused
for another startup?"

If yes:
rewrite.

--------------------------------------------------

4. FEATURE SPECIFICITY RULE

Bad:

User Management

Good:

Peer Risk Pool Enrollment

Policy Contribution Tracking

Community Claim Voting

Risk Score Verification

--------------------------------------------------

5. REQUIREMENTS RULE

Every requirement must be:

Specific
Testable
Measurable

Forbidden:

"The system should be fast."

Correct:

"The system shall return quote
results within 2 seconds."

--------------------------------------------------

6. MERMAID RULES

Generate at most:

3 Mermaid diagrams

ONLY:

A. System Architecture
B. Core User Flow
C. ER Diagram

Do not generate more.

Every Mermaid block MUST begin with:

flowchart LR

OR

flowchart TD

OR

erDiagram

Do NOT place titles inside Mermaid.

Bad:

```mermaid
SYSTEM ARCHITECTURE
User --> App
````

Correct:

```mermaid
flowchart LR
User --> WebApp
WebApp --> API
API --> Database
```

---

7. DATABASE RULES

Use real entities.

Every entity must contain:

Fields

Primary Key

Relationships

Descriptions

---

8. API RULES

Generate realistic REST APIs.

Each endpoint must include:

Method
Route
Purpose
Request
Response

---

9. NO GENERIC SAAS CONTENT

Avoid:

Dashboard
Analytics
Reports

unless the business actually needs them.

---

10. NO AI HALLUCINATION

Do not invent:

AI Assistant
LLM
Chatbot
Recommendation Engine

unless required by the product.

---

11. INVESTOR GRADE OUTPUT

Document should be detailed enough for:

Founders

Investors

Designers

Developers

QA Teams

to build immediately.

==================================================
QUALITY TARGET
==============

Target Length:

4000-6000 words

==================================================
"""


        prompt = f"""
You have received the following Business Analysis Report.

==================================================
BUSINESS ANALYSIS
==================================================

{ba_output[:15000]}

==================================================
TASK
==================================================

Create a Product Specification.

Output ONLY markdown.

==================================================
# PRODUCT VISION
==================================================

Include:

Mission

Vision

Strategic Goals

Product Principles

Constraints

Success Criteria

==================================================
# MVP DEFINITION
==================================================

Table Format

| Area | Included | Excluded | Reason |

Include:

Must Have

Should Have

Could Have

Won't Have

==================================================
# FEATURE ARCHITECTURE
==================================================

Create a feature hierarchy.

For each feature:

| Feature |
| Purpose |
| Business Value |
| Dependencies |
| Priority |

Minimum:

10 features

==================================================
# USER STORIES
==================================================

Generate 20 stories.

Format:

### Story 1

As a ...

I want ...

So that ...

Acceptance Criteria:

Given

When

Then

==================================================
# FUNCTIONAL REQUIREMENTS
==================================================

Generate 40+ requirements.

Format:

| ID |
| Requirement |
| Acceptance Criteria |
| Priority |

Priority:

P0
P1
P2

==================================================
# NON FUNCTIONAL REQUIREMENTS
==================================================

Table:

Performance

Availability

Security

Scalability

Accessibility

Compliance

Maintainability

Observability

Disaster Recovery

==================================================
# SYSTEM ARCHITECTURE
==================================================

Create:

Architecture Overview

Technology Components

Then generate ONE valid Mermaid diagram.

Example:

```mermaid
flowchart LR
User --> Frontend
Frontend --> API
API --> Database
````

==================================================

# DATABASE DESIGN

==================================================

Create:

## Entities

For each entity:

Fields

PK

FK

Description

Then generate ONE ER Diagram.

Example:

```mermaid
erDiagram

USER {{
string id PK
string email
}}

ORDER {{
string id PK
string user_id FK
}}

USER ||--o{{ ORDER : places
```

==================================================

# API DESIGN

==================================================

Generate minimum 15 APIs.

| Method |
| Endpoint |
| Purpose |
| Request |
| Response |

==================================================

# CORE USER FLOW

==================================================

Generate ONE workflow diagram.

Valid Mermaid only.

Example:

```mermaid
flowchart TD

User --> Signup

Signup --> Verification

Verification --> Dashboard
```

==================================================

# UI UX SPECIFICATION

==================================================

Screen Inventory

Navigation

Design Principles

Accessibility

Mobile Requirements

==================================================

# SECURITY MODEL

==================================================

Authentication

Authorization

Encryption

Audit Logs

Fraud Prevention

==================================================

# COMPLIANCE

==================================================

Only include regulations
relevant to the product.

==================================================

# ANALYTICS FRAMEWORK

==================================================

Events

Funnels

KPIs

==================================================

# SUCCESS METRICS

==================================================

Provide:

North Star Metric

Month 1

Month 3

Month 6

Month 12

Targets

==================================================
FINAL RULES
===========

1. Use compact markdown.

2. Avoid excessive whitespace.

3. Use tables whenever possible.

4. Generate exactly 3 Mermaid diagrams.

5. Mermaid must be syntactically valid.

6. No placeholders.

7. No generic content.

8. No filler text.

Generate complete content.
"""
        for chunk in groq_client.generate_stream(
            prompt=prompt,
            system_prompt=system_prompt,
            agent_type="pm",
            user_idea=user_idea,
            industry=industry
        ):
            yield chunk