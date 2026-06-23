from typing import Generator
from backend.agents import BaseAgent


class ProductManager(BaseAgent):
    def __init__(self):
        super().__init__("pm")

    def run(self, groq_client, ba_output: str, user_idea: str, industry: str) -> Generator[str, None, None]:
        """
        Executes the Product Manager agent to generate a complete, engineer-ready PRD draft.
        """
        system_prompt = """You are a Principal Product Manager with 12 years of experience at Google, Stripe, and Airbnb.

You have shipped 0-to-1 products used by millions. Your PRDs are legendary because:
- Engineers implement them without a single clarification meeting
- QA teams write test cases directly from your acceptance criteria
- Designers wireframe from your UX specs without guessing
- Investors understand the product vision in 2 minutes

YOUR MANDATORY STANDARDS:
1. NEVER write a functional requirement without explicit acceptance criteria (3+ criteria per requirement).
2. ALWAYS define ALL system roles — not just end-users. Admins, operators, compliance officers, support agents matter.
3. ALWAYS include the complete business workflow — the end-to-end transaction or value chain.
4. ALWAYS define error states, edge cases, and failure scenarios for every major feature.
5. ALWAYS include compliance and regulatory requirements as first-class functional requirements.
6. ALWAYS define notification requirements (what triggers them, who receives them, what channel).
7. ALWAYS include data model hints — what entities need to be stored in the database.
8. ALWAYS define the admin dashboard requirements separately from the customer-facing product.
9. MoSCoW prioritization must reflect what can realistically ship in 12 weeks with a 3-person team.
10. Every user story must follow: "As a [specific role], I want to [specific action], so that [measurable outcome]." """

        prompt = f"""You are drafting a complete Product Requirements Document (PRD) draft.

PRODUCT IDEA: {user_idea}
INDUSTRY: {industry}

BUSINESS ANALYSIS CONTEXT (use this to inform your requirements):
{ba_output[:2800] if len(ba_output) > 2800 else ba_output}

Produce a thorough PRD draft in markdown. Do NOT skip any section. Engineers will read this document on Day 1.

---

# Product Requirements Document — Draft
## Product: {user_idea}
**Version:** 0.9 (Draft) | **Author:** Product Manager | **Status:** Pending QA Review

---

## Executive Summary
- **Product Vision**: (one sentence that captures why this exists)
- **Core Problem**: (the specific pain point with quantification from BA analysis)
- **Our Solution**: (what we build and its unique mechanism)
- **MVP Scope**: (what ships in v1.0 — be explicit about what is IN and OUT)
- **Target Launch**: (realistic timeline assuming 3-5 person team)
- **Success in 6 Months**: (one measurable outcome)

---

## 1. All System Roles & Permissions
Define EVERY role that will interact with the system — customers AND internal users:
| Role | Description | Key Capabilities | Access Level |
|------|-------------|-----------------|--------------|
Include at minimum: [primary customer role], [admin role], [operator/support role]. Add industry-specific roles (e.g., Pharmacist, Driver, Compliance Officer, Instructor, etc.)

---

## 2. End-to-End Business Workflow
Define the complete transaction/value chain for the core product flow:
```
Step 1: [First user action]
    → System response: [what happens in the backend]
Step 2: [Next user action]
    → System response: [validation, routing, storage]
...continue until the value is fully delivered...
Final Step: [Confirmation / delivery / completion]
    → Post-completion: [notifications, records, follow-ups]
```
This is the backbone of your data model and API design.

---

## 3. User Personas (3 Complete Profiles)
For each persona:
### Persona [N]: [Name, Role]
- **Demographics**: age, location, job title, company size
- **Daily Workflow**: how they currently work (before your product)
- **Primary Pain Points**: what wastes their time or money
- **Goals**: what success looks like for them
- **Technology Comfort**: which tools they already use
- **Budget Authority**: can they sign off on payment themselves?
- **Representative Quote**: a realistic quote expressing their frustration
- **How They'll Use the Product**: typical weekly usage pattern

---

## 4. User Stories — MoSCoW Prioritization

### 🔴 Must Have (MVP — Sprint 1-4, ship in ≤ 12 weeks)
For each story:
**[US-XXX]** As a [role], I want to [action], so that [measurable outcome].
- **Priority**: Must Have
- **Story Points**: [1-13 Fibonacci]
- **Acceptance Criteria**:
  - Given [context], when [action], then [result]
  - Given [error context], when [action], then [error state shown]
  - [Performance criterion if applicable]

Include stories for: onboarding, core value delivery, payment/monetization, admin management, notifications, error recovery.
Aim for 10-12 Must Have stories.

### 🟡 Should Have (Sprint 5-6, second iteration)
5-6 stories with brief acceptance criteria.

### 🟢 Could Have (Post-MVP, 3+ months)
3-4 stories with one-line description.

### ⚫ Won't Have (Explicitly OUT of MVP scope)
3-5 items with justification for exclusion.

---

## 5. Functional Requirements

Complete table. Every row must have full acceptance criteria.

| ID | Feature | Role | Description | Acceptance Criteria | Priority | Dependencies |
|----|---------|------|-------------|---------------------|----------|--------------|

Organize into these groups (add product-specific features within each group):

### 5.1 Authentication & Account Management
- User registration (email, social, phone)
- Login / logout
- Password reset
- Profile management
- Account deletion (GDPR right to erasure)
- Role-based access control

### 5.2 Core Product Features
[Write all product-specific features here — this is the heart of the product]
Be exhaustive. Include the complete workflow from section 2 as individual requirements.

### 5.3 Admin & Operator Dashboard
- User management (view, suspend, delete accounts)
- Content/order/transaction management
- Analytics and reporting views
- System health monitoring
- Configuration management

### 5.4 Payment & Billing
- Payment method collection (card, UPI, etc.)
- Payment processing
- Invoice generation
- Refund handling
- Payment failure retry

### 5.5 Notifications & Communications
| Trigger Event | Recipients | Channel (Email/SMS/Push) | Template Description |
List ALL notification triggers explicitly.

### 5.6 Compliance & Regulatory Requirements
[Industry-specific — e.g., for healthcare: prescription verification, pharmacist approval workflow, controlled substances; for fintech: KYC, AML; for edtech: COPPA]
- Each compliance requirement must be a first-class functional requirement with acceptance criteria.

### 5.7 Data Management & Privacy
- Data collection scope
- Data retention policy (how long is data kept?)
- Data deletion on account closure
- Export of personal data (GDPR portability)
- Audit logging requirements

---

## 6. Non-Functional Requirements

### 6.1 Performance SLAs
| Metric | Requirement | Measurement |
|--------|-------------|-------------|
| API response time (p50) | < 200ms | Datadog APM |
| API response time (p95) | < 500ms | Datadog APM |
| Page load time | < 2s (LCP) | Lighthouse |
| Uptime SLA | 99.9% monthly | Status page |
| Database query time (p95) | < 100ms | Query logs |

### 6.2 Security Requirements
- Authentication: [JWT / OAuth2 / Session-based — specify]
- Password policy: minimum requirements
- Data encryption at rest: [specify algorithm]
- Data encryption in transit: TLS 1.2+
- Session management: timeout rules
- Rate limiting: requests per minute per IP
- Input validation: XSS, SQL injection, CSRF protection
- Secrets management: environment variables, no hardcoded keys

### 6.3 Scalability Plan
| Phase | Users | Architecture | Database | Infra Cost/mo |
|-------|-------|-------------|----------|---------------|
| MVP | 0–500 | Monolith | Single DB | ~$50-100 |
| Growth | 500–10K | Modular monolith | Read replicas | ~$200-500 |
| Scale | 10K+ | Microservices (selective) | Sharding/caching | ~$1,000+ |

### 6.4 Accessibility
- WCAG 2.1 Level AA compliance
- Screen reader support (ARIA labels)
- Keyboard navigation for all interactive elements
- Minimum contrast ratio: 4.5:1

---

## 7. UI/UX Requirements

### 7.1 Screen Inventory
| Screen Name | Primary Role | Purpose | Entry Point | Exit Points |
|-------------|-------------|---------|-------------|-------------|
List every screen in the application.

### 7.2 Critical User Flows
Describe the 3 most important user journeys step-by-step (numbered steps).

### 7.3 Design Principles
- 3-5 design principles specific to this product
- Component library recommendation (e.g., shadcn/ui, Material UI, Ant Design)
- Responsive breakpoints: mobile (320px), tablet (768px), desktop (1280px)

---

## 8. Technical Constraints & Assumptions
- **Platform targets**: web-first, then iOS/Android (or native-first — specify)
- **Browser support**: Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
- **Third-party APIs**: list any external services (payment gateway, maps, SMS, etc.)
- **Known limitations**: anything that constrains technical choices
- **Assumptions**: decisions made without full validation (flag these for the QA agent)

---

## 9. Data Entities (Key Database Tables)
Hint to engineers what data needs to be persisted:
| Entity | Purpose | Key Fields | Relationships |
|--------|---------|-----------|---------------|
Include all entities that appear in the business workflow.

---

## 10. MVP Exclusions (Explicit Out-of-Scope List)
| Feature | Why Excluded from MVP | When to Consider |
|---------|----------------------|-----------------|

---

This draft is ready for QA Critic review."""

        for chunk in groq_client.generate_stream(
            prompt=prompt,
            system_prompt=system_prompt,
            agent_type="pm",
            user_idea=user_idea,
            industry=industry
        ):
            yield chunk
