<div align="center">

# Intervue

**Adaptive AI Mock Interview Coach & Career Intelligence Platform**

*Rigorous engineering simulations · Real-time cognitive adaptation · Latent blindspot diagnosis*

<br />

[![Next.js](https://img.shields.io/badge/Next.js-15-black?style=flat&logo=next.js)](https://nextjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-3178C6?style=flat&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Async-4169E1?style=flat&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-neutral?style=flat)](LICENSE)

<table align="center">
  <tr>
    <td align="center"><a href="#overview"><b>&nbsp;Overview&nbsp;</b></a></td>
    <td align="center"><a href="#interview-workflow"><b>&nbsp;Workflow&nbsp;</b></a></td>
    <td align="center"><a href="#core-features"><b>&nbsp;Core Features&nbsp;</b></a></td>
    <td align="center"><a href="#hidden-weakness-engine"><b>&nbsp;Hidden Weaknesses&nbsp;</b></a></td>
    <td align="center"><a href="#quickstart"><b>&nbsp;Quickstart&nbsp;</b></a></td>
    <td align="center"><a href="#architecture"><b>&nbsp;Architecture&nbsp;</b></a></td>
    <td align="center"><a href="#api-reference"><b>&nbsp;API Docs&nbsp;</b></a></td>
  </tr>
</table>

</div>

---

## Overview

**Intervue** is an executive-grade AI mock interview coach engineered for senior software engineers, tech leads, and engineering leaders.

Unlike generic chatbots that follow static question lists, Intervue operates as an **adaptive state machine**: it maintains complete multi-turn memory, dynamically probes your architectural decisions, challenges edge cases when you perform well, and diagnoses latent communication blindspots that traditional interview tools miss.

---

## Interview Workflow

```mermaid
flowchart LR
    A[Resume / Role Setup] --> B[AI Ingestion & Grounding]
    B --> C[Adaptive Interview Room]
    C -->|Real-time Turn Memory| D{Score & Depth Analysis}
    D -->|>80% Depth| E[Escalate to Concurrency & Scale]
    D -->|Ambiguity Found| F[Inject Deep-Dive Follow-up]
    D -->|<60% Score| G[Calibrate Practical Fundamentals]
    E & F & G --> C
    C -->|Session Completed| H[Scorecard & Hidden Weaknesses]
```

---

## Core Features

### 1. Five Calibrated Interview Tracks
| Track | Target Scope | Focus Areas |
|---|---|---|
| **Technical** | Systems & Architecture | Invariants, concurrency, memory models, distributed data, profiling, algorithms |
| **Behavioral** | Leadership & STAR | Team conflict, critical ownership trade-offs, stakeholder alignment, failure lessons |
| **HR Screening** | Culture & Trajectory | Motivations, career growth arcs, compensation discussion framing, work philosophy |
| **Mixed** | Full-Loop Simulation | Comprehensive cross-section of technical rigor, design trade-offs, and soft skills |
| **Job-Specific** | Grounded Tailoring | Strictly aligns with target job description requirements, tools, and domain constraints |

### 2. Resume-Grounded Question Generation
Upload your real resume (**PDF / TXT**) or paste your work history:
- **Automatic Extraction**: Parses **Skills**, **Production Projects** (with tech stack & architecture), and **Role Timelines**.
- **1-Click Role Calibration**: Automatically recommends appropriate seniority (`Senior`, `Lead`, `Principal`) and title.
- **Contextual Anchoring**: Every question cites your real accomplishments with explicit visual grounding badges (e.g. `Grounded in: Payment Gateway / Node.js & Redis`).

### 3. Real-Time Adaptive Engine
- **Cross-Question Continuity**: Weaves technologies and decisions you brought up in previous turns into subsequent questions.
- **Performance-Driven Scaling**:
  - **High Performance (>80%)**: The engine dynamically escalates to distributed race conditions, cache stampedes, and failover edge cases.
  - **Foundational Gaps (<60%)**: Calibrates to practical fundamentals without condescension or repeating failed prompts.
- **Follow-up Probe Injection**: Automatically triggers targeted deep dives when candidate answers leave important ambiguities.

---

## Hidden Weakness Engine

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
<summary><b>View All 5 Diagnosed Blindspot Archetypes</b></summary>
<br />

1. **"What vs Why" Bias**: Describing API features and mechanics instead of defending architectural trade-offs against alternatives.
2. **Concept Without Concrete Evidence**: Understanding textbook theory (CAP, ACID, Microservices) but omitting production numbers, throughput metrics, and war stories.
3. **Follow-up Degradation**: Starting strong on high-level architecture, but becoming evasive or hand-wavy when probed on concrete failure protocols.
4. **Happy-Path Assumption**: Assuming dependencies, networks, and disks never fail; forgetting timeouts, circuit breakers, and degradation modes.
5. **Over-Engineering Bias**: Recommending heavy distributed clusters (Kafka + Kubernetes) for straightforward low-throughput use cases.

</details>

---

## Evaluation Rubric

Each turn is scored on a senior engineering rubric:

$$\text{Turn Score} = (0.40 \times \text{Technical}) + (0.25 \times \text{Relevance}) + (0.20 \times \text{Depth}) + (0.15 \times \text{Clarity})$$

- **Technical Accuracy (40%)**: Invariant correctness, domain mastery, and edge-case handling.
- **Direct Relevance (25%)**: Concise precision without drifting off-topic.
- **Depth & Completeness (20%)**: Proactive coverage of telemetry, failure recovery, and trade-offs.
- **Clarity & Structure (15%)**: Executive presence, crisp communication, and strong structure.
- **Senior Model Answers**: Model answers provided for every single question to accelerate practice.

---

## AI Provider Support

Switch AI providers instantly in `.env` without modifying application code:

| Provider | Best For | Typical Latency | API Key Required? |
|---|---|---|---|
| **Google Gemini** | Complex reasoning & deep evaluation | ~1.2s | Yes (Free tier available) |
| **Groq Cloud** | Ultra-fast interactive turns | ~0.4s | Yes |
| **Ollama** | 100% private, local air-gapped simulation | Local GPU dependent | No |
| **Mock Provider** | Instant local offline development & testing | <50ms | **No API Key Needed** |

---

## Architecture

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
│   │   │   ├── interview_engine.py  # Multi-turn adaptive state machine
│   │   │   ├── resume_parser.py     # PDF & raw text parser
│   │   │   └── llm/                 # Provider implementations (Gemini, Groq, Ollama, Mock)
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

## Quickstart

### 1. Clone & Set Environment

```bash
git clone https://github.com/WoranutKhwanpongdee/Intervue.git
cd Intervue
```

Create `.env` in the root directory:

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

> **Zero-Setup Offline Mode**: If no API keys are configured, Intervue automatically starts in **Mock Provider** mode so you can test every screen, resume extraction, adaptive turns, and scorecards immediately with zero external dependencies.

### 2. Launch Backend (FastAPI)

```bash
cd backend

# On Windows (PowerShell):
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# On macOS / Linux:
# python3 -m venv .venv && source .venv/bin/activate

pip install -r requirements.txt
python run.py
```
- API Server: `http://localhost:8000`
- Interactive Swagger Docs: `http://localhost:8000/docs`

### 3. Launch Frontend (Next.js)

In a separate terminal:

```bash
cd frontend
npm install
npm run dev
```
- Web Application: `http://localhost:3000`

---

## Keyboard Shortcuts

| Shortcut | Action |
|---|---|
| `⌘ + Enter` / `Ctrl + Enter` | Submit current turn response for instant AI evaluation |
| `Print / Save PDF` | One-click export of executive interview evaluation scorecard |

---

## API Reference

```
POST   /api/interviews                       # Initialize interview session & generate Q1
GET    /api/interviews                       # List past interview sessions with scores
GET    /api/interviews/{id}                  # Get session details, turns, metrics & blindspots
POST   /api/interviews/{id}/turns/{t}/answer # Submit response & adapt next question
POST   /api/interviews/{id}/finish           # Conclude session early & compile final report
DELETE /api/interviews/{id}                  # Delete interview record
POST   /api/resume/parse                     # Parse resume PDF/TXT file
POST   /api/resume/analyze-text              # Extract skills & projects from raw text
GET    /api/health                           # Health check & active LLM provider status
```

---

## License

This project is licensed under the [MIT License](LICENSE).
