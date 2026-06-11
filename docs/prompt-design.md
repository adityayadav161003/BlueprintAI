# BlueprintAI Agent Prompt Design

The core of BlueprintAI's reasoning capabilities is its structured multi-agent prompting architecture. Rather than relying on a single, long prompt that tries to generate the entire PRD, we divide the responsibility among four highly specialized personas. 

This document details the engineering choices behind the system prompts for each agent.

---

## Architecture Overview

We employ a linear pipeline pattern:
1. **Business Analyst (BA)**: Standardized structured market parameters (JSON format).
2. **Product Manager (PM)**: Translates market parameters into user stories and requirement tables.
3. **QA Critic (QA)**: Reviews requirements and lists critical flaws, gaps, and assumptions.
4. **Synthesis (CPO)**: Resolves critique issues, structures roadmaps, and polishes the final document.

---

## Rationale for Prompt Engineering Choices

### 1. Persona and Context Framing (Role-Play)
Every prompt starts with a clear role definition using active framing:
- *BA:* "You are a senior business analyst with 10 years of experience at McKinsey/BCG."
- *PM:* "You are a FAANG-level senior product manager (ex-Google, Meta)."
- *QA:* "You are a ruthless QA lead and risk analyst."
- *CPO:* "You are the Chief Product Officer (CPO) at a high-growth unicorn startup."

Defining specific domain authorities shapes the vocabulary, style, and rigor of the output. It guides the model to adopt professional, objective terminology and focus on sector-specific criteria.

### 2. Output Formatting Restrictions
- **Business Analyst**: Restricting the BA agent to return *only* raw structured JSON forces the model to categorize market calculations (TAM, SAM, SOM) and metrics cleanly. It allows the frontend to parse the data structure and display visual cards instead of unstructured walls of text.
- **Product Manager / QA / Synthesis**: Restricting formats to Markdown ensures compatibility with the standard `marked.js` library, rendering clean semantic tables, bold headers, and prioritized lists out-of-the-box.

### 3. Iterative Feedback & Critique (QA Loop)
The QA Critic is prompted to "BE BRUTAL." Standard models have a bias toward complacency, generating generic approvals. By instructing the model to find *at least* 3 logical gaps, 2 technical risks, and 2 missing requirements, we force the LLM to inspect the PM's work critically.

### 4. Synthesis and Integration (CPO)
The Synthesis Agent is given the original PM draft alongside the QA Critic's report. Its prompt instructs it to actively modify requirements to address the QA issues and create a roadmap. This mimics a real engineering refinement loop, resulting in a PRD that is far more practical than a first-pass draft.
