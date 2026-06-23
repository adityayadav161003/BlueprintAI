from typing import Generator
from backend.agents import BaseAgent


class Synthesis(BaseAgent):
    def __init__(self):
        super().__init__("syn")

    def run(self, groq_client, pm_output: str, qa_output: str, user_idea: str, industry: str) -> Generator[str, None, None]:
        """
        Executes the Synthesis agent — produces the final board-ready, investor-grade PRD.
        """
        system_prompt = """You are the Chief Product Officer (CPO) of a unicorn startup. You have taken 3 products from $0 to $100M ARR.

You are writing the FINAL, DEFINITIVE Product Requirements Document. This document:
- Gets handed to the engineering team on Day 1 of development
- Gets presented to seed investors in fundraising
- Gets referenced by QA teams for every sprint
- Gets used by the CEO to explain the product to the board

YOUR ABSOLUTE STANDARDS:
1. Incorporate EVERY valid concern raised by the QA Critic. If a QA gap is in the input — it MUST be fixed in your output.
2. Include ALL user roles — not just the primary customer. Missing roles = missing product areas.
3. The business workflow must be complete, step-by-step, and map directly to functional requirements.
4. Compliance requirements must be first-class functional requirements with acceptance criteria — not footnotes.
5. Technical architecture must name SPECIFIC technologies with specific justifications.
6. The data model must define key entities, fields, and relationships — not just mention "a database".
7. API design must include real endpoints with HTTP methods, paths, request, and response shapes.
8. The roadmap must be WEEK-BY-WEEK, not "Phase 1, Phase 2, Phase 3" with vague timelines.
9. KPIs must include baseline, targets, and measurement methodology.
10. The launch checklist must be actionable — every item should be assignable to a specific role.
11. Format for Notion/Confluence publication quality — professional tables, clear headers, scannable layout.
12. Do NOT copy-paste from the draft — synthesize, elevate, and fix everything.
13. This document must stand alone. A new hire must understand the entire product from this document in 30 minutes."""

        prompt = f"""You are producing the FINAL, board-ready Product Requirements Document.

PRODUCT IDEA: {user_idea}
INDUSTRY: {industry}

DRAFT PRD (PM's first pass — synthesize and improve):
{pm_output[:2200] if len(pm_output) > 2200 else pm_output}

QA CRITIC REPORT (ALL gaps MUST be addressed in your output):
{qa_output[:1800] if len(qa_output) > 1800 else qa_output}

Produce the complete final PRD below. Every section is mandatory. Do not omit, summarize, or truncate any section.

---

# {user_idea}
# Product Requirements Document

**Version:** 1.0 | **Status:** ✅ Final | **Classification:** Internal — Confidential
**Prepared by:** Product & Engineering Leadership | **Review Cycle:** Quarterly

---

## Executive Summary

| Field | Detail |
|-------|--------|
| **Product Vision** | [One powerful sentence: what world does this create?] |
| **Core Problem** | [Specific pain point with quantification] |
| **Our Solution** | [What we build and the unique mechanism] |
| **Target Customer** | [Specific segment — not "everyone"] |
| **Business Model** | [Primary and secondary revenue streams] |
| **MVP Launch Target** | [Realistic date assuming team size of X] |
| **Success in 6 Months** | [Specific measurable outcome — MRR, users, etc.] |

---

## 1. Problem Statement & Opportunity

### The Problem (Real-World Scenario)
[Write a concrete scenario: "Maria is a 45-year-old diabetic who... Every month she..."]

### Why Existing Solutions Fail
[For each major existing alternative, explain the specific failure mode]

### Market Timing (Why Now)
[3 specific reasons this is viable NOW — regulatory changes, behavior shifts, technology readiness]

### Cost of Inaction for the Customer
[Quantify: "$X wasted per year", "Y hours lost per week", "Z% error rate"]

---

## 2. All System Roles & Permission Matrix

Every role that will interact with the platform:

| Role | Description | Core Capabilities | Access Level | Notes |
|------|-------------|------------------|--------------|-------|
[Include ALL roles: end-user, admin, operator, support, compliance officer, and any industry-specific roles]

---

## 3. End-to-End Business Workflow

The complete transaction/value chain — this is the backbone of the system design:

```
WORKFLOW: [Core Product Flow Name]
═══════════════════════════════════════════════════════

Step 1: [User Action]
  Actor: [Role]
  System: [What happens in the backend — validation, storage, routing]
  Success: [What the user sees]
  Failure: [What happens if this step fails]

Step 2: [Next Action]
  Actor: [Role]
  System: [Processing description]
  Success: [Outcome]
  Failure: [Error handling]

[...continue for ALL steps until value is fully delivered...]

Final Step: [Completion / Delivery]
  System: [Confirmation, records, audit log entry]
  Post-Completion: [Notifications triggered, refill reminders, invoices, etc.]
```

---

## 4. User Personas

### Persona 1: [Name] — [Primary Role]
| Field | Detail |
|-------|--------|
| Demographics | Age, location, job title, company/situation |
| Daily Workflow | How they work TODAY (before this product) |
| Primary Pain Points | Top 3 frustrations with the current way |
| Goals | What success looks like for them |
| Technology Stack | Apps and tools they already use |
| Budget Authority | Can they purchase independently? |
| Representative Quote | A sentence they would actually say |
| Product Usage Pattern | How often, when, and for what |

### Persona 2: [Name] — [Secondary Role]
[Same structure]

### Persona 3: [Name] — [Admin/Operator Role]
[Same structure — this is your internal user who manages the platform]

---

## 5. Prioritized User Stories (MoSCoW)

### 🔴 Must Have — Sprint 1-4 (Weeks 1-12)
These are the minimum to deliver real value. Without these, the product doesn't work.

**[US-001]** As a [role], I want to [action], so that [measurable outcome].
- Story Points: X | Priority: P0
- Acceptance Criteria:
  - ✅ Given [normal context], when [action taken], then [expected result]
  - ✅ Given [edge case], when [action taken], then [graceful handling]
  - ✅ Given [error condition], when [action taken], then [user-friendly error displayed]
  - ✅ Performance: [e.g., "response within 2 seconds"]

[Write 10-14 Must Have stories covering: onboarding, core value delivery, payments, admin management, compliance, notifications, error recovery]

### 🟡 Should Have — Sprint 5-6
5-6 stories with acceptance criteria (2 criteria each minimum)

### 🟢 Could Have — Post-MVP (Month 4+)
4-5 stories with one-line descriptions

### ⚫ Won't Have — Explicit MVP Exclusions
| Feature | Justification | Revisit When |
|---------|--------------|--------------|

---

## 6. Functional Requirements

### 6.1 Authentication & Account Management
| ID | Feature | Description | Acceptance Criteria | Priority |
|----|---------|-------------|---------------------|----------|
| FR-001 | User Registration | ... | AC1; AC2; AC3 | P0 |
| FR-002 | Login | ... | ... | P0 |
| FR-003 | Password Reset | ... | ... | P0 |
| FR-004 | Account Deletion | GDPR right to erasure — delete all PII on request within 30 days | ... | P1 |
| FR-005 | Role-Based Access Control | ... | ... | P0 |

### 6.2 Core Product Features
[All product-specific features — map directly to workflow steps from Section 3]
| ID | Feature | Description | Acceptance Criteria | Priority |
Use IDs FR-010 through FR-099 for core features.

### 6.3 Admin & Operator Dashboard
| ID | Feature | Description | Acceptance Criteria | Priority |
|----|---------|-------------|---------------------|----------|
| FR-100 | User Management | View, filter, suspend, reinstate, delete users | ... | P0 |
| FR-101 | Transaction/Order Management | View all transactions with filters and search | ... | P0 |
| FR-102 | Analytics Dashboard | Key metrics: DAU, MAU, revenue, conversion, retention | ... | P1 |
| FR-103 | Support Tools | View user history, add internal notes, escalation | ... | P1 |
| FR-104 | Configuration Management | Feature flags, rate limits, pricing updates | ... | P1 |
| FR-105 | Audit Log | Tamper-proof log of all admin actions with user, timestamp, action | ... | P0 |

### 6.4 Payment & Billing
| ID | Feature | Description | Acceptance Criteria | Priority |
|----|---------|-------------|---------------------|----------|
| FR-200 | Payment Collection | Accept [card / UPI / bank transfer] via [Stripe/Razorpay/etc.] | ... | P0 |
| FR-201 | Payment Failure Handling | Retry logic, user notification, order hold | ... | P0 |
| FR-202 | Refund Processing | Initiate, track, and confirm refunds with timeline | ... | P0 |
| FR-203 | Invoice Generation | Auto-generate PDF invoice per transaction | ... | P1 |
| FR-204 | Subscription Management | Upgrade, downgrade, cancel, reactivate | ... | P1 |

### 6.5 Notifications & Communications
| Trigger Event | Actor Notified | Channel | Message Summary |
|--------------|---------------|---------|----------------|
[List ALL notification triggers — every important system event must trigger a notification]

### 6.6 Compliance & Regulatory Requirements
[These are first-class functional requirements — not footnotes]
| ID | Regulation | Requirement | Acceptance Criteria | Priority |
|----|-----------|-----------|----|
[List ALL applicable regulations for the product's industry with specific implementation requirements]

### 6.7 Data Management & Privacy
| ID | Feature | Description | Acceptance Criteria | Priority |
|----|---------|-------------|---------------------|----------|
| FR-400 | Data Retention Policy | [Specify: how long each data type is retained] | ... | P0 |
| FR-401 | Personal Data Export | User can download all their data in JSON/CSV | ... | P1 |
| FR-402 | Account Deletion | Delete all PII on request, retain anonymized analytics | ... | P1 |
| FR-403 | Consent Management | Explicit consent for data processing, recorded with timestamp | ... | P0 |
| FR-404 | Audit Trail | Log all data access and modifications for compliance | ... | P0 |

---

## 7. Non-Functional Requirements

### 7.1 Performance SLAs
| Metric | Requirement | Breach Response | Measurement |
|--------|-------------|-----------------|-------------|
| API p50 latency | < 200ms | Alert engineering | Datadog |
| API p95 latency | < 500ms | PagerDuty alert | Datadog |
| Page LCP | < 2.5s | Sprint hotfix | Lighthouse CI |
| Uptime | 99.9%/month | Incident response | Status page |
| DB query p95 | < 100ms | Query optimization | Slow query log |
| File upload | < 30s for 10MB | Progress indicator | Client-side |

### 7.2 Security Requirements
| Requirement | Standard | Implementation |
|------------|---------|----------------|
| Authentication | OAuth2 / JWT | [Specify: access token expiry, refresh token rotation] |
| Password storage | OWASP | bcrypt with cost factor 12+ |
| Data at rest | AES-256 | Database-level encryption |
| Data in transit | TLS 1.2+ | Enforce HTTPS, HSTS header |
| API security | OWASP Top 10 | Rate limiting, input validation, SQL injection prevention |
| Secrets | 12-factor | Environment variables, secret manager |
| PII masking | Internal | Mask PII in logs, error messages |
| Session security | OWASP | Secure, HttpOnly, SameSite cookies |
| Vulnerability scanning | DevSecOps | SAST in CI/CD pipeline |

### 7.3 Scalability Plan
| Phase | Users | Architecture | DB Strategy | Monthly Infra Cost |
|-------|-------|--------------|-------------|-------------------|
| MVP | 0–1,000 | Monolith on single VM | Single PostgreSQL | ~$80-150 |
| Growth | 1K–20K | Modular monolith, CDN for assets | Read replicas | ~$300-600 |
| Scale | 20K+ | Selective microservices | Connection pooling, caching layer | ~$1,000+ |

### 7.4 Accessibility
- WCAG 2.1 Level AA compliance
- Screen reader support: ARIA landmarks, roles, and labels
- Keyboard navigation: all interactive elements reachable via Tab
- Color contrast: minimum 4.5:1 for normal text, 3:1 for large text
- Focus indicators: visible focus ring on all interactive elements

---

## 8. Technical Architecture

### 8.1 Recommended Tech Stack
| Layer | Technology | Justification |
|-------|------------|---------------|
| Frontend | [React / Next.js / Vue — specify] | [Specific reason: SSR needs, team expertise, ecosystem] |
| Backend | [Node.js/Express / FastAPI / Django — specify] | [Specific reason] |
| Database (Primary) | [PostgreSQL / MySQL — specify] | [Specific reason: ACID, relational needs, JSON support] |
| Cache | [Redis — specify] | [Session storage, rate limiting, frequently accessed queries] |
| File Storage | [AWS S3 / GCS — specify] | [Object storage for uploads, CDN integration] |
| Authentication | [Auth0 / Supabase Auth / Firebase Auth / custom JWT] | [Specific reason] |
| Payment | [Stripe / Razorpay / PayPal — specify] | [Coverage, fee structure, regional support] |
| Email | [SendGrid / AWS SES — specify] | [Deliverability, template management] |
| SMS / OTP | [Twilio / AWS SNS — specify] | [If applicable] |
| Hosting | [AWS / GCP / Railway / Render — specify] | [Cost, region, team familiarity] |
| CI/CD | [GitHub Actions / GitLab CI — specify] | [Automated testing and deployment] |
| Monitoring | [Datadog / Sentry / New Relic — specify] | [Error tracking, APM, alerting] |

### 8.2 System Architecture Diagram
```
┌─────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                          │
│  [Web Browser]              [Mobile App - future]            │
│       │                           │                          │
└───────┼───────────────────────────┼──────────────────────────┘
        │ HTTPS                     │
┌───────▼───────────────────────────▼──────────────────────────┐
│                     CDN / LOAD BALANCER                       │
│              [CloudFront / Nginx / Vercel Edge]               │
└───────────────────────────┬──────────────────────────────────┘
                            │
┌───────────────────────────▼──────────────────────────────────┐
│                    APPLICATION SERVER                          │
│                 [Backend API — REST / GraphQL]                │
│                                                              │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────────┐ │
│  │ Auth Module │  │ Core Feature │  │ Admin/Ops Module    │ │
│  │  (JWT/OAuth)│  │   Modules    │  │ (Dashboard + RBAC)  │ │
│  └─────────────┘  └──────────────┘  └─────────────────────┘ │
└──────────┬─────────────────────────────────┬─────────────────┘
           │                                 │
┌──────────▼────────────┐       ┌────────────▼────────────────┐
│   PRIMARY DATABASE    │       │       CACHE LAYER           │
│   [PostgreSQL]        │       │   [Redis — sessions,        │
│   ACID, relational    │       │    rate limits, hot data]   │
└──────────┬────────────┘       └─────────────────────────────┘
           │
┌──────────▼────────────────────────────────────────────────────┐
│                    EXTERNAL SERVICES                           │
│  [Payment API]  [Email Service]  [SMS/OTP]  [File Storage]    │
│  [Maps API]     [Analytics]      [Monitoring]                 │
└───────────────────────────────────────────────────────────────┘
```

### 8.3 Data Model — Key Entities
| Entity | Purpose | Key Fields | Relationships |
|--------|---------|-----------|---------------|
[Define every entity that appears in the business workflow with its primary fields]
Example row: `users | Customer accounts | id, email, role, created_at, status | has many orders`

### 8.4 API Design — Key Endpoints
| Method | Endpoint | Description | Auth Required | Request Body | Response |
|--------|---------|-------------|--------------|-------------|---------|
[Define all major API endpoints — minimum 12 endpoints covering all major features]
Example: `POST | /api/v1/auth/register | Register new account | No | {{email, password, name}} | {{user, token}}`

---

## 9. UI/UX Specifications

### 9.1 Screen Inventory
| Screen | Role | Purpose | Entry Point | Exit Points |
|--------|------|---------|-------------|-------------|
[List every screen in the application]

### 9.2 Critical User Flows

**Flow 1: [Primary Onboarding Flow]**
Step 1 → Step 2 → Step 3 → ... → [First value moment]

**Flow 2: [Core Value Delivery Flow]**
Step 1 → Step 2 → ... → [Value delivered]

**Flow 3: [Payment / Conversion Flow]**
Step 1 → Step 2 → ... → [Transaction complete]

### 9.3 Design System
- **Component Library**: [shadcn/ui / Ant Design / Material UI — specify with reason]
- **Typography**: [Font family, scale — e.g., Inter, 14/16/20/24/32px]
- **Color System**: [Primary brand color, semantic colors for success/error/warning]
- **Spacing**: [8px base grid]
- **Responsive Breakpoints**: 320px (mobile), 768px (tablet), 1280px (desktop)

---

## 10. QA & Testing Strategy
| Test Type | Scope | Tool | Coverage Target | Frequency |
|-----------|-------|------|-----------------|-----------|
| Unit Tests | Business logic, utilities | Jest / Pytest | ≥ 80% | Every commit |
| Integration Tests | API endpoints, DB queries | Supertest / Pytest | Critical paths | Every PR |
| E2E Tests | Core user flows (3 flows) | Playwright / Cypress | 3 critical flows | Every release |
| Performance Tests | Load testing key endpoints | k6 / Locust | p95 < 500ms at 100 RPS | Pre-release |
| Security Scan | OWASP Top 10 | OWASP ZAP / Snyk | Full scan | Monthly |
| UAT | End-to-end with real users | Manual | All Must Have stories | Pre-launch |

---

## 11. Risk Register & Mitigation Plan
| Risk | Category | Likelihood | Impact | Mitigation | Owner | Review Date |
|------|----------|------------|--------|------------|-------|-------------|
[Include minimum 8 risks covering: technical, compliance, market, competitive, team, financial]

---

## 12. Project Roadmap — Week by Week

### Phase 1: Foundation (Weeks 1-4)
**Goal**: Core infrastructure, auth, and data model running.
| Week | Deliverables | Milestone |
|------|-------------|-----------|
| Week 1 | Project setup, CI/CD pipeline, database schema, auth skeleton | Dev environment live |
| Week 2 | User registration, login, role-based access, basic API structure | Auth complete |
| Week 3 | [Core Feature 1 backend], admin dashboard scaffold | First API integrated |
| Week 4 | [Core Feature 1 frontend], basic UI, internal demo | ✅ Demo-ready MVP skeleton |

### Phase 2: Core Features (Weeks 5-8)
**Goal**: All Must Have user stories implemented and tested.
| Week | Deliverables | Milestone |
|------|-------------|-----------|
| Week 5 | [Core Feature 2] — backend + frontend | Feature 2 complete |
| Week 6 | Payment integration, billing flow, invoice generation | ✅ Payments live |
| Week 7 | Notifications (email + SMS), compliance features | Notifications live |
| Week 8 | Admin dashboard complete, audit logging, internal QA | ✅ Feature-complete internally |

### Phase 3: Beta & Polish (Weeks 9-12)
**Goal**: Beta user onboarding, bug fixing, performance optimization.
| Week | Deliverables | Milestone |
|------|-------------|-----------|
| Week 9 | Private beta launch (25-50 users), feedback collection | ✅ Beta live |
| Week 10 | Bug fixes from beta feedback, UX polish | Beta stable |
| Week 11 | Performance optimization, security audit, load testing | Performance validated |
| Week 12 | Final UAT, documentation, production deploy prep | ✅ Launch-ready |

### Phase 4: Launch & Growth (Weeks 13-16)
**Goal**: Public launch, first paying customers, initial growth.
| Week | Deliverables | Milestone |
|------|-------------|-----------|
| Week 13 | Public launch, marketing activation, press/social | ✅ Public v1.0 live |
| Week 14 | Monitor KPIs, support first users, quick fixes | Operations stable |
| Week 15 | First revenue milestone, referral program launch | ✅ First $X MRR |
| Week 16 | Retrospective, Should Have features begin, Series A prep | v1.1 planning begins |

### Team Requirements
| Role | Level | Key Responsibilities | When Needed |
|------|-------|---------------------|-------------|
| Full-Stack Engineer | Senior | Backend API + database + core features | Week 1 |
| Frontend Engineer | Mid-Senior | React UI, responsive design, UX flows | Week 1 |
| Product Manager | Lead | Specs, prioritization, stakeholder comms | Week 1 |
| UI/UX Designer | Mid | Wireframes, design system, user testing | Week 1-8 |
| QA Engineer | Mid | Test automation, UAT coordination | Week 7+ |
| DevOps / Infra | Fractional | CI/CD, cloud infra, security | Week 1, then as needed |

---

## 13. Success Metrics & KPIs

### North Star Metric
**[The single metric]** — Definition: [exactly how it's calculated]

### Full KPI Framework
| Metric | Baseline | Month 1 | Month 3 | Month 6 | Month 12 | Measurement |
|--------|----------|---------|---------|---------|----------|-------------|
| Monthly Recurring Revenue (MRR) | $0 | $X | $X | $X | $X | Stripe |
| Monthly Active Users (MAU) | 0 | X | X | X | X | Product analytics |
| Day-30 Retention | — | X% | X% | X% | X% | Cohort analysis |
| Activation Rate (first core action) | — | X% | X% | X% | X% | Funnel analytics |
| Customer Acquisition Cost (CAC) | — | $X | $X | $X | $X | Marketing spend ÷ new customers |
| LTV:CAC Ratio | — | X:1 | X:1 | X:1 | X:1 | LTV ÷ CAC |
| Net Promoter Score (NPS) | — | X | X | X | X | Quarterly survey |
| Churn Rate (monthly) | — | X% | X% | X% | X% | Cancelled ÷ active |

### Analytics Implementation
Core events to track (minimum):
1. `user_registered` — source, device, plan
2. `user_activated` — time to first core action
3. `[core_action]_completed` — primary value event
4. `payment_initiated` — amount, method
5. `payment_completed` — amount, method, plan
6. `payment_failed` — error code, amount
7. `feature_used` — which feature, frequency
8. `user_churned` — reason (if captured)
9. `support_ticket_created` — category, severity
10. `admin_action_performed` — action type, admin id

---

## 14. Launch Checklist

### Pre-Launch — T-4 Weeks
- [ ] All Must Have user stories pass UAT
- [ ] Security audit completed (OWASP Top 10 verified)
- [ ] Load test passed: [X] concurrent users at p95 < 500ms
- [ ] Payment processing tested in production environment with real transactions
- [ ] All compliance requirements verified (see Section 6.6)
- [ ] Privacy Policy and Terms of Service live on website
- [ ] Cookie consent / data consent flow implemented
- [ ] Error monitoring (Sentry) configured with alert routing
- [ ] Uptime monitoring and status page live
- [ ] Database backups automated and restore tested
- [ ] GDPR data deletion flow tested end-to-end
- [ ] Admin dashboard tested by operations team

### Launch Week
- [ ] Feature flags tested (can disable any feature without deploy)
- [ ] Rollback plan documented and tested
- [ ] Customer support email / chat configured
- [ ] Onboarding email sequence activated
- [ ] Analytics verified (all key events firing correctly in production)
- [ ] All DNS, SSL certificates valid and auto-renewing
- [ ] Marketing site live with accurate product description
- [ ] Product hunt / launch campaign scheduled
- [ ] Team on-call schedule defined for launch week

### Post-Launch — Week 1-4
- [ ] Daily KPI review: activation, retention, revenue, errors
- [ ] User feedback collection: in-app NPS or Typeform survey activated
- [ ] Week 1: Review all support tickets and categorize by root cause
- [ ] Week 2: First cohort retention analysis (Day-7)
- [ ] Week 2: Fix top 3 bugs reported by real users
- [ ] Week 4: First retrospective: what's working, what's not
- [ ] Week 4: Day-30 retention analysis for launch cohort
- [ ] Week 4: Should Have features prioritization for v1.1

---

## Appendix: Decisions Log
| Decision | Options Considered | Decision Made | Rationale | Decided By | Date |
|----------|-------------------|--------------|-----------|-----------|------|

---

*This document is the single source of truth for the {user_idea} product. All changes require review by the Product Manager and sign-off by the CPO. Version history maintained in Git.*"""

        for chunk in groq_client.generate_stream(
            prompt=prompt,
            system_prompt=system_prompt,
            agent_type="syn",
            user_idea=user_idea,
            industry=industry
        ):
            yield chunk
