# BlueprintAI Evaluation Rubric & Checklist

This document provides a grading checklist to self-evaluate the implementation of the BlueprintAI project against the GLA University workshop parameters.

---

## 1. Core Grading Matrix

| Workshop Parameter | Checklist Criteria | Weight | Self-Score |
| :--- | :--- | :---: | :---: |
| **Problem Understanding** | Does the BA agent extract clear pain points, identify precise user segments, and estimate realistic TAM/SAM/SOM? | 15% | [ ] / 15 |
| **Architecture** | Is the multi-agent pipeline sequential? Are statuses streamed in real-time via FastAPI SSE? | 20% | [ ] / 20 |
| **Prompt Design** | Are prompts role-played? Do they separate logic (Role, Context, Task, Format)? | 15% | [ ] / 15 |
| **Code Quality** | Is the backend modular? Are dependencies contained in venv? Does it handle fallbacks gracefully? | 15% | [ ] / 15 |
| **Innovation** | Does the system feature a critique loop (QA Critic) and dynamic synthesis? | 15% | [ ] / 15 |
| **Demo Fluency & UI** | Is the Lumina Nexus UI high-end? Are transition states animated? Can users export data? | 10% | [ ] / 10 |
| **Documentation** | Is the README detailed? Are setup instructions copy-pasteable? Is prompt rationale explained? | 10% | [ ] / 10 |

---

## 2. Technical Self-Assessment Questions

### Problem Understanding & Market Analysis
- [ ] BA agent outputs valid JSON schema.
- [ ] Market calculations avoid placeholder ranges (e.g. "$1B - $10B") and show specific estimations.
- [ ] At least 2 real competitors are analyzed with distinct strengths/weaknesses.

### Architecture & Piping
- [ ] FastAPI uses async generators to stream data.
- [ ] Event stream uses standard `data: { ... }\n\n` format.
- [ ] Browser frontend reads the SSE stream using a text decoder reader without stalling.
- [ ] The history page loads previously cached documents from the store.

### Robustness & Fallbacks
- [ ] The application starts and runs correctly if local Ollama is offline (Mock fallback triggered).
- [ ] ChromaDB does not block application imports if compilation libraries are missing.
- [ ] Frontend handles SSE network dropouts gracefully without freezing the UI.
