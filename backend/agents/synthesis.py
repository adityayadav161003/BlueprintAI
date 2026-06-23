from typing import Generator
from backend.agents import BaseAgent


class Synthesis(BaseAgent):
    def __init__(self):
        super().__init__("syn")

    def run(self, groq_client, ba_output: str, pm_output: str, qa_output: str, user_idea: str, industry: str) -> Generator[str, None, None]:
        """
        Final editor — assembles all agent outputs into the complete 12-section PRD.
        """
        system_prompt = f"""You are the final editor producing the complete Product Requirements Document for: "{user_idea}"

ABSOLUTE RULES — violate any and the document is rejected:
1. Every sentence is about "{user_idea}" specifically. Not a template. Not a generic SaaS product.
2. Never write "[insert here]", "[describe feature]", or any placeholder text. Write the actual content.
3. Never use fake competitor names. Only real companies.
4. Never mention ChromaDB, SSE, Ollama, vector databases, or AI pipeline infrastructure.
5. Every KPI must have a real number — not "X%" or "TBD".
6. Every acceptance criterion must be testable with a yes/no answer.
7. The Mermaid diagram nodes must be named after this product's actual components.
8. Write like a senior PM at a well-funded startup. Specific, confident, no filler, no buzzwords.
9. The document must stand alone — a new engineer joining the team should understand the full product from this document."""

        # Trim inputs to fit context
        ba_trimmed = ba_output[:2000] if len(ba_output) > 2000 else ba_output
        pm_trimmed = pm_output[:2000] if len(pm_output) > 2000 else pm_output
        qa_trimmed = qa_output[:1200] if len(qa_output) > 1200 else qa_output

        prompt = f"""Write the complete, final Product Requirements Document for:

PRODUCT: {user_idea}
INDUSTRY: {industry}

BUSINESS ANALYST OUTPUT (use for Sections 1, 2, 3, 4, 5):
{ba_trimmed}

PRODUCT MANAGER OUTPUT (use for Sections 6, 7, 8, 9, 10):
{pm_trimmed}

QA CRITIC OUTPUT (use for Sections 11, 12):
{qa_trimmed}

---

Produce the full PRD below. All 12 sections are mandatory. Write specific content for every section — no placeholders, no generic filler.

---

# {user_idea}
## Product Requirements Document

**Version:** 1.0 | **Status:** Final | **Industry:** {industry}

---

## Executive Summary

Write 3–4 sentences: what "{user_idea}" is, who it's for, the specific problem it solves, and why now is the right time. Make every word count. No generic phrasing.

---

## 1. Problem Statement

Describe the exact problem "{user_idea}" solves. Write it as a real scenario — how does a real user of this product experience this problem today, step by step? How often does it happen? What does it cost them in time, money, or frustration? Why do existing solutions fail them?

This section should make someone reading it think: "Yes, this problem is real and it needs a solution."

---

## 2. Goals & Objectives

List 5–6 specific, measurable goals this product must achieve. Format each as:

**Goal:** [What we achieve]
**Measure:** [How we know we achieved it]
**Target:** [Specific number or outcome]

Cover: user growth, engagement, revenue, retention, and at least one product quality goal.

---

## 3. Scope

### In Scope — MVP (Version 1.0)
List every feature, screen, and capability that will exist when this product launches. Be specific — name the actual flows and functions, not categories.

### Out of Scope — Deliberately Excluded from v1.0
List the features that are excluded from the first version. For each, state why it's excluded and when it will be reconsidered.

---

## 4. Target Users & Stakeholders

### Primary Users
For each user type that genuinely uses "{user_idea}", write:
- **Who they are** — realistic profile (age, situation, tech comfort, geography)
- **What they need** — what they come to this product to accomplish
- **What they do today** — their current workaround before this product exists

Only include user types that actually exist for this product.

### Personas
Present 3 personas who are real users of "{user_idea}". Each must be a distinct person with different circumstances.

For each persona:
**[Name], [Age] — [Occupation], [City]**
- **Pain:** [their specific frustration with the current situation]
- **Goal:** [what they want to achieve using this product]
- **Quote:** "[something they would actually say — in casual language, not corporate speak]"
- **Usage pattern:** [how often and in what context they use this product]

### Key Stakeholders
- **Founder/CEO:** product vision and investor relations
- **Engineering team:** building and maintaining the product
- **Ops/Support team:** handling user issues and moderation
- [Add any other relevant stakeholders for this specific product]

---

## 5. User Flows

Describe the 3 most important end-to-end user flows. Each flow shows exactly what the user does at each step and what the system does in response.

**Flow 1: [Name this flow for {user_idea}]**
1. User: [specific action]
   System: [specific response]
2. User: [specific action]
   System: [specific response]
[...continue until user achieves their goal]

**Flow 2: [Name this flow]**
[Same format]

**Flow 3: [Name this flow]**
[Same format]

---

## 6. System Architecture

[Write one paragraph describing the technical approach for "{user_idea}" — what type of clients (web/mobile), what backend architecture, what databases, what key external services.]

```mermaid
flowchart LR
    User(["👤 User"]) --> App["Frontend App"]
    App --> Auth["Auth Service"]
    App --> API["API Gateway"]
    API --> CoreService["Core Feature Service"]
    API --> AdminPanel["Admin Panel"]
    CoreService --> DB[("Database")]
    CoreService --> FileStorage["File Storage"]
    API --> NotifService["Notification Service"]
    NotifService --> Email["Email"]
    NotifService --> Push["Push Notifications"]
    CoreService --> ExtAPI["External APIs"]
```

Replace every node label above with the actual component name for "{user_idea}". For example, for a dating app: "Cafe Match Engine", "Profile Service", "Date Request API". Add or remove nodes to match what this product actually needs.

---

## 7. Functional Requirements

List every feature this product must have. Every requirement must describe a real feature of "{user_idea}" — not a generic software concept.

| ID | Feature | Description | Acceptance Criteria | Priority |
|----|---------|-------------|---------------------|----------|

Use these priority levels: **P0** = must have at launch, **P1** = first 30 days post-launch, **P2** = future

Group by:
1. **Account & Authentication** (FR-001 to FR-009)
2. **[Core Feature Area 1 — name it for this product]** (FR-010 to FR-029)
3. **[Core Feature Area 2 — name it for this product]** (FR-030 to FR-049)
4. **Notifications** (FR-050 to FR-059)
5. **Admin & Moderation** (FR-060 to FR-079)
6. **Privacy & Data** (FR-080 to FR-089)

Write a minimum of 12 requirements. Every acceptance criterion must be testable.

---

## 8. Non-Functional Requirements

| Category | Requirement | Target | Notes |
|----------|-------------|--------|-------|
| Performance | Page/screen load time | < 2 seconds on 4G | Measured at p95 |
| Performance | API response time | < 500ms | For core actions |
| Scalability | MVP concurrent users | [realistic number for this product] | Single server |
| Scalability | 12-month user growth | [projected number] | Plan architecture accordingly |
| Security | Authentication | [JWT / OAuth2 / specify] | Access + refresh tokens |
| Security | Data encryption | AES-256 at rest, TLS in transit | [note any special PII concerns] |
| Compliance | [applicable law for this product] | [specific requirement] | [deadline if applicable] |
| Availability | Uptime SLA | 99.5% | Maintenance window: [time] |
| Accessibility | WCAG compliance | Level AA | [any specific device requirements] |

Fill in every [bracket] with real values specific to "{user_idea}".

---

## 9. Acceptance Criteria

List the specific, testable pass/fail conditions that must be true before this product can launch. A QA engineer should be able to test each one with a clear yes or no answer.

Group by area:

**Core User Flows**
- [specific pass/fail condition for Flow 1 of {user_idea}]
- [specific pass/fail condition for Flow 2 of {user_idea}]
- [specific pass/fail condition for Flow 3 of {user_idea}]

**Key Features**
- [specific test for each critical feature of {user_idea}]

**Performance**
- App loads in under 2 seconds on a standard 4G connection
- [any product-specific performance requirement]

**Security**
- All authenticated API endpoints return 401 for requests without a valid token
- [any product-specific security requirement]

**Data Integrity**
- [specific data integrity requirement for {user_idea}]

Write a minimum of 15 acceptance criteria total. Make every one specific to this product.

---

## 10. Success Metrics (KPIs)

| Metric | What It Measures | Month 1 Target | Month 6 Target | Month 12 Target |
|--------|-----------------|----------------|----------------|-----------------|

Choose the 6–8 metrics that matter most for this specific type of product. For example:
- A dating/social app: match rate, conversation start rate, D30 retention, date conversion rate
- A marketplace: listings posted, transaction volume, buyer return rate, GMV
- A SaaS tool: activation rate, daily active usage, trial-to-paid conversion, NPS

**North Star Metric:** [The single number that best represents if "{user_idea}" is working]

Every target must be a real number.

---

## 11. Risks & Dependencies

### Risks

| Risk | Category | Likelihood | Impact | Mitigation |
|------|----------|------------|--------|------------|

List 6–8 risks specific to "{user_idea}" and its market context. A dating app has trust and safety risks. A marketplace has fraud and counterfeit risks. Every risk must be something the founding team of this product would genuinely worry about.

### Dependencies

List every external system, service, or API this product depends on to function:

| Dependency | Purpose | What Breaks If It Fails | Fallback |
|-----------|---------|------------------------|---------|

---

## 12. Release Plan

### Phase 1 — Foundation (Weeks 1–4)
**Goal:** Core infrastructure working, users can register and use the primary feature.

| Week | Focus | Deliverables | Done When |
|------|-------|-------------|-----------|
| Week 1 | [specific setup tasks for this product] | [specific output] | [testable milestone] |
| Week 2 | [specific tasks] | [specific output] | [testable milestone] |
| Week 3 | [specific tasks] | [specific output] | [testable milestone] |
| Week 4 | [specific tasks] | [specific output] | [testable milestone] |

### Phase 2 — Core Features (Weeks 5–8)
**Goal:** All must-have features implemented and tested internally.

| Week | Focus | Deliverables | Done When |
|------|-------|-------------|-----------|

### Phase 3 — Beta & Polish (Weeks 9–12)
**Goal:** Real users testing, feedback incorporated, launch-ready.

| Week | Focus | Deliverables | Done When |
|------|-------|-------------|-----------|

### 6-Month Stretch Goals
After the MVP is proven, these are the natural next steps for "{user_idea}":

1. **[Expansion 1]:** [What it is and why it makes sense as a next step for this specific product]
2. **[Expansion 2]:** [Same format]
3. **[Expansion 3]:** [Same format]

---

*PRD Version 1.0 — {user_idea} | {industry} | Generated by BlueprintAI*"""

        for chunk in groq_client.generate_stream(
            prompt=prompt,
            system_prompt=system_prompt,
            agent_type="syn",
            user_idea=user_idea,
            industry=industry
        ):
            yield chunk
