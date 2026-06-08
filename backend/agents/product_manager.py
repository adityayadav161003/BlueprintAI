from typing import Generator
from backend.agents import BaseAgent
from backend.models.groq_client import GroqClient

class ProductManager(BaseAgent):
    def __init__(self):
        super().__init__("pm")

    def run(self, groq_client: GroqClient, ba_output: str, user_idea: str, industry: str) -> Generator[str, None, None]:
        """
        Executes the Product Manager agent to generate a comprehensive draft PRD.
        """
        system_prompt = """You are a Principal Product Manager with 10 years at Google, Meta, and Stripe.

You have shipped products used by 100M+ users. You write PRDs that:
- Engineers can implement without clarification meetings
- Designers can wireframe from directly
- Executives can present to the board
- QA teams can write test cases from immediately

CRITICAL RULES:
- Use the INVEST framework for every user story
- Include explicit acceptance criteria for every functional requirement
- Never leave ambiguity — if something is unclear, make a decision and document it
- Every section must have enough detail that a new team member could understand it in 30 minutes
- Write in clean markdown — use tables, bullet points, numbered lists appropriately"""

        prompt = f"""You are writing the first draft of a Product Requirements Document (PRD).

PRODUCT IDEA: {user_idea}
INDUSTRY: {industry}

BUSINESS ANALYSIS CONTEXT:
{ba_output[:3000] if len(ba_output) > 3000 else ba_output}

Create a comprehensive PRD in markdown format with the following sections:

# Product Requirements Document: [Product Name]

## Executive Summary
- One-paragraph product vision
- Core value proposition (one sentence)
- MVP definition (what is in/out of scope)

## 1. User Personas (3 detailed personas)
For each persona:
- Name, age, role, company size
- Goals and motivations
- Current frustrations and pain points  
- Technology comfort level
- How they'll use this product daily
- Quote that represents their mindset

## 2. User Stories (MoSCoW Prioritization)
### Must Have (MVP Critical)
List 6-8 user stories in format: "As a [persona], I want to [action], so that [outcome]."
Each with: Priority, Story Points (1-13), Acceptance Criteria (3+ bullet points)

### Should Have (Post-MVP)
List 4-5 user stories

### Could Have (Future)
List 3-4 user stories

### Won't Have (Explicitly Excluded)
List 2-3 items with justification

## 3. Functional Requirements
Table format with columns: ID | Feature | Description | Acceptance Criteria | Priority | Dependencies

Include at minimum:
- Authentication & Authorization
- Core feature set (product-specific)
- Data management & persistence
- Export / sharing capabilities
- Error handling & recovery
- Admin/settings panel

## 4. Non-Functional Requirements
### Performance
- Response time SLAs (p50, p95, p99)
- Throughput targets
- Concurrent user capacity

### Security
- Authentication method
- Data encryption (at rest, in transit)
- Privacy compliance (GDPR/CCPA if applicable)

### Scalability
- Expected growth trajectory
- Infrastructure scaling strategy

### Accessibility
- WCAG compliance level
- Screen reader support
- Keyboard navigation

## 5. UI/UX Requirements
- Key screens list with purpose
- Navigation flow description
- Critical interaction patterns
- Design principles for this product
- Responsive breakpoints

## 6. Technical Constraints & Assumptions
- Platform targets (web, iOS, Android, etc.)
- Browser/OS compatibility
- Known technical limitations
- Third-party dependencies

## 7. Out of Scope (MVP)
- Explicit list of features NOT in MVP with brief justification

Be thorough, specific, and engineer-ready. No vague requirements."""

        for chunk in groq_client.generate_stream(
            prompt=prompt,
            system_prompt=system_prompt,
            agent_type="pm",
            user_idea=user_idea,
            industry=industry
        ):
            yield chunk
