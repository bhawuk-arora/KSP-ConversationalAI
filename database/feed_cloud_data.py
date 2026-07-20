import os, sys, subprocess, time

def ensure_package(pkg, import_name=None):
    import_name = import_name or pkg
    try: __import__(import_name)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg, "-q"])

ensure_package("psycopg2-binary", "psycopg2")
ensure_package("neo4j")

import psycopg2
from neo4j import GraphDatabase

DATABASE_URL = "postgresql://neondb_owner:npg_o7QjMaed3fxA@ep-holy-credit-aw6zey5m.c-12.us-east-1.aws.neon.tech/neondb?sslmode=require"
NEO4J_URI    = "neo4j+s://c54cb456.databases.neo4j.io"
NEO4J_USER   = "c54cb456"
NEO4J_PASS   = "fO3h9T_ZYFxN28V95WY2DL5JUEsptFd-Y0no5DDkBiA"

BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
SCHEMA_FILE  = os.path.join(BASE_DIR, "schema.sql")
RAW_DATA_DIR = os.path.join(BASE_DIR, "raw_data")

# Table names unquoted so PostgreSQL matches them case-insensitively
TABLES_IMPORT_ORDER = [
    ("State","State.csv"),("UnitType","UnitType.csv"),("Rank","Rank.csv"),
    ("Designation","Designation.csv"),("CasteMaster","CasteMaster.csv"),
    ("ReligionMaster","ReligionMaster.csv"),("OccupationMaster","OccupationMaster.csv"),
    ("CaseCategory","CaseCategory.csv"),("GravityOffence","GravityOffence.csv"),
    ("CaseStatusMaster","CaseStatusMaster.csv"),("CrimeHead","CrimeHead.csv"),
    ("Act","Act.csv"),("District","District.csv"),("Section","Section.csv"),
    ("CrimeSubHead","CrimeSubHead.csv"),("CrimeHeadActSection","CrimeHeadActSection.csv"),
    ("Court","Court.csv"),("Unit","Unit.csv"),("Employee","Employee.csv"),
    ("CaseMaster","CaseMaster.csv"),("ComplainantDetails","ComplainantDetails.csv"),
    ("Victim","Victim.csv"),("Accused","Accused.csv"),
    ("ActSectionAssociation","ActSectionAssociation.csv"),
    ("ArrestSurrender","ArrestSurrender.csv"),("ChargesheetDetails","ChargesheetDetails.csv"),
]

print("\n=== STEP 1: NeonDB Schema Setup ===")
conn = psycopg2.connect(DATABASE_URL)
conn.autocommit = True
cur = conn.cursor()
try:
    cur.execute("CREATE EXTENSION IF NOT EXISTS postgis;")
    print("PostGIS enabled.")
except Exception as e:
    print(f"PostGIS skip: {e}")
conn.autocommit = False
cur.execute("DROP SCHEMA public CASCADE; CREATE SCHEMA public;")
try: cur.execute("CREATE EXTENSION IF NOT EXISTS postgis;")
except: pass
with open(SCHEMA_FILE,"r",encoding="utf-8") as f: cur.execute(f.read())
conn.commit(); cur.close(); conn.close()
print("Schema ready!")

# Verify actual table names in DB
print("Verifying table names in DB...")
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()
cur.execute("SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename;")
db_tables = {row[0] for row in cur.fetchall()}
print(f"Found tables: {sorted(db_tables)}")
cur.close(); conn.close()

print("\n=== STEP 2: CSV Import to NeonDB ===")
t0 = time.time()
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()
for table, csv_file in TABLES_IMPORT_ORDER:
    path = os.path.join(RAW_DATA_DIR, csv_file)
    if not os.path.exists(path):
        print(f"  SKIP {csv_file} (file not found)"); continue
    # Find matching table name (case-insensitive)
    match = next((t for t in db_tables if t.lower() == table.lower()), None)
    if not match:
        print(f"  SKIP {csv_file} (no table matching '{table}' found in DB)"); continue
    print(f"  {csv_file} -> {match}...", end=" ", flush=True)
    t1 = time.time()
    try:
        with open(path,"r",encoding="utf-8") as f:
            header = f.readline().strip()
            cols = ", ".join([c.strip().lower() for c in header.split(",")])
            f.seek(0)
            # Use unquoted table name so it matches the lowercase stored name
            cur.copy_expert(f"COPY {match} ({cols}) FROM STDIN WITH CSV HEADER", f)
        cur.execute(f"SELECT COUNT(*) FROM {match};")
        n = cur.fetchone()[0]
        print(f"{n:,} rows ({time.time()-t1:.1f}s)")
    except Exception as e:
        conn.rollback()
        print(f"ERROR: {e}")
        continue
conn.commit(); cur.close(); conn.close()
print(f"All CSVs imported in {time.time()-t0:.1f}s!")

print("\n=== STEP 3: Neo4j Aura Graph Population ===")
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))
driver.verify_connectivity()
print("Neo4j connected!")
pg = psycopg2.connect(DATABASE_URL)
pgc = pg.cursor()
with driver.session() as s:
    print("Clearing graph and setting constraints...")
    s.run("MATCH (n) DETACH DELETE n;")
    for q in [
        "CREATE CONSTRAINT IF NOT EXISTS FOR (p:PoliceStation) REQUIRE p.id IS UNIQUE;",
        "CREATE CONSTRAINT IF NOT EXISTS FOR (c:Case) REQUIRE c.id IS UNIQUE;",
        "CREATE CONSTRAINT IF NOT EXISTS FOR (a:Accused) REQUIRE a.id IS UNIQUE;",
        "CREATE CONSTRAINT IF NOT EXISTS FOR (d:District) REQUIRE d.id IS UNIQUE;",
    ]:
        try: s.run(q)
        except: pass

    # District nodes
    pgc.execute("SELECT districtid, districtname FROM district;")
    rows = pgc.fetchall()
    for did, dname in rows:
        s.run("MERGE (d:District {id:$id}) SET d.name=$name;", id=did, name=dname)
    print(f"Districts: {len(rows)} loaded")

    # PoliceStation nodes
    pgc.execute("SELECT unitid, unitname, districtid FROM unit;")
    rows = pgc.fetchall()
    for uid, uname, did in rows:
        s.run(
            "MERGE (p:PoliceStation {id:$id}) SET p.name=$name "
            "WITH p MATCH (d:District {id:$did}) MERGE (p)-[:BELONGS_TO]->(d);",
            id=uid, name=uname, did=did
        )
    print(f"PoliceStations: {len(rows)} loaded")

    # Case nodes (up to 10k)
    pgc.execute(
        "SELECT casemasterid, crimeno, crimemajorheadid, crimeregistereddate, policestation "
        "FROM casemaster WHERE policestation IS NOT NULL LIMIT 10000;"
    )
    cases = pgc.fetchall()
    for cid, cno, mhid, rdate, sid in cases:
        try:
            s.run(
                "MERGE (c:Case {id:$id}) SET c.crime_no=$cn, c.crime_head=$ch, c.registered_date=$rd "
                "WITH c MATCH (p:PoliceStation {id:$sid}) MERGE (c)-[:REPORTED_AT]->(p);",
                id=cid, cn=str(cno or ""), ch=str(mhid or ""), rd=str(rdate or ""), sid=sid
            )
        except: pass
    print(f"Cases: {len(cases)} loaded")

    # Accused nodes (up to 10k)
    pgc.execute(
        "SELECT accusedmasterid, accusedname, genderid, ageyear, casemasterid "
        "FROM accused WHERE accusedname IS NOT NULL AND casemasterid IS NOT NULL LIMIT 10000;"
    )
    accused = pgc.fetchall()
    for aid, aname, gid, age, cid in accused:
        try:
            s.run(
                "MERGE (a:Accused {id:$id}) SET a.name=$name, a.gender=$gender, a.age=$age "
                "WITH a MATCH (c:Case {id:$cid}) MERGE (a)-[:ACCUSED_IN]->(c);",
                id=aid, name=(aname.strip() if aname else "Unknown"),
                gender=str(gid or "M"), age=int(age or 30), cid=cid
            )
        except: pass
    print(f"Accused: {len(accused)} loaded")

    # Co-accused relationships
    print("Building CO_ACCUSED_WITH links...", end=" ", flush=True)
    s.run(
        "MATCH (a1:Accused)-[:ACCUSED_IN]->(c:Case)<-[:ACCUSED_IN]-(a2:Accused) "
        "WHERE a1.id < a2.id "
        "MERGE (a1)-[r:CO_ACCUSED_WITH]-(a2) "
        "ON CREATE SET r.cases_count=1 ON MATCH SET r.cases_count=r.cases_count+1;"
    )
    print("done")

pgc.close(); pg.close(); driver.close()
print("\n ALL DONE!")
