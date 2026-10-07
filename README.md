<div align="center">

```
  ___       _                               
 |_ _|_ __ | |_ ___ _ ____   ___   _  ___   
  | || '_ \| __/ _ \ '__\ \ / / | | |/ _ \  
  | || | | | ||  __/ |   \ V /| |_| |  __/  
 |___|_| |_|\__\___|_|    \_/  \__,_|\___|  
```

### Executive AI Mock Interview Coach & Adaptive Engineering Assessor

*Rigorous simulation. Real-time cognitive adaptation. Deep blindspot diagnosis.*

<br/>

[![Next.js](https://img.shields.io/badge/Next.js_15-000000?style=for-the-badge&logo=nextdotjs&logoColor=white)](https://nextjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript_5.0-3178C6?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python_3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white)](https://tailwindcss.com/)

<br/>

[Key Highlights](#-key-capabilities) • [System Workflow](#-interview-workflow) • [Hidden Weakness Engine](#-hidden-weakness-detection-engine) • [Quickstart](#-quickstart-guide) • [Architecture](#-architecture) • [API Docs](#-rest-api-reference)

</div>

---

## ⚡ Overview

**Intervue** is a professional-grade mock interview intelligence platform designed for senior software engineers, tech leads, and engineering leaders. 

Unlike generic chatbots that regurgitate static lists of LeetCode questions, Intervue orchestrates an **adaptive state machine**: it maintains complete multi-turn memory, dynamically probes your architectural decisions, challenges edge cases when you perform well, and diagnoses latent communication blindspots that traditional interview tools miss.

```mermaid
flowchart LR
    A[📄 Resume / Role Setup] --> B[🧠 AI Ingestion & Grounding]
    B --> C[🎙️ Adaptive Interview Room]
    C -->|Real-time Turn Memory| D{Score & Depth Analysis}
    D -->|>80% Depth| E[⚡ Escalate to Concurrency & Scale]
    D -->|Ambiguity Found| F[🔍 Inject Deep-Dive Probe]
    D -->|<60% Score| G[🎯 Calibrate Practical Fundamentals]
    E & F & G --> C
    C -->|Session Completed| H[📊 Scorecard & Hidden Weaknesses]
```

---

## 💎 Key Capabilities

### 🎯 1. 5 Calibrated Interview Tracks
| Mode | Target Scope | Focus Areas |
|---|---|---|
| **Technical** | Systems & Architecture | Invariants, concurrency, memory models, distributed data, profiling, algorithms |
| **Behavioral** | Leadership & STAR | Team conflict, critical ownership trade-offs, stakeholder alignment, failure lessons |
| **HR Screening** | Culture & Trajectory | Motivations, career growth arcs, compensation discussion framing, work philosophy |
| **Mixed** | Full-Loop Simulation | Comprehensive cross-section of technical rigor, design trade-offs, and soft skills |
| **Job-Specific** | Grounded Tailoring | Strictly aligns with target job description requirements, tools, and domain constraints |

---

### 📄 2. Resume-Grounded Question Generation
Upload your real resume (**PDF / TXT**) or paste your work history:
- **Automatic Extraction**: Parses **Skills**, **Production Projects** (with tech stack & architecture), and **Role Timelines**.
- **1-Click Role Calibration**: Automatically recommends appropriate seniority (`Senior`, `Lead`, `Principal`) and title.
- **Contextual Anchoring**: Every question cites your real accomplishments with explicit visual grounding badges (e.g. `📌 Grounded in: Payment Gateway / Node.js & Redis`).

---

### 🧠 3. Real-Time Adaptive Engine
```
Turn 1: Candidate mentions using Kafka with partition keys for ordering.
           ↓ (AI remembers and tracks this architectural claim)
Turn 2: "In your previous response you discussed Kafka partition keys. How does your consumer group 
         handle rebalancing when a rebalance storm occurs during heavy consumer deployment?"
```
- **Performance-Driven Scaling**:
  - **High Performance (>80%)**: The engine dynamically escalates to distributed race conditions, cache stampedes, and failover edge cases.
  - **Foundational Gaps (<60%)**: Calibrates to practical fundamentals without condescension or repeating failed prompts.
- **Follow-up Probe Injection**: Automatically triggers targeted deep dives when candidate answers leave important ambiguities.

---

### ⚠️ 4. Hidden Weakness Detection Engine

> *"A great coach doesn't just grade right vs. wrong—they diagnose what you cannot see about yourself."*

Intervue evaluates subtle cognitive habits and delivery patterns across multiple turns:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│  ⚠️ HIDDEN BLINDSPOT DIAGNOSIS                                                         │
│                                                                                        │
│  [What vs Why Bias]                                                                    │
│  "You tend to describe what a technology does rather than explaining why you chose it."│
│                                                                                        │
│  • Evidence: In Q2, you detailed Redis cache operations without comparing memory       │
│    overhead against in-memory LRU or justifying the extra network hop.                 │
│                                                                                        │
│  💡 Pro Coaching Tip: Follow the 'Why-First' rule: always name the 1-2 alternatives    │
│    you rejected and the constraint that made your choice the winner.                   │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

<details>
<summary><b>🔍 View All 5 Diagnosed Blindspot Archetypes</b></summary>
<br/>

1. **"What vs Why" Bias**: Describing API features and mechanics instead of defending architectural trade-offs against alternatives.
2. **Concept Without Concrete Evidence**: Understanding textbook theory (CAP, ACID, Microservices) but omitting production numbers, throughput metrics, and war stories.
3. **Follow-up Degradation**: Starting strong on high-level architecture, but becoming evasive or hand-wavy when probed on concrete failure protocols.
4. **Happy-Path Assumption**: Assuming dependencies, networks, and disks never fail; forgetting timeouts, circuit breakers, and degradation modes.
5. **Over-Engineering Bias**: Recommending heavy distributed clusters (Kafka + Kubernetes) for straightforward low-throughput use cases.

</details>

---

### 📊 5. Multi-Dimensional Scoring Rubric

Each turn is scored on a senior engineering rubric:

$$\text{Turn Score} = (0.40 \times \text{Technical}) + (0.25 \times \text{Relevance}) + (0.20 \times \text{Depth}) + (0.15 \times \text{Clarity})$$

- **Technical Accuracy (40%)**: Invariant correctness, domain mastery, and edge-case handling.
- **Direct Relevance (25%)**: Concise precision without drifting off-topic.
- **Depth & Completeness (20%)**: Proactive coverage of telemetry, failure recovery, and trade-offs.
- **Clarity & Structure (15%)**: Executive presence, crisp communication, and strong structure.
- **Senior Model Answers**: Model answers provided for every single question to accelerate practice.

---

## 🔌 Pluggable AI Provider Abstraction

Switch AI providers instantly in `.env` without modifying a single line of application code:

```
                  ┌───────────────┐
                  │ Base Provider │
                  └───────┬───────┘
          ┌───────────────┼───────────────┬───────────────┐
          ▼               ▼               ▼               ▼
    Google Gemini       Groq        Local Ollama    Offline Mock
   (1.5 / 2.0 Flash) (Llama 3.3 70B) (Llama 3.2 / R1)  (Zero Config)
```

| Provider | Best For | Typical Latency | API Key Required? |
|---|---|---|---|
| **Google Gemini** | Complex reasoning & deep evaluation | ~1.2s | Yes (Free Tier available) |
| **Groq Cloud** | Ultra-fast interactive turns | ~0.4s | Yes |
| **Ollama** | 100% private, local air-gapped simulation | Local GPU dependent | No |
| **Mock Provider** | Instant local offline development & testing | <50ms | **No API Key Needed** |

---

## 🏛️ Architecture & Clean Codebase

```
intervue/
├── backend/                         # FastAPI (Python 3.10+)
│   ├── app/
│   │   ├── config.py                # Pydantic Settings & environment config
│   │   ├── main.py                  # Lifespan, CORS, and router registration
│   │   ├── db/
│   │   │   ├── models.py            # SQLAlchemy models (Sessions, Turns, Blindspots)
│   │   │   └── session.py           # Async engine (PostgreSQL with SQLite fallback)
│   │   ├── schemas/
│   │   │   ├── interview.py         # Request/Response Pydantic DTOs
│   │   │   └── llm.py               # Structured output contracts for AI
│   │   ├── services/
│   │   │   ├── interview_engine.py # Multi-turn adaptive state machine
│   │   │   ├── resume_parser.py    # PDF & raw text parser
│   │   │   └── llm/                 # Provider implementations
│   │   │       ├── base.py          # Abstract provider interface & prompts
│   │   │       ├── factory.py       # Auto-discovery provider factory
│   │   │       ├── gemini.py        # Gemini client
│   │   │       ├── groq.py          # Groq client
│   │   │       ├── ollama.py        # Ollama client
│   │   │       └── mock.py          # Deterministic offline engine
│   │   └── routers/
│   │       ├── interviews.py        # /api/interviews CRUD & turn execution
│   │       ├── resume.py            # /api/resume/parse & text analysis
│   │       └── health.py            # /api/health
│   ├── requirements.txt
│   └── run.py
│
└── frontend/                        # Next.js 15 (App Router, Tailwind CSS)
    ├── src/
    │   ├── app/
    │   │   ├── page.tsx             # Editorial landing page
    │   │   ├── setup/page.tsx       # Calibration wizard & resume intelligence card
    │   │   ├── interview/[id]/      # Real-time interview room & adaptive tags
    │   │   ├── report/[id]/         # Scorecard, blindspots & printable report
    │   │   └── history/page.tsx     # Session history & score archive
    │   ├── components/ui/           # Minimalist design tokens (Button, MetricCard, Badge)
    │   ├── lib/api.ts               # Typed frontend client
    │   └── types/interview.ts       # Shared domain TypeScript types
```

---

## 🚀 Quickstart Guide

### 1. Clone & Set Environment

```bash
git clone https://github.com/WoranutKhwanpongdee/Intervue.git
cd Intervue
```

Create a `.env` file in the root directory:

```env
# Database (Auto-fallback to local SQLite if PostgreSQL is offline)
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/intervue_db
SQLITE_FALLBACK_URL=sqlite+aiosqlite:///./intervue.db

# LLM Provider: "auto", "gemini", "groq", "ollama", or "mock"
LLM_PROVIDER=auto

# Google Gemini (Recommended)
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-1.5-flash

# Groq (Optional)
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile

# Ollama (Optional Local AI)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2

# Frontend Endpoint
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

> **💡 Zero-Setup Offline Mode**: If no API keys are configured, Intervue automatically starts in **Mock Provider** mode so you can test every screen, resume extraction, adaptive turns, and scorecards immediately!

---

### 2. Launch Backend (FastAPI)

```bash
cd backend

# Create & activate virtual environment (Windows PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# (On macOS / Linux)
# python3 -m venv .venv && source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run server
python run.py
```
- API starts at: `http://localhost:8000`
- Interactive Swagger docs: `http://localhost:8000/docs`

---

### 3. Launch Frontend (Next.js)

In a separate terminal:

```bash
cd frontend
npm install
npm run dev
```
- Web Application starts at: `http://localhost:3000`

---

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|---|---|
| `⌘ + Enter` / `Ctrl + Enter` | Submit current turn response for instant AI evaluation |
| `Print / Save PDF` | One-click export of executive interview evaluation scorecard |

---

## 📡 REST API Reference

```
POST   /api/interviews                  # Initialize interview session & generate Q1
GET    /api/interviews                  # List past interview sessions with scores
GET    /api/interviews/{id}             # Get session details, turns, metrics & blindspots
POST   /api/interviews/{id}/turns/{t}/answer # Submit response & adapt next question
POST   /api/interviews/{id}/finish      # Conclude session early & compile final report
DELETE /api/interviews/{id}             # Delete interview record
POST   /api/resume/parse                # Parse resume PDF/TXT file
POST   /api/resume/analyze-text         # Extract skills & projects from raw text
GET    /api/health                      # Health check & active LLM provider status
```

---

## 🎨 Design Philosophy

- **Apple / Linear Aesthetic**: Monochrome typography, crisp border contrasts, and restrained layout.
- **Zero AI Slop**: Free of fake rainbow gradients, glowing blobs, and superfluous decorative noise.
- **High Utility**: Built for focused practice, actionable feedback, and immediate preparation ROI.

---

<div align="center">

Made with engineering discipline by **Woranut Khwanpongdee**  
Licensed under the [MIT License](LICENSE)

</div>
