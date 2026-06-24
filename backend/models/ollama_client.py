import os
import json
import time
import urllib.request
import urllib.error
from typing import Generator

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")
ENABLE_MOCK_FALLBACK = os.getenv("ENABLE_MOCK_FALLBACK", "true").lower() == "true"

class OllamaClient:
    def __init__(self, base_url: str = None, default_model: str = None):
        # Read from environment directly to ensure latest config is picked up
        self.base_url = (base_url or os.getenv("OLLAMA_BASE_URL", OLLAMA_BASE_URL)).rstrip("/")
        self.default_model = default_model or os.getenv("OLLAMA_MODEL", OLLAMA_MODEL)

    def check_connection(self) -> bool:
        """
        Checks if Ollama is running and accessible using built-in urllib.
        """
        try:
            url = f"{self.base_url}/api/tags"
            # Set a low timeout to fail fast
            with urllib.request.urlopen(url, timeout=1.0) as response:
                if response.status == 200:
                    return True
        except Exception:
            pass
        return False

    def get_best_model(self) -> str:
        """
        Queries Ollama tags and returns the best model available.
        Prioritizes 'qwen', then 'llama', then the default model.
        """
        try:
            url = f"{self.base_url}/api/tags"
            with urllib.request.urlopen(url, timeout=1.0) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    models = [m.get("name") for m in data.get("models", [])]
                    
                    # Prioritize Qwen (since user mentioned downloading it)
                    for m in models:
                        if "qwen" in m.lower():
                            return m
                    # Then Llama
                    for m in models:
                        if "llama" in m.lower():
                            return m
                    
                    if models:
                        return models[0]
        except Exception:
            pass
        return self.default_model

    def generate_stream(
        self,
        prompt: str,
        system_prompt: str,
        agent_type: str = "ba",
        user_idea: str = "",
        industry: str = ""
    ) -> Generator[str, None, None]:
        """
        Streams responses from local Ollama or falls back to mock simulation.
        """
        if self.check_connection():
            try:
                url = f"{self.base_url}/api/generate"
                payload = {
                    "model": self.default_model,
                    "prompt": prompt,
                    "system": system_prompt,
                    "stream": True,
                    "options": {
                        "temperature": 0.7
                    }
                }
                
                req = urllib.request.Request(
                    url,
                    data=json.dumps(payload).encode('utf-8'),
                    headers={'Content-Type': 'application/json'},
                    method='POST'
                )
                
                with urllib.request.urlopen(req, timeout=30.0) as response:
                    for line in response:
                        if not line:
                            continue
                        try:
                            data = json.loads(line.decode('utf-8'))
                            chunk = data.get("response", "")
                            if chunk:
                                yield chunk
                        except json.JSONDecodeError:
                            continue
                return  # Success
            except Exception as e:
                print(f"Ollama stream error: {e}. Falling back to mock generator...")

        # Fallback to simulated high-quality product metrics
        global ENABLE_MOCK_FALLBACK
        enable_mock = os.getenv("ENABLE_MOCK_FALLBACK", "true").lower() == "true"
        if enable_mock:
            for chunk in self._generate_mock_stream(agent_type, user_idea, industry):
                yield chunk
        else:
            raise RuntimeError("Ollama is offline and mock fallback is disabled.")

    def _customize_mock_text(self, text: str, idea: str, industry: str) -> str:
        # Standardize inputs
        if not idea:
            idea = "a modern software product"
        if not industry:
            industry = "Technology"

        # Determine short name for the product (e.g. "Placement App" or capitalized idea)
        short_name = idea.split(" for ")[0].split(" to ")[0].strip()
        # Capitalize first letters of words in short name
        short_name = " ".join([w.capitalize() for w in short_name.split(" ")])

        # Replace default placement app concept
        text = text.replace("A placement app for university students to grab opportunity from big companies", idea)
        text = text.replace("a placement app for university students to grab opportunity from big companies", idea.lower())
        text = text.replace("A Placement App For University Students To Grab Opportunity From Big Companies", short_name)
        text = text.replace("A placement app for university students to grab opportunity from big companies", short_name)
        text = text.replace("A placement app", short_name)
        text = text.replace("a placement app", short_name.lower())
        
        # Replace default target audience and companies
        text = text.replace("university students", "target users")
        text = text.replace("university student", "user")
        text = text.replace("University Students", "Target Users")
        text = text.replace("University Student", "User")
        
        text = text.replace("big companies", "external partners/employers")
        text = text.replace("big company", "partner/employer")
        text = text.replace("Big Companies", "Partners & Employers")
        
        # Replace industry
        text = text.replace("SaaS / Web App", industry)
        text = text.replace("SaaS/Web App", industry)

        # Replace specific placement terms to make it generic
        text = text.replace("placement portal", f"{short_name.lower()} portal")
        text = text.replace("job match", "core match")
        text = text.replace("job listings", "listings/items")
        text = text.replace("job listing", "listing/item")
        text = text.replace("Job Listings", "Listings & Items")
        text = text.replace("Job Listing", "Listing & Item")
        text = text.replace("job search", "search & discovery")
        text = text.replace("job application", "submission/transaction")
        text = text.replace("Job Application", "Submission & Transaction")
        
        # Persona replacements
        text = text.replace("Emily Chen", "Emily Chen (User)")
        text = text.replace("Rohan Patel", "Rohan Patel (Secondary User)")
        
        return text

    def _generate_mock_stream(self, agent_type: str, user_idea: str, industry: str) -> Generator[str, None, None]:
        """
        Simulates high-quality, product-specific agent outputs for the frontend.
        """
        idea = user_idea or "Selected Product Idea"
        ind = industry or "General Tech"

        if agent_type == "ba":
            mock_data = self._get_mock_ba(idea, ind)
        elif agent_type == "pm":
            mock_data = self._get_mock_pm(idea, ind)
        elif agent_type == "qa":
            mock_data = self._get_mock_qa(idea, ind)
        else:
            mock_data = self._get_mock_syn(idea, ind)

        # Customize mock data dynamically to avoid outputting same text for every idea
        mock_data = self._customize_mock_text(mock_data, idea, ind)

        words = mock_data.split(" ")
        chunk_size = 3
        for i in range(0, len(words), chunk_size):
            chunk = " ".join(words[i:i+chunk_size]) + " "
            yield chunk
            # Typing animation speed control
            time.sleep(0.015)

    def _get_mock_ba(self, idea: str, industry: str) -> str:
        return f"""## Executive Summary

Provide a high-level summary of the product blueprint using the following bullet points:
- **Product Vision:** To become the premier platform for A placement app for university students to grab opportunity from big companies, establishing a seamless link between university students and opportunities.
- **Core Problem:** University students struggle to find and secure job placements, while big companies face high friction and difficulty in filtering the best candidate profiles efficiently.
- **Our Solution:** A placement app provides a streamlined matching engine, verified candidate credentials, and direct communication channels.
- **Target Customer:** University students seeking internships/placements and recruiters from big companies.
- **Business Model:** Premium subscription tiers for employers, premium resume services for students, and success fee commissions.
- **MVP Launch Target:** 12 weeks.
- **Success Definition:** 5,000 active university students registered, 50 big companies onboarded, and over 1,000 successful placements in Month 1.

---

## 1. Problem Statement & Opportunity

The specific problem that this product solves is the difficulty university students face in finding and securing job placements with big companies. Currently, students rely on university career fairs, online job boards like LinkedIn and Indeed, and personal networking to find opportunities. However, these methods often result in a high volume of unqualified applicants, slow response cycles, and a lack of specific match indicators.

The market size for this problem is significant, with over 20 million university students in the US alone. The market opportunity is estimated to be around $1.5 billion, considering the average cost of recruiting a single candidate is around $4,000. Recently, the shift towards online recruitment and the increasing importance of digital presence have made it viable for a dedicated product to address this problem.

---

## 2. Target User Personas

### Emily Chen, 21 — Junior majoring in Computer Science, San Francisco
- **Demographics:** Female, 21, undergraduate student, tech-savvy, lives in shared university housing.
- **Daily Workflow:** Emily spends several hours a week browsing job boards, attending career fairs, and networking with alumni to find internship opportunities.
- **Pain Points:** Frustrated with the lack of personalized job recommendations on platforms like LinkedIn and the difficulty in standing out in a crowded applicant pool.
- **Goals:** Emily wants to secure a summer internship at a top tech firm and eventually land a full-time job offer after graduation.
- **Tech Stack:** High comfort; uses macOS, iOS, GitHub, Slack, and LinkedIn daily.
- **Budget Authority:** Student budget, highly price-sensitive; willing to pay up to $10/month for premium career tools.
- **Success Metrics:** Landing at least 3 interviews within 2 weeks of profile completion.
- **Quote:** "I feel like I'm just throwing my resume into a black hole when I apply for jobs online. I wish there was a way to get my foot in the door."
- **Usage Pattern:** Daily usage to check match status, application views, and respond to recruiter messages.

### Rohan Patel, 22 — Senior majoring in Business Administration, New York
- **Demographics:** Male, 22, graduating senior, highly ambitious, active in student finance societies.
- **Daily Workflow:** Rohan networks extensively with professionals in his industry, attends career fairs, and applies to job openings on company websites.
- **Pain Points:** Lack of transparency in the recruitment process and the difficulty in getting feedback on his applications.
- **Goals:** Rohan wants to land a full-time job at a top investment bank or consulting firm after graduation.
- **Tech Stack:** Medium comfort; uses Windows, iOS, MS Office, and LinkedIn.
- **Budget Authority:** Moderate; willing to invest $50 for a professional resume review.
- **Success Metrics:** Receiving direct inquiries from at least 2 big companies.
- **Quote:** "I want to apply to companies where I know my profile matches what they want. Traditional portals don't show the match percentage."
- **Usage Pattern:** Browses weekly, submits 2-3 applications a day.

### Sarah Jenkins, 28 — Campus Recruiter at a Tech Giant, Seattle
- **Demographics:** Female, 28, corporate recruiter, busy schedule, travels for university events.
- **Daily Workflow:** Sarah reviews thousands of resumes, coordinates with university career centers, and conducts initial screening interviews.
- **Pain Points:** Overwhelmed by low-quality, generic resume submissions and manual scheduling overhead.
- **Goals:** Quickly identify top-tier talent matching specific engineering benchmarks and reduce time-to-hire.
- **Tech Stack:** High comfort; uses Workday ATS, Slack, Zoom, and Outlook.
- **Budget Authority:** Corporate department budget; authorized up to $5,000/year for recruiting platform licenses.
- **Success Metrics:** Reducing candidate screening time by 40% and increasing interview-to-offer conversion rate.
- **Quote:** "I need a way to filter candidates by actual verified skills and project portfolios, not just their GPA or school name."
- **Usage Pattern:** Active daily during peak recruiting seasons (Fall/Spring), spending 3-4 hours per day on the portal."""

    def _get_mock_pm(self, idea: str, industry: str) -> str:
        return f"""## 3. Prioritized User Stories

### Must-Have (Core Loop)
*Without these, the product does not work.*
- **As a university student**, I want to create a profile showcasing my skills and projects, so that I can make my profile visible to employers.
  > **AC:** Given I am a registered student, When I save my profile with valid fields, Then the profile is stored and visible to recruiter searches.
- **As a university student**, I want to search and filter job listings, so that I can find matching placements.
  > **AC:** Given I am on the job search page, When I input a search keyword or select a filter, Then the system returns filtered job listings within 500ms.
- **As a university student**, I want to submit job applications directly, so that I can apply to big companies instantly.
  > **AC:** Given I view a job listing, When I click "Apply", Then my profile data is sent to the company's recruiter and status changes to "Submitted".
- **As a recruiter**, I want to view candidate applications and update their status, so that I can manage my hiring pipeline.
  > **AC:** Given I am logged in as a recruiter, When I view a candidate, Then I can change their status (e.g. Under Review, Interview, Rejected).

### Should-Have
*Significantly improves the experience.*
- **As a university student**, I want to see a compatibility match score for each listing, so that I can prioritize where to apply.
  > **AC:** Given I view job listings, When my profile has completed skills, Then each job displays a match percentage (e.g., 85% match).
- **As a recruiter**, I want to schedule interviews directly through the app, so that I don't have to coordinate via email.
  > **AC:** Given a candidate is moved to "Interview", When I click "Schedule", Then the system integrates with calendar availability.

### Could-Have
*Defer if needed.*
- **As a university student**, I want to get suggestions to improve my resume, so that I can increase my interview chances.
  > **AC:** Given my profile is incomplete, When I request tips, Then the app highlights missing keywords based on popular job listings.

### Won't-Have (MVP Exclusions)
- **Automatic Background Verification:** Automated background checks for candidates will be excluded for the initial release to reduce complexity, relying on university-provided graduation lists instead.

---

## 4. Functional Requirements

| ID | FEATURE | USER STORY REF | DETAILED DESCRIPTION | ACCEPTANCE CRITERIA | PRIORITY | EST. EFFORT |
|----|---------|----------------|----------------------|---------------------|----------|-------------|
| FR-101 | Profile Creator | US-101 | Allows students to enter education, projects, skills, and upload resumes. | Fields validated, saved, and searchable. | High | 3 days |
| FR-102 | Job Listing Search | US-102 | Index and search job listings by title, skills, location, and salary. | Search query returns relevant items within 500ms. | High | 4 days |
| FR-103 | One-Click Apply | US-103 | Package profile details and send them as an application to the recruiter. | Application status updated in real-time. | High | 2 days |
| FR-104 | Match Engine | US-105 | Algorithm comparing candidate skills with job requirements to calculate % match. | Score displays dynamically on job card. | Medium | 5 days |
| FR-105 | Recruiter Dashboard | US-104 | Interface for recruiters to view, sort, and change status of applicants. | Pipeline kanban or list view updates instantly. | High | 4 days |

---

## 5. Non-Functional Requirements

### Performance SLAs
| METRIC | REQUIREMENT | MEASUREMENT METHOD |
|--------|-------------|--------------------|
| Page Load Time | < 2.0 seconds for landing page, < 1.0 second for dashboard. | Lighthouse Audits & Web Vitals. |
| Search API Latency | Median latency < 300ms under load. | Server logs and APM tracing. |
| Data Sync Delay | Real-time SSE updates within 200ms. | End-to-end telemetry. |

### Security & Compliance
| REQUIREMENT | STANDARD | IMPLEMENTATION |
|-------------|----------|----------------|
| Data Encryption | AES-256 at rest, TLS 1.3 in transit. | HTTPS setup & AWS KMS managed keys. |
| Authentication | OAuth 2.0 with JWT. | Auth0 integration & session token storage. |
| Compliance | GDPR and CCPA. | Consent dialogs, data export, and deletion workflows. |

### Scalability Plan
- **Phase 1 (0-1K users):** Single database instance, server cache, standard backend deployment.
- **Phase 2 (1K-10K users):** Read replicas for database, horizontally scaled backend pods with load balancer.
- **Phase 3 (10K+ users):** Microservices migration, Redis caching cluster, Elasticsearch cluster for search.

---

## 6. Technical Architecture

### Recommended Tech Stack
| LAYER | TECHNOLOGY | JUSTIFICATION |
|-------|------------|---------------|
| Frontend | React.js, Tailwind CSS | Rapid UI development, responsive component rendering. |
| Backend | Node.js / Express | Non-blocking I/O, ideal for streaming updates and REST APIs. |
| Database | PostgreSQL | Relational integrity for user profiles, applications, and job listings. |
| Cache & SSE | Redis | Session state management and SSE message pub/sub. |
| Hosting | AWS (ECS / RDS) | Enterprise security, reliable backups, and automatic scaling. |

### System Architecture Overview
A placement app for university students to grab opportunity from big companies is built on a modern decoupled architecture. The React frontend interacts with the Express backend via REST endpoints and maintains an SSE connection for instant status updates.

```mermaid
flowchart TD
    Client[React Web App] -->|HTTPS Requests| API[Express API Gateway]
    API -->|Authenticate| Auth[Auth0 Provider]
    API -->|Read/Write| DB[(PostgreSQL DB)]
    API -->|Cache / SSE| Cache[(Redis Cache)]
    Cache -.->|Real-time Updates| Client
```

### Data Model (Key Entities)
- **User:** `id (PK)`, `email`, `password_hash`, `role (student/recruiter)`, `created_at`
- **StudentProfile:** `id (PK)`, `user_id (FK)`, `first_name`, `last_name`, `skills`, `education`, `resume_url`
- **JobListing:** `id (PK)`, `recruiter_id (FK)`, `title`, `description`, `required_skills`, `location`, `status`
- **Application:** `id (PK)`, `job_listing_id (FK)`, `student_id (FK)`, `status`, `submitted_at`

### API Design (Key Endpoints)
| METHOD | ENDPOINT | DESCRIPTION | REQUEST BODY | RESPONSE |
|--------|----------|-------------|--------------|----------|
| POST | `/api/auth/register` | Register new user. | `{{email, password, role}}` | `{{token, user_id}}` |
| GET | `/api/jobs` | Get filtered job listings. | None (Query params) | `[JobListing]` |
| POST | `/api/applications` | Apply for a job. | `{{job_id}}` | `{{application_id, status}}` |
| PATCH | `/api/applications/:id` | Update application status. | `{{status}}` | `{{success: true}}` |

---

## 7. UI/UX Specifications

### Screen Inventory
- **Landing Page:** Marketing page introducing the portal to students and recruiters.
- **Student Dashboard:** View match scores, saved jobs, applied jobs, and profile status.
- **Profile Builder:** Multi-step wizard to input skills, projects, and upload a resume.
- **Job Search Portal:** Search bar, advanced filters, and detailed job preview panel.
- **Recruiter Pipeline:** Kanban board representing applicant statuses (New, Screen, Interview, Offer, Rejected).

### Design System Requirements
- **Typography:** Inter (Primary sans-serif) for high readability. Heading font Outfit for premium aesthetic.
- **Color Palette:** Sleek HSL dark mode. Primary: Deep Navy `#0F172A`, Accent: Vibrant Cobalt `#2563EB`, Success: Emerald `#10B981`.
- **Spacing System:** 4px baseline grid (padding/margins: 8px, 16px, 24px, 32px).

### Critical User Flows
1. **Student Onboarding:** Sign up -> Input Skills -> Complete Profile -> Land on customized Job Search page with match scores.
2. **Job Application:** Browse listing -> View Match Score -> Click Apply -> SSE notification triggers success -> Application appears in Recruiter Kanban.

---

## 11. Success Metrics & KPIs

- **North Star Metric:** Successful Placement Rate (Number of students hired per month).

### Metric Framework
| METRIC | BASELINE | MONTH 1 | MONTH 3 | MONTH 6 | MONTH 12 |
|--------|----------|---------|---------|---------|----------|
| Active Student Profiles | 0 | 1,000 | 5,000 | 20,000 | 50,000 |
| Job Listings Posted | 0 | 150 | 600 | 2,500 | 8,000 |
| Application Submission Rate | 0 | 70% | 75% | 80% | 85% |
| Monthly Placement Volume | 0 | 50 | 250 | 1,200 | 4,000 |

### Analytics Implementation
- **Events to Track:** `user_signup`, `profile_completed`, `job_search_executed`, `application_submitted`, `status_changed`.
- **Funnel Definitions:** Signup -> Profile Completion -> Job Search -> Apply -> Hire.
- **Dashboard Requirements:** Metabase / Looker Studio dashboard tracking active funnels, latency metrics, and daily match rates."""

    def _get_mock_qa(self, idea: str, industry: str) -> str:
        return f"""## 8. QA & Testing Strategy

### Testing Types
- **Unit Testing:** 80% coverage target using Jest/Vitest for frontend helpers and backend controllers.
- **Integration Testing:** Test API endpoints, Auth0 flow, and Redis-SSE connections using Supertest.
- **End-to-End (E2E) Testing:** Playwright suites covering Student Onboarding and Recruiter Application Management.
- **Performance Testing:** Load testing via k6 to verify system response under 2,000 concurrent user streams.
- **User Acceptance Testing (UAT):** Private beta with 50 students and 5 campus recruiters for feedback loops.

---

## 9. Risk Register & Mitigation Plan

| RISK | CATEGORY | LIKELIHOOD | IMPACT | MITIGATION STRATEGY | OWNER |
|------|----------|------------|--------|---------------------|-------|
| Low Student Engagement | Market | Medium | High | Partner directly with university career centers to mandate registration. | Product Manager |
| Recruiter Churn | Market | Low | High | Ensure high-quality, pre-screened matches so recruiters find value quickly. | Business Analyst |
| API Rate Limits (LinkedIn/Indeed APIs) | Technical | High | Medium | Implement Redis caching layers and limit job refresh fetch cycles. | Tech Lead |
| Privacy Data Breach | Security | Low | Critical | Conduct quarterly third-party security audits and encrypt PII data. | Security Lead |

---

## 10. Project Build Plan & Roadmap

### Phased Roadmap
- **Phase 1: Foundation (Weeks 1-4):** Database schemas, authentication, onboarding flows, and basic profiles.
- **Phase 2: Core Matching & Listings (Weeks 5-8):** Search index, job listings portal, and matching engine calculation.
- **Phase 3: Applications & Dashboard (Weeks 9-12):** Apply button flow, recruiter kanban board, and SSE notification system.
- **Phase 4: Launch & Optimization (Weeks 13-16):** UAT beta testing, performance tuning, and public launch.

### Week-by-Week Month 1
- **Week 1:** Set up PostgreSQL database tables and API routing skeleton.
- **Week 2:** Implement Auth0 login, register flows, and secure session management.
- **Week 3:** Build frontend Onboarding Wizard and profile editor form.
- **Week 4:** Unit test onboarding and profile saves; run first mock integration build.

### Team Requirements
- **1 Product Manager** (Roadmap, specifications, UAT feedback)
- **1 Lead Engineer** (System architecture, database schema, DevOps setup)
- **1 Frontend Engineer** (React web application, Tailwind styling, dashboards)
- **1 Backend Engineer** (Express API, database indexing, Redis pub/sub)
- **1 QA Automation Engineer** (Playwright test suites, k6 load testing, validation)

---

## 12. Launch Checklist

### Pre-Launch (T-4 weeks)
- [ ] Complete code freeze and run full Playwright E2E suite.
- [ ] Conduct vulnerability scan and penetration testing.
- [ ] Setup production AWS cluster, databases, and backup routines.
- [ ] Verify university integration partnerships.

### Launch Week
- [ ] Execute database migrations and deploy production build.
- [ ] Conduct smoke testing on live production environment.
- [ ] Enable Metabase and Sentry dashboards for monitoring.
- [ ] Send welcome emails to pre-registered university students and recruiters.

### Post-Launch (Weeks 1-4)
- [ ] Monitor error logging and SSE connection drop rates.
- [ ] Gather feedback from recruiters regarding application quality.
- [ ] Release weekly bug-fix patches.

---

## Appendix: Open Questions & Decisions Log

| QUESTION | DECISION MADE | RATIONALE | DATE |
|----------|---------------|-----------|------|
| Should we allow anonymous job searches? | No. Registration is mandatory to view listings. | Protects proprietary job data and ensures all search activity yields high-intent leads. | 2026-06-20 |
| Which calendar tool should we support first for scheduling? | Google Calendar. | Over 90% of target students and participating companies use Google Workspace. | 2026-06-22 |
| How do we handle manual resume uploads? | Parse via standard PDF parsers and index the raw text. | Allows the matching engine to read resume keywords and rank candidates accurately. | 2026-06-23 |"""

    def _get_mock_syn(self, idea: str, industry: str) -> str:
        return f"""# A placement app for university students to grab opportunity from big companies
## Product Requirements Document

**Version:** 1.0 | **Status:** Final | **Industry:** SaaS / Web App

---

## Executive Summary

Provide a high-level summary of the product blueprint using the following bullet points:
- **Product Vision:** To become the premier platform for A placement app for university students to grab opportunity from big companies, establishing a seamless link between university students and opportunities.
- **Core Problem:** University students struggle to find and secure job placements, while big companies face high friction and difficulty in filtering the best candidate profiles efficiently.
- **Our Solution:** A placement app provides a streamlined matching engine, verified candidate credentials, and direct communication channels.
- **Target Customer:** University students seeking internships/placements and recruiters from big companies.
- **Business Model:** Premium subscription tiers for employers, premium resume services for students, and success fee commissions.
- **MVP Launch Target:** 12 weeks.
- **Success Definition:** 5,000 active university students registered, 50 big companies onboarded, and over 1,000 successful placements in Month 1.

---

## 1. Problem Statement & Opportunity

The specific problem that this product solves is the difficulty university students face in finding and securing job placements with big companies. Currently, students rely on university career fairs, online job boards like LinkedIn and Indeed, and personal networking to find opportunities. However, these methods often result in a high volume of unqualified applicants, slow response cycles, and a lack of specific match indicators.

The market size for this problem is significant, with over 20 million university students in the US alone. The market opportunity is estimated to be around $1.5 billion, considering the average cost of recruiting a single candidate is around $4,000. Recently, the shift towards online recruitment and the increasing importance of digital presence have made it viable for a dedicated product to address this problem.

---

## 2. Target User Personas

### Emily Chen, 21 — Junior majoring in Computer Science, San Francisco
- **Demographics:** Female, 21, undergraduate student, tech-savvy, lives in shared university housing.
- **Daily Workflow:** Emily spends several hours a week browsing job boards, attending career fairs, and networking with alumni to find internship opportunities.
- **Pain Points:** Frustrated with the lack of personalized job recommendations on platforms like LinkedIn and the difficulty in standing out in a crowded applicant pool.
- **Goals:** Emily wants to secure a summer internship at a top tech firm and eventually land a full-time job offer after graduation.
- **Tech Stack:** High comfort; uses macOS, iOS, GitHub, Slack, and LinkedIn daily.
- **Budget Authority:** Student budget, highly price-sensitive; willing to pay up to $10/month for premium career tools.
- **Success Metrics:** Landing at least 3 interviews within 2 weeks of profile completion.
- **Quote:** "I feel like I'm just throwing my resume into a black hole when I apply for jobs online. I wish there was a way to get my foot in the door."
- **Usage Pattern:** Daily usage to check match status, application views, and respond to recruiter messages.

### Rohan Patel, 22 — Senior majoring in Business Administration, New York
- **Demographics:** Male, 22, graduating senior, highly ambitious, active in student finance societies.
- **Daily Workflow:** Rohan networks extensively with professionals in his industry, attends career fairs, and applies to job openings on company websites.
- **Pain Points:** Lack of transparency in the recruitment process and the difficulty in getting feedback on his applications.
- **Goals:** Rohan wants to land a full-time job at a top investment bank or consulting firm after graduation.
- **Tech Stack:** Medium comfort; uses Windows, iOS, MS Office, and LinkedIn.
- **Budget Authority:** Moderate; willing to invest $50 for a professional resume review.
- **Success Metrics:** Receiving direct inquiries from at least 2 big companies.
- **Quote:** "I want to apply to companies where I know my profile matches what they want. Traditional portals don't show the match percentage."
- **Usage Pattern:** Browses weekly, submits 2-3 applications a day.

### Sarah Jenkins, 28 — Campus Recruiter at a Tech Giant, Seattle
- **Demographics:** Female, 28, corporate recruiter, busy schedule, travels for university events.
- **Daily Workflow:** Sarah reviews thousands of resumes, coordinates with university career centers, and conducts initial screening interviews.
- **Pain Points:** Overwhelmed by low-quality, generic resume submissions and manual scheduling overhead.
- **Goals:** Quickly identify top-tier talent matching specific engineering benchmarks and reduce time-to-hire.
- **Tech Stack:** High comfort; uses Workday ATS, Slack, Zoom, and Outlook.
- **Budget Authority:** Corporate department budget; authorized up to $5,000/year for recruiting platform licenses.
- **Success Metrics:** Reducing candidate screening time by 40% and increasing interview-to-offer conversion rate.
- **Quote:** "I need a way to filter candidates by actual verified skills and project portfolios, not just their GPA or school name."
- **Usage Pattern:** Active daily during peak recruiting seasons (Fall/Spring), spending 3-4 hours per day on the portal.

---

## 3. Prioritized User Stories

### Must-Have (Core Loop)
*Without these, the product does not work.*
- **As a university student**, I want to create a profile showcasing my skills and projects, so that I can make my profile visible to employers.
  > **AC:** Given I am a registered student, When I save my profile with valid fields, Then the profile is stored and visible to recruiter searches.
- **As a university student**, I want to search and filter job listings, so that I can find matching placements.
  > **AC:** Given I am on the job search page, When I input a search keyword or select a filter, Then the system returns filtered job listings within 500ms.
- **As a university student**, I want to submit job applications directly, so that I can apply to big companies instantly.
  > **AC:** Given I view a job listing, When I click "Apply", Then my profile data is sent to the company's recruiter and status changes to "Submitted".
- **As a recruiter**, I want to view candidate applications and update their status, so that I can manage my hiring pipeline.
  > **AC:** Given I am logged in as a recruiter, When I view a candidate, Then I can change their status (e.g. Under Review, Interview, Rejected).

### Should-Have
*Significantly improves the experience.*
- **As a university student**, I want to see a compatibility match score for each listing, so that I can prioritize where to apply.
  > **AC:** Given I view job listings, When my profile has completed skills, Then each job displays a match percentage (e.g., 85% match).
- **As a recruiter**, I want to schedule interviews directly through the app, so that I don't have to coordinate via email.
  > **AC:** Given a candidate is moved to "Interview", When I click "Schedule", Then the system integrates with calendar availability.

### Could-Have
*Defer if needed.*
- **As a university student**, I want to get suggestions to improve my resume, so that I can increase my interview chances.
  > **AC:** Given my profile is incomplete, When I request tips, Then the app highlights missing keywords based on popular job listings.

### Won't-Have (MVP Exclusions)
- **Automatic Background Verification:** Automated background checks for candidates will be excluded for the initial release to reduce complexity, relying on university-provided graduation lists instead.

---

## 4. Functional Requirements

| ID | FEATURE | USER STORY REF | DETAILED DESCRIPTION | ACCEPTANCE CRITERIA | PRIORITY | EST. EFFORT |
|----|---------|----------------|----------------------|---------------------|----------|-------------|
| FR-101 | Profile Creator | US-101 | Allows students to enter education, projects, skills, and upload resumes. | Fields validated, saved, and searchable. | High | 3 days |
| FR-102 | Job Listing Search | US-102 | Index and search job listings by title, skills, location, and salary. | Search query returns relevant items within 500ms. | High | 4 days |
| FR-103 | One-Click Apply | US-103 | Package profile details and send them as an application to the recruiter. | Application status updated in real-time. | High | 2 days |
| FR-104 | Match Engine | US-105 | Algorithm comparing candidate skills with job requirements to calculate % match. | Score displays dynamically on job card. | Medium | 5 days |
| FR-105 | Recruiter Dashboard | US-104 | Interface for recruiters to view, sort, and change status of applicants. | Pipeline kanban or list view updates instantly. | High | 4 days |

---

## 5. Non-Functional Requirements

### Performance SLAs
| METRIC | REQUIREMENT | MEASUREMENT METHOD |
|--------|-------------|--------------------|
| Page Load Time | < 2.0 seconds for landing page, < 1.0 second for dashboard. | Lighthouse Audits & Web Vitals. |
| Search API Latency | Median latency < 300ms under load. | Server logs and APM tracing. |
| Data Sync Delay | Real-time SSE updates within 200ms. | End-to-end telemetry. |

### Security & Compliance
| REQUIREMENT | STANDARD | IMPLEMENTATION |
|-------------|----------|----------------|
| Data Encryption | AES-256 at rest, TLS 1.3 in transit. | HTTPS setup & AWS KMS managed keys. |
| Authentication | OAuth 2.0 with JWT. | Auth0 integration & session token storage. |
| Compliance | GDPR and CCPA. | Consent dialogs, data export, and deletion workflows. |

### Scalability Plan
- **Phase 1 (0-1K users):** Single database instance, server cache, standard backend deployment.
- **Phase 2 (1K-10K users):** Read replicas for database, horizontally scaled backend pods with load balancer.
- **Phase 3 (10K+ users):** Microservices migration, Redis caching cluster, Elasticsearch cluster for search.

---

## 6. Technical Architecture

### Recommended Tech Stack
| LAYER | TECHNOLOGY | JUSTIFICATION |
|-------|------------|---------------|
| Frontend | React.js, Tailwind CSS | Rapid UI development, responsive component rendering. |
| Backend | Node.js / Express | Non-blocking I/O, ideal for streaming updates and REST APIs. |
| Database | PostgreSQL | Relational integrity for user profiles, applications, and job listings. |
| Cache & SSE | Redis | Session state management and SSE message pub/sub. |
| Hosting | AWS (ECS / RDS) | Enterprise security, reliable backups, and automatic scaling. |

### System Architecture Overview
A placement app for university students to grab opportunity from big companies is built on a modern decoupled architecture. The React frontend interacts with the Express backend via REST endpoints and maintains an SSE connection for instant status updates.

```mermaid
flowchart TD
    Client[React Web App] -->|HTTPS Requests| API[Express API Gateway]
    API -->|Authenticate| Auth[Auth0 Provider]
    API -->|Read/Write| DB[(PostgreSQL DB)]
    API -->|Cache / SSE| Cache[(Redis Cache)]
    Cache -.->|Real-time Updates| Client
```

### Data Model (Key Entities)
- **User:** `id (PK)`, `email`, `password_hash`, `role (student/recruiter)`, `created_at`
- **StudentProfile:** `id (PK)`, `user_id (FK)`, `first_name`, `last_name`, `skills`, `education`, `resume_url`
- **JobListing:** `id (PK)`, `recruiter_id (FK)`, `title`, `description`, `required_skills`, `location`, `status`
- **Application:** `id (PK)`, `job_listing_id (FK)`, `student_id (FK)`, `status`, `submitted_at`

### API Design (Key Endpoints)
| METHOD | ENDPOINT | DESCRIPTION | REQUEST BODY | RESPONSE |
|--------|----------|-------------|--------------|----------|
| POST | `/api/auth/register` | Register new user. | `{{email, password, role}}` | `{{token, user_id}}` |
| GET | `/api/jobs` | Get filtered job listings. | None (Query params) | `[JobListing]` |
| POST | `/api/applications` | Apply for a job. | `{{job_id}}` | `{{application_id, status}}` |
| PATCH | `/api/applications/:id` | Update application status. | `{{status}}` | `{{success: true}}` |

---

## 7. UI/UX Specifications

### Screen Inventory
- **Landing Page:** Marketing page introducing the portal to students and recruiters.
- **Student Dashboard:** View match scores, saved jobs, applied jobs, and profile status.
- **Profile Builder:** Multi-step wizard to input skills, projects, and upload a resume.
- **Job Search Portal:** Search bar, advanced filters, and detailed job preview panel.
- **Recruiter Pipeline:** Kanban board representing applicant statuses (New, Screen, Interview, Offer, Rejected).

### Design System Requirements
- **Typography:** Inter (Primary sans-serif) for high readability. Heading font Outfit for premium aesthetic.
- **Color Palette:** Sleek HSL dark mode. Primary: Deep Navy `#0F172A`, Accent: Vibrant Cobalt `#2563EB`, Success: Emerald `#10B981`.
- **Spacing System:** 4px baseline grid (padding/margins: 8px, 16px, 24px, 32px).

### Critical User Flows
1. **Student Onboarding:** Sign up -> Input Skills -> Complete Profile -> Land on customized Job Search page with match scores.
2. **Job Application:** Browse listing -> View Match Score -> Click Apply -> SSE notification triggers success -> Application appears in Recruiter Kanban.

---

## 8. QA & Testing Strategy

### Testing Types
- **Unit Testing:** 80% coverage target using Jest/Vitest for frontend helpers and backend controllers.
- **Integration Testing:** Test API endpoints, Auth0 flow, and Redis-SSE connections using Supertest.
- **End-to-End (E2E) Testing:** Playwright suites covering Student Onboarding and Recruiter Application Management.
- **Performance Testing:** Load testing via k6 to verify system response under 2,000 concurrent user streams.
- **User Acceptance Testing (UAT):** Private beta with 50 students and 5 campus recruiters for feedback loops.

---

## 9. Risk Register & Mitigation Plan

| RISK | CATEGORY | LIKELIHOOD | IMPACT | MITIGATION STRATEGY | OWNER |
|------|----------|------------|--------|---------------------|-------|
| Low Student Engagement | Market | Medium | High | Partner directly with university career centers to mandate registration. | Product Manager |
| Recruiter Churn | Market | Low | High | Ensure high-quality, pre-screened matches so recruiters find value quickly. | Business Analyst |
| API Rate Limits (LinkedIn/Indeed APIs) | Technical | High | Medium | Implement Redis caching layers and limit job refresh fetch cycles. | Tech Lead |
| Privacy Data Breach | Security | Low | Critical | Conduct quarterly third-party security audits and encrypt PII data. | Security Lead |

---

## 10. Project Build Plan & Roadmap

### Phased Roadmap
- **Phase 1: Foundation (Weeks 1-4):** Database schemas, authentication, onboarding flows, and basic profiles.
- **Phase 2: Core Matching & Listings (Weeks 5-8):** Search index, job listings portal, and matching engine calculation.
- **Phase 3: Applications & Dashboard (Weeks 9-12):** Apply button flow, recruiter kanban board, and SSE notification system.
- **Phase 4: Launch & Optimization (Weeks 13-16):** UAT beta testing, performance tuning, and public launch.

### Week-by-Week Month 1
- **Week 1:** Set up PostgreSQL database tables and API routing skeleton.
- **Week 2:** Implement Auth0 login, register flows, and secure session management.
- **Week 3:** Build frontend Onboarding Wizard and profile editor form.
- **Week 4:** Unit test onboarding and profile saves; run first mock integration build.

### Team Requirements
- **1 Product Manager** (Roadmap, specifications, UAT feedback)
- **1 Lead Engineer** (System architecture, database schema, DevOps setup)
- **1 Frontend Engineer** (React web application, Tailwind styling, dashboards)
- **1 Backend Engineer** (Express API, database indexing, Redis pub/sub)
- **1 QA Automation Engineer** (Playwright test suites, k6 load testing, validation)

---

## 12. Launch Checklist

### Pre-Launch (T-4 weeks)
- [ ] Complete code freeze and run full Playwright E2E suite.
- [ ] Conduct vulnerability scan and penetration testing.
- [ ] Setup production AWS cluster, databases, and backup routines.
- [ ] Verify university integration partnerships.

### Launch Week
- [ ] Execute database migrations and deploy production build.
- [ ] Conduct smoke testing on live production environment.
- [ ] Enable Metabase and Sentry dashboards for monitoring.
- [ ] Send welcome emails to pre-registered university students and recruiters.

### Post-Launch (Weeks 1-4)
- [ ] Monitor error logging and SSE connection drop rates.
- [ ] Gather feedback from recruiters regarding application quality.
- [ ] Release weekly bug-fix patches.

---

## Appendix: Open Questions & Decisions Log

| QUESTION | DECISION MADE | RATIONALE | DATE |
|----------|---------------|-----------|------|
| Should we allow anonymous job searches? | No. Registration is mandatory to view listings. | Protects proprietary job data and ensures all search activity yields high-intent leads. | 2026-06-20 |
| Which calendar tool should we support first for scheduling? | Google Calendar. | Over 90% of target students and participating companies use Google Workspace. | 2026-06-22 |
| How do we handle manual resume uploads? | Parse via standard PDF parsers and index the raw text. | Allows the matching engine to read resume keywords and rank candidates accurately. | 2026-06-23 |

---

*PRD Version 1.0 — {idea} | {industry} | Generated by BlueprintAI*"""
