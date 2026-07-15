# KSP Crime Intelligence Platform

> **Enterprise-grade AI-powered Crime Intelligence & Analytics Platform** built for the **Karnataka State Police (KSP)**. Transforms fragmented manual record-keeping into a proactive, data-driven policing and intelligent suspect profiling system.

[![CI/CD](https://github.com/bhawuk-arora/KSP-ConversationalAI/actions/workflows/ci.yml/badge.svg)](https://github.com/bhawuk-arora/KSP-ConversationalAI/actions/workflows/ci.yml)

---

## 🚀 Quick Start (Local Dev)

### Prerequisites
- Python 3.11+
- Node.js 20+
- Docker & Docker Compose

### 1. Clone & Set Up Environment
```bash
git clone https://github.com/bhawuk-arora/KSP-ConversationalAI.git
cd KSP-ConversationalAI
cp .env.example .env   # fill in your values
```

### 2. Start Data Services (Docker)
```bash
docker compose up postgres neo4j qdrant redis -d
```

### 3. Run the Backend
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Run the Frontend
```bash
cd frontend
npm install
npm run dev
# → http://localhost:3000
```

### 5. Full Stack via Docker Compose
```bash
docker compose up --build
# Backend → http://localhost:8000
# Frontend → http://localhost:3000
```

---

## 🔑 Demo Logins

| Role | Email | Password |
|------|-------|----------|
| DGP (Full Access) | `dgp@ksp.gov.in` | `password123` |
| Investigating Officer | `io@ksp.gov.in` | `password123` |
| Constable (Limited) | `constable@ksp.gov.in` | `password123` |
| Crime Analyst | `analyst@ksp.gov.in` | `password123` |

---

## 🧩 Platform Features

| Module | Status |
|--------|--------|
| ✅ JWT Authentication & RBAC | Complete |
| ✅ Case Search & Detail APIs | Complete |
| ✅ Accused / Suspect Profiling | Complete |
| ✅ AI Conversational Copilot (SSE streaming) | Complete |
| ✅ Suspect Network Graph (Neo4j) | Complete |
| ✅ GIS Crime Hotspot Map (Leaflet) | Complete |
| ✅ PDF Intelligence Reports (ReportLab) | Complete |
| ✅ Scenario Simulation Engine | Complete |
| ✅ Demo Mode PII Masking | Complete |
| ✅ Docker Compose (Full Stack) | Complete |
| ✅ GitHub Actions CI/CD | Complete |

---

## 📡 API Reference

Interactive docs available at `http://localhost:8000/docs`

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/auth/token` | JWT login |
| `POST` | `/api/v1/chat/message` | AI Copilot (SSE stream) |
| `GET`  | `/api/v1/cases/search` | Search cases |
| `GET`  | `/api/v1/cases/{id}` | Case detail |
| `GET`  | `/api/v1/cases/{id}/timeline` | Case timeline |
| `GET`  | `/api/v1/cases/{id}/similar` | Similar case finder |
| `GET`  | `/api/v1/accused/search` | Suspect search |
| `GET`  | `/api/v1/accused/{id}/history` | Offender history |
| `GET`  | `/api/v1/network/suspect/{id}` | Co-offender graph |
| `GET`  | `/api/v1/gis/hotspots` | Crime hotspot coords |
| `POST` | `/api/v1/reports/pdf` | Generate PDF report |
| `POST` | `/api/v1/simulation/simulate` | Scenario simulation |
| `GET`  | `/api/health` | Health check |

---

## 📂 Project Structure

```text
KSP-ConversationalAI/
├── .github/workflows/ci.yml   # GitHub Actions CI/CD
├── docs/                      # Architecture, PRD, API specs (10 docs)
├── backend/                   # FastAPI — 8 endpoints, JWT, RBAC, PDF
│   ├── app/api/api_v1/endpoints/
│   ├── app/models/
│   ├── app/schemas/
│   └── Dockerfile
├── frontend/                  # Next.js 16, TypeScript, Glassmorphism UI
│   ├── src/app/page.tsx       # Main SPA with 5 tabs
│   ├── src/components/        # 7 components incl. Chat, Network, GIS
│   └── Dockerfile
├── docker-compose.yml         # Full stack: PG, Neo4j, Qdrant, Redis, API, UI
├── .env.example               # Environment variable template
└── README.md
```

---

## 📖 Documentation Index

1. [PRD](docs/PRD.md) — Personas, functional modules
2. [Architecture](docs/Architecture.md) — System topology, multi-agent flows
3. [Database](docs/Database.md) — PostgreSQL + Neo4j ER schema
4. [AI Strategy](docs/AI.md) — LangGraph agents, RAG, SQL generation
5. [Design System](docs/Design.md) — Dark theme, glassmorphism, UI tokens
6. [API Spec](docs/API.md) — REST endpoints, JWT, SSE streaming
7. [Coding Rules](docs/Rules.md) — Standards, DDD, SOLID
8. [Phases](docs/Phases.md) — 10-phase implementation roadmap
9. [Tech Stack](docs/TechStack.md) — Stack justifications
10. [Memory Ledger](docs/Memory.md) — Progress tracking