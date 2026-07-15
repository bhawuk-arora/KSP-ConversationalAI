# Project Rules & Coding Standards

This document establishes the architectural guidelines, code standards, conventions, and patterns required to maintain a highly scalable, clean, and professional enterprise-grade platform.

---

## 1. Architectural Principles

### 1.1 Decoupled Layering (Domain-Driven Design)
- **Domain Layer (Core)**: Houses the business logic and entity models. This layer has zero dependencies on frameworks, databases, or third-party packages.
- **Repository Layer**: Interfaces with storage engines (PostgreSQL, Neo4j, Qdrant). Decoupled via Interfaces (Abstract Base Classes in Python) to allow database mocking in unit tests.
- **Service Layer**: Coordinates operations, agent runs (LangGraph), and transaction controls.
- **API/Router Layer**: Handles requests, HTTP formatting, payload parsing, and output formatting.

### 1.2 SOLID & DRY
- **Single Responsibility (SRP)**: Each class, module, or function must do exactly one thing. Do not write monolithic helper files.
- **Open/Closed (OCP)**: Routings or operations should be open to extension but closed to modification (e.g. adding a new agent node to LangGraph should only require defining a new node function, not modifying the core executor loop).
- **Dependency Inversion (DIP)**: High-level modules must not depend on low-level modules. Always depend on abstractions (interfaces).

---

## 2. Naming Conventions

### 2.1 Backend (Python)
- **Variables & Functions**: `snake_case` (e.g., `calculate_crime_trend`).
- **Classes**: `PascalCase` (e.g., `CaseRepository`).
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `MAX_TOKEN_LIMIT`).
- **File Names**: `snake_case` (e.g., `case_router.py`).

### 2.2 Frontend (TypeScript & React)
- **Components**: `PascalCase` (e.g., `GeospatialMap.tsx`).
- **Hooks & Utilities**: `camelCase` (e.g., `useSessionMemory.ts`).
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `BASE_API_URL`).
- **Styles / CSS ClassNames**: CSS modules or camelCase variable exports.

### 2.3 Database
- **Tables & Columns**: Match the KSP ER diagram schema exactly. Do not abbreviate or change casing unless required by DB drivers.
- **Keys & Indices**: Prefixed consistently (`pk_`, `fk_`, `idx_`, `gist_`).

---

## 3. Testing Rules

- **Code Coverage**: Aim for at least 80% coverage on service-level logic and database mapping files.
- **No Network in Unit Tests**: External services (OpenAI, Gemini, Zoho Catalyst APIs) and database calls must be mocked in unit tests (`unittest.mock` in Python, MSW/Jest in TypeScript).
- **Test Command Conventions**:
  - Python: Run tests with `pytest` within the `backend/` directory.
  - TypeScript: Run tests with `npm test` within the `frontend/` directory.

---

## 4. System Integrity & Git Strategy

- **No Placeholder Code**: Do not commit code containing comments like `// TODO: Implement later` or `pass # placeholder`. All files must contain production-ready logic or raising `NotImplementedError` templates with structural details.
- **Commit Messages**: Follow Conventional Commits:
  - `feat: add Neo4j graph RAG router`
  - `fix: correct index constraint on CaseMaster`
  - `docs: update deployment pipelines`
- **Environment Variables**: Never hardcode API keys, passwords, or connection strings. Always retrieve from environment configuration or Zoho Catalyst client variables.
- **Documentation**: Inline docstrings must accompany all API classes, database models, and GraphRAG nodes.
