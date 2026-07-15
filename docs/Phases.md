# Project Roadmap & Implementation Phases

This document details the phased implementation strategy for the KSP Crime Intelligence Platform. Each phase represents a distinct milestone that requires review and approval before proceeding.

---

## Roadmap Overview

```mermaid
gantt
    title KSP Crime Intelligence Platform Implementation Roadmap
    dateFormat  YYYY-MM-DD
    section Phase 1-3: Core Foundational
    Architecture & Docs         :active, p1, 2026-07-16, 2d
    Database Migrations         : p2, after p1, 3d
    Backend Base (FastAPI)     : p3, after p2, 4d
    section Phase 4-5: Access & UI
    Authentication & RBAC       : p4, after p3, 2d
    Frontend Scaffold & Design  : p5, after p4, 4d
    section Phase 6-7: AI & Graph
    AI Engine (LangGraph/RAG)   : p6, after p5, 5d
    Graph Engine (Neo4j Link)   : p7, after p6, 4d
    section Phase 8-10: Vis & Deploy
    GIS Mapping & Dashboards    : p8, after p7, 4d
    PDF Reports & Simulation    : p9, after p8, 3d
    Catalyst Deployment & Demo   : p10, after p9, 3d
```

---

## Phase Breakdowns

### Phase 1: Architecture & Documentation (Current Phase)
- **Goal**: Create directory structures, detail system components, design database mappings, define API signatures, and write coding rules.
- **Deliverables**: PRD, Architecture, Database, AI, Design, API, Rules, Phases, TechStack, and Memory files in `docs/`.
- **Review Trigger**: Approval of Phase 1 files.

### Phase 2: Database Setup & Migration
- **Goal**: Spin up local PostgreSQL instance, write SQL schema files based on KSP ER model, and write seeding scripts with synthetic data.
- **Deliverables**: Database migrations, DDL scripts, SQL seed files, and validation scripts verifying relationships.

### Phase 3: Backend Core Development
- **Goal**: Set up the FastAPI framework, build ORM models, create repository layers, and build standard CRUD and search endpoints.
- **Deliverables**: FastAPI base application, unit test framework, CRUD APIs for CaseMaster, Accused, and Victims.

### Phase 4: Authentication & RBAC
- **Goal**: Configure Zoho Catalyst Authentication, build middleware to parse JWT claims, and enforce role permissions.
- **Deliverables**: Auth middleware, role validation hooks, security mock tests.

### Phase 5: Frontend Skeleton & Design System
- **Goal**: Initialize Next.js project with TailwindCSS and Shadcn UI, set up the layout structure (sidebar, chat drawer), and implement the global dark theme.
- **Deliverables**: Next.js scaffolding, global CSS theme system, dashboard layout component, responsive chat shell.

### Phase 6: AI Conversational Engine
- **Goal**: Implement the LangGraph routing agent, integrate Qdrant vector search, and build the structured SQL execution agent.
- **Deliverables**: LangGraph coordinator script, SQL translation prompt, Qdrant indexing script, streaming chat endpoint.

### Phase 7: Graph Engine & Link Analysis
- **Goal**: Integrate Neo4j database, build Cypher query generator, and connect relationship nodes to the conversational assistant.
- **Deliverables**: Neo4j client connection, Cypher agent tool, graph payload generator, community detection analytics.

### Phase 8: GIS & Map Visualizations
- **Goal**: Embed Leaflet maps in frontend, map spatial coordinates of CaseMaster, and build cluster heatmaps.
- **Deliverables**: Map component, spatiotemporal filters, heat-cluster overlays, emerging spike alert markers.

### Phase 9: PDF Reports & Scenario Simulation
- **Goal**: Integrate PDF generation library to export chat transcripts and case summaries, and build a trend simulation dashboard.
- **Deliverables**: PDF export function, scenario simulator charts (Patrol frequency vs Crime Rate model).

### Phase 10: Catalyst Deployment & Demo Prep
- **Goal**: Containerize FastAPI, deploy Client to Catalyst App hosting, configure environment secrets, and verify Demo Mode PII masking.
- **Deliverables**: Dockerfiles, catalyst.json config, GitHub actions workflow, final testing verification walkthrough.
