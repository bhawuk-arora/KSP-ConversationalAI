# KSP Crime Intelligence Platform - Database Seeding Script
# Populates PostgreSQL with realistic KSP records and lookup values

import os
import sys
import subprocess
import random
from datetime import datetime, date

# Ensure psycopg2-binary is installed
try:
    import psycopg2
    from psycopg2.extras import execute_values
except ImportError:
    print("psycopg2 not found. Installing psycopg2-binary dynamically...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "psycopg2-binary"])
    import psycopg2
    from psycopg2.extras import execute_values

# Database connection credentials
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = os.environ.get("DB_PORT", "5432")
DB_USER = os.environ.get("DB_USER", "postgres")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "postgres")
DB_NAME = os.environ.get("DB_NAME", "ksp_db")

# Sample Data Elements for Karnataka Police Context
DISTRICTS = [
    (1, "Bengaluru City", 1, True),
    (2, "Mysuru City", 1, True),
    (3, "Mangaluru City", 1, True),
    (4, "Belagavi City", 1, True),
    (5, "Hubballi-Dharwada City", 1, True),
    (6, "Shivamogga", 1, True),
    (7, "Udupi", 1, True)
]

COURTS = [
    (1, "Principal District & Sessions Court, Bengaluru", 1, 1, True),
    (2, "JMFC I Court, Bengaluru", 1, 1, True),
    (3, "Principal District & Sessions Court, Mysuru", 2, 1, True),
    (4, "JMFC II Court, Mysuru", 2, 1, True),
    (5, "District Court, Mangaluru", 3, 1, True)
]

UNIT_TYPES = [
    (1, "Police Station", "Station", 5, True),
    (2, "Circle Office", "Circle", 4, True),
    (3, "Sub-Division", "Sub-Division", 3, True),
    (4, "District Police Office", "District", 2, True),
    (5, "State Police Headquarters", "State", 1, True)
]

UNITS = [
    (1, "State Police HQ", 5, None, 1, 1, 1, True),
    (2, "Bengaluru City Police Office", 4, 1, 1, 1, 1, True),
    (3, "Mysuru City Police Office", 4, 1, 1, 1, 2, True),
    (1001, "Vidhana Soudha Police Station", 1, 2, 1, 1, 1, True),
    (1002, "Kalasipalya Police Station", 1, 2, 1, 1, 1, True),
    (1003, "Devaraja Police Station", 1, 3, 1, 1, 2, True),
    (1004, "Lashkar Police Station", 1, 3, 1, 1, 2, True),
    (1005, "Kadri Police Station", 1, 1, 1, 1, 3, True)
]

RANKS = [
    (1, "Director General of Police (DGP)", 1, True),
    (2, "Inspector General of Police (IGP)", 2, True),
    (3, "Superintendent of Police (SP)", 3, True),
    (4, "Deputy Superintendent of Police (DySP)", 4, True),
    (5, "Police Inspector (PI)", 5, True),
    (6, "Sub-Inspector of Police (PSI)", 6, True),
    (7, "Assistant Sub-Inspector (ASI)", 7, True),
    (8, "Head Constable (HC)", 8, True),
    (9, "Police Constable (PC)", 9, True)
]

DESIGNATIONS = [
    (1, "Investigating Officer (IO)", True, 1),
    (2, "Station House Officer (SHO)", True, 2),
    (3, "Station Writer", True, 3),
    (4, "General Duty Officer", True, 4)
]

EMPLOYEES = [
    (101, 1, 1001, 5, 2, "KGID00124", "Ravi Kumar", date(1982, 5, 14), 1, 1, False, date(2005, 8, 1)),
    (102, 1, 1002, 6, 1, "KGID00395", "Siddaraju", date(1988, 11, 22), 1, 2, False, date(2012, 6, 15)),
    (103, 1, 1002, 9, 4, "KGID00982", "Kavitha M", date(1995, 3, 8), 2, 3, False, date(2020, 2, 1)),
    (104, 2, 1003, 6, 1, "KGID00483", "Venkatesh Murthy", date(1985, 4, 18), 1, 1, False, date(2010, 12, 1)),
    (105, 2, 1004, 5, 2, "KGID00273", "Shashikanth", date(1980, 1, 30), 1, 2, True, date(2003, 4, 10))
]

CASTES = [
    (1, "Vokkaliga"),
    (2, "Lingayat"),
    (3, "Kuruba"),
    (4, "SC"),
    (5, "ST"),
    (6, "General")
]

RELIGIONS = [
    (1, "Hindu"),
    (2, "Muslim"),
    (3, "Christian"),
    (4, "Sikh"),
    (5, "Jain")
]

OCCUPATIONS = [
    (1, "Agriculturist"),
    (2, "Business Owner"),
    (3, "Software Engineer"),
    (4, "Daily Wage Worker"),
    (5, "Student"),
    (6, "Unemployed"),
    (7, "Auto Driver")
]

CASE_CATEGORIES = [
    (1, "FIR"),
    (3, "UDR"),
    (4, "PAR"),
    (8, "Zero FIR")
]

GRAVITY_OFFENCES = [
    (1, "Heinous"),
    (2, "Non-Heinous")
]

CASE_STATUSES = [
    (1, "Under Investigation"),
    (2, "Charge Sheeted"),
    (3, "Closed (Undetected)"),
    (4, "Closed (False Case)")
]

CRIME_HEADS = [
    (1, "Crimes Against Body", True),
    (2, "Crimes Against Property", True),
    (3, "Narcotics & NDPS", True),
    (4, "Cyber Crimes", True)
]

CRIME_SUB_HEADS = [
    (1, 1, "Murder (Sec 302)", 1),
    (2, 1, "Attempt to Murder (Sec 307)", 2),
    (3, 2, "House Breaking & Theft By Night (Sec 380)", 3),
    (4, 2, "Robbery (Sec 392)", 4),
    (5, 3, "Drug Trafficking (NDPS Act)", 5),
    (6, 4, "Phishing & Financial Fraud (IT Act)", 6)
]

ACTS = [
    ("IPC", "Indian Penal Code", "IPC", True),
    ("NDPS", "Narcotics Drugs and Psychotropic Substances Act", "NDPS", True),
    ("IT_ACT", "Information Technology Act", "IT Act", True)
]

SECTIONS = [
    ("IPC", "302", "Punishment for Murder", True),
    ("IPC", "307", "Attempt to Murder", True),
    ("IPC", "379", "Punishment for Theft", True),
    ("IPC", "380", "Theft in dwelling house, etc.", True),
    ("IPC", "392", "Punishment for Robbery", True),
    ("NDPS", "20", "Contravention in relation to cannabis", True),
    ("NDPS", "21", "Manufacture or possession of drugs", True),
    ("IT_ACT", "66C", "Identity Theft", True),
    ("IT_ACT", "66D", "Cheating by personation using computer resource", True)
]

CRIME_HEAD_SECTIONS = [
    (1, "IPC", "302"),
    (1, "IPC", "307"),
    (2, "IPC", "379"),
    (2, "IPC", "380"),
    (2, "IPC", "392"),
    (3, "NDPS", "20"),
    (3, "NDPS", "21"),
    (4, "IT_ACT", "66C"),
    (4, "IT_ACT", "66D")
]

# Case Master Data Generation helper
def make_crime_no(category, district, unit, year, serial):
    return f"{category}{district:04d}{unit:04d}{year:04d}{serial:05d}"

CASE_MASTERS = [
    # Heinous Crimes (Murder / Attempted)
    (101, make_crime_no(1, 1, 1002, 2026, 1), "202600001", date(2026, 1, 15), 102, 1002, 1, 1, 1, 1, 2, 1,
     datetime(2026, 1, 14, 23, 30), datetime(2026, 1, 15, 0, 30), datetime(2026, 1, 15, 6, 0),
     12.9648, 77.5894,
     "On the night of 14-01-2026, near Kalasipalya bus stand, an altercation broke out between two rival gang members. The accused used a sharp metal dagger to stab the victim multiple times over territory dominance, leading to fatal injuries."),
     
    (102, make_crime_no(1, 1, 1001, 2026, 2), "202600002", date(2026, 2, 20), 101, 1001, 1, 1, 1, 2, 1, 2,
     datetime(2026, 2, 20, 10, 15), datetime(2026, 2, 20, 10, 45), datetime(2026, 2, 20, 11, 30),
     12.9796, 77.5908,
     "A political argument near the outer parking lot of Vidhana Soudha turned violent. The suspect pulled out a licensed firearm and fired one round at the victim, hitting the left shoulder. Bystanders disarmed the shooter and handed him over to patrols."),

    # Thefts (Housebreaking) - Link Accused across these to show repeat offender!
    (103, make_crime_no(1, 1, 1002, 2026, 3), "202600003", date(2026, 3, 5), 103, 1002, 1, 2, 2, 3, 1, 2,
     datetime(2026, 3, 4, 22, 0), datetime(2026, 3, 5, 4, 0), datetime(2026, 3, 5, 9, 0),
     12.9620, 77.5850,
     "Complainant reported that locks of his gold jewelry shop in Kalasipalya market were cut open using industrial cutters. Cash and silver items worth Rs 4.5 Lakhs were stolen. CCTV footage shows a masked individual matching a known MO."),

    (104, make_crime_no(1, 2, 1003, 2026, 4), "202600004", date(2026, 3, 18), 104, 1003, 1, 2, 2, 3, 1, 3,
     datetime(2026, 3, 17, 23, 0), datetime(2026, 3, 18, 5, 0), datetime(2026, 3, 18, 8, 30),
     12.3021, 76.6482,
     "Lock of a residential house in Devaraja, Mysuru was broken at night. Gold ornaments of 80 grams and cash of Rs 50,000 were stolen while the family was out of town. Footprints and locks cutter signature match a gang operating out of Bengaluru."),

    # Drugs (NDPS)
    (105, make_crime_no(1, 1, 1002, 2026, 5), "202600005", date(2026, 4, 12), 102, 1002, 1, 1, 3, 5, 1, 2,
     datetime(2026, 4, 12, 15, 0), datetime(2026, 4, 12, 15, 40), datetime(2026, 4, 12, 16, 15),
     12.9598, 77.5822,
     "Based on credible tip-off, Kalasipalya police raided a public park near K.R. Market. The suspect was found in possession of commercial quantities of Ganja (cannabis plant extract) packed in small plastic pouches intended for distribution to college students."),

    # Cyber Crimes
    (106, make_crime_no(1, 2, 1004, 2026, 6), "202600006", date(2026, 5, 3), 105, 1004, 1, 2, 4, 6, 2, 4,
     datetime(2026, 5, 1, 9, 0), datetime(2026, 5, 2, 18, 0), datetime(2026, 5, 3, 11, 0),
     12.3110, 76.6590,
     "Complainant was duped of Rs 1.8 Lakhs by a caller impersonating a bank customer executive. The victim was convinced to share OTPs to unblock their credit card, leading to immediate illegal fund routing to mule accounts.")
]

# Complainants, Victims, Accused
COMPLAINANTS = [
    (201, 101, "Anil Gowda", 34, 2, 1, 1, 1),
    (202, 102, "Siddappa K", 52, 1, 1, 2, 1),
    (203, 103, "Mahesh Shah", 45, 2, 5, 6, 1),
    (204, 104, "Kiran Kumar", 38, 3, 1, 1, 1),
    (205, 105, "PSI Kalasipalya", 30, 2, 1, 1, 1), -- Police complainant
    (206, 106, "Sunita Rao", 29, 3, 1, 6, 2)
]

VICTIMS = [
    (301, 101, "Manjunath A", 28, 1, "0"),
    (302, 102, "Prashanth Shetty", 40, 1, "0"),
    (303, 103, "Mahesh Shah", 45, 1, "0"),
    (304, 104, "Kiran Kumar", 38, 1, "0"),
    (305, 106, "Sunita Rao", 29, 2, "0")
]

# Note: Ravi "Kariya" alias Ravi is the accused in both 103 (Kalasipalya Theft) and 104 (Devaraja Theft)
# to serve as a link in repeat offender queries.
ACCUSED = [
    (401, 101, "Ganesh alias Gani", 26, 1, "A1"),
    (402, 102, "Prakash Gowda", 39, 1, "A1"),
    (403, 103, "Ravi alias Kariya", 31, 1, "A1"), -- REPEAT OFFENDER
    (404, 104, "Ravi alias Kariya", 31, 1, "A1"), -- REPEAT OFFENDER LINK
    (405, 105, "Imran Khan", 24, 1, "A1"),
    (406, 106, "Unknown Caller", 35, 1, "A1")
]

ACT_SECTION_ASSOCS = [
    (101, "IPC", "302", 1, 1),
    (102, "IPC", "307", 1, 1),
    (103, "IPC", "379", 1, 1),
    (103, "IPC", "380", 1, 2),
    (104, "IPC", "379", 1, 1),
    (104, "IPC", "380", 1, 2),
    (105, "NDPS", "20", 1, 1),
    (106, "IT_ACT", "66C", 1, 1),
    (106, "IT_ACT", "66D", 1, 2)
]

ARREST_EVENTS = [
    (501, 101, 1, date(2026, 1, 16), 1, 1, 1002, 102, 1, 401, True, False),
    (502, 102, 1, date(2026, 2, 20), 1, 1, 1001, 101, 2, 402, True, False),
    (503, 103, 1, date(2026, 3, 15), 1, 1, 1002, 102, 1, 403, True, False),
    (504, 105, 1, date(2026, 4, 12), 1, 1, 1002, 102, 1, 405, True, False)
]

CHARGESHEETS = [
    (601, 101, datetime(2026, 4, 10, 11, 0), "A", 102),
    (602, 106, datetime(2026, 6, 20, 14, 0), "B", 105)
]

def seed_database():
    print(f"Connecting to database '{DB_NAME}' to insert seed data...")
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            dbname=DB_NAME
        )
        cursor = conn.cursor()
        
        # Clear existing data to support clean restarts
        print("Clearing historical table data...")
        tables_to_clear = [
            "ChargesheetDetails", "ArrestSurrender", "ActSectionAssociation", 
            "Accused", "Victim", "ComplainantDetails", "CaseMaster", 
            "CrimeHeadActSection", "Section", "Act", "CrimeSubHead", "CrimeHead", 
            "CaseStatusMaster", "GravityOffence", "CaseCategory", "OccupationMaster", 
            "ReligionMaster", "CasteMaster", "Employee", "Designation", "Rank", 
            "Unit", "UnitType", "Court", "District", "State"
        ]
        for tbl in tables_to_clear:
            cursor.execute(f"TRUNCATE TABLE {tbl} CASCADE;")
            
        print("Seeding lookups and masters...")
        # Inserts using execute_values or execute
        execute_values(cursor, "INSERT INTO State (StateID, StateName, NationalityID, Active) VALUES %s", STATES := [(1, "Karnataka", 1, True)])
        execute_values(cursor, "INSERT INTO District (DistrictID, DistrictName, StateID, Active) VALUES %s", DISTRICTS)
        execute_values(cursor, "INSERT INTO Court (CourtID, CourtName, DistrictID, StateID, Active) VALUES %s", COURTS)
        execute_values(cursor, "INSERT INTO UnitType (UnitTypeID, UnitTypeName, CityDistState, Hierarchy, Active) VALUES %s", UNIT_TYPES)
        execute_values(cursor, "INSERT INTO Unit (UnitID, UnitName, TypeID, ParentUnit, NationalityID, StateID, DistrictID, Active) VALUES %s", UNITS)
        execute_values(cursor, "INSERT INTO Rank (RankID, RankName, Hierarchy, Active) VALUES %s", RANKS)
        execute_values(cursor, "INSERT INTO Designation (DesignationID, DesignationName, Active, SortOrder) VALUES %s", DESIGNATIONS)
        execute_values(cursor, "INSERT INTO Employee (EmployeeID, DistrictID, UnitID, RankID, DesignationID, KGID, FirstName, EmployeeDOB, GenderID, BloodGroupID, PhysicallyChallenged, AppointmentDate) VALUES %s", EMPLOYEES)
        execute_values(cursor, "INSERT INTO CasteMaster (caste_master_id, caste_master_name) VALUES %s", CASTES)
        execute_values(cursor, "INSERT INTO ReligionMaster (ReligionID, ReligionName) VALUES %s", RELIGIONS)
        execute_values(cursor, "INSERT INTO OccupationMaster (OccupationID, OccupationName) VALUES %s", OCCUPATIONS)
        execute_values(cursor, "INSERT INTO CaseCategory (CaseCategoryID, LookupValue) VALUES %s", CASE_CATEGORIES)
        execute_values(cursor, "INSERT INTO GravityOffence (GravityOffenceID, LookupValue) VALUES %s", GRAVITY_OFFENCES)
        execute_values(cursor, "INSERT INTO CaseStatusMaster (CaseStatusID, CaseStatusName) VALUES %s", CASE_STATUSES)
        
        print("Seeding crimes, acts and sections...")
        execute_values(cursor, "INSERT INTO CrimeHead (CrimeHeadID, CrimeGroupName, Active) VALUES %s", CRIME_HEADS)
        execute_values(cursor, "INSERT INTO CrimeSubHead (CrimeSubHeadID, CrimeHeadID, CrimeHeadName, SeqID) VALUES %s", CRIME_SUB_HEADS)
        execute_values(cursor, "INSERT INTO Act (ActCode, ActDescription, ShortName, Active) VALUES %s", ACTS)
        execute_values(cursor, "INSERT INTO Section (ActCode, SectionCode, SectionDescription, Active) VALUES %s", SECTIONS)
        execute_values(cursor, "INSERT INTO CrimeHeadActSection (CrimeHeadID, ActCode, SectionCode) VALUES %s", CRIME_HEAD_SECTIONS)
        
        print("Seeding transactional KSP cases...")
        execute_values(cursor, "INSERT INTO CaseMaster (CaseMasterID, CrimeNo, CaseNo, CrimeRegisteredDate, PolicePersonID, PoliceStationID, CaseCategoryID, GravityOffenceID, CrimeMajorHeadID, CrimeMinorHeadID, CaseStatusID, CourtID, IncidentFromDate, IncidentToDate, InfoReceivedPSDate, latitude, longitude, BriefFacts) VALUES %s", CASE_MASTERS)
        execute_values(cursor, "INSERT INTO ComplainantDetails (ComplainantID, CaseMasterID, ComplainantName, AgeYear, OccupationID, ReligionID, CasteID, GenderID) VALUES %s", COMPLAINANTS)
        execute_values(cursor, "INSERT INTO Victim (VictimMasterID, CaseMasterID, VictimName, AgeYear, GenderID, VictimPolice) VALUES %s", VICTIMS)
        execute_values(cursor, "INSERT INTO Accused (AccusedMasterID, CaseMasterID, AccusedName, AgeYear, GenderID, PersonID) VALUES %s", ACCUSED)
        execute_values(cursor, "INSERT INTO ActSectionAssociation (CaseMasterID, ActCode, SectionCode, ActOrderID, SectionOrderID) VALUES %s", ACT_SECTION_ASSOCS)
        execute_values(cursor, "INSERT INTO ArrestSurrender (ArrestSurrenderID, CaseMasterID, ArrestSurrenderTypeID, ArrestSurrenderDate, ArrestSurrenderStateId, ArrestSurrenderDistrictId, PoliceStationID, IOID, CourtID, AccusedMasterID, IsAccused, IsComplainantAccused) VALUES %s", ARREST_EVENTS)
        execute_values(cursor, "INSERT INTO ChargesheetDetails (CSID, CaseMasterID, csdate, cstype, PolicePersonID) VALUES %s", CHARGESHEETS)
        
        conn.commit()
        print("Synthetic KSP crime database records seeded successfully.")
        
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error seeding database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    seed_database()
    print("Database seeding process completed.")
