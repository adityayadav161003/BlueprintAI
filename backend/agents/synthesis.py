from typing import Generator
from backend.agents import BaseAgent


class Synthesis(BaseAgent):
    """
    Final PRD Synthesizer

    Inputs:

    - Business Analyst Report
    - Product Manager Report
    - QA Architect Report

    Responsibility:

    Convert 3 expert reports into
    a single investor-grade PRD.

    This agent DOES NOT summarize.

    This agent MERGES.

    Output Target:

    8000 - 12000 words
    """

    def __init__(self):
        super().__init__("syn")

    def run(
        self,
        groq_client,
        ba_output: str,
        pm_output: str,
        qa_output: str,
        user_idea: str,
        industry: str
    ) -> Generator[str, None, None]:

        # NO TRUNCATION
        ba_report = ba_output
        pm_report = pm_output
        qa_report = qa_output

        system_prompt = f"""
You are a Chief Product Officer.

Background:

- Ex Google VP Product
- YC Partner
- Startup Founder
- Enterprise Architect

==================================================
PRODUCT
==================================================

{user_idea}

INDUSTRY

{industry}

==================================================
YOUR ROLE
==================================================

You have received three expert reports.

1. Business Analysis Report
2. Product Design Report
3. QA & Risk Assessment

Your responsibility is NOT
to summarize.

Your responsibility is to:

- Merge
- Resolve conflicts
- Remove duplication
- Improve quality
- Create a single coherent PRD

==================================================
ABSOLUTE RULES
==================================================

1. NEVER LOSE INFORMATION

Preserve important findings.

--------------------------------------------------

2. RESOLVE CONFLICTS

If BA says:

Target users = students

and PM says:

Target users = professionals

Choose the better answer.

Explain if necessary.

--------------------------------------------------

3. NO PLACEHOLDERS

Forbidden:

TBD

To be decided

Placeholder

Insert here

Example only

--------------------------------------------------

4. NO GENERIC CONTENT

Everything must relate to:

{user_idea}

--------------------------------------------------

5. REAL COMPANIES ONLY

Never invent competitors.

--------------------------------------------------

6. ALL TABLES MUST BE COMPLETE

No empty columns.

--------------------------------------------------

7. ALL KPIs MUST HAVE NUMBERS

No:

X%

TBD

N/A

--------------------------------------------------

8. ALL DIAGRAMS MUST BE VALID

Mermaid syntax only.

--------------------------------------------------

9. INVESTOR GRADE

The document must be detailed enough for:

- founders
- engineers
- investors
- designers
- QA teams

to execute from.

==================================================
QUALITY TARGET
==================================================

Minimum:

8000 words

Preferred:

12000+ words

==================================================
"""

        prompt = f"""
You have received three reports.

==================================================
BUSINESS ANALYSIS REPORT
==================================================

{ba_report}

==================================================
PRODUCT MANAGEMENT REPORT
==================================================

{pm_report}

==================================================
QA & RISK REPORT
==================================================

{qa_report}

==================================================
YOUR TASK
==================================================

Create the FINAL PRODUCT
REQUIREMENTS DOCUMENT.

This should feel like:

Amazon PRFAQ
Google Product Spec
YC Startup Memo

combined.

==================================================
FINAL DOCUMENT STRUCTURE
==================================================

# COVER PAGE

Product Name

Industry

Version

Date

Status

Owner

--------------------------------------------------

# EXECUTIVE SUMMARY

Vision

Mission

Problem

Solution

Target Market

Business Model

Success Definition

--------------------------------------------------

# PRODUCT OVERVIEW

Background

Opportunity

Why Now

Product Goals

Product Principles

--------------------------------------------------

# MARKET ANALYSIS

Market Size

TAM

SAM

SOM

Industry Trends

Competitive Landscape

Market Risks

--------------------------------------------------

# CUSTOMER RESEARCH

Target Segments

Personas

User Journey Maps

Pain Points

Desired Outcomes

--------------------------------------------------

# PRODUCT STRATEGY

Unique Value Proposition

Differentiation

Go-To-Market

Revenue Strategy

Growth Strategy

Retention Strategy

--------------------------------------------------

# MVP DEFINITION

Goals

Scope

Success Criteria

Exclusions

MoSCoW Prioritization

--------------------------------------------------

# FEATURE SPECIFICATION

Feature Hierarchy

Feature Descriptions

Business Value

Dependencies

--------------------------------------------------

# USER STORIES

Must Have

Should Have

Could Have

Acceptance Criteria

--------------------------------------------------

# FUNCTIONAL REQUIREMENTS

Minimum 40+

Requirements

Priorities

Acceptance Criteria

--------------------------------------------------

# NON FUNCTIONAL REQUIREMENTS

Performance

Security

Availability

Scalability

Compliance

Accessibility

Observability

Maintainability

--------------------------------------------------

# SYSTEM ARCHITECTURE

Architecture Overview

Technology Components

Generate exactly ONE valid flowchart diagram:
```mermaid
flowchart LR
User --> Frontend
Frontend --> API
API --> Database
```

Data Flow

Deployment Considerations

--------------------------------------------------

# DATABASE DESIGN

Entities

Relationships

Keys

Constraints

Generate exactly ONE valid ER Diagram:
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

--------------------------------------------------

# API DESIGN

Endpoint Catalogue

Request Models

Response Models

Authentication

Rate Limiting

--------------------------------------------------

# WORKFLOW DIAGRAMS

Generate exactly FIVE separate, valid flowchart diagrams. For each flowchart:
- Every node ID must be a single alphanumeric word (no spaces, e.g., use `onboarding` instead of `User Onboarding`).
- If a node label has spaces, you MUST wrap it in double quotes (e.g., `onboarding["User Onboarding"]`).
- Always use `-->` for arrows. Never use `->`.

A. User Onboarding
```mermaid
flowchart TD
start_node["Start Onboarding"] --> input_node["Input Details"]
input_node --> submit_node["Submit Verification"]
```

B. Core Product Flow
```mermaid
flowchart TD
action_start["Start Action"] --> processing["Process Request"]
processing --> result_page["Display Result"]
```

C. Transaction Flow
```mermaid
flowchart TD
select_pay["Select Payment"] --> initiate["Initiate Charge"]
initiate --> confirm_pay["Confirm Payment"]
```

D. Admin Flow
```mermaid
flowchart TD
login_admin["Admin Login"] --> view_dashboard["View Console"]
view_dashboard --> update_settings["Update Settings"]
```

E. Support Flow
```mermaid
flowchart TD
submit_ticket["Submit Ticket"] --> assign_agent["Assign Agent"]
assign_agent --> resolve_ticket["Resolve Issue"]
```

--------------------------------------------------

# UI UX SPECIFICATION

Screen Inventory

Navigation

Design System

Accessibility

Mobile Considerations

--------------------------------------------------

# SECURITY MODEL

Authentication

Authorization

Encryption

Audit Logs

Fraud Prevention

Threat Mitigation

--------------------------------------------------

# PRIVACY & COMPLIANCE

GDPR

CCPA

HIPAA

PCI-DSS

SOC2

Only if relevant.

--------------------------------------------------

# ANALYTICS FRAMEWORK

Event Tracking

Funnels

KPIs

Dashboards

--------------------------------------------------

# RISK REGISTER

Business Risks

Technical Risks

Security Risks

Compliance Risks

Operational Risks

Mitigations

--------------------------------------------------

# EDGE CASE REVIEW

Failure Modes

Abuse Cases

Recovery Scenarios

--------------------------------------------------

# TESTING STRATEGY

Unit Testing

Integration Testing

E2E Testing

Load Testing

Security Testing

Accessibility Testing

--------------------------------------------------

# MVP READINESS REVIEW

Readiness Score

Launch Blockers

Required Fixes

Go / No-Go Decision

--------------------------------------------------

# IMPLEMENTATION ROADMAP

Month 1

Month 2

Month 3

Month 6

Month 12

Deliverables

Milestones

--------------------------------------------------

# SUCCESS METRICS

North Star Metric

Acquisition

Activation

Retention

Revenue

Referral

Targets:

Month 1

Month 3

Month 6

Month 12

--------------------------------------------------

# APPENDICES

Glossary

Assumptions

Open Questions

Future Opportunities

==================================================
FINAL RULES
==================================================

1. Produce complete, professional content without placeholders (no TBD, To Be Decided, X%).

2. Never say: "refer to previous section" or "already covered". Write out all content in full detail.

3. DENSE DOCUMENT LAYOUT (NO EXCESSIVE WHITESPACE):
   - Use a clean, professional, compact typography structure.
   - Use at most ONE blank line between headers, paragraphs, and sections.
   - Do NOT include any blank lines between list items or bullets.
   - Align markdown tables properly and ensure they have no empty cells.

4. STRICT MERMAID DIAGRAM SYNTAX:
   - Ensure all Mermaid code blocks are syntactically valid.
   - Every flowchart MUST start with `flowchart LR` or `flowchart TD`.
   - Every ER diagram MUST start with `erDiagram`.
   - Never put titles, headers, descriptions, or comments inside the ```mermaid block.
   - If node labels contain special characters (like parentheses, brackets, colons, or quotes), you MUST wrap the entire label in double quotes, e.g., `NodeA["Login (OAuth2)"]`.
   - Never use HTML tags inside Mermaid code.
   - Ensure all relationships in ER diagrams use standard Mermaid syntax (e.g., `||--o{{` or `||--||`).

5. Merge intelligently, remove duplication, and keep the strongest, most detailed version of each section.

Generate complete document.
"""

        for chunk in groq_client.generate_stream(
            prompt=prompt,
            system_prompt=system_prompt,
            agent_type="syn",
            user_idea=user_idea,
            industry=industry
        ):
            yield chunk
