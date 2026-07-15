# Database Architecture & Design Document

This document explains the database design for the KSP Crime Intelligence Platform, matching the Karnataka Police ER Schema.

---

## 1. Table Definitions & ER Schema Mapping

The core relational database is built on **PostgreSQL**. The following tables model the police records exactly as defined in the ER diagram:

### 1.1 Core Case Records
- **`CaseMaster`**: The primary entity representing a First Information Report (FIR), Unnatural Death Report (UDR), or Police Action Report (PAR).
  - *Primary Key*: `CaseMasterID` (INT)
  - *Key Columns*: `CrimeNo` (Structured: Case Category + District + Station + Year + Serial), `CaseNo`, `CrimeRegisteredDate` (DATE), `PolicePersonID` (FK -> Employee), `PoliceStationID` (FK -> Unit), `CaseCategoryID` (FK -> CaseCategory), `GravityOffenceID` (FK -> GravityOffence), `CrimeMajorHeadID` (FK -> CrimeHead), `CrimeMinorHeadID` (FK -> CrimeSubHead), `CaseStatusID` (FK -> CaseStatusMaster), `CourtID` (FK -> Court), `IncidentFromDate`, `IncidentToDate`, `latitude` (DECIMAL), `longitude` (DECIMAL), `BriefFacts` (TEXT).
- **`ComplainantDetails`**: Details of individuals filing the case.
  - *Key Columns*: `ComplainantID` (PK), `CaseMasterID` (FK -> CaseMaster), `ComplainantName`, `AgeYear`, `OccupationID` (FK -> OccupationMaster), `ReligionID` (FK -> ReligionMaster), `CasteID` (FK -> CasteMaster), `GenderID` (INT).
- **`Victim`**: Details of victims associated with the case.
  - *Key Columns*: `VictimMasterID` (PK), `CaseMasterID` (FK -> CaseMaster), `VictimName`, `AgeYear`, `GenderID` (INT), `VictimPolice` (BIT flag).
- **`Accused`**: Individuals identified or suspect in the case.
  - *Key Columns*: `AccusedMasterID` (PK), `CaseMasterID` (FK -> CaseMaster), `AccusedName`, `AgeYear`, `GenderID` (INT), `PersonID` (Sorting order identifier like A1, A2).

### 1.2 Legal Acts & Sections
- **`Act`**: Legal acts (e.g., Indian Penal Code, NDPS).
  - *Key Columns*: `ActCode` (VARCHAR PK), `ActDescription`, `ShortName`, `Active` (BIT).
- **`Section`**: Specific sections belonging to an Act.
  - *Key Columns*: `ActCode` (VARCHAR FK -> Act), `SectionCode` (VARCHAR), `SectionDescription`, `Active` (BIT).
- **`ActSectionAssociation`**: Junction table mapping multiple acts/sections to a single CaseMaster.
  - *Key Columns*: `CaseMasterID` (FK -> CaseMaster), `ActCode` (FK -> Act), `SectionCode` (FK -> Section), `ActOrderID`, `SectionOrderID`.

### 1.3 Case Outcomes & Events
- **`ArrestSurrender`**: Records details of arrests or voluntary surrenders.
  - *Key Columns*: `ArrestSurrenderID` (PK), `CaseMasterID` (FK -> CaseMaster), `ArrestSurrenderTypeID` (Lookup), `ArrestSurrenderDate` (DATE), `ArrestSurrenderStateId` (FK -> State), `ArrestSurrenderDistrictId` (FK -> District), `PoliceStationID` (FK -> Unit), `IOID` (FK -> Employee), `CourtID` (FK -> Court), `AccusedMasterID` (FK -> Accused), `IsAccused` (BIT), `IsComplainantAccused` (BIT).
- **`ChargesheetDetails`**: Records final outcome reports filed in court.
  - *Key Columns*: `CSID` (PK), `CaseMasterID` (FK -> CaseMaster), `csdate` (DATETIME), `cstype` (CHAR: A -> Chargesheet, B -> False Case, C -> Undetected), `PolicePersonID` (FK -> Employee).

### 1.4 Demographics & Administrative Master Tables
- **`State`**, **`District`**, **`Court`**, **`Unit`** (Police Station/Circle Office), **`UnitType`**
- **`Employee`** (KSP Police personnel), **`Rank`**, **`Designation`**
- **`CasteMaster`**, **`ReligionMaster`**, **`OccupationMaster`**, **`CaseStatusMaster`**, **`CaseCategory`**, **`GravityOffence`**

---

## 2. PostgreSQL Indexes & Optimizations

To handle hundreds of thousands of crime records efficiently, Postgres is configured with the following optimizations:

- **B-Tree Indexes**: Created on all Foreign Keys (`CaseMasterID`, `AccusedMasterID`, `UnitID`, `CrimeMajorHeadID`, etc.) to speed up relational joins.
- **Geospatial Index (GiST)**: 
  ```sql
  CREATE INDEX idx_casemaster_geom ON CaseMaster USING gist (ST_SetSRID(ST_MakePoint(longitude, latitude), 4326));
  ```
  Enables sub-second radial/bounding box spatial searches (e.g. finding cases within 20km).
- **Trigram Full-Text Index (GIN)**:
  ```sql
  CREATE INDEX idx_casemaster_brief_facts_gin ON CaseMaster USING gin (BriefFacts gin_trgm_ops);
  ```
  Accelerates prefix/suffix and typo-tolerant searches on FIR BriefFacts.
- **Table Partitioning**: `CaseMaster` is range-partitioned by `CrimeRegisteredDate` annually to keep active indexes small and historical queries performant.

---

## 3. Graph Database (Neo4j) Network Schema

Relational schemas fail to efficiently track deep suspect networks (e.g., suspect linked to a phone, linked to another suspect, linked to a transaction). Neo4j represents these explicitly:

### Nodes
- `(:Accused {id: String, name: String, age: Integer, gender: String})`
- `(:Victim {id: String, name: String, age: Integer, gender: String})`
- `(:CaseMaster {id: Integer, crime_no: String, date: Date, brief: String})`
- `(:Vehicle {plate_no: String, model: String})`
- `(:Phone {phone_no: String})`
- `(:Account {account_no: String, bank_name: String})`

### Relationships
- `(:Accused)-[:ACCUSED_IN]->(:CaseMaster)`
- `(:Victim)-[:VICTIM_IN]->(:CaseMaster)`
- `(:Accused)-[:ASSOCIATED_WITH {type: String}]->(:Accused)`
- `(:Accused)-[:USES_PHONE]->(:Phone)`
- `(:Accused)-[:OWNER_OF]->(:Vehicle)`
- `(:Phone)-[:CALLED {duration_sec: Integer, date: DateTime}]->(:Phone)`
- `(:Accused)-[:TRANSACTED_WITH {amount: Float, date: DateTime}]->(:Account)`

---

## 4. Vector Database (Qdrant) Schema

Used for semantically searching crime narratives, enabling semantic search beyond exact keywords.

- **Collection Name**: `ksp_fir_briefs`
- **Vector Size**: 1536 (OpenAI `text-embedding-3-small`) or 384 (BGE/E5 small model).
- **Payload Schema**:
  ```json
  {
    "case_master_id": 120445,
    "crime_no": "FIR:104430006202600001",
    "crime_major_head": "Theft",
    "crime_minor_head": "House Breaking By Night",
    "registered_date": "2026-03-12",
    "police_station_id": 4044
  }
  ```
- **Index Config**: HNSW (Hierarchical Navigable Small World) with Cosine metric for fast semantic retrieval.
