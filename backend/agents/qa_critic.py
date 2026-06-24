from typing import Generator
from backend.agents import BaseAgent


class QACritic(BaseAgent):
    """
    QA / Risk Architect Agent

    Responsibilities:

    - Risk Assessment
    - Compliance Review
    - Security Threat Modeling
    - Test Planning
    - Edge Case Discovery
    - Product Readiness Review
    - Acceptance Validation
    - MVP Risk Analysis
    - Roadmap Validation

    Output Target:
    2500-4000 words
    """

    def __init__(self):
        super().__init__("qa")

    def run(
        self,
        groq_client,
        pm_output: str,
        user_idea: str,
        industry: str
    ) -> Generator[str, None, None]:

        system_prompt = f"""
You are a Principal QA Architect.

Background:

- Ex Google SRE
- Security Architect
- Product Risk Lead
- Enterprise QA Director

You are responsible for challenging
the Product Manager output.

You are NOT a writer.

You are an auditor.

==================================================
PRODUCT
==================================================

{user_idea}

INDUSTRY

{industry}

==================================================
YOUR JOB
==================================================

Find:

- Risks
- Gaps
- Security concerns
- Missing assumptions
- Compliance issues
- Edge cases
- Failure modes

==================================================
ABSOLUTE RULES
==================================================

1. PRODUCT SPECIFIC

Every risk must be specific.

Bad:

"System outage"

Good:

"Medicine delivery driver unable
to complete delivery due to
temperature-sensitive storage failure."

--------------------------------------------------

2. NO GENERIC RISKS

Avoid:

- server crash
- downtime
- bug

unless expanded and contextualized.

--------------------------------------------------

3. THREAT MODEL LIKE A SECURITY TEAM

Think:

Fraud

Abuse

Data Leakage

Identity Theft

Compliance Violations

Marketplace Abuse

Supply Chain Failure

etc.

--------------------------------------------------

4. CHALLENGE THE PM

Do not assume PM is correct.

Find weaknesses.

--------------------------------------------------

5. THINK LIKE INVESTORS

What can kill this startup?

What can block adoption?

What can create legal exposure?

==================================================
QUALITY TARGET
==================================================

Minimum:

2500 words

Preferred:

4000 words

==================================================
"""

        prompt = f"""
You have received the Product Specification.

==================================================
PRODUCT SPECIFICATION
==================================================

{pm_output}

==================================================
YOUR TASK
==================================================

Conduct a comprehensive
QA and Risk Review.

==================================================
SECTION 1
PRODUCT READINESS REVIEW
==================================================

Evaluate:

- Product Completeness
- Scope Realism
- Technical Complexity
- Operational Complexity

Provide:

Readiness Score

0-100

Explain reasoning.

==================================================
SECTION 2
RISK REGISTER
==================================================

Generate at least 15 risks.

Table:

| Risk ID |
| Risk |
| Category |
| Likelihood |
| Impact |
| Severity |
| Mitigation |

Categories:

Business
Technical
Operational
Security
Compliance
Market

==================================================
SECTION 3
ASSUMPTIONS
==================================================

Identify at least 15 assumptions.

For each:

- assumption
- why it matters
- validation approach

==================================================
SECTION 4
CONSTRAINTS
==================================================

List:

Technical Constraints

Business Constraints

Regulatory Constraints

Operational Constraints

==================================================
SECTION 5
EDGE CASE ANALYSIS
==================================================

Generate at least 25 edge cases.

Examples:

User abandonment

Fraud attempts

Data corruption

Incorrect input

Payment failures

Account recovery failures

Create table.

==================================================
SECTION 6
SECURITY THREAT MODEL
==================================================

Perform threat analysis.

Cover:

Authentication

Authorization

Data Exposure

Fraud

API Abuse

Account Takeover

Insider Threats

Payment Fraud

Supply Chain Risks

Generate:

| Threat |
| Attack Vector |
| Impact |
| Mitigation |

==================================================
SECTION 7
PRIVACY REVIEW
==================================================

Review:

User Data

Storage

Processing

Deletion

Consent

Data Portability

Retention

Explain compliance concerns.

==================================================
SECTION 8
COMPLIANCE REVIEW
==================================================

Determine applicable standards.

Examples:

GDPR

CCPA

HIPAA

PCI-DSS

SOC2

ISO27001

Provide:

Requirements

Risks

Controls

==================================================
SECTION 9
TEST STRATEGY
==================================================

Generate complete strategy.

Cover:

Unit Testing

Integration Testing

API Testing

UI Testing

E2E Testing

Performance Testing

Load Testing

Stress Testing

Security Testing

Accessibility Testing

Regression Testing

==================================================
SECTION 10
TEST CASE MATRIX
==================================================

Generate at least 30 test cases.

Table:

| ID |
| Module |
| Scenario |
| Expected Result |
| Priority |

==================================================
SECTION 11
ACCEPTANCE CHECKLIST
==================================================

Generate at least 50
acceptance checks.

Grouped by feature.

==================================================
SECTION 12
PERFORMANCE TEST PLAN
==================================================

Create targets.

Measure:

Latency

Concurrency

Availability

Throughput

Recovery

==================================================
SECTION 13
ACCESSIBILITY REVIEW
==================================================

Evaluate:

WCAG

Keyboard Navigation

Screen Readers

Color Contrast

Focus States

Mobile Accessibility

==================================================
SECTION 14
TECHNICAL DEBT REVIEW
==================================================

Identify:

Potential shortcuts

Future scaling risks

Maintenance risks

Architecture risks

==================================================
SECTION 15
MVP READINESS DECISION
==================================================

Provide:

Go / No-Go Recommendation

Required Fixes

Nice-To-Have Fixes

Launch Blockers

==================================================
SECTION 16
ROADMAP VALIDATION
==================================================

Review roadmap.

Create:

Month 1

Month 2

Month 3

Month 6

Month 12

Quality Milestones

==================================================
SECTION 17
POST-LAUNCH MONITORING
==================================================

Define:

Operational Metrics

Security Metrics

Business Metrics

Customer Metrics

Alert Thresholds

==================================================
IMPORTANT
==================================================

Be critical.

Be realistic.

Be detailed.

Find weaknesses.

Do not praise blindly.

Generate complete content.
"""

        for chunk in groq_client.generate_stream(
            prompt=prompt,
            system_prompt=system_prompt,
            agent_type="qa",
            user_idea=user_idea,
            industry=industry
        ):
            yield chunk
