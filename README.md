# KSP Crime Intelligence Platform

An enterprise-grade, AI-powered Crime Intelligence and Analytics Platform built for the **Karnataka State Police (KSP)**. This platform replaces fragmented manual spreadsheets with a consolidated, reactive-to-proactive data intelligence framework utilizing PostgreSQL, Neo4j, Qdrant, and stateful LangGraph agents.

---

## 📂 Project Directory Structure

```text
KSP-ConversationalAI/
│
├── docs/                      # Core Design & Project Documentation
│   ├── PRD.md                 # Product Requirements Document
│   ├── Architecture.md        # System & Catalyst Architecture
│   ├── Database.md            # Postgres & Neo4j ER Schema Mapping
│   ├── AI.md                  # LangGraph, RAG & SQL Agent Specs
│   ├── Design.md              # UI/UX & Glassmorphism Guidelines
│   ├── API.md                 # REST API Spec & Request Payloads
│   ├── Rules.md               # Coding Standards & Guidelines
│   ├── Phases.md              # 10-Phase Roadmap & Milestones
│   ├── TechStack.md           # Visual/Stack Choice Justifications
│   └── Memory.md              # Project Progress & State Ledger
│
├── backend/                   # Python FastAPI Application
├── frontend/                  # React, Next.js, & TypeScript Interface
├── ai-engine/                 # LangGraph Agent Workflows
├── analytics/                 # Custom Analytics & Scoring Models
├── graph-engine/              # Neo4j Graph Queries & Clusters
├── services/                  # Common/Shared Core Services
├── infra/                     # Docker, CI/CD, & Server Setup
├── catalyst/                  # Zoho Catalyst Deployment files
├── database/                  # SQL Migrations & Database Seeds
└── README.md                  # Main project index
```

---

## 📖 System Documentation Index

We have established a robust codebase design context inside the `docs/` folder. Read the specific files below for full details:

1. **[Product Requirements (docs/PRD.md)](file:///c:/Users/bhawu/Documents/GitHub/KSP-ConversationalAI/docs/PRD.md)**: Personas (Constables to DGP), detailed functional modules (Conversational AI, GIS heatmaps, Offender profiling, Graph link analysis, Audit logs).
2. **[Architecture (docs/Architecture.md)](file:///c:/Users/bhawu/Documents/GitHub/KSP-ConversationalAI/docs/Architecture.md)**: System topology, multi-agent flows, Zoho Catalyst serverless integration.
3. **[Database Mapping (docs/Database.md)](file:///c:/Users/bhawu/Documents/GitHub/KSP-ConversationalAI/docs/Database.md)**: Detailed representation of the KSP FIR ER diagram, including indexes (GiST/GIN), Neo4j nodes/edges, and Qdrant payload schemas.
4. **[AI & Search Strategy (docs/AI.md)](file:///c:/Users/bhawu/Documents/GitHub/KSP-ConversationalAI/docs/AI.md)**: Multi-agent LangGraph routes, SQL/Cypher code generation, Semantic caching, and Citizen-safe demo mode masking.
5. **[UI/UX Design System (docs/Design.md)](file:///c:/Users/bhawu/Documents/GitHub/KSP-ConversationalAI/docs/Design.md)**: Dark theme tokens, HSL colors, glassmorphism cards, map aesthetics, and React Flow suspect graphs.
6. **[API Specifications (docs/API.md)](file:///c:/Users/bhawu/Documents/GitHub/KSP-ConversationalAI/docs/API.md)**: REST interfaces, Bearer JWT RBAC security, Server-Sent Events (SSE) chat streaming, and error handling.
7. **[Coding Standards (docs/Rules.md)](file:///c:/Users/bhawu/Documents/GitHub/KSP-ConversationalAI/docs/Rules.md)**: DDD modular layouts, SOLID rules, formatting guidelines (snake_case vs camelCase), and mock testing constraints.
8. **[Project Milestones (docs/Phases.md)](file:///c:/Users/bhawu/Documents/GitHub/KSP-ConversationalAI/docs/Phases.md)**: 10-Phase roadmap timeline detailing the development sequence.
9. **[Tech Stack Choices (docs/TechStack.md)](file:///c:/Users/bhawu/Documents/GitHub/KSP-ConversationalAI/docs/TechStack.md)**: Technical justifications for FastAPI, PostgreSQL, Neo4j, Qdrant, React Flow, and Zoho Catalyst functions/hosting.
10. **[State Memory Ledger (docs/Memory.md)](file:///c:/Users/bhawu/Documents/GitHub/KSP-ConversationalAI/docs/Memory.md)**: Progress tracking tool that preserves context across subsequent steps.

---

## ⚡ Next Steps
Now that the project environment, architecture, and docs are established in Phase 1, we are ready to transition to **Phase 2: Database Setup & Migration**.