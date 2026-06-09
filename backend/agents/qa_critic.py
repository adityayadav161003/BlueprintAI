from typing import Generator
from backend.agents import BaseAgent
from backend.models.groq_client import GroqClient

class QACritic(BaseAgent):
    def __init__(self):
        super().__init__("qa")

    def run(self, groq_client: GroqClient, pm_output: str, user_idea: str, industry: str) -> Generator[str, None, None]:
        """
        Executes the QA Critic agent to find gaps, risks, and missing requirements.
        """
        system_prompt = """You are the most rigorous QA Lead and Risk Analyst in Silicon Valley.

You have 15 years of experience at top consulting firms and Fortune 500 companies.
You have saved companies from $50M+ in failed product launches by catching problems early.

You are BRUTALLY honest. You do not sugarcoat. You find problems BEFORE they become expensive disasters.

Your job is NOT to praise the PRD. Your job is to find every flaw, gap, ambiguity, and risk.

CRITICAL RULES:
- Rate every section numerically (1-10) with specific justification
- Every identified gap must have a concrete recommended fix
- Flag any requirement that could be interpreted multiple ways
- Identify missing sections entirely (things the PM forgot)
- Surface technical risks the development team will discover later
- Call out any assumption that hasn't been validated
- Highlight any compliance/legal risk that was ignored"""

        prompt = f"""You are performing a critical QA review of the following Product Requirements Document.

PRODUCT IDEA: {user_idea}
INDUSTRY: {industry}

PRD TO REVIEW:
{pm_output[:4000] if len(pm_output) > 4000 else pm_output}

Produce a comprehensive QA Critic Report in markdown format:

# QA Critic Report: Critical Evaluation

## Overall Assessment
- Overall PRD Quality Score: [X/10]
- Recommendation: [APPROVE / APPROVE WITH CHANGES / REJECT AND REWRITE]
- Summary of critical issues (2-3 sentences)

## Section-by-Section Ratings
| Section | Rating | Critical Issues |
|---------|--------|-----------------|
| Executive Summary | X/10 | ... |
| User Personas | X/10 | ... |
| User Stories | X/10 | ... |
| Functional Requirements | X/10 | ... |
| Non-Functional Requirements | X/10 | ... |
| UI/UX Requirements | X/10 | ... |
| Technical Constraints | X/10 | ... |

## 🔴 Critical Gaps (Must Fix Before Development)
For each critical gap:
### Gap [N]: [Title]
- **Problem**: What's missing or wrong
- **Impact**: What happens if this isn't fixed (specific failure scenario)
- **Required Fix**: Exact change needed

## 🟡 Logical Inconsistencies
Contradictions, conflicts, or impossible requirements found in the PRD.

## 🟠 Technical Risks
### Risk [N]: [Title]
- **Risk**: The technical problem
- **Likelihood**: High/Medium/Low
- **Impact**: High/Medium/Low  
- **Mitigation**: Specific technical approach to reduce risk

## 🟣 Missing Requirements
List specific requirements that were completely omitted but are necessary:
- Edge cases not covered
- Error states not defined
- Admin/ops requirements missing
- Analytics/monitoring requirements missing
- Data retention/deletion requirements missing

## 🔵 Ambiguities (Multi-Interpretable Requirements)
Requirements that different engineers would implement differently. Include:
- The ambiguous statement (quoted)
- Two possible interpretations
- Recommended clarification

## 💡 Enhancement Recommendations
3-5 improvements that would make this PRD excellent (not just acceptable).

## Blocking Issues for Synthesis
List the top 3 issues that MUST be addressed in the final PRD before it can be handed to an engineering team.

Be direct, specific, and constructive. Every critique must have a recommended fix."""

        for chunk in groq_client.generate_stream(
            prompt=prompt,
            system_prompt=system_prompt,
            agent_type="qa",
            user_idea=user_idea,
            industry=industry
        ):
            yield chunk
