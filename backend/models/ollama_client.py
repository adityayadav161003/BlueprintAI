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
        self.base_url = (base_url or os.getenv("OLLAMA_BASE_URL", OLLAMA_BASE_URL)).rstrip("/")
        self.default_model = default_model or os.getenv("OLLAMA_MODEL", OLLAMA_MODEL)

    def check_connection(self) -> bool:
        try:
            url = f"{self.base_url}/api/tags"
            with urllib.request.urlopen(url, timeout=1.0) as response:
                if response.status == 200:
                    return True
        except Exception:
            pass
        return False

    def get_best_model(self) -> str:
        try:
            url = f"{self.base_url}/api/tags"
            with urllib.request.urlopen(url, timeout=1.0) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    models = [m.get("name") for m in data.get("models", [])]
                    for m in models:
                        if "qwen" in m.lower():
                            return m
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
                return
            except Exception as e:
                print(f"Ollama stream error: {e}. Falling back to mock generator...")

        global ENABLE_MOCK_FALLBACK
        enable_mock = os.getenv("ENABLE_MOCK_FALLBACK", "true").lower() == "true"
        if enable_mock:
            for chunk in self._generate_mock_stream(agent_type, user_idea, industry):
                yield chunk
        else:
            raise RuntimeError("Ollama is offline and mock fallback is disabled.")

    def _detect_theme(self, idea: str, industry: str) -> str:
        idea_lower = idea.lower()
        ind_lower = industry.lower() if industry else ""
        
        if any(w in idea_lower for w in ["dating", "cafe", "hangout", "vibe", "match", "meet", "social", "friend", "connect"]) or "dating" in ind_lower or "social" in ind_lower:
            return "dating"
        if any(w in idea_lower for w in ["car", "share", "decentralized", "smart contract", "blockchain", "ride", "vehicle", "transit"]) or "sharing" in ind_lower or "blockchain" in ind_lower:
            return "car_sharing"
        if any(w in idea_lower for w in ["health", "medicine", "delivery", "deliever", "doctor", "pharmacy", "clinic", "patient"]) or "health" in ind_lower:
            return "healthcare"
        if any(w in idea_lower for w in ["resell", "marketplace", "laptop", "buy", "sell", "used", "store", "shop"]) or "marketplace" in ind_lower or "ecommerce" in ind_lower:
            return "marketplace"
        if any(w in idea_lower for w in ["placement", "job", "career", "hiring", "recruit", "student", "university", "internship"]) or "recruit" in ind_lower:
            return "placement"
        return "general"

    def _get_short_name(self, idea: str) -> str:
        if not idea:
            return "App"
        short_name = idea.split(" for ")[0].split(" to ")[0].strip()
        short_name = " ".join([w.capitalize() for w in short_name.split(" ")])
        words = short_name.split(" ")
        if len(words) > 3:
            short_name = " ".join(words[:3])
        return short_name

    def _customize_mock_text(self, text: str, idea: str, industry: str) -> str:
        if not idea:
            idea = "a modern software product"
        if not industry:
            industry = "Technology"

        short_name = self._get_short_name(idea)

        text = text.replace("A placement app for university students to grab opportunity from big companies", idea)
        text = text.replace("a placement app for university students to grab opportunity from big companies", idea.lower())
        text = text.replace("A Placement App For University Students To Grab Opportunity From Big Companies", short_name)
        text = text.replace("A placement app for university students to grab opportunity from big companies", short_name)
        text = text.replace("A placement app", short_name)
        text = text.replace("a placement app", short_name.lower())
        
        text = text.replace("university students", "target users")
        text = text.replace("university student", "user")
        text = text.replace("University Students", "Target Users")
        text = text.replace("University Student", "User")
        
        text = text.replace("big companies", "external partners/employers")
        text = text.replace("big company", "partner/employer")
        text = text.replace("Big Companies", "Partners & Employers")
        
        text = text.replace("SaaS / Web App", industry)
        text = text.replace("SaaS/Web App", industry)

        text = text.replace("placement portal", f"{short_name.lower()} portal")
        text = text.replace("job match", "core match")
        text = text.replace("job listings", "listings/items")
        text = text.replace("job listing", "listing/item")
        text = text.replace("Job Listings", "Listings & Items")
        text = text.replace("Job Listing", "Listing & Item")
        text = text.replace("job search", "search & discovery")
        text = text.replace("job application", "submission/transaction")
        text = text.replace("Job Application", "Submission & Transaction")
        
        text = text.replace("Emily Chen", "Emily Chen (User)")
        text = text.replace("Rohan Patel", "Rohan Patel (Secondary User)")
        
        return text

    def _generate_mock_stream(self, agent_type: str, user_idea: str, industry: str) -> Generator[str, None, None]:
        idea = user_idea or "Selected Product Idea"
        ind = industry or "General Tech"
        theme = self._detect_theme(idea, ind)

        if agent_type == "ba":
            mock_data = self._get_mock_ba(idea, ind)
        elif agent_type == "pm":
            mock_data = self._get_mock_pm(idea, ind)
        elif agent_type == "qa":
            mock_data = self._get_mock_qa(idea, ind)
        else:
            mock_data = self._get_mock_syn(idea, ind)

        if theme == "placement" or theme == "general":
            mock_data = self._customize_mock_text(mock_data, idea, ind)

        words = mock_data.split(" ")
        chunk_size = 3
        for i in range(0, len(words), chunk_size):
            chunk = " ".join(words[i:i+chunk_size]) + " "
            yield chunk
            time.sleep(0.012)

    def _get_mock_ba(self, idea: str, industry: str) -> str:
        theme = self._detect_theme(idea, industry)
        short_name = self._get_short_name(idea)
        
        if theme == "dating":
            return f"""## Executive Summary

Provide a high-level summary of the product blueprint using the following bullet points:
- **Product Vision:** To create a low-pressure, vibe-aligned social experience through {short_name}, connecting users in real-world local cafes.
- **Core Problem:** Digital fatigue from endless swiping without meeting, combined with the high-pressure environment of traditional first dates.
- **Our Solution:** A double-opt-in matching algorithm based on vibe filters, followed by structured, low-pressure casual cafe meetups.
- **Target Customer:** Urban singles (ages 20-35) seeking casual hangouts and local cafe owners looking for foot traffic.
- **Business Model:** Freemium model with premium filters, cafe booking reservation commissions, and in-app partner promotions.
- **MVP Launch Target:** 12 weeks.
- **Success Definition:** 10,000 active profiles, 100 cafe partners onboarded, and 2,000 successful match meetups in Month 1.

---

## 1. Problem Statement & Opportunity

The dating and social app market is plagued by "burnout." Users spend hours swiping on profiles, but only a small fraction result in actual conversations, and even fewer lead to real-life meetups. Traditional date settings (like formal dinners) feel high-pressure and awkward if the vibe doesn't match in person. 

This creates a massive market opportunity for {short_name}. By focusing exclusively on casual, low-pressure cafe dates, {short_name} bridges the gap between digital matching and physical meeting. The global online dating market is valued at $8.8 billion, and a micro-dating platform targeted at casual hangouts represents a highly lucrative segment.

---

## 2. Target User Personas

### Leo, 24 — Software Developer, Seattle
- **Demographics:** Male, 24, single, tech-savvy, lives in a downtown apartment.
- **Daily Workflow:** Works from home or local cafes; spends evenings browsing social media or gaming.
- **Pain Points:** Tired of swiping on apps for weeks only to have conversations fizzle out before meeting.
- **Goals:** Find a casual way to meet people in real life without the pressure of a formal dinner date.
- **Tech Stack:** High comfort; uses macOS, iOS, Spotify, Discord.
- **Budget Authority:** Personal entertainment budget of $150/month.
- **Success Metrics:** Going from match to a 30-minute cafe meetup within 3 days.
- **Quote:** "I just want to grab a coffee and see if we vibe, rather than exchanging text messages for a month."
- **Usage Pattern:** Opens the app daily after work to view local vibe-matches.

### Maya, 27 — Graphic Designer & Creative, Austin
- **Demographics:** Female, 27, outgoing, passionate about art and coffee culture.
- **Daily Workflow:** Visits local cafes to sketch and work; active in local community groups.
- **Pain Points:** Safety concerns when meeting strangers online and bad experiences with high-pressure dates.
- **Goals:** Meet vibe-matched partners in public, friendly spots with clear safety guidelines.
- **Tech Stack:** Outfit, Pinterest, Instagram, iOS.
- **Budget Authority:** Moderate budget; willing to pay $15/month for safety and verified profile features.
- **Success Metrics:** Meeting partners at vetted local partner cafes.
- **Quote:** "A cafe date is perfect because I can leave in 15 minutes if there's no spark, or stay for hours if we connect."
- **Usage Pattern:** Checks app 2-3 times a week, prioritizing verified profiles.

### Jordan, 35 — Cafe Owner, Chicago
- **Demographics:** Non-binary, 35, local business owner, active in merchant associations.
- **Daily Workflow:** Manages daily operations, inventory, and marketing campaigns for a local cafe.
- **Pain Points:** High competition from major chains and low weekday afternoon traffic.
- **Goals:** Attract recurring customers and fill empty tables during off-peak hours.
- **Tech Stack:** Point-of-sale systems, Instagram business, Square.
- **Budget Authority:** Business marketing budget of $500/month.
- **Success Metrics:** Generating at least 30 new tables per month via in-app bookings.
- **Quote:** "I love hosting casual date check-ins. It brings new faces to my shop and boosts our sales."
- **Usage Pattern:** Checks the partner dashboard twice a week to manage bookings."""

        elif theme == "car_sharing":
            return f"""## Executive Summary

Provide a high-level summary of the product blueprint using the following bullet points:
- **Product Vision:** To democratize urban mobility through {short_name}, a decentralized peer-to-peer car sharing platform secured by smart contracts.
- **Core Problem:** High cost of car ownership in cities, underutilized vehicles, and high middleman fees from traditional car rental services.
- **Our Solution:** A trustless peer-to-peer sharing system with smart contract-escrow payments and hardware-integrated IoT locks.
- **Target Customer:** City residents without cars, and local vehicle owners looking to monetize idle vehicles.
- **Business Model:** Low protocol transaction fee (5%) on each rental transaction.
- **MVP Launch Target:** 12 weeks.
- **Success Definition:** 500 cars listed, 2,500 rental days completed, and zero major contract exploits in Month 1.

---

## 1. Problem Statement & Opportunity

Urban car ownership is increasingly expensive and inefficient, with vehicles remaining parked 95% of the time. Traditional car-sharing companies charge high overhead fees and require extensive manual verification, leading to friction. By building a peer-to-peer sharing service backed by smart contracts, {short_name} eliminates intermediaries, lowers costs, and distributes value directly to owners and renters.

The global car-sharing market is projected to reach $15 billion by 2030. Utilizing decentralized ledger technologies for reputation tracking, deposit escrow, and automated insurance agreements presents a massive opportunity to capture market share.

---

## 2. Target User Personas

### Alex, 29 — Digital Marketing Lead, Chicago
- **Demographics:** Male, 29, lives in a transit-oriented neighborhood, does not own a vehicle.
- **Daily Workflow:** Commutes via subway; needs a vehicle occasionally for weekend errands or trips.
- **Pain Points:** High cost and rigid pickup times of traditional car rental agencies.
- **Goals:** Instantly find and unlock a nearby vehicle for a few hours without paperwork.
- **Tech Stack:** High comfort; Android, Chrome, MetaMask, Coinbase app.
- **Budget Authority:** Transportation budget of $200/month.
- **Success Metrics:** Unlocking a car within 10 minutes of booking.
- **Quote:** "I just want to grab a nearby car, run my errands, and return it without talking to a single agent."
- **Usage Pattern:** Weekly rental on weekends.

### Elena, 34 — Financial Analyst, New York
- **Demographics:** Female, 34, owns a Tesla Model 3, parks in a secure garage.
- **Daily Workflow:** Commutes via train; her car sits unused in the garage Monday through Friday.
- **Pain Points:** High monthly car payments and insurance fees for an underutilized asset.
- **Goals:** Earn passive income safely by renting out her car to verified drivers.
- **Tech Stack:** Tesla App, iOS, decentralized web apps.
- **Budget Authority:** Vehicle expenses budget.
- **Success Metrics:** Earning at least $400/month to offset car payments.
- **Quote:** "My car should be earning money when I'm not using it, but I need to know the insurance and lock security are handled."
- **Usage Pattern:** Lists car for rent every weekday.

### David, 42 — Web3 Smart Contract Auditor, Denver
- **Demographics:** Male, 42, security researcher, safety-conscious.
- **Daily Workflow:** Audits blockchain protocols; travels frequently for tech conferences.
- **Pain Points:** Concern over security vulnerabilities in Web3 protocols and escrow handlers.
- **Goals:** Verify the security and safety of peer-to-peer agreements on-chain.
- **Tech Stack:** Linux, Solidity tools, hardware wallets.
- **Budget Authority:** Moderate price sensitivity.
- **Success Metrics:** Zero contract security issues reported.
- **Quote:** "The code is the law. The escrow contract must be fully transparent and audited before any transaction happens."
- **Usage Pattern:** Uses the service during business travel, auditing the contract parameters before renting."""

        elif theme == "healthcare":
            return f"""## Executive Summary

Provide a high-level summary of the product blueprint using the following bullet points:
- **Product Vision:** To redefine prescription logistics via {short_name}, ensuring secure, HIPAA-compliant, real-time medicine delivery.
- **Core Problem:** Vulnerable patients face delays, long pharmacy lines, and delivery errors for critical medications.
- **Our Solution:** A pharmacy-integrated dispatch platform with cold-chain tracking and secure prescription validation.
- **Target Customer:** Elderly or chronic patients, local independent pharmacies, and medical courier agents.
- **Business Model:** Per-delivery transaction fees paid by pharmacies and patients, and premium subscription options.
- **MVP Launch Target:** 12 weeks.
- **Success Definition:** 2,000 deliveries completed, 20 partner pharmacies onboarded, and 99.8% on-time delivery in Month 1.

---

## 1. Problem Statement & Opportunity

Patients with chronic illnesses rely on consistent medication access, yet traditional mail delivery is slow and local pharmacy pickup requires travel and waiting in lines. For time-sensitive or temperature-sensitive medications (like insulin), any logistics delay poses serious health risks. 

{short_name} addresses this by connecting pharmacies with medical-grade couriers for on-demand delivery. The digital health market is growing rapidly, with medicine delivery services representing a critical component of the healthcare logistics opportunity.

---

## 2. Target User Personas

### Mary, 72 — Retired Teacher, Miami
- **Demographics:** Female, 72, retired, lives alone, has chronic arthritis.
- **Daily Workflow:** Stays at home; relies on neighbors or family for grocery trips.
- **Pain Points:** Painful and difficult to travel to the pharmacy, wait in line, and manage refills.
- **Goals:** Receive medications directly at her doorstep reliably every month.
- **Tech Stack:** Low comfort; uses iPad for video calls and simple apps.
- **Budget Authority:** Fixed retirement pension; highly sensitive to delivery costs.
- **Success Metrics:** Medicine delivered on time with clear, easy-to-read dosage instructions.
- **Quote:** "I just want my blood pressure pills delivered without having to ask my daughter to drive me to the pharmacy."
- **Usage Pattern:** Monthly recurring prescription delivery.

### Dr. Samuel, 45 — Primary Care Physician, Boston
- **Demographics:** Male, 45, manages a busy family practice clinic.
- **Daily Workflow:** Diagnoses patients, updates electronic health records, and sends prescriptions.
- **Pain Points:** Patients forgetting to pick up their medications, leading to poor health outcomes.
- **Goals:** Direct-to-home prescription options to improve patient medication adherence.
- **Tech Stack:** Epic EHR system, macOS, iOS.
- **Budget Authority:** Clinic manager.
- **Success Metrics:** Verified patient delivery notifications returned to the clinic EHR.
- **Quote:** "If I can prescribe a medicine and have it show up at the patient's house within 4 hours, treatment success sky-rockets."
- **Usage Pattern:** Active daily when sending prescriptions.

### John, 31 — Medical Courier, Houston
- **Demographics:** Male, 31, professional driver, independent courier contractor.
- **Daily Workflow:** Drives a refrigerated vehicle; accepts medical delivery dispatches.
- **Pain Points:** Disorganized routing, lack of cold-chain monitoring tools, and HIPAA compliance paperwork.
- **Goals:** Maximize daily deliveries with efficient routing while maintaining medical standards.
- **Tech Stack:** Android smartphone, GPS routing apps.
- **Budget Authority:** Vehicle maintenance budget.
- **Success Metrics:** Completing 15 deliveries per day safely.
- **Quote:** "I need to know the temperature of the package is tracked automatically so I'm not held liable for spoiled medicine."
- **Usage Pattern:** Active daily during work shifts."""

        elif theme == "marketplace":
            return f"""## Executive Summary

Provide a high-level summary of the product blueprint using the following bullet points:
- **Product Vision:** To build the most trusted circle for tech hardware transactions through {short_name}, a verified, escrow-secured used marketplace.
- **Core Problem:** High rates of fraud, broken hardware, and payment scams on unvetted marketplaces (like Craigslist or Facebook Marketplace).
- **Our Solution:** A local escrow-payment marketplace with certified quality checks and secure transaction pick-up centers.
- **Target Customer:** Budget-conscious tech buyers (students, freelancers) and individual tech sellers.
- **Business Model:** Flat commission fee (8%) on successful seller transactions.
- **MVP Launch Target:** 12 weeks.
- **Success Definition:** 1,500 active listings, 500 completed transactions, and zero reported buyer scam losses in Month 1.

---

## 1. Problem Statement & Opportunity

Buying used electronics is a risky process. Buyers often receive hardware with hidden defects, while sellers face chargeback scams, ghosting, and safety concerns during physical meetups. {short_name} solves this by introducing a verified hardware diagnostic checklist, secure Stripe-based escrow payments, and local partner meetup spots.

With global e-waste awareness rising and inflation driving demand for refurbished tech, the secondary electronics market is expanding rapidly. Establishing a secure, trusted niche marketplace offers a high-value opportunity.

---

## 2. Target User Personas

### Jake, 21 — College Student, Boston
- **Demographics:** Male, 21, student, tight budget, lives in university dorms.
- **Daily Workflow:** Attends classes, studies, works part-time at a library.
- **Pain Points:** Can't afford a brand new laptop for his classes; fears getting scammed with a broken machine on Craigslist.
- **Goals:** Buy a reliable, pre-owned laptop with verified hardware specs and battery health.
- **Tech Stack:** Windows laptop, iOS smartphone, Discord.
- **Budget Authority:** Hard budget of $400.
- **Success Metrics:** Buying a laptop that matches the exact verified diagnostics report.
- **Quote:** "I just want a laptop that works. If the battery is bad, I want to know before I pay."
- **Usage Pattern:** Browses listings daily until purchase.

### Chloe, 26 — Freelance Video Editor, Austin
- **Demographics:** Female, 26, upgrading her workstation, tech-savvy.
- **Daily Workflow:** Works from home editing videos; frequently sells older gear to fund upgrades.
- **Pain Points:** Time wasted dealing with lowball offers, safety concerns during meetups, and transaction chargebacks.
- **Goals:** Sell her old MacBook Pro quickly to a verified buyer for a fair price.
- **Tech Stack:** macOS, Premiere Pro, Stripe.
- **Budget Authority:** Reinvesting sale proceeds.
- **Success Metrics:** Securely receiving payment in her bank account within 3 days.
- **Quote:** "I don't want to meet strangers in dark parking lots. I want a secure escrow process that protects my gear and money."
- **Usage Pattern:** Lists items 2-3 times a year.

### Mark, 38 — Refurbishment Technician, Philadelphia
- **Demographics:** Male, 38, electronics repair expert, works in a local workshop.
- **Daily Workflow:** Diagnoses, cleans, and repairs laptops and smartphones.
- **Pain Points:** Hard to find local buyers for refurbished stock; lack of standardized diagnostic logs.
- **Goals:** Certify and list refurbished electronics easily, reaching local buyers.
- **Tech Stack:** Hardware testing tools, desktop inventory apps.
- **Budget Authority:** Owner of repair shop.
- **Success Metrics:** Generating diagnostic reports that directly boost sales conversion.
- **Quote:** "When I upload a certified hardware report, it shows the buyer that the device has been fully tested and cleaned."
- **Usage Pattern:** Uploads 5-10 diagnostic reports weekly."""

        else:
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
        theme = self._detect_theme(idea, industry)
        short_name = self._get_short_name(idea)
        
        if theme == "dating":
            return f"""## 3. Prioritized User Stories

### Must-Have (Core Loop)
*Without these, the product does not work.*
- **As a user**, I want to build a profile with my vibe preferences and interests, so that I can get matches.
  > **AC:** Given I am a registered user, When I save my vibe selections, Then the system updates my profile match pool.
- **As a user**, I want to browse local partner cafes and book a date slot, so that I can meet my match.
  > **AC:** Given I am matched, When I select a cafe and confirm a slot, Then the booking is made and both users receive a calendar invite.
- **As a user**, I want to message my matched partner, so that we can coordinate the meetup.
  > **AC:** Given we are matched, When I send a message, Then my partner receives a push notification within 200ms.

### Should-Have
*Significantly improves the experience.*
- **As a user**, I want to view verified profiles to avoid scams, so that I can meet safely.
  > **AC:** Given I view a profile, When the user has verified their identity, Then a verification badge is displayed.

### Could-Have
*Defer if needed.*
- **As a user**, I want to pre-order my coffee or drinks, so that we don't have to queue when we arrive.
  > **AC:** Given I have a booked table slot, When I select drinks, Then the order is sent to the cafe POS system.

### Won't-Have (MVP Exclusions)
- **Video Chat Matching:** Pre-meet video calls will be deferred for the initial release.

---

## 4. Functional Requirements

| ID | FEATURE | USER STORY REF | DETAILED DESCRIPTION | ACCEPTANCE CRITERIA | PRIORITY | EST. EFFORT |
|----|---------|----------------|----------------------|---------------------|----------|-------------|
| FR-101 | Vibe Matcher | US-101 | Algorithmic matching based on shared music, hobbies, and social goals. | Matched profiles display compatibility %. | High | 4 days |
| FR-102 | Cafe Booking | US-102 | Calendar integration with local cafe slots for real-time table booking. | Booking confirmed via email and SMS. | High | 5 days |
| FR-103 | Trust Center | US-104 | Verification module via photo selfie comparison. | Verification badge issued upon validation. | Medium | 3 days |

---

## 5. Non-Functional Requirements

### Performance SLAs
| METRIC | REQUIREMENT | MEASUREMENT METHOD |
|--------|-------------|--------------------|
| Feed Load Latency | < 1.5 seconds for match deck. | client-side telemetry. |
| Booking API Latency | < 500ms for reservation. | APM trace logs. |

### Security & Compliance
| REQUIREMENT | STANDARD | IMPLEMENTATION |
|-------------|----------|----------------|
| Privacy | GDPR & CCPA. | Profile deletion options and cookie consent. |
| Authentication | Multi-Factor Authentication. | SMS OTP via Twilio. |

### Scalability Plan
- **Phase 1 (0-1K users):** Single PostgreSQL instance, server-side cache.
- **Phase 2 (1K-10K users):** Horizontally scaled backend pods, Redis caching cluster for match lists.

---

## 6. Technical Architecture

### Recommended Tech Stack
| LAYER | TECHNOLOGY | JUSTIFICATION |
|-------|------------|---------------|
| Frontend | React Native, Tailwind CSS | Native mobile feel for iOS/Android with rapid UI iteration. |
| Backend | Node.js, Express | Non-blocking socket connections for real-time chat. |
| Database | PostgreSQL | Strong relations for bookings, users, and matches. |

### System Architecture Overview
The application consists of a React Native mobile client talking to an Express API Gateway. Match events and chat messages are synced via socket servers and cached in Redis.

```mermaid
flowchart TD
    App[React Native App] -->|Socket.io| Backend[Express Chat Server]
    Backend -->|Cache Matches| Redis[(Redis Caching)]
    Backend -->|Store Bookings| DB[(PostgreSQL Database)]
```

### Data Model (Key Entities)
- **User:** `id`, `name`, `email`, `vibe_vector`, `created_at`
- **CafePartner:** `id`, `name`, `address`, `available_slots`
- **Match:** `id`, `user1_id`, `user2_id`, `status`
- **Booking:** `id`, `match_id`, `cafe_id`, `slot_time`, `status`

### API Design (Key Endpoints)
| METHOD | ENDPOINT | DESCRIPTION | REQUEST BODY | RESPONSE |
|--------|----------|-------------|--------------|----------|
| POST | `/api/matches/match` | Attempt match. | `{{user_id}}` | `{{matched: true, room_id}}` |
| POST | `/api/bookings` | Book a table. | `{{match_id, cafe_id, slot}}` | `{{booking_id, status: confirmed}}` |

---

## 7. UI/UX Specifications

### Screen Inventory
- **Onboarding Wizard:** Vibe selector and profile setup.
- **Match Discovery:** Cards showing profile info, photos, and match percentage.
- **Chat & Meet Panel:** Chat thread with direct "Book Cafe" integration.
- **Cafe Detail Panel:** Selected cafe description, reviews, and calendar picker.

### Design System Requirements
- **Typography:** Outfit (Headings) and Inter (Body).
- **Color Palette:** Warm HSL dark mode. Background: Charcoal `#121212`, Primary Accent: Peach `#FF6B6B`, Success: Emerald `#10B981`.

### Critical User Flows
1. **Match to Meetup:** Match screen -> Open Chat -> Click Book Table -> Select slot -> Receive invitation.

---

## 11. Success Metrics & KPIs

- **North Star Metric:** Meetup Completion Rate (Percentage of matches that complete a physical cafe date).

### Metric Framework
| METRIC | BASELINE | MONTH 1 | MONTH 3 | MONTH 6 | MONTH 12 |
|--------|----------|---------|---------|---------|----------|
| Completed Dates | 0 | 500 | 2,000 | 8,000 | 25,000 |
| In-App Booking Rate | 0 | 40% | 50% | 60% | 75% |
| User Retention (D28) | 0 | 25% | 30% | 35% | 45% |

### Analytics Implementation
- **Events to Track:** `match_created`, `chat_sent`, `booking_initiated`, `booking_completed`, `check_in_at_cafe`."""

        elif theme == "car_sharing":
            return f"""## 3. Prioritized User Stories

### Must-Have (Core Loop)
*Without these, the product does not work.*
- **As a renter**, I want to view a map of nearby shared vehicles, so that I can rent one close to me.
  > **AC:** Given I am on the map tab, When the app loads, Then it displays pins for all available vehicles within a 2-mile radius.
- **As an owner**, I want to list my vehicle on the platform with pricing, so that renters can book it.
  > **AC:** Given I own a vehicle, When I complete the vehicle registration form, Then it becomes active on the listing map.
- **As a renter**, I want to lock/unlock the vehicle via smart contract trigger, so that I can access the car.
  > **AC:** Given I have an active reservation, When I click "Unlock" in the app, Then the hardware lock status transitions in 2 seconds.

### Should-Have
*Significantly improves the experience.*
- **As a renter**, I want to submit security deposits in escrow, so that I can rent premium cars.
  > **AC:** Given I book a vehicle, When I sign the transaction, Then the security deposit is locked in the smart contract.

### Could-Have
*Defer if needed.*
- **As an owner**, I want to view battery or fuel levels of my vehicle remotely, so that I can schedule servicing.
  > **AC:** Given my car is listed, When I open my owner console, Then the OBD-II metrics are loaded in real-time.

### Won't-Have (MVP Exclusions)
- **Multi-Chain Payments:** Renting via tokens on chains other than Ethereum/Polygon is deferred.

---

## 4. Functional Requirements

| ID | FEATURE | USER STORY REF | DETAILED DESCRIPTION | ACCEPTANCE CRITERIA | PRIORITY | EST. EFFORT |
|----|---------|----------------|----------------------|---------------------|----------|-------------|
| FR-101 | Map Finder | US-101 | Displays available cars using Google Maps API. | Pins update based on GPS moves. | High | 4 days |
| FR-102 | IoT Lock Controller | US-103 | Direct integration with vehicle's Bluetooth/IoT hardware lock system. | Unlock action fires in 2 seconds. | High | 6 days |
| FR-103 | Smart Escrow Contract | US-104 | Solidity contract locking deposit until trip is marked complete. | Funds release automatically on trip close. | High | 5 days |

---

## 5. Non-Functional Requirements

### Performance SLAs
| METRIC | REQUIREMENT | MEASUREMENT METHOD |
|--------|-------------|--------------------|
| Map Pin Update | < 1.0 second upon location shift. | Frontend telemetry. |
| Lock Latency | < 3 seconds from phone click to physical unlock. | End-to-end trace logs. |

### Security & Compliance
| REQUIREMENT | STANDARD | IMPLEMENTATION |
|-------------|----------|----------------|
| Smart Contract Audit | SECP256k1 Elliptic Curve & OpenZeppelin. | Multi-sig lock controllers and external audits. |
| Compliance | KYC/AML verification. | Stripe Identity integration. |

### Scalability Plan
- **Phase 1 (0-1K users):** Shared RPC node connection, centralized SQL cache.
- **Phase 2 (1K-10K users):** Dedicated Infura/Alchemy RPC cluster, partitioned database indexing.

---

## 6. Technical Architecture

### Recommended Tech Stack
| LAYER | TECHNOLOGY | JUSTIFICATION |
|-------|------------|---------------|
| Frontend | React.js, Tailwind CSS | Modular structures, rich map interfaces. |
| Backend | Node.js, Web3.js | Direct interaction with EVM blockchains and REST API servers. |
| Database | PostgreSQL | Storing user accounts, telemetry, and trip logs. |

### System Architecture Overview
The frontend queries active cars from PostgreSQL while writing booking details directly to an Ethereum Virtual Machine (EVM) Smart Contract. IoT hardware triggers verify contract state before opening.

```mermaid
flowchart TD
    App[React App] -->|REST API| Backend[Node.js Server]
    App -->|Web3 Transaction| EVM[EVM Smart Contract]
    Backend -->|Polls Events| EVM
    EVM -->|Triggers Unlock| Car[Vehicle IoT Lock]
```

### Data Model (Key Entities)
- **User:** `id`, `wallet_address`, `verified_license_url`
- **Vehicle:** `id`, `owner_id`, `vin`, `gps_lat`, `gps_lng`, `status`
- **Booking:** `id`, `renter_id`, `vehicle_id`, `contract_tx_hash`, `status`

### API Design (Key Endpoints)
| METHOD | ENDPOINT | DESCRIPTION | REQUEST BODY | RESPONSE |
|--------|----------|-------------|--------------|----------|
| GET | `/api/vehicles/map` | Get vehicles. | None (Query bounding box) | `[Vehicle]` |
| POST | `/api/trips/unlock` | Request unlock. | `{{booking_id, signature}}` | `{{unlocked: true}}` |

---

## 7. UI/UX Specifications

### Screen Inventory
- **Map View Dashboard:** Full-screen map with active cars and radius search.
- **Vehicle Info Sheet:** Drawer showing vehicle range, rating, price, and "Book" CTA.
- **Trip Console:** In-progress interface with "Unlock Door" and "End Trip" buttons.
- **Owner Dashboard:** Earnings charts, trip history logs, and vehicle status toggles.

### Design System Requirements
- **Typography:** Outfit (Headings) and Inter (Body).
- **Color Palette:** Tech-premium dark mode. Background: Slate `#0B0F19`, Accent: Emerald `#10B981`, Warning: Amber `#F59E0B`.

### Critical User Flows
1. **Rent and Unlock:** Open app -> Tap car pin -> Confirm booking -> Tap "Unlock" -> IoT lock triggers -> Trip starts.

---

## 11. Success Metrics & KPIs

- **North Star Metric:** Daily Completed Rental Hours (Total hours vehicles are actively rented per day).

### Metric Framework
| METRIC | BASELINE | MONTH 1 | MONTH 3 | MONTH 6 | MONTH 12 |
|--------|----------|---------|---------|---------|----------|
| Active Cars Listed | 0 | 100 | 500 | 2,000 | 5,000 |
| Rental Hour Volume | 0 | 400 hrs | 2,500 hrs| 12,000 hrs| 45,000 hrs|
| IoT Unlock Success Rate | 0 | 99.5% | 99.8% | 99.9% | 99.9% |

### Analytics Implementation
- **Events to Track:** `car_listed`, `booking_signed`, `iot_unlock_triggered`, `trip_completed`, `escrow_released`."""

        elif theme == "healthcare":
            return f"""## 3. Prioritized User Stories

### Must-Have (Core Loop)
*Without these, the product does not work.*
- **As a patient**, I want to upload a prescription photo, so that I can order my medicines.
  > **AC:** Given I am on the checkout screen, When I upload a PDF or image, Then the file is stored and queued for pharmacist verification.
- **As a pharmacist**, I want to verify prescriptions and fill medication boxes, so that they can be dispatched.
  > **AC:** Given a pending order, When I click "Approve", Then the order status shifts to "Ready for Dispatch".
- **As a courier**, I want to accept delivery routes, so that I can deliver medicine boxes to patients.
  > **AC:** Given my driver app is active, When an order is ready within 5 miles, Then I receive a delivery card.

### Should-Have
*Significantly improves the experience.*
- **As a patient**, I want to track cold-chain temperature status of my insulin, so that I know it is safe.
  > **AC:** Given my delivery is in transit, When I check the map, Then the real-time package temperature is shown.

### Could-Have
*Defer if needed.*
- **As a patient**, I want automatic monthly refill deliveries, so that I don't run out of critical meds.
  > **AC:** Given a chronic prescription, When I opt-in to auto-refills, Then the app creates delivery orders every 28 days.

### Won't-Have (MVP Exclusions)
- **Direct Insurance Billing:** Auto-calculating co-pays with national insurance networks is deferred.

---

## 4. Functional Requirements

| ID | FEATURE | USER STORY REF | DETAILED DESCRIPTION | ACCEPTANCE CRITERIA | PRIORITY | EST. EFFORT |
|----|---------|----------------|----------------------|---------------------|----------|-------------|
| FR-101 | Document Uploader | US-101 | Upload and preview prescriptions securely. | Upload complies with HIPAA storage rules. | High | 3 days |
| FR-102 | Dispatch Terminal | US-103 | Interactive map and order queue for pharmacists and couriers. | Real-time queue syncs via SSE. | High | 5 days |
| FR-103 | Cold-Chain Sync | US-104 | Bluetooth sync with portable temperature tags in courier boxes. | Temperature breaches trigger instant alerts. | Medium | 4 days |

---

## 5. Non-Functional Requirements

### Performance SLAs
| METRIC | REQUIREMENT | MEASUREMENT METHOD |
|--------|-------------|--------------------|
| Image Upload Speed | < 3.0 seconds for 5MB file. | Client network stats. |
| Courier Routing Delay | Route generation < 2.0 seconds. | Google Matrix API response logging. |

### Security & Compliance
| REQUIREMENT | STANDARD | IMPLEMENTATION |
|-------------|----------|----------------|
| Compliance | HIPAA Standards. | Database encryption at rest, secure PII access logging. |
| Cryptography | AES-256 for medical records. | Encrypted file blobs on AWS S3 buckets. |

### Scalability Plan
- **Phase 1 (0-1K users):** Central RDS PostgreSQL, standard S3 bucket.
- **Phase 2 (1K-10K users):** Multi-region file hosting, read replica databases for reporting tools.

---

## 6. Technical Architecture

### Recommended Tech Stack
| LAYER | TECHNOLOGY | JUSTIFICATION |
|-------|------------|---------------|
| Frontend | React Native | Single codebase for patient and driver mobile apps. |
| Backend | Node.js, Express | Fast asynchronous routing and push notification dispatch. |
| Database | PostgreSQL | Relational schema suited for auditing prescriptions and deliveries. |

### System Architecture Overview
The system coordinates patient orders, pharmacist verifications, and courier dispatch. Telemetry data from courier Bluetooth sensors is pushed to the API gateway.

```mermaid
flowchart TD
    PatientApp[Patient App] -->|Upload Doc| S3[(Secure S3 Storage)]
    PatientApp -->|API Request| API[Express API Gateway]
    PharmacistPortal[Pharmacist UI] -->|Approve| API
    API -->|Dispatch Route| DriverApp[Driver App]
    API -->|Store Audits| DB[(PostgreSQL)]
```

### Data Model (Key Entities)
- **User:** `id`, `name`, `role (patient/pharmacist/driver)`, `hipaa_consent`
- **Prescription:** `id`, `patient_id`, `pharmacist_id`, `doctor_name`, `file_url`, `status`
- **Order:** `id`, `prescription_id`, `driver_id`, `temp_log`, `status`, `delivered_at`

### API Design (Key Endpoints)
| METHOD | ENDPOINT | DESCRIPTION | REQUEST BODY | RESPONSE |
|--------|----------|-------------|--------------|----------|
| POST | `/api/prescriptions/upload` | Upload document. | `{{patient_id, file_bytes}}` | `{{doc_id, status: pending}}` |
| PATCH | `/api/orders/:id/status` | Update dispatch status. | `{{status, temp_reading}}` | `{{success: true}}` |

---

## 7. UI/UX Specifications

### Screen Inventory
- **Patient Dashboard:** Refill alerts, active delivery maps, and history.
- **Prescription Uploader:** Simple modal to snap a photo or pick a PDF file.
- **Pharmacy Dashboard:** Queue of pending orders with prescription images side-by-side.
- **Courier Map Console:** Turn-by-turn map, delivery details, and temperature indicators.

### Design System Requirements
- **Typography:** Outfit (Headings) and Inter (Body).
- **Color Palette:** Clean clinical palette. Background: Light Grey `#F9FAFB` (with HSL Dark Mode option), Teal `#0D9488`, Warning: Coral `#F43F5E`.

### Critical User Flows
1. **Prescribe to Deliver:** Upload file -> Pharmacist approves -> Driver accepts -> Delivery confirmed with photo.

---

## 11. Success Metrics & KPIs

- **North Star Metric:** Pharmacy Dispatch Time (Average minutes from prescription approval to courier delivery at patient home).

### Metric Framework
| METRIC | BASELINE | MONTH 1 | MONTH 3 | MONTH 6 | MONTH 12 |
|--------|----------|---------|---------|---------|----------|
| Completed Deliveries | 0 | 1,000 | 4,000 | 15,000 | 60,000 |
| Average Delivery Time | 0 | 4.2 hrs | 2.5 hrs | 1.8 hrs | 1.2 hrs |
| Temperature Integrity | 0 | 99.9% | 99.9% | 99.9% | 100% |

### Analytics Implementation
- **Events to Track:** `prescription_uploaded`, `prescription_approved`, `route_assigned`, `delivery_completed`, `temperature_alert`."""

        elif theme == "marketplace":
            return f"""## 3. Prioritized User Stories

### Must-Have (Core Loop)
*Without these, the product does not work.*
- **As a seller**, I want to list my used laptop with specs, photos, and price, so that buyers can purchase it.
  > **AC:** Given I am logged in, When I save the laptop form, Then the listing goes live on the marketplace search.
- **As a buyer**, I want to search and filter laptop listings by brand, RAM, storage, and price, so that I can find matching machines.
  > **AC:** Given I am on the search feed, When I select a filter, Then the results update in 300ms.
- **As a buyer**, I want to purchase a laptop via secure escrow, so that my money is held safely until I inspect the device.
  > **AC:** Given I click "Buy Now", When I pay via Stripe, Then the funds are locked in escrow and the seller is notified to ship.

### Should-Have
*Significantly improves the experience.*
- **As a seller**, I want to run a software diagnostic check and upload the logs, so that I can prove my laptop's health.
  > **AC:** Given I edit a listing, When I run the diagnostic helper, Then verified battery health and CPU logs are attached.

### Could-Have
*Defer if needed.*
- **As a buyer**, I want to compare two laptop listings side-by-side, so that I can choose the best deal.
  > **AC:** Given I select two devices, When I click "Compare", Then a spec table displays.

### Won't-Have (MVP Exclusions)
- **Trade-in Appraisals:** Auto-calculating trade-in value for old devices will be deferred.

---

## 4. Functional Requirements

| ID | FEATURE | USER STORY REF | DETAILED DESCRIPTION | ACCEPTANCE CRITERIA | PRIORITY | EST. EFFORT |
|----|---------|----------------|----------------------|---------------------|----------|-------------|
| FR-101 | Laptop Listing Wizard | US-101 | Multi-step form with specs, condition checklist, and image uploads. | Listing is saved and live instantly. | High | 3 days |
| FR-102 | Escrow Payment Gateway | US-103 | Stripe escrow integration holding funds until delivery is confirmed. | Escrow payouts trigger after 3-day inspection window. | High | 5 days |
| FR-103 | Diagnostic Parser | US-104 | Upload and parse diagnostic log files (.txt/.json) to display battery health. | Battery health shown as verified badge. | Medium | 4 days |

---

## 5. Non-Functional Requirements

### Performance SLAs
| METRIC | REQUIREMENT | MEASUREMENT METHOD |
|--------|-------------|--------------------|
| Search Response | < 300ms for keyword search. | Database query timing logs. |
| Image Load Latency | < 1.0 second for high-res listings. | CDN edge cache monitoring. |

### Security & Compliance
| REQUIREMENT | STANDARD | IMPLEMENTATION |
|-------------|----------|----------------|
| Payment Security | PCI-DSS Compliance. | Stripe Elements tokenization. |
| Escrow Disputes | Arbitration workflow. | Manual dispute ticket escalation system. |

### Scalability Plan
- **Phase 1 (0-1K users):** Standard PostgreSQL DB with CDN caching for media.
- **Phase 2 (1K-10K users):** Algolia/Elasticsearch integration for search indexing, read replica databases.

---

## 6. Technical Architecture

### Recommended Tech Stack
| LAYER | TECHNOLOGY | JUSTIFICATION |
|-------|------------|---------------|
| Frontend | Next.js, React | Server-side rendering (SSR) for fast product detail page SEO. |
| Backend | Python, Django | Strong ORM, out-of-the-box admin panel, excellent text parsing. |
| Database | PostgreSQL | Structured relational integrity for transactions and specs. |

### System Architecture Overview
The Next.js client renders static product pages served via Cloudflare CDN. Transactions and escrow flows are handled via Django and synchronized with Stripe.

```mermaid
flowchart TD
    Client[Next.js Web App] -->|CDN Cache| CDN[Cloudflare CDN]
    Client -->|REST API| API[Django Backend]
    API -->|Escrow Payment| Stripe[Stripe Escrow API]
    API -->|Query Devices| DB[(PostgreSQL Database)]
```

### Data Model (Key Entities)
- **User:** `id`, `username`, `email`, `rating`
- **LaptopListing:** `id`, `seller_id`, `brand`, `cpu`, `ram_gb`, `storage_gb`, `condition`, `price`, `status`
- **Transaction:** `id`, `listing_id`, `buyer_id`, `stripe_escrow_intent_id`, `status`

### API Design (Key Endpoints)
| METHOD | ENDPOINT | DESCRIPTION | REQUEST BODY | RESPONSE |
|--------|----------|-------------|--------------|----------|
| GET | `/api/laptops` | Search listings. | None (Query params) | `[LaptopListing]` |
| POST | `/api/transactions/escrow` | Initiate purchase. | `{{listing_id}}` | `{{checkout_url, tx_id}}` |

---

## 7. UI/UX Specifications

### Screen Inventory
- **Home Feed:** Main search feed with condition filters (Mint, Good, Fair) and specs.
- **Listing Details:** Image carousel, verified diagnostics badges, seller ratings, and buy button.
- **Listing Creator:** Upload wizard with file selector for diagnostic logs.
- **Transaction Center:** Status tracker showing (Paid, Shipped, In Inspection, Completed).

### Design System Requirements
- **Typography:** Outfit (Headings) and Inter (Body).
- **Color Palette:** Sleek HSL dark mode. Background: Deep charcoal `#1E293B`, Accent: Cobalt `#3B82F6`, Success: Emerald `#10B981`.

### Critical User Flows
1. **List Laptop with Diagnostics:** Click Sell -> Fill specs -> Drag-and-drop diagnostic file -> System parses battery health -> Click Publish.

---

## 11. Success Metrics & KPIs

- **North Star Metric:** Escrow Success Rate (Percentage of transactions completed without disputes or returns).

### Metric Framework
| METRIC | BASELINE | MONTH 1 | MONTH 3 | MONTH 6 | MONTH 12 |
|--------|----------|---------|---------|---------|----------|
| Active Listings | 0 | 300 | 1,200 | 5,000 | 15,000 |
| Completed Sales | 0 | 100 | 450 | 2,000 | 7,500 |
| Average Time to Sell | 0 | 14 days | 10 days | 7 days | 4 days |

### Analytics Implementation
- **Events to Track:** `item_listed`, `diagnostics_uploaded`, `purchase_initiated`, `shipment_confirmed`, `escrow_released`, `dispute_raised`."""

        else:
            return f"""## 3. Prioritized User Stories

### Must-Have (Core Loop)
*Without these, the product does not work.*
1. **As a university student**, I want to create a profile showcasing my skills, education, and experience, so that I can increase my visibility to potential employers.
   > **AC:** Given I am a registered user, When I fill out the profile form, Then my profile is created and visible to me and potential employers.
2. **As a university student**, I want to browse and search for job listings from big companies, so that I can find opportunities that match my skills and interests.
   > **AC:** Given I am a registered user, When I use the search function, Then I see a list of relevant job listings with company information and job details.
3. **As a university student**, I want to apply for job listings directly through the app, so that I can easily submit my application and resume.
   > **AC:** Given I am a registered user, When I click the "Apply" button on a job listing, Then my application and resume are submitted to the employer.
4. **As a recruiter**, I want to view candidate applications and update their status, so that I can manage my hiring pipeline.
   > **AC:** Given I am logged in as a recruiter, When I view a candidate, Then I can change their status (e.g. Under Review, Interview, Rejected).

### Should-Have
*Significantly improves the experience.*
5. **As a university student**, I want to see a compatibility match score for each listing, so that I can prioritize where to apply.
   > **AC:** Given I view job listings, When my profile has completed skills, Then each job displays a match percentage (e.g., 85% match).
6. **As a recruiter**, I want to schedule interviews directly through the app, so that I don't have to coordinate via email.
   > **AC:** Given a candidate is moved to "Interview", When I click "Schedule", Then the system integrates with calendar availability.

### Could-Have
*Defer if needed.*
7. **As a university student**, I want to get suggestions to improve my resume, so that I can increase my interview chances.
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
        theme = self._detect_theme(idea, industry)
        short_name = self._get_short_name(idea)
        
        if theme == "dating":
            return f"""## 8. QA & Testing Strategy

### Testing Types
- **Unit Testing:** 80% coverage target using Jest/Vitest for math, age validation, and vibe matching scores.
- **Integration Testing:** Verification of table slot reservations and calendar bookings.
- **End-to-End (E2E) Testing:** Playwright scenarios checking the chat screen's "Book Cafe" redirection.
- **Performance Testing:** k6 check simulating 1,500 concurrent match deck swiping events.
- **User Acceptance Testing (UAT):** Private trial with 4 local cafes and 40 active singles.

---

## 9. Risk Register & Mitigation Plan

| RISK | CATEGORY | LIKELIHOOD | IMPACT | MITIGATION STRATEGY | OWNER |
|------|----------|------------|--------|---------------------|-------|
| Trust & Safety Incidents | Security | Medium | Critical | Mandatory photo selfie verification and in-app reporting button. | Product Manager |
| Cafe Double-Booking | Operational | Medium | Medium | Implement locking mutexes on database reservations. | Tech Lead |
| Low In-App Conversions | Market | High | High | Offer free first-coffee credits at partner cafes to initiate meetups. | Business Analyst |

---

## 10. Project Build Plan & Roadmap

### Phased Roadmap
- **Phase 1: Foundation (Weeks 1-4):** Auth, profile setup, geo-location mapping.
- **Phase 2: Match Engine (Weeks 5-8):** Profile indexing, vibe match scores, chat threads.
- **Phase 3: Cafe Booking (Weeks 9-12):** Cafe slot database integrations, calendar reminders, POS trigger.
- **Phase 4: Launch (Weeks 13-16):** UAT beta tests, local marketing launch.

### Week-by-Week Month 1
- **Week 1:** Initialize React Native shell and backend routes.
- **Week 2:** Implement user signups and SMS OTP codes.
- **Week 3:** Build vibe-selector onboarding UI cards.
- **Week 4:** Write unit tests for matching algorithms.

### Team Requirements
- **1 Product Manager**
- **1 Frontend Native Dev**
- **1 Backend Node Dev**
- **1 QA Engineer**

---

## 12. Launch Checklist

### Pre-Launch (T-4 weeks)
- [ ] Freeze code features and run security penetration tests.
- [ ] Sign final contracts with initial 15 cafe partners.
- [ ] Configure Apple App Store and Google Play credentials.

### Launch Week
- [ ] Deploy server to AWS production node.
- [ ] Run automated health check monitors on Redis/Postgres.
- [ ] Launch local Instagram influencer promo campaign.

### Post-Launch (Weeks 1-4)
- [ ] Review customer support tickets regarding matching bugs.
- [ ] Verify cafe referral payouts and billing.

---

## Appendix: Open Questions & Decisions Log

| QUESTION | DECISION MADE | RATIONALE | DATE |
|----------|---------------|-----------|------|
| Can users search matches outside their city? | No. Initially locked to local geo-radius. | Ensures actual meetup rates remain high. | 2026-06-21 |
| Should we support custom meetup locations? | No. Only vetted partner cafes are supported. | Ensures safety and control over reservation APIs. | 2026-06-22 |"""

        elif theme == "car_sharing":
            return f"""## 8. QA & Testing Strategy

### Testing Types
- **Unit Testing:** 80% coverage on Solidity contracts using Hardhat/Truffle, and 85% on backend APIs.
- **Integration Testing:** Verification of transaction status flow from RPC logs to SQL cache database.
- **End-to-End (E2E) Testing:** Testing app-based lock/unlock signals with a mock IoT vehicle simulator.
- **Performance Testing:** Load testing Web3 event queries with k6.
- **User Acceptance Testing (UAT):** Private trial renting 10 cars with 30 drivers.

---

## 9. Risk Register & Mitigation Plan

| RISK | CATEGORY | LIKELIHOOD | IMPACT | MITIGATION STRATEGY | OWNER |
|------|----------|------------|--------|---------------------|-------|
| Smart Contract Vulnerability | Technical | Low | Critical | Open-source contract code and run professional CertiK audits. | Solidity Dev |
| Vehicle Damage or Theft | Operational | Medium | Critical | Require credit holds and integrate commercial peer-to-peer insurance. | Business Analyst |
| Bluetooth IoT lock connection drop | Technical | High | Medium | Support offline backup codes generated via local hardware keys. | Tech Lead |

---

## 10. Project Build Plan & Roadmap

### Phased Roadmap
- **Phase 1: Solidity & DB (Weeks 1-4):** Write escrow contracts, deploy to testnet, design database tables.
- **Phase 2: Renter UI (Weeks 5-8):** Build search maps, renter profiles, Web3 payment integrations.
- **Phase 3: Hardware Sync (Weeks 9-12):** Bluetooth lock API, check-in flows, driver trip metrics.
- **Phase 4: Launch (Weeks 13-16):** UAT beta trial, insurance coverage onboarding.

### Week-by-Week Month 1
- **Week 1:** Draft Solidity smart contracts for rental escrow.
- **Week 2:** Setup database models and Express API skeleton.
- **Week 3:** Integrate Web3.js libraries into React frontend.
- **Week 4:** Unit test Solidity contracts via Hardhat.

### Team Requirements
- **1 Product Manager**
- **1 Solidity/Smart Contract Dev**
- **1 Full-Stack Web3 Dev**
- **1 QA Engineer**

---

## 12. Launch Checklist

### Pre-Launch (T-4 weeks)
- [ ] Complete smart contract security audits.
- [ ] Onboard third-party insurance agent dashboard.
- [ ] Setup production RPC endpoints and API load-balancers.

### Launch Week
- [ ] Deploy escrow contracts to Mainnet.
- [ ] Verify frontend RPC nodes are live.
- [ ] Push React app to production servers.

### Post-Launch (Weeks 1-4)
- [ ] Monitor gas usage fees and RPC latency.
- [ ] Process owner payout payouts.

---

## Appendix: Open Questions & Decisions Log

| QUESTION | DECISION MADE | RATIONALE | DATE |
|----------|---------------|-----------|------|
| Who pays gas fees for unlock commands? | Renter pays at booking, backend relays lock triggers. | Reduces friction during the physical unlock event. | 2026-06-21 |
| How is vehicle cleaning verified? | Renter must upload check-out photos. | Disincentivizes messy drivers and automates reviews. | 2026-06-23 |"""

        elif theme == "healthcare":
            return f"""## 8. QA & Testing Strategy

### Testing Types
- **Unit Testing:** 90% coverage target on prescription parsers and driver route calculations.
- **Integration Testing:** Verification of prescription status flow from upload to pharmacist screen.
- **End-to-End (E2E) Testing:** Complete order lifecycle test from patient phone to courier driver app.
- **Performance Testing:** Load testing prescription upload speeds under high traffic.
- **User Acceptance Testing (UAT):** Private trial with 2 clinics and 15 patients.

---

## 9. Risk Register & Mitigation Plan

| RISK | CATEGORY | LIKELIHOOD | IMPACT | MITIGATION STRATEGY | OWNER |
|------|----------|------------|--------|---------------------|-------|
| HIPAA Data Leak | Security | Low | Critical | Store PII in fully encrypted DB, log all data access attempts. | Security Lead |
| Medicine Temperature Breach | Operational | Medium | High | Dispatch alert to driver app, cancel order, schedule replacement. | Tech Lead |
| Delayed Delivery of Critical Meds | Operational | Medium | High | Maintain fallback stock at nearby partner hubs. | Logistics Lead |

---

## 10. Project Build Plan & Roadmap

### Phased Roadmap
- **Phase 1: Prescription Flow (Weeks 1-4):** Upload API, HIPAA storage keys, pharmacist approval panel.
- **Phase 2: Driver Portal (Weeks 5-8):** Driver app, location sharing, route dispatch algorithms.
- **Phase 3: Sensors Sync (Weeks 9-12):** IoT temp tags integration, push notifications, signature captures.
- **Phase 4: Launch (Weeks 13-16):** UAT beta trial, regulatory compliance review.

### Week-by-Week Month 1
- **Week 1:** Build secure AWS S3 prescription document storage.
- **Week 2:** Implement user accounts and HIPAA consent signing flow.
- **Week 3:** Build pharmacy dashboard order queue interface.
- **Week 4:** Write unit tests for prescription verification flows.

### Team Requirements
- **1 Product Manager**
- **1 Mobile App Dev (React Native)**
- **1 Backend Dev (Node/HIPAA)**
- **1 QA Engineer**

---

## 12. Launch Checklist

### Pre-Launch (T-4 weeks)
- [ ] Complete external HIPAA security audit.
- [ ] Purchase medical cold-chain temperature tags.
- [ ] Verify pharmacy license databases.

### Launch Week
- [ ] Launch production server environment.
- [ ] Deploy patient and driver apps to App Stores.
- [ ] Conduct live route tests with mock orders.

### Post-Launch (Weeks 1-4)
- [ ] Monitor courier response speeds and temperature drop logs.
- [ ] Verify regulatory compliance reports.

---

## Appendix: Open Questions & Decisions Log

| QUESTION | DECISION MADE | RATIONALE | DATE |
|----------|---------------|-----------|------|
| Can drivers open medicine boxes? | No. Boxes must be tamper-evident sealed. | Protects patient privacy and medicine safety. | 2026-06-21 |
| What happens if a patient is not home? | Medicine must be returned to the hub. | HIPAA/regulations prohibit dropping medicines unattended. | 2026-06-22 |"""

        elif theme == "marketplace":
            return f"""## 8. QA & Testing Strategy

### Testing Types
- **Unit Testing:** 80% coverage on database specs and diagnostic files parses.
- **Integration Testing:** Verification of Stripe payment intents and escrow holds.
- **End-to-End (E2E) Testing:** Complete listing creation, checkout, and shipping tracking flow.
- **Performance Testing:** Load testing high-resolution image uploads.
- **User Acceptance Testing (UAT):** Private trial with 50 college students buying used laptops.

---

## 9. Risk Register & Mitigation Plan

| RISK | CATEGORY | LIKELIHOOD | IMPACT | MITIGATION STRATEGY | OWNER |
|------|----------|------------|--------|---------------------|-------|
| Fraudulent Listings / Counterfeit | Security | Medium | High | Diagnostics logs upload required for premium badges. | Product Manager |
| Payment Chargebacks | Financial | Medium | High | Escrow funds only release after buyer inspection approval. | Finance Lead |
| Shipping Damage Disputes | Operational | High | Medium | Mandatory shipping protection insurance and check-out photos. | Logistics Lead |

---

## 10. Project Build Plan & Roadmap

### Phased Roadmap
- **Phase 1: Listing Wizard (Weeks 1-4):** Database schemas, laptop search engine, condition selection forms.
- **Phase 2: Stripe Escrow (Weeks 5-8):** Payment intents, payout holds, manual dispute tickets.
- **Phase 3: Log Parser (Weeks 9-12):** Uploading files, cpu/battery logs parser, badge display logic.
- **Phase 4: Launch (Weeks 13-16):** UAT beta trial, student marketing launch.

### Week-by-Week Month 1
- **Week 1:** Setup database tables for laptop listings and specifications.
- **Week 2:** Implement user profiles and seller rating database models.
- **Week 3:** Build frontend listing creator forms and upload wizard.
- **Week 4:** Implement basic filters on the laptop search feed.

### Team Requirements
- **1 Product Manager**
- **1 Frontend Dev (Next.js)**
- **1 Backend Dev (Django)**
- **1 QA Engineer**

---

## 12. Launch Checklist

### Pre-Launch (T-4 weeks)
- [ ] Run E2E checkout verification tests.
- [ ] Connect production Stripe gateway account.
- [ ] Set up Zendesk dispute arbitration pipeline.

### Launch Week
- [ ] Launch production server and web client.
- [ ] Monitor checkout funnel metrics.
- [ ] Distribute flyer promo codes to local college campuses.

### Post-Launch (Weeks 1-4)
- [ ] Monitor escrow disputes and processing times.
- [ ] Push UI updates for listing detail reviews.

---

## Appendix: Open Questions & Decisions Log

| QUESTION | DECISION MADE | RATIONALE | DATE |
|----------|---------------|-----------|------|
| How long is the buyer inspection window? | 72 hours from package delivery. | Balances buyer safety with seller cash flow expectations. | 2026-06-20 |
| Can sellers reject returns? | No. Escrow rules mandate returns for spec mismatches. | Protects buyer trust in device quality. | 2026-06-22 |"""

        else:
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
        theme = self._detect_theme(idea, industry)
        short_name = self._get_short_name(idea)
        
        ba_sec = self._get_mock_ba(idea, industry)
        pm_sec = self._get_mock_pm(idea, industry)
        qa_sec = self._get_mock_qa(idea, industry)
        
        return f"""# {short_name}
## Product Requirements Document

**Version:** 1.0 | **Status:** Final | **Industry:** {industry}

---

{ba_sec}

---

{pm_sec}

---

{qa_sec}

---

*PRD Version 1.0 — {idea} | {industry} | Generated by BlueprintAI*"""
