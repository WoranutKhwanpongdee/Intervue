<div align="center">

# 🎙️ Intervue

### Real-Time Adaptive AI Mock Interview Coach & Career Intelligence Platform

[![Next.js](https://img.shields.io/badge/Next.js-15-black?style=flat-square&logo=next.js)](https://nextjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-3178C6?style=flat-square&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Async-4169E1?style=flat-square&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/License-MIT-neutral?style=flat-square)](LICENSE)

<p align="center">
  <b>Intervue</b> is an elite, executive-grade AI mock interview platform that simulates rigorous engineering, behavioral, and architectural rounds. Built with an editorial Apple/Linear monochrome design system, Intervue pairs dynamic adaptive questioning with perceptive blindspot diagnosis.
</p>

</div>

---

## ⚡ Key Highlights & Core Features

### 🎯 1. 5 Distinct Interview Modes
Calibrate your session to match the exact interview format you are preparing for:
- **Technical**: System architecture, concurrency invariants, memory models, distributed data, algorithms, and production debugging.
- **Behavioral (STAR Method)**: Leadership situations, cross-functional conflicts, ownership trade-offs, and critical decision-making.
- **HR Screening**: Career trajectory, motivation alignment, culture fit, and compensation negotiation handling.
- **Mixed**: A balanced cross-section simulating real-world full-loop technical and executive onsite interviews.
- **Job-Specific**: Strictly grounded in the target job description requirements, toolchains, and industry domain.

---

### 📄 2. Resume-Based Interview Grounding
Upload your resume (PDF or TXT) or paste your experience:
- **AI Extraction**: Automatically parses **Skills**, **Key Projects (with Tech Stack & Architecture)**, and **Work History**.
- **Role Ingestion**: Recommends target role and seniority level with a 1-click apply button.
- **Contextual Anchoring**: Questions are explicitly grounded in your actual career achievements with live `Grounded: [Project / Tech Stack]` badges.

---

### 🧠 3. Real-Time Adaptive Engine with Full Memory
Unlike generic chatbots with static question lists, Intervue remembers your past responses throughout the interview:
- **Cross-Question Continuity**: Weaves technologies and decisions you brought up in previous turns into subsequent questions.
- **Performance-Based Dynamic Difficulty**:
  - **High Performance (>80%)**: Escalates into high-scale concurrency, distributed race conditions, and failover scenarios.
  - **Identified Gaps (<60%)**: Calibrates to adjacent practical fundamentals without repeating failed questions.
- **Targeted Follow-up Probes**: Automatically triggers deep-dive questions when a response leaves an important trade-off or ambiguity.

---

### ⚠️ 4. Hidden Weakness & Coaching Blindspot Detection
A true interview coach doesn't just check if an answer is technically correct—it uncovers **invisible communication and cognitive habits**:
- ⚠️ **"What vs Why" Bias**: *Explaining what a technology does rather than justifying why you chose it over alternatives.*
- ⚠️ **Concept Without Concrete Evidence**: *Knowing theoretical concepts well, but omitting production numbers, throughput metrics, or architecture war stories.*
- ⚠️ **Follow-up Degradation**: *Sounding confident initially, but becoming vague or evasive when drilled on deep edge cases.*
- ⚠️ **Happy-Path Assumption**: *Assuming dependencies never fail and neglecting retries, timeouts, and graceful degradation.*
- ⚠️ **Over-Engineering Bias**: *Recommending massive distributed clusters for simple monolithic workloads.*

> Every detected blindspot includes **Observed Evidence** from your transcript and an actionable **Pro Coaching Tip** to eliminate the habit in real interviews.

---

### 📊 5. Multi-Dimensional Evaluation Rubric
Answers are rigorously scored across four weighted dimensions:
- **Technical Accuracy (40%)**: Domain depth, architectural correctness, and edge case coverage.
- **Direct Relevance (25%)**: Concise focus on what the interviewer asked without drifting.
- **Depth & Completeness (20%)**: Proactive consideration of scalability, failure modes, and trade-offs.
- **Clarity & Structure (15%)**: Clear communication, structured thinking, and conviction.
- **Model Reference Answers**: Provides senior-level model answers for every single question.

---

### 🔌 6. Pluggable Multi-LLM Provider Architecture
Seamlessly switch between AI engines via `.env`:
- **Google Gemini** (`gemini-1.5-flash`, `gemini-2.0-flash` or Pro)
- **Groq** (`llama-3.3-70b-versatile` — ultra-fast sub-second generation)
- **Ollama** (Local offline LLMs: `llama3.2`, `mistral`, `deepseek-r1`)
- **Deterministic Mock Provider** (Zero API keys required — full offline simulator)

---

## 🏛️ Architecture & Project Structure

```
Intervue/
├── backend/                  # FastAPI (Python 3.10+)
│   ├── app/
│   │   ├── config.py         # Pydantic Settings & environment variables
│   │   ├── main.py           # FastAPI lifecycle, middleware & CORS
│   │   ├── db/
│   │   │   ├── models.py     # SQLAlchemy models (Session, Turns, Scores, Blindspots)
│   │   │   └── session.py    # Async SQLAlchemy (PostgreSQL with SQLite fallback)
│   │   ├── schemas/
│   │   │   ├── interview.py  # Request & response Pydantic DTOs
│   │   │   └── llm.py        # Structured schemas for AI questions, evaluations & reports
│   │   ├── services/
│   │   │   ├── interview_engine.py  # Real-time adaptive orchestrator & state machine
│   │   │   ├── resume_parser.py     # PDF & text resume ingestion
│   │   │   └── llm/                 # Pluggable AI provider abstraction
│   │   │       ├── base.py          # Abstract LLM provider interface
│   │   │       ├── factory.py       # Provider auto-discovery & selection
│   │   │       ├── gemini.py        # Google Gemini integration
│   │   │       ├── groq.py          # Groq Cloud integration
│   │   │       ├── ollama.py        # Local Ollama client
│   │   │       └── mock.py          # Offline heuristic simulation
│   │   └── routers/
│   │       ├── interviews.py        # /api/interviews CRUD & turn answering
│   │       ├── resume.py            # /api/resume/parse & text analysis
│   │       └── health.py            # /api/health
│   ├── requirements.txt
│   └── run.py
│
└── frontend/                 # Next.js 15 (App Router, Tailwind CSS, TypeScript)
    ├── src/
    │   ├── app/
    │   │   ├── page.tsx             # Executive minimal landing page
    │   │   ├── setup/page.tsx       # Calibration wizard & resume intelligence card
    │   │   ├── interview/[id]/      # Real-time interview room with adaptive tags
    │   │   ├── report/[id]/         # Scorecard, blindspot diagnosis & transcript
    │   │   └── history/page.tsx     # Session history & score records
    │   ├── components/ui/           # Minimalist design tokens (Button, Badge, MetricCard)
    │   ├── lib/api.ts               # Typed frontend API client
    │   └── types/interview.ts       # Shared TypeScript domain types
```

---

## 🚀 Quickstart Guide

### 1. Clone & Configure Environment

```bash
git clone https://github.com/WoranutKhwanpongdee/Intervue.git
cd Intervue
```

Create `.env` in the root directory (or in `backend/`):

```env
# Database (Defaults to PostgreSQL with auto-fallback to SQLite)
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

> **💡 Zero-Config Offline Mode**: If no API keys are provided, Intervue automatically defaults to the **Mock Provider** so you can test the entire workflow, adaptive turns, and scorecards immediately with zero configuration!

---

### 2. Run Backend (FastAPI)

```bash
cd backend

# Create & activate virtual environment
# On Windows (PowerShell):
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# On macOS / Linux:
# python3 -m venv .venv
# source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the server
python run.py
```

Backend will start at **`http://localhost:8000`**.  
Interactive Swagger API docs available at **`http://localhost:8000/docs`**.

---

### 3. Run Frontend (Next.js)

In a new terminal window:

```bash
cd frontend

# Install dependencies
npm install

# Start Next.js development server
npm run dev
```

Open **`http://localhost:3000`** in your browser.

---

## 📡 REST API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Health check & active LLM provider status |
| `POST` | `/api/interviews` | Initialize an interview session & generate Q1 |
| `GET` | `/api/interviews` | List all previous interview sessions |
| `GET` | `/api/interviews/{id}` | Get full interview session, turns & scorecard |
| `POST` | `/api/interviews/{id}/turns/{turn_id}/answer` | Submit turn response, evaluate & adapt next turn |
| `POST` | `/api/interviews/{id}/finish` | Conclude session early & compile final report |
| `DELETE` | `/api/interviews/{id}` | Delete interview session record |
| `POST` | `/api/resume/parse` | Parse PDF / TXT file and extract structured intelligence |
| `POST` | `/api/resume/analyze-text` | Extract skills, projects & roles from raw resume text |

---

## 🎨 Design Philosophy

- **Editorial Precision**: Clean, distraction-free monochrome typography inspired by Apple & Linear interfaces.
- **Zero AI Slop**: No fake rainbow gradients, glowing blobs, or gratuitous badge clutter.
- **High Utility**: Real keyboard shortcuts (`⌘/Ctrl + Enter`), responsive layout, and instant printable PDF scorecards.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
