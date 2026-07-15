# Product Requirements Document (PRD)

## Project Overview
The **KSP Crime Intelligence Platform** is an enterprise-grade AI-powered investigative and analytics solution designed for the Karnataka State Police. The platform integrates traditional relational databases (PostgreSQL), knowledge graphs (Neo4j), vector stores (Qdrant), and Advanced AI (LLMs, LangGraph, and NLP) to transition law enforcement from reactive manual record-keeping to proactive, data-driven policing and intelligent suspect profiling.

---

## Target Audience & Personas

| Persona | Role in System | Key Requirements |
| :--- | :--- | :--- |
| **Constable / Field Officer** | Field Reporting & Lookup | Voice-enabled search (Kannada & English), basic case lookups, check list guidance. |
| **Investigator (IO)** | Case Management & Leads | Node-based association maps, similarity searches for cases, digital timelines, checklist generation. |
| **Crime Analyst / SCRB** | Trend Analysis & Patterns | Geo-spatial hot spot layers, seasonal correlations, spatiotemporal spikes, anomaly alerts. |
| **Supervisors (SP, DIG, DGP)** | State/District oversight | Executive dashboards, high-level KPIs, district comparisons, resource allocation simulation. |
| **Policy Makers** | Long-term Strategy | Sociological correlation reports (urbanization, migration, demographics), policy feedback. |

---

## Key Functional Modules

### 1. Conversational Crime Intelligence Interface
- **Natural Language Querying**: Multi-turn conversation capability allowing users to ask questions in natural language.
- **Multilingual Support**: Primary languages: **English** and **Kannada**. Integrates Kannada NLP using IndicTrans/Whisper for speech-to-text.
- **Context-Aware Memory**: Retains conversation history within the session so follow-ups do not need redundant framing.
- **Evidence Citation & Explainability**: Every query response must display the exact data sources used, SQL queries executed, Neo4j graph paths traversed, and AI confidence scores.
- **Export Capabilities**: Clean, formatted PDF exports of conversation logs and retrieved crime summaries.

### 2. Criminal Network & Link Analysis
- **Entity Relationship Mapping**: Interactive graph visualizing connections between suspects, victims, phone numbers, vehicles, bank accounts, and addresses.
- **Organized Crime/Gang Detection**: Neo4j community detection algorithms (e.g., Louvain) to spot clustered illegal groups.
- **Modus Operandi (MO) Matcher**: Links suspects to multiple cases across jurisdictions based on recurring behavioral indicators.

### 3. Crime Pattern & Trend Analytics
- **Spatiotemporal Clusters**: Map layers of time of day and crime categories to identify spatiotemporal hotspots.
- **Emerging Spikes**: Warning indicator (e.g., red pulsing alert) when a specific crime head spikes compared to a 3-year running average in a station limit.
- **Seasonal Analysis**: Identification of crime spikes linked to specific festivals, seasons, or local economic cycles.

### 4. Sociological Crime Insights
- **Demographic Overlays**: Correlate crime rates with census metrics such as population density, age, gender, education level, and urbanization.
- **Migration & Stress Mapping**: Cross-reference crime hotspots with migration inflows and economic stress indicators.

### 5. Investigator Decision Support
- **Digital Case Timeline**: Chronological presentation of the life-cycle of a case (FIR registration -> arrest -> investigation events -> chargesheet -> court trial).
- **Similar Case Finder**: Finds solved cases with matching MOs, section associations, and profiles to suggest next investigation steps.
- **Lead Generation & Missing Links**: Flagging missing parameters in current cases (e.g., missing statements, phone records not analyzed).

### 6. Financial Transaction Link Analysis
- **Money Trails**: Track money flow across accounts associated with suspects.
- **Suspicious Transaction Networks**: Flag accounts receiving bulk transfers from known offender profiles.

### 7. Crime Forecasting & Resource Allocation
- **Scenario Simulation**: Allow supervisors to simulate shifting patrol routes or increasing police density in a hotspot and view simulated impacts on crime occurrences.
- **Risk Score Forecasting**: Predictive scores indicating high-probability crime windows and sectors.

### 8. Security & Governance
- **Role-Based Access Control (RBAC)**: Fine-grained permissions matching police hierarchy.
- **Citizen-Safe Demo Mode**: Active toggle to mask personally identifiable information (PII) like names, specific telephone numbers, and addresses during public hackathon demonstrations.
- **Audit Logs**: Cryptographically signed logs tracking which user searched for what case file or suspect record.
