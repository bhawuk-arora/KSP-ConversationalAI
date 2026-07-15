# Technology Stack & Selection Justifications

This document explains the technology stack selected for the KSP Crime Intelligence Platform and justifies why each component was chosen for an enterprise-grade government solution.

---

## 1. Core Hosting & Infrastructure: Zoho Catalyst

The platform is designed around **Zoho Catalyst** to satisfy enterprise scalability, security standards, and rapid deployment cycles required in hackathon environments.

- **App Hosting (Server & Client)**: Catalyst App Hosting runs both our Dockerized FastAPI backend container and our statically compiled Next.js frontend, ensuring single-domain communication and low latency.
- **Catalyst Authentication**: Eliminates the overhead of building OAuth/session services from scratch, providing secure, ready-to-use user databases, password hashes, and session validation.
- **Catalyst File Store**: Serves as a secure cloud storage bucket for sensitive media files, uploaded voice records, and PDF investigation reports, removing local filesystem dependencies.
- **Catalyst Zia AI**: Used for baseline NLP, translation fallback, or document OCR during chargesheet uploads, integrating seamlessly with Zoho infrastructure.

---

## 2. Backend & Relational Database Layer

- **FastAPI (Python)**: Selected over Django/Flask due to native asynchronous handling (high concurrency for LLM streaming), automatic OpenAPI/Swagger generation, and execution speeds approaching Go/NodeJS.
- **PostgreSQL**: The standard for relational data. Its robust transactional integrity (ACID) matches KSP’s requirements. Supported by **PostGIS** to perform calculations like finding crimes within a 15km radius of a police station.
- **SQLAlchemy & Alembic**: Object Relational Mapping (ORM) and migration tools to ensure version-controlled database schema iterations.

---

## 3. Knowledge Graph & Vector Engines

- **Neo4j**: Traditional SQL joins become slow and complex when querying multi-hop networks (e.g., suspect -> phone number -> call log -> other suspect -> shared bank account). Neo4j handles index-free adjacency, returning deep network structures instantly.
- **Qdrant**: High-performance vector database to index and search dense vector representations of FIR narratives (`BriefFacts`). Supports HNSW indexing for rapid semantic querying.
- **Redis**: Acts as an in-memory data store for semantic caching (checking if a query was run recently) and maintaining conversation session state parameters.

---

## 4. Front-End & Visualization Framework

- **Next.js (React) & TypeScript**: Modern frontend framework offering static site generation (SSG) and server-side rendering (SSR). TypeScript ensures type safety and reduces run-time exceptions on complex data structures.
- **TailwindCSS & Shadcn UI**: Tailwind allows custom visual styling (such as glassmorphism filters and smooth dark themes) directly in-utility. Shadcn UI provides accessible, clean components out of the box.
- **Leaflet Maps**: Lightweight, highly customizable mapping library to display GIS overlays and crime cluster hotspots.
- **React Flow**: Node-based graphing utility to visualize suspect relationships, enabling interactive dragging, grouping, and traversal.
- **Apache ECharts**: Selected for analytics dashboards because it handles massive datasets (thousands of points) smoothly using canvas/SVG rendering and provides out-of-the-box dark themes.

---

## 5. Conversational AI & NLP

- **LangGraph**: Orchestrates stateful, multi-agent LLM workflows. Unlike linear pipelines, LangGraph supports cycles (e.g., trying a SQL query, catching a syntax error, correcting it, and retrying).
- **IndicTrans & Whisper**:
  - **Whisper**: Converts speech inputs (police constables speaking on the field) to text.
  - **IndicTrans**: Translates Kannada input text into English for LLM processing, and translates responses back to Kannada.
- **OpenAI GPT / Google Gemini / Anthropic Claude**: Utilized via uniform API layers. Gemini is preferred for large-context case summarization, while GPT-4o/Claude 3.5 Sonnet are utilized for precise SQL and Cypher query generation.
