-- KSP Crime Intelligence Platform - Database Schema
-- Target Database: PostgreSQL 15+

-- Enable extensions if not already present
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- =========================================================================
-- 1. Administrative & Demographic Master Tables
-- =========================================================================

CREATE TABLE State (
    StateID SERIAL PRIMARY KEY,
    StateName VARCHAR(100) NOT NULL,
    NationalityID INT DEFAULT 1,
    Active BOOLEAN DEFAULT TRUE
);

CREATE TABLE District (
    DistrictID INT PRIMARY KEY,
    DistrictName VARCHAR(100) NOT NULL,
    StateID INT REFERENCES State(StateID),
    Active BOOLEAN DEFAULT TRUE
);

CREATE TABLE Court (
    CourtID INT PRIMARY KEY,
    CourtName VARCHAR(255) NOT NULL,
    DistrictID INT REFERENCES District(DistrictID),
    StateID INT REFERENCES State(StateID),
    Active BOOLEAN DEFAULT TRUE
);

CREATE TABLE UnitType (
    UnitTypeID INT PRIMARY KEY,
    UnitTypeName VARCHAR(100) NOT NULL,
    CityDistState VARCHAR(50),
    Hierarchy INT,
    Active BOOLEAN DEFAULT TRUE
);

CREATE TABLE Unit (
    UnitID INT PRIMARY KEY,
    UnitName VARCHAR(150) NOT NULL,
    TypeID INT REFERENCES UnitType(UnitTypeID),
    ParentUnit INT REFERENCES Unit(UnitID),
    NationalityID INT DEFAULT 1,
    StateID INT REFERENCES State(StateID),
    DistrictID INT REFERENCES District(DistrictID),
    Active BOOLEAN DEFAULT TRUE
);

CREATE TABLE Rank (
    RankID INT PRIMARY KEY,
    RankName VARCHAR(100) NOT NULL,
    Hierarchy INT,
    Active BOOLEAN DEFAULT TRUE
);

CREATE TABLE Designation (
    DesignationID INT PRIMARY KEY,
    DesignationName VARCHAR(100) NOT NULL,
    Active BOOLEAN DEFAULT TRUE,
    SortOrder INT
);

CREATE TABLE Employee (
    EmployeeID INT PRIMARY KEY,
    DistrictID INT REFERENCES District(DistrictID),
    UnitID INT REFERENCES Unit(UnitID),
    RankID INT REFERENCES Rank(RankID),
    DesignationID INT REFERENCES Designation(DesignationID),
    KGID VARCHAR(50) UNIQUE NOT NULL,
    FirstName VARCHAR(100) NOT NULL,
    EmployeeDOB DATE,
    GenderID INT, -- Lookup mapping (e.g. 1=Male, 2=Female, 3=Other)
    BloodGroupID INT,
    PhysicallyChallenged BOOLEAN DEFAULT FALSE,
    AppointmentDate DATE
);

CREATE TABLE CasteMaster (
    caste_master_id INT PRIMARY KEY,
    caste_master_name VARCHAR(100) NOT NULL
);

CREATE TABLE ReligionMaster (
    ReligionID INT PRIMARY KEY,
    ReligionName VARCHAR(100) NOT NULL
);

CREATE TABLE OccupationMaster (
    OccupationID INT PRIMARY KEY,
    OccupationName VARCHAR(150) NOT NULL
);

CREATE TABLE CaseCategory (
    CaseCategoryID INT PRIMARY KEY,
    LookupValue VARCHAR(50) NOT NULL -- FIR, UDR, Zero FIR, PAR...
);

CREATE TABLE GravityOffence (
    GravityOffenceID INT PRIMARY KEY,
    LookupValue VARCHAR(50) NOT NULL -- Heinous, Non-Heinous
);

CREATE TABLE CaseStatusMaster (
    CaseStatusID INT PRIMARY KEY,
    CaseStatusName VARCHAR(100) NOT NULL -- Under Investigation, Charge Sheeted, Closed...
);

-- =========================================================================
-- 2. Legal Acts, Sections & Offence Classifications
-- =========================================================================

CREATE TABLE CrimeHead (
    CrimeHeadID INT PRIMARY KEY,
    CrimeGroupName VARCHAR(150) NOT NULL, -- e.g. Crimes Against Body
    Active BOOLEAN DEFAULT TRUE
);

CREATE TABLE CrimeSubHead (
    CrimeSubHeadID INT PRIMARY KEY,
    CrimeHeadID INT REFERENCES CrimeHead(CrimeHeadID),
    CrimeHeadName VARCHAR(150) NOT NULL, -- e.g. Murder, Robbery
    SeqID INT
);

CREATE TABLE Act (
    ActCode VARCHAR(50) PRIMARY KEY, -- e.g. IPC, NDPS
    ActDescription VARCHAR(255) NOT NULL,
    ShortName VARCHAR(50),
    Active BOOLEAN DEFAULT TRUE
);

CREATE TABLE Section (
    ActCode VARCHAR(50) REFERENCES Act(ActCode),
    SectionCode VARCHAR(50) NOT NULL, -- e.g. 302, 307
    SectionDescription TEXT,
    Active BOOLEAN DEFAULT TRUE,
    PRIMARY KEY (ActCode, SectionCode)
);

CREATE TABLE CrimeHeadActSection (
    CrimeHeadID INT REFERENCES CrimeHead(CrimeHeadID),
    ActCode VARCHAR(50),
    SectionCode VARCHAR(50),
    PRIMARY KEY (CrimeHeadID, ActCode, SectionCode),
    FOREIGN KEY (ActCode, SectionCode) REFERENCES Section(ActCode, SectionCode)
);

-- =========================================================================
-- 3. Case Records & Associated Entities
-- =========================================================================

CREATE TABLE CaseMaster (
    CaseMasterID INT PRIMARY KEY,
    CrimeNo VARCHAR(50) UNIQUE NOT NULL, -- Structured KSP Crime Number
    CaseNo VARCHAR(50) NOT NULL,         -- Year + Serial (Last 9 digits of CrimeNo)
    CrimeRegisteredDate DATE NOT NULL,
    PolicePersonID INT REFERENCES Employee(EmployeeID),
    PoliceStationID INT REFERENCES Unit(UnitID),
    CaseCategoryID INT REFERENCES CaseCategory(CaseCategoryID),
    GravityOffenceID INT REFERENCES GravityOffence(GravityOffenceID),
    CrimeMajorHeadID INT REFERENCES CrimeHead(CrimeHeadID),
    CrimeMinorHeadID INT REFERENCES CrimeSubHead(CrimeSubHeadID),
    CaseStatusID INT REFERENCES CaseStatusMaster(CaseStatusID),
    CourtID INT REFERENCES Court(CourtID),
    IncidentFromDate TIMESTAMP,
    IncidentToDate TIMESTAMP,
    InfoReceivedPSDate TIMESTAMP,
    latitude DECIMAL(9, 6),
    longitude DECIMAL(9, 6),
    BriefFacts TEXT
);

CREATE TABLE ComplainantDetails (
    ComplainantID INT PRIMARY KEY,
    CaseMasterID INT REFERENCES CaseMaster(CaseMasterID) ON DELETE CASCADE,
    ComplainantName VARCHAR(255) NOT NULL,
    AgeYear INT,
    OccupationID INT REFERENCES OccupationMaster(OccupationID),
    ReligionID INT REFERENCES ReligionMaster(ReligionID),
    CasteID INT REFERENCES CasteMaster(caste_master_id),
    GenderID INT -- Lookup mapping (e.g. 1=Male, 2=Female, 3=Other)
);

CREATE TABLE Victim (
    VictimMasterID INT PRIMARY KEY,
    CaseMasterID INT REFERENCES CaseMaster(CaseMasterID) ON DELETE CASCADE,
    VictimName VARCHAR(255) NOT NULL,
    AgeYear INT,
    GenderID INT, -- Lookup mapping
    VictimPolice VARCHAR(10) -- e.g. "1" if police, "0" otherwise
);

CREATE TABLE Accused (
    AccusedMasterID INT PRIMARY KEY,
    CaseMasterID INT REFERENCES CaseMaster(CaseMasterID) ON DELETE CASCADE,
    AccusedName VARCHAR(255) NOT NULL,
    AgeYear INT,
    GenderID VARCHAR(10), -- M/F/T in CSV data
    PersonID VARCHAR(10) NOT NULL -- Accused Identifier order (e.g. A1, A2...)
);

CREATE TABLE ActSectionAssociation (
    CaseMasterID INT REFERENCES CaseMaster(CaseMasterID) ON DELETE CASCADE,
    ActID VARCHAR(50),
    SectionID VARCHAR(50),
    ActOrderID INT,
    SectionOrderID INT,
    PRIMARY KEY (CaseMasterID, ActID, SectionID),
    FOREIGN KEY (ActID, SectionID) REFERENCES Section(ActCode, SectionCode)
);

CREATE TABLE ArrestSurrender (
    ArrestSurrenderID INT PRIMARY KEY,
    CaseMasterID INT REFERENCES CaseMaster(CaseMasterID) ON DELETE CASCADE,
    ArrestSurrenderTypeID INT, -- Lookup: Arrest vs. Voluntary Surrender
    ArrestSurrenderDate DATE NOT NULL,
    ArrestSurrenderStateId INT REFERENCES State(StateID),
    ArrestSurrenderDistrictId INT REFERENCES District(DistrictID),
    PoliceStationID INT REFERENCES Unit(UnitID),
    IOID INT REFERENCES Employee(EmployeeID),
    CourtID INT REFERENCES Court(CourtID),
    AccusedMasterID INT REFERENCES Accused(AccusedMasterID) ON DELETE CASCADE,
    IsAccused BOOLEAN DEFAULT TRUE,
    IsComplainantAccused BOOLEAN DEFAULT FALSE
);

CREATE TABLE ChargesheetDetails (
    CSID INT PRIMARY KEY,
    CaseMasterID INT REFERENCES CaseMaster(CaseMasterID) ON DELETE CASCADE,
    csdate TIMESTAMP NOT NULL,
    cstype CHAR(1) CHECK (cstype IN ('A', 'B', 'C')), -- A -> Chargesheet, B -> False Case, C -> Undetected
    PolicePersonID INT REFERENCES Employee(EmployeeID)
);

-- =========================================================================
-- 4. Indexes & Optimizations
-- =========================================================================

-- Standard B-Tree Indexes on Foreign Keys for faster relational joins
CREATE INDEX idx_casemaster_station ON CaseMaster(PoliceStationID);
CREATE INDEX idx_casemaster_date ON CaseMaster(CrimeRegisteredDate);
CREATE INDEX idx_casemaster_major_head ON CaseMaster(CrimeMajorHeadID);
CREATE INDEX idx_casemaster_minor_head ON CaseMaster(CrimeMinorHeadID);
CREATE INDEX idx_casemaster_status ON CaseMaster(CaseStatusID);

CREATE INDEX idx_accused_case ON Accused(CaseMasterID);
CREATE INDEX idx_victim_case ON Victim(CaseMasterID);
CREATE INDEX idx_complainant_case ON ComplainantDetails(CaseMasterID);
CREATE INDEX idx_arrest_case ON ArrestSurrender(CaseMasterID);
CREATE INDEX idx_arrest_accused ON ArrestSurrender(AccusedMasterID);
CREATE INDEX idx_chargesheet_case ON ChargesheetDetails(CaseMasterID);

-- Geospatial index using PostGIS for distance & boundary checks
CREATE INDEX idx_casemaster_geo ON CaseMaster USING gist (ST_SetSRID(ST_MakePoint(longitude, latitude), 4326));

-- Trigram GIN index for full-text search on Brief Facts narrative
CREATE INDEX idx_casemaster_brief_facts_trgm ON CaseMaster USING GIN (BriefFacts gin_trgm_ops);
