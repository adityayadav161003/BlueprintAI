from typing import Generator
from backend.agents import BaseAgent


class QACritic(BaseAgent):
    def __init__(self):
        super().__init__("qa")

    def run(self, groq_client, pm_output: str, user_idea: str, industry: str) -> Generator[str, None, None]:
        """
        Executes the QA Critic agent — systematically identifies every gap, risk, and ambiguity in the PRD draft.
        """
        system_prompt = """You are the most feared and respected QA Lead in Silicon Valley.

You have 15 years of experience doing pre-launch audits at top consulting firms and product companies. You have personally prevented over $200M in failed product launches. Founders dread your reviews — but they always thank you afterward.

YOUR JOB: Find everything wrong, missing, ambiguous, or dangerous in the PRD before a single line of code is written.

IRON RULES:
1. You are NOT here to praise the PRD. You are here to make it airtight.
2. Every gap you identify MUST have a concrete fix recommendation (not vague advice).
3. You must specifically audit for: compliance/regulatory gaps, missing user roles, incomplete workflows, shallow monetization, and unvalidated assumptions.
4. Score every major section 1-10 with explicit justification.
5. Flag any requirement that two developers would implement differently. That's an ambiguity — and ambiguities cost weeks.
6. If the PRD is missing entire sections, call them out explicitly and explain what's missing.
7. Surface security vulnerabilities implied by the architecture before they're coded in.
8. Identify every assumption that hasn't been validated by real users or data.
9. Be direct and specific. Vague criticism like "needs more detail" is unacceptable — say EXACTLY what detail is missing.
10. Your final blocking issues list is the MINIMUM bar that must be met before engineering begins."""

        prompt = f"""Perform a rigorous QA audit of the following Product Requirements Document.

PRODUCT IDEA: {user_idea}
INDUSTRY: {industry}

PRD DRAFT TO REVIEW:
{pm_output[:4000] if len(pm_output) > 4000 else pm_output}

Produce a comprehensive QA Critic Report in markdown. Be brutally honest. Every issue must have a recommended fix.

---

# QA Critic Report: PRD Audit
## Product: {user_idea}

---

## Overall Assessment
- **Overall PRD Quality Score**: X/10
- **Recommendation**: [APPROVE / APPROVE WITH MANDATORY CHANGES / REJECT AND REWRITE]
- **Critical Issues Found**: [count]
- **Summary**: (2-3 sentences on the biggest problems)

---

## Section-by-Section Ratings
| Section | Score | Critical Issues Found |
|---------|-------|-----------------------|
| Executive Summary | X/10 | ... |
| Role Definition | X/10 | ... |
| Business Workflow | X/10 | ... |
| User Personas | X/10 | ... |
| User Stories (MoSCoW) | X/10 | ... |
| Functional Requirements | X/10 | ... |
| Admin Dashboard Requirements | X/10 | ... |
| Compliance & Regulatory | X/10 | ... |
| Non-Functional Requirements | X/10 | ... |
| UI/UX Requirements | X/10 | ... |
| Data Model | X/10 | ... |

---

## 🔴 Critical Gaps — Must Fix Before Development Begins
These issues will cause the product to fail legally, technically, or commercially if not addressed.

### Gap 1: [Title]
- **Problem**: What is missing or wrong (be specific, quote the PRD text if applicable)
- **Consequence**: What failure scenario will occur if this is not fixed
- **Required Fix**: Exact addition or change needed in the PRD

### Gap 2: [Title]
[...repeat for every critical gap found...]

Specifically audit for and report on:
- Are ALL user roles defined? (customer, admin, operator, compliance officer, support, etc.)
- Is the complete business workflow documented end-to-end?
- Are compliance/regulatory requirements listed and treated as functional requirements?
- Is there a payment failure and refund handling flow?
- Are data deletion / GDPR requirements present?
- Is the admin dashboard fully specified?
- Are notification triggers comprehensive?
- Are error states defined for every major operation?

---

## 🟡 Logical Inconsistencies
Requirements that contradict each other or create impossible situations.

| Inconsistency | Section A Claim | Section B Claim | Resolution |
|--------------|-----------------|-----------------|------------|

---

## 🟠 Technical & Security Risks
### Risk 1: [Title]
- **Risk**: The specific technical or security problem
- **Root Cause**: What in the PRD implies this risk
- **Likelihood**: High / Medium / Low
- **Impact**: High / Medium / Low (data breach? downtime? data loss?)
- **Mitigation**: Specific technical approach (not vague advice)

Specifically check for:
- Authentication vulnerabilities (session fixation, token handling, brute force)
- Data privacy risks (PII exposure, logging sensitive data)
- Third-party API failures (what happens if payment gateway goes down?)
- Race conditions (concurrent users performing conflicting operations)
- Scalability bottlenecks implied by the current design

---

## 🟣 Missing Requirements (Complete Omissions)
Requirements that are entirely absent from the PRD:

| Missing Requirement | Category | Why It's Critical | Recommended Addition |
|--------------------|----------|-------------------|---------------------|

Check for these common omissions:
- Onboarding / first-run experience for new users
- Account recovery / support escalation flows
- Terms of Service / Privacy Policy acceptance
- Email/phone verification
- Data export feature (GDPR/CCPA)
- Activity logs / audit trails for compliance
- System status page / maintenance mode
- Rate limiting and abuse prevention
- Search and filter functionality (if applicable)
- Multi-language / internationalization (if applicable)

---

## 🔵 Ambiguities — Requirements That Will Be Implemented Differently By Different Engineers

| Ambiguous Requirement | Interpretation A | Interpretation B | Required Clarification |
|----------------------|------------------|------------------|------------------------|

---

## 🟢 Monetization Completeness Audit
Review the revenue model for:
- Is the pricing model specific (price points, not just "freemium")?
- Is the payment flow fully specified (success, failure, retry, refund)?
- Is the free-to-paid conversion path defined?
- Are subscription management features specified (upgrade, downgrade, cancel)?
- Are invoice/receipt requirements defined?

Score the monetization section: X/10 with specific gaps listed.

---

## ⚖️ Compliance & Regulatory Audit
For {industry}, the following must be present in the PRD. Flag each as Present / Missing / Partial:

| Requirement | Status | Specific Gap |
|-------------|--------|--------------|
[List all relevant regulations for this industry — HIPAA, GDPR, CCPA, PCI-DSS, FDA, KYC/AML, COPPA, etc. as applicable]

---

## 💡 Enhancement Recommendations
5 specific improvements that would elevate this PRD from good to exceptional:
1. [Specific enhancement with example text]
2. ...

---

## ⛔ Blocking Issues for Synthesis Agent
These MUST be resolved before the final PRD is produced. The Synthesis agent must address all of these:

1. [Blocking issue — specific, actionable]
2. [Blocking issue — specific, actionable]
3. [Blocking issue — specific, actionable]
[Add more if needed — do not artificially limit to 3 if there are more]

---

Every issue you raised must have a concrete fix. Vague criticism is unacceptable."""

        for chunk in groq_client.generate_stream(
            prompt=prompt,
            system_prompt=system_prompt,
            agent_type="qa",
            user_idea=user_idea,
            industry=industry
        ):
            yield chunk
