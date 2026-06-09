from typing import Generator
from backend.agents import BaseAgent
from backend.models.groq_client import GroqClient

class Synthesis(BaseAgent):
    def __init__(self):
        super().__init__("syn")

    def run(self, groq_client: GroqClient, pm_output: str, qa_output: str, user_idea: str, industry: str) -> Generator[str, None, None]:
        """
        Executes the Synthesis agent to produce the final board-ready PRD.
        """
        system_prompt = """You are the Chief Product Officer (CPO) at a high-growth unicorn startup.

You have 15 years of product leadership experience. You have taken 3 products from 0 to $100M ARR.
You write documents that win board approvals, secure Series A funding, and get development teams aligned in one meeting.

CRITICAL RULES:
- Incorporate ALL valid QA feedback into the final document
- Every section must be complete, specific, and actionable
- Include a full technical architecture section with tech stack recommendations
- Include a complete project build plan with phases, milestones, and deliverables
- The PRD must be publication-grade — formatted for Notion, Confluence, or a board deck
- Do not copy-paste from earlier drafts — synthesize and elevate the content
- Include actual technology choices with justification (not "a database" — say "PostgreSQL because...")
- Roadmap must have specific week-by-week milestones, not vague phases"""

        prompt = f"""You are synthesizing a final, board-ready Product Requirements Document.

PRODUCT IDEA: {user_idea}
INDUSTRY: {industry}

DRAFT PRD (from Product Manager):
{pm_output[:2500] if len(pm_output) > 2500 else pm_output}

QA CRITIC FEEDBACK (must be incorporated):
{qa_output[:2000] if len(qa_output) > 2000 else qa_output}

Produce the complete, final PRD. This is the document that gets handed to the engineering team on Day 1.

---

# {user_idea} — Product Requirements Document
**Version:** 1.0 | **Status:** Final | **Classification:** Internal

---

## Executive Summary
- **Product Vision**: (one powerful sentence)
- **Core Problem**: (specific pain point with quantification)
- **Our Solution**: (what we build and why it's different)
- **Target Customer**: (specific segment)
- **Business Model**: (how we make money)
- **MVP Launch Target**: (realistic timeline)
- **Success Definition**: (measurable outcome in 6 months)

---

## 1. Problem Statement & Opportunity
Detailed narrative covering:
- The exact problem (with real-world scenario)
- Current workarounds and why they fail
- Market timing — why now is the right time
- The cost of inaction (for the customer)

---

## 2. User Personas (3 Complete Profiles)
For each persona include: demographics, daily workflow, pain points, goals, tech stack they use, budget authority, success metrics, and a representative quote.

---

## 3. Prioritized User Stories (MoSCoW)

### Must Have (Sprint 1-2)
[8+ stories with acceptance criteria]

### Should Have (Sprint 3-4)  
[5+ stories]

### Could Have (Post-MVP)
[4+ stories]

### Won't Have (MVP Exclusions)
[3+ explicit exclusions with justification]

---

## 4. Functional Requirements
Complete table with: ID | Feature | User Story Ref | Detailed Description | Acceptance Criteria | Priority | Est. Effort

Include ALL of: auth, core features, data management, exports, error handling, notifications, admin panel, API integrations, analytics tracking.

---

## 5. Non-Functional Requirements

### Performance SLAs
| Metric | Requirement | Measurement Method |

### Security & Compliance
| Requirement | Standard | Implementation |

### Scalability Plan
- Phase 1 (0-1K users): architecture
- Phase 2 (1K-10K users): scaling changes
- Phase 3 (10K+ users): major infrastructure changes

---

## 6. Technical Architecture

### Recommended Tech Stack
| Layer | Technology | Justification |
|-------|------------|---------------|
| Frontend | ... | Why this specific choice |
| Backend | ... | Why this specific choice |
| Database | ... | Why this specific choice |
| Cache | ... | Why this specific choice |
| Search | ... | Why this specific choice |
| Auth | ... | Why this specific choice |
| Hosting | ... | Why this specific choice |
| CI/CD | ... | Why this specific choice |

### System Architecture Overview
```
[Draw ASCII architecture diagram showing major components and their connections]
```

### Data Model (Key Entities)
Define the main database tables/collections with key fields:
- Entity name, purpose, key fields, relationships

### API Design (Key Endpoints)
| Method | Endpoint | Description | Request Body | Response |

---

## 7. UI/UX Specifications

### Screen Inventory
List every screen with: name, purpose, key elements, user flow entry/exit points.

### Design System Requirements
- Typography, color palette approach, spacing system
- Component library recommendation
- Responsive breakpoints

### Critical User Flows
Describe 3 core user journeys step-by-step.

---

## 8. QA & Testing Strategy
- Unit testing coverage targets
- Integration testing approach
- E2E testing critical paths
- Performance testing plan
- User acceptance testing (UAT) process

---

## 9. Risk Register & Mitigation Plan

| Risk | Category | Likelihood | Impact | Mitigation Strategy | Owner |
|------|----------|------------|--------|---------------------|-------|

Include: technical, business, regulatory, and team risks.

---

## 10. Project Build Plan & Roadmap

### Phase 1: Foundation (Weeks 1-4)
Week-by-week breakdown:
- Week 1: [specific deliverables]
- Week 2: [specific deliverables]
- Week 3: [specific deliverables]
- Week 4: [milestone: what is demo-ready]

### Phase 2: Core Features (Weeks 5-8)
Week-by-week breakdown with deliverables and milestones.

### Phase 3: Beta & Polish (Weeks 9-12)
Week-by-week with beta launch milestone.

### Phase 4: Launch & Growth (Weeks 13-16)
Public launch, marketing activation, first revenue.

### Team Requirements
| Role | Seniority | Responsibilities | Estimated Start |

---

## 11. Success Metrics & KPIs

### North Star Metric
[The single metric that best captures product value]

### Metric Framework
| Metric | Baseline | Month 1 | Month 3 | Month 6 | Month 12 |
|--------|----------|---------|---------|---------|----------|

### Analytics Implementation
- Events to track (list 10+ specific events)
- Funnel definition
- Dashboard requirements

---

## 12. Launch Checklist

### Pre-Launch (T-4 weeks)
- [ ] Item 1
[List 10+ specific checklist items]

### Launch Week
- [ ] Item 1
[List 10+ specific checklist items]

### Post-Launch (Week 1-4)
- [ ] Item 1
[List 10+ specific monitoring and response items]

---

## Appendix: Open Questions & Decisions Log
| Question | Decision Made | Rationale | Date |

---

This document represents the complete, authoritative specification. Any changes require CPO sign-off."""

        for chunk in groq_client.generate_stream(
            prompt=prompt,
            system_prompt=system_prompt,
            agent_type="syn",
            user_idea=user_idea,
            industry=industry
        ):
            yield chunk
