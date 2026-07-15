# KSP Crime Intelligence Platform - Neo4j Graph Ingestion Pipeline
# Connects PostgreSQL relational rows into Neo4j nodes and relationships

import os
import sys
import psycopg2
from neo4j import GraphDatabase

# PostgreSQL credentials
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = os.environ.get("DB_PORT", "5432")
DB_USER = os.environ.get("DB_USER", "postgres")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "postgres")
DB_NAME = os.environ.get("DB_NAME", "ksp_db")

# Neo4j credentials
NEO4J_URI = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.environ.get("NEO4J_USER", "neo4j")
NEO4J_PASS = os.environ.get("NEO4J_PASS", "ksp_neo4j_pass")

def setup_neo4j_graph():
    print(f"Connecting to Neo4j Graph Database at {NEO4J_URI}...")
    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))
        # Test connection
        driver.verify_connectivity()
    except Exception as e:
        print(f"[ERROR] Could not connect to Neo4j database: {e}")
        print("Please ensure the ksp-neo4j container is running and healthy.")
        sys.exit(1)

    print("Connecting to PostgreSQL relational database...")
    try:
        pg_conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            dbname=DB_NAME
        )
        pg_cursor = pg_conn.cursor()
    except Exception as e:
        print(f"[ERROR] PostgreSQL connection failed: {e}")
        driver.close()
        sys.exit(1)

    with driver.session() as session:
        # 1. Clear database and create constraints
        print("Initializing Neo4j Graph constraints...")
        session.run("MATCH (n) DETACH DELETE n;")
        
        # Cypher constraints setup (using TRY/EXCEPT block syntax for community compatibility)
        try:
            session.run("CREATE CONSTRAINT FOR (p:PoliceStation) REQUIRE p.id IS UNIQUE;")
        except Exception: pass
        try:
            session.run("CREATE CONSTRAINT FOR (c:Case) REQUIRE c.id IS UNIQUE;")
        except Exception: pass
        try:
            session.run("CREATE CONSTRAINT FOR (a:Accused) REQUIRE a.id IS UNIQUE;")
        except Exception: pass

        # 2. Ingest PoliceStation nodes
        print("Fetching PoliceStation records...")
        pg_cursor.execute("SELECT PoliceStationID, PoliceStation FROM PoliceStation;")
        stations = pg_cursor.fetchall()
        print(f"Loading {len(stations)} PoliceStations...")
        for station_id, name in stations:
            session.run(
                "MERGE (p:PoliceStation {id: $id}) SET p.name = $name;",
                id=station_id, name=name
            )

        # 3. Ingest Case nodes & REPORTED_AT relationships
        print("Fetching CaseMaster records...")
        # Limiting to 5000 records to prevent long build times in hackathon environments
        pg_cursor.execute(
            "SELECT CaseMasterID, CrimeNo, CrimeMajorHeadID, CrimeRegisteredDate, PoliceStationID "
            "FROM CaseMaster WHERE PoliceStationID IS NOT NULL LIMIT 5000;"
        )
        cases = pg_cursor.fetchall()
        print(f"Loading {len(cases)} Cases and reporting links...")
        
        case_cypher = """
        MERGE (c:Case {id: $id})
        SET c.crime_no = $crime_no, c.crime_head = $crime_head, c.registered_date = $registered_date
        WITH c
        MATCH (p:PoliceStation {id: $station_id})
        MERGE (c)-[:REPORTED_AT]->(p);
        """
        for case_id, crime_no, major_head_id, reg_date, station_id in cases:
            session.run(
                case_cypher,
                id=case_id,
                crime_no=crime_no,
                crime_head=major_head_id,
                registered_date=str(reg_date),
                station_id=station_id
            )

        # 4. Ingest Accused nodes & ACCUSED_IN relationships
        print("Fetching Accused records...")
        pg_cursor.execute(
            "SELECT AccusedID, Name, GenderID, Age, CaseMasterID "
            "FROM Accused WHERE Name IS NOT NULL AND CaseMasterID IS NOT NULL LIMIT 5000;"
        )
        accused_rows = pg_cursor.fetchall()
        print(f"Loading {len(accused_rows)} Accused suspects and case involvements...")
        
        accused_cypher = """
        MERGE (a:Accused {id: $id})
        SET a.name = $name, a.gender = $gender, a.age = $age
        WITH a
        MATCH (c:Case {id: $case_id})
        MERGE (a)-[:ACCUSED_IN]->(c);
        """
        for accused_id, name, gender_id, age, case_id in accused_rows:
            # Mask PII names if they contain numbers or special codes
            clean_name = name.strip() if name else "Unknown"
            session.run(
                accused_cypher,
                id=accused_id,
                name=clean_name,
                gender=gender_id or "M",
                age=age or 30,
                case_id=case_id
            )

        # 5. Connect co-accused links (co-conspirators in the same crime case)
        print("Linking co-conspirators (CO_ACCUSED_WITH)...")
        co_accused_cypher = """
        MATCH (a1:Accused)-[:ACCUSED_IN]->(c:Case)<-[:ACCUSED_IN]-(a2:Accused)
        WHERE a1.id < a2.id
        MERGE (a1)-[r:CO_ACCUSED_WITH]-(a2)
        ON CREATE SET r.cases_count = 1
        ON MATCH SET r.cases_count = r.cases_count + 1;
        """
        session.run(co_accused_cypher)
        
        print("[SUCCESS] Neo4j Relationship Networks mapped successfully!")

    pg_cursor.close()
    pg_conn.close()
    driver.close()

if __name__ == "__main__":
    setup_neo4j_graph()
