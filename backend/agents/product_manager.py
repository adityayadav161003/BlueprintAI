from typing import Generator
from backend.agents import BaseAgent


class ProductManager(BaseAgent):
    def __init__(self):
        super().__init__("pm")

    def run(self, groq_client, ba_output: str, user_idea: str, industry: str) -> Generator[str, None, None]:
        """
        Executes the Product Manager agent — Sections 6-9 of the PRD.
        """
        system_prompt = f"""You are a senior Product Manager at a well-funded startup. You will translate user needs into precise product requirements for: "{user_idea}"

THE MOST CRITICAL RULE:
Everything you write must describe features and requirements of "{user_idea}" ONLY.

ABSOLUTE PROHIBITIONS:
- Never write user stories that could apply to a different product
- Never describe ChromaDB, SSE streaming, Ollama, vector databases, or any AI pipeline infrastructure as features of the user's product
- Never use placeholder competitor names
- Never write functional requirements for a generic SaaS template — write them for THIS specific product
- Never include stories like "generate a structured outline" unless the product literally is a document generator

QUALITY GATE: For every user story and functional requirement, ask: "Is this an action a real user of {user_idea} would actually perform?" If no, delete it."""

        prompt = f"""You are a senior Product Manager. You have received business context from the BA agent. Now translate user needs into precise product requirements for:

PRODUCT: {user_idea}
INDUSTRY: {industry}

BUSINESS CONTEXT FROM BA AGENT:
{ba_output[:3000] if len(ba_output) > 3000 else ba_output}

Produce the following sections. Everything must describe features of "{user_idea}" only.

---

## 6. System Architecture

Write one paragraph describing the technical architecture of "{user_idea}": what type of clients (web/mobile), what backend, what databases, what key external services.

Then produce a Mermaid flowchart. Name every node after the actual components of "{user_idea}" — for example, a placement app might have nodes named "Placement Portal", "Job Match Service", "Resume Storage", "Company API". Do NOT use generic labels like "Core Service" or "Frontend App". Build the diagram from the product's real architecture.

```mermaid
flowchart LR
    [build the diagram here with product-specific node names]
```

---

## 7. Prioritized User Stories

Write 10–15 user stories using the format:
"As a [specific persona type from the BA analysis], I want to [perform a specific action in {user_idea}], so that [specific outcome or benefit]."

**Must-Have (core loop — without these the product doesn't work):**
At least 5 stories covering the primary user flow end-to-end in {user_idea}.

**Should-Have (significantly improves experience):**
At least 3 stories for important but non-blocking features.

**Could-Have (nice to have, defer if needed):**
2–3 stories for enhancements.

For each story, include Acceptance Criteria:
- Given [specific context in {user_idea}], When [specific user action], Then [specific system behavior or outcome]

CRITICAL: Every story must describe a real action inside {user_idea}. Never reuse generic stories that could apply to any app.

---

## 8. Functional Requirements

List 10–15 functional requirements as a table:

| ID | Feature Area | Description | Acceptance Criteria | Priority |
|----|-------------|-------------|---------------------|----------|

Requirements must cover the areas relevant to {user_idea}:
- Core product actions (what users primarily DO in this product day to day)
- Data management (what information is stored, retrieved, updated)
- User authentication and account management
- Search, filter, or discovery features (if applicable to this product)
- Notifications or communication features (if applicable)
- Transaction or payment flows (if applicable)
- Moderation or admin capabilities (if applicable)

CRITICAL: Every requirement must describe a feature of "{user_idea}". Do NOT describe the AI pipeline, SSE streaming, ChromaDB, Ollama, or any internal tool infrastructure. Those are implementation details of the generator, not the product.

---

## 9. Non-Functional Requirements

Cover all of the following for {user_idea} specifically:

**Performance:** What are the load time and response time requirements? How many concurrent users should the MVP support? Are there any real-time requirements specific to this product type?

**Scalability:** What is the realistic user growth trajectory for this product? What data volumes should the system handle at launch vs. 6 months vs. 12 months?

**Security:** What authentication method is appropriate? What sensitive data does this product handle (location, payment, personal identity, messages, etc.) and how must it be protected?

**Compliance:** What laws and regulations apply to {user_idea} in its target geography? Consider: data privacy laws (GDPR, IT Act, CCPA), industry-specific regulations, age verification requirements, financial regulations (if payments are involved).

**Availability:** What uptime SLA is required? Are there peak usage patterns to plan for?

**Accessibility:** What WCAG level is targeted? What device and browser support is required at launch?

---

## 10. Success Metrics & KPIs

Define measurable success for {user_idea} across all five stages. Every metric must be relevant to this specific product type.

**Acquisition:** How do we know users are discovering and signing up?
Include: sign-up conversion rate, primary acquisition channel, CAC target

**Activation:** How do we know users completed their first meaningful action in {user_idea}?
Define what "activated" means specifically for this product (e.g., first match made, first listing posted, first purchase, first date booked) and the target rate.

**Retention:** How do we know users come back?
Include: D7 retention target, D30 retention target, WAU/MAU ratio target

**Revenue:** How does {user_idea} make money and what are the Month 3 and Month 12 targets?
Include: primary revenue model, price point, MRR or GMV target

**Satisfaction:** How do we measure user happiness?
Include: NPS target, app store rating target, primary feedback channel

All metrics must have specific target numbers — not "X%" or "TBD"."""

        for chunk in groq_client.generate_stream(
            prompt=prompt,
            system_prompt=system_prompt,
            agent_type="pm",
            user_idea=user_idea,
            industry=industry
        ):
            yield chunk
