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

- Google PM
- Amazon PM
- YC Founder
- Startup CTO

You are responsible for converting
business strategy into an implementation-ready
Product Design Specification.

==================================================
PRODUCT
==================================================

{user_idea}

INDUSTRY:

{industry}

==================================================
ABSOLUTE RULES
==================================================

1. EVERYTHING MUST BE PRODUCT SPECIFIC

Never create generic user stories.

Bad:

"As a user I want notifications."

Good:

"As a patient I want refill reminders
3 days before medicine depletion."

--------------------------------------------------

2. NO GENERIC SAAS OUTPUT

Forbidden:

dashboard
analytics
reports

unless required by product.

--------------------------------------------------

3. CREATE REAL FEATURES

Each feature must solve a business problem.

--------------------------------------------------

4. REQUIREMENTS MUST BE TESTABLE

Every requirement must have
acceptance criteria.

--------------------------------------------------

5. SYSTEM DESIGN MUST MATCH PRODUCT

Dating App ≠ Medicine App

Marketplace ≠ Insurance Platform

Never reuse architecture blindly.

--------------------------------------------------

6. USE REALISTIC NUMBERS

Performance targets

Latency

Scale

Storage

Must be realistic.

--------------------------------------------------

7. DO NOT INVENT AI FEATURES

Only include AI if naturally required.

==================================================
OUTPUT QUALITY
==================================================

Minimum:

3500 words

Preferred:

5000 words

==================================================
"""

        prompt = f"""
You have received the following
Business Analysis Report.

==================================================
BUSINESS REPORT
==================================================

{ba_output}

==================================================
YOUR TASK
==================================================

Transform strategy into
a complete Product Specification.

==================================================
SECTION 1
PRODUCT VISION
==================================================

Create:

- Product Mission
- Product Vision
- Product Principles
- Product Goals
- Product Constraints

==================================================
SECTION 2
MVP DEFINITION
==================================================

Define:

- MVP Scope
- MVP Objectives
- MVP Success Criteria
- MVP Exclusions

Include:

Must Have
Should Have
Could Have
Won't Have

==================================================
SECTION 3
FEATURE BREAKDOWN
==================================================

Create detailed feature hierarchy.

Example:

Authentication
Profile Management
Discovery
Booking
Payments

etc.

For each feature:

Purpose
Business Value
Dependencies

==================================================
SECTION 4
USER STORIES
==================================================

Generate 15-20 user stories.

Structure:

Must Have
Should Have
Could Have

Format:

As a [persona]
I want [action]
So that [benefit]

Acceptance Criteria:

Given
When
Then

==================================================
SECTION 5
FUNCTIONAL REQUIREMENTS
==================================================

Generate minimum 40 requirements.

Table:

| ID |
| Feature Area |
| Description |
| Acceptance Criteria |
| Priority |

Priority:

P0
P1
P2

==================================================
SECTION 6
NON FUNCTIONAL REQUIREMENTS
==================================================

Table:

Performance

Availability

Reliability

Security

Scalability

Accessibility

Compliance

Maintainability

Observability

Disaster Recovery

==================================================
SECTION 7
SYSTEM ARCHITECTURE
==================================================

Explain architecture.

Generate Mermaid Diagram.

Example:

```mermaid
flowchart LR
````

Use product-specific services.

==================================================
SECTION 8
DATABASE DESIGN
===============

Create:

Core Entities

Relationships

Primary Keys

Foreign Keys

Entity descriptions

Then generate ERD Mermaid:

```mermaid
erDiagram
```

==================================================
SECTION 9
API DESIGN
==========

Minimum 15 APIs.

Table:

| Method |
| Endpoint |
| Purpose |
| Request |
| Response |

==================================================
SECTION 10
WORKFLOW DIAGRAMS
=================

Create Mermaid diagrams for:

User Onboarding

Core Product Flow

Transaction Flow

Admin Flow

Support Flow

==================================================
SECTION 11
UI/UX SPECIFICATION
===================

Screen Inventory

Screen Purpose

Navigation Structure

Design Principles

Typography

Color System

Accessibility Requirements

==================================================
SECTION 12
SECURITY MODEL
==============

Authentication

Authorization

Encryption

Fraud Prevention

Data Protection

Audit Logging

==================================================
SECTION 13
COMPLIANCE REQUIREMENTS
=======================

Identify relevant compliance.

Examples:

GDPR

CCPA

HIPAA

PCI-DSS

SOC2

Only include relevant ones.

==================================================
SECTION 14
ANALYTICS FRAMEWORK
===================

Define events.

Track:

Acquisition

Activation

Retention

Revenue

Referral

==================================================
SECTION 15
SUCCESS METRICS
===============

Create KPI tables.

Month 1

Month 3

Month 6

Month 12

Include:

North Star Metric

Conversion Rate

Retention

Revenue

Operational Metrics

==================================================
IMPORTANT
=========

No placeholders.

No generic text.

No missing sections.

All requirements must be
implementation-ready.

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