# Intervue — Adaptive AI Mock Interview Coach

**Intervue** is an AI-powered mock interview coach built with **Next.js**, **FastAPI**, and **PostgreSQL**. Unlike generic chatbots, Intervue uses an adaptive interview engine that dynamically probes your architectural reasoning, evaluates answers using a structured multi-dimensional rubric, and generates detailed performance debriefs.

---

## Key Highlights

- **Adaptive Questioning**: Probes trade-offs, scalability, and edge cases based on your actual responses rather than following a static list.
- **Multi-Dimensional Scoring**: Evaluates answers across four dimensions:
  - Technical Accuracy (40%)
  - Direct Relevance (25%)
  - Depth & Completeness (20%)
  - Communication Clarity (15%)
- **Model Answer Generation**: Provides senior-level sample answers and targeted study recommendations for every question.
- **Provider Abstraction**: First-class support for **Google Gemini**, **Groq**, **Ollama**, and a deterministic **Mock Provider** for offline/zero-API-key testing.
- **Resume Grounding**: Upload a PDF or plain-text resume to generate questions tailored to your tech stack and experience.
- **Minimal, Modern Design**: Clean editorial interface designed with Tailwind CSS and Lucide icons—free of generic AI gradients or distracting glows.

---

## Architecture & Tech Stack

```
intervue/
├── backend/                  # FastAPI Python backend
│   ├── app/
│   │   ├── config.py         # Pydantic Settings & environment config
│   │   ├── main.py           # FastAPI entrypoint, CORS, lifespan
│   │   ├── db/
│   │   │   ├── models.py     # SQLAlchemy models (Session, Turns, Scores)
│   │   │   └── session.py    # Async SQLAlchemy (PostgreSQL + SQLite fallback)
│   │   ├── schemas/
│   │   │   ├── interview.py  # Request/response DTOs
│   │   │   └── llm.py        # Structured Pydantic models for AI output
│   │   ├── services/
│   │   │   ├── interview_engine.py  # Adaptive interview state orchestration
│   │   │   ├── resume_parser.py     # PDF & text parser
│   │   │   └── llm/                 # Provider abstraction
│   │   │       ├── base.py          # Abstract LLM provider interface
│   │   │       ├── factory.py       # Auto-selection & fallback factory
│   │   │       ├── gemini.py        # Google Gemini provider
│   │   │       ├── groq.py          # Groq provider (Llama 3.3)
│   │   │       ├── ollama.py        # Local Ollama provider
│   │   │       └── mock.py          # Deterministic test simulation
│   │   └── routers/
│   │       ├── interviews.py # /api/interviews endpoints
│   │       ├── resume.py     # /api/resume/parse
│   │       └── health.py     # /api/health
│   ├── requirements.txt
│   └── run.py
└── frontend/                 # Next.js 15+ App Router
    ├── src/
    │   ├── app/
    │   │   ├── page.tsx            # Executive landing page
    │   │   ├── setup/page.tsx      # Calibration wizard & resume upload
    │   │   ├── interview/[id]/     # AI interview room & adaptive turns
    │   │   ├── report/[id]/        # Final performance report & transcript
    │   │   └── history/page.tsx    # Past sessions & scores
    │   ├── components/             # Reusable UI components
    │   ├── lib/api.ts              # Typed API client
    │   └── types/interview.ts      # Shared TypeScript types
```

---

## Getting Started

### 1. Prerequisites

- **Node.js** v18+ and **npm**
- **Python** 3.10+
- *(Optional)* **PostgreSQL** (if not installed, the app automatically falls back to local SQLite with zero setup)

### 2. Environment Variables

Copy `.env.example` in both root or backend:

```bash
# In the project root
cp .env.example .env
```

Example `.env`:

```env
# Database (defaults to PostgreSQL with auto-fallback to SQLite)
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/intervue_db
SQLITE_FALLBACK_URL=sqlite+aiosqlite:///./intervue.db

# LLM Provider: "auto", "gemini", "groq", "ollama", or "mock"
LLM_PROVIDER=auto

# Google Gemini (Recommended)
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-1.5-flash

# Groq (Ultra-fast inference)
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile

# Ollama (Local LLM)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2

# Frontend Client
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

> **Note**: If you don't provide an API key, the system automatically uses the built-in **Mock Provider**, allowing you to test questions, adaptive turns, scoring, and reports immediately without any external dependency.

---

### 3. Backend Setup

```bash
# Navigate to backend
cd backend

# Create & activate virtual environment (Windows PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# (Or on macOS/Linux)
# source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the API server
python run.py
```

The backend starts at `http://localhost:8000`. You can inspect the Swagger documentation at `http://localhost:8000/docs`.

---

### 4. Frontend Setup

In a separate terminal:

```bash
# Navigate to frontend
cd frontend

# Install packages
npm install

# Start development server
npm run dev
```

Open `http://localhost:3000` in your browser.

---

## Usage Walkthrough

1. **Overview & Calibration**: Go to `http://localhost:3000/setup`.
2. **Select Parameters**:
   - Job Position: e.g. *Senior Frontend Engineer* or *Backend Distributed Systems*
   - Seniority: *Junior*, *Mid*, *Senior*, *Lead*, or *Principal*
   - Track: *Technical Deep-Dive*, *System Design*, *Behavioral (STAR)*, or *Leadership*
   - Rigor: *Foundational*, *Standard Bar*, or *Principal Bar*
   - Number of Questions: 3, 5, 7, or 10
   - *(Optional)* Upload a PDF or paste plain-text resume to ground the questions in your background.
3. **Conduct Interview**:
   - Answer technical prompts via text.
   - Use `Ctrl + Enter` to submit.
   - If an answer leaves an ambiguity or highlights a trade-off, the AI dynamically injects a follow-up probe.
4. **View Final Report**:
   - Review overall score and readiness badge (*Strong Hire*, *Interview Ready*, etc.).
   - Inspect breakdown across Technical Accuracy, Relevance, Communication, and Depth.
   - Review question-by-question model answers and targeted study recommendations.
5. **Session History**:
   - Revisit all previous scores, transcripts, and evaluations anytime at `/history`.

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Health check & active LLM provider info |
| `POST` | `/api/interviews` | Create interview session & first question |
| `GET` | `/api/interviews` | List historical sessions & summaries |
| `GET` | `/api/interviews/{id}` | Get session details, questions & evaluations |
| `POST` | `/api/interviews/{id}/turns/{turn_id}/answer` | Submit answer & trigger adaptive evaluation |
| `POST` | `/api/interviews/{id}/finish` | Conclude session early & compile final report |
| `DELETE` | `/api/interviews/{id}` | Delete interview session record |
| `POST` | `/api/resume/parse` | Parse PDF / text resume upload |

---

## License

MIT
