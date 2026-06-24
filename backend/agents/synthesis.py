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

Mermaid Diagram

Data Flow

Deployment Considerations

--------------------------------------------------

# DATABASE DESIGN

Entities

Relationships

Keys

Constraints

Mermaid ERD

--------------------------------------------------

# API DESIGN

Endpoint Catalogue

Request Models

Response Models

Authentication

Rate Limiting

--------------------------------------------------

# WORKFLOW DIAGRAMS

User Onboarding

Core Product Flow

Transaction Flow

Admin Flow

Support Flow

All as Mermaid diagrams.

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

1. Produce complete content.

2. Never say:
"refer to previous section."

3. Never say:
"already covered."

4. Write all content.

5. Merge intelligently.

6. Remove duplicates.

7. Keep strongest version.

8. Final output must feel
like a real startup PRD.

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
