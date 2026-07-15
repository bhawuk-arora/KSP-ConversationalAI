# KSP Crime Intelligence Platform - CSV Bulk Importer Script
# Highly optimized bulk import using PostgreSQL COPY protocol.

import os
import sys
import subprocess
import time

# Ensure psycopg2-binary is installed
try:
    import psycopg2
except ImportError:
    print("psycopg2 not found. Installing psycopg2-binary dynamically...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "psycopg2-binary"])
    import psycopg2

# Database connection credentials
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = os.environ.get("DB_PORT", "5432")
DB_USER = os.environ.get("DB_USER", "postgres")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "postgres")
DB_NAME = os.environ.get("DB_NAME", "ksp_db")

RAW_DATA_DIR = os.path.join(os.path.dirname(__file__), "raw_data")

# Topological order of tables to prevent constraint violations
TABLES_IMPORT_ORDER = [
    ("State", "State.csv"),
    ("UnitType", "UnitType.csv"),
    ("Rank", "Rank.csv"),
    ("Designation", "Designation.csv"),
    ("CasteMaster", "CasteMaster.csv"),
    ("ReligionMaster", "ReligionMaster.csv"),
    ("OccupationMaster", "OccupationMaster.csv"),
    ("CaseCategory", "CaseCategory.csv"),
    ("GravityOffence", "GravityOffence.csv"),
    ("CaseStatusMaster", "CaseStatusMaster.csv"),
    ("CrimeHead", "CrimeHead.csv"),
    ("Act", "Act.csv"),
    ("District", "District.csv"),
    ("Section", "Section.csv"),
    ("CrimeSubHead", "CrimeSubHead.csv"),
    ("CrimeHeadActSection", "CrimeHeadActSection.csv"),
    ("Court", "Court.csv"),
    ("Unit", "Unit.csv"),
    ("Employee", "Employee.csv"),
    ("CaseMaster", "CaseMaster.csv"),
    ("ComplainantDetails", "ComplainantDetails.csv"),
    ("Victim", "Victim.csv"),
    ("Accused", "Accused.csv"),
    ("ActSectionAssociation", "ActSectionAssociation.csv"),
    ("ArrestSurrender", "ArrestSurrender.csv"),
    ("ChargesheetDetails", "ChargesheetDetails.csv")
]

def import_all_data():
    """Bulk imports all 26 CSV files into PostgreSQL in topological order."""
    start_time = time.time()
    print(f"Connecting to database '{DB_NAME}' for bulk import...")
    
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            dbname=DB_NAME
        )
        cursor = conn.cursor()
        
        # 1. Attempt to disable constraint checks during bulk COPY for performance & safety
        disable_triggers = False
        try:
            cursor.execute("SET session_replication_role = 'replica';")
            disable_triggers = True
            print("Session replication role set to 'replica' (Triggers/FKs temporarily bypassed for copying).")
        except Exception:
            conn.rollback()
            print("[WARNING] Could not set session_replication_role to replica (requires superuser). Loading with standard FK checks.")
        
        # 2. Iterate and import each table
        for table_name, csv_filename in TABLES_IMPORT_ORDER:
            csv_path = os.path.join(RAW_DATA_DIR, csv_filename)
            if not os.path.exists(csv_path):
                print(f"[ERROR] CSV file not found at {csv_path}. Skipping.")
                continue
                
            print(f"Importing {csv_filename} into table '{table_name}'...")
            table_start = time.time()
            
            with open(csv_path, "r", encoding="utf-8") as f:
                # Get headers to explicitly list columns
                header_line = f.readline().strip()
                columns = header_line.split(",")
                columns_str = ", ".join([f'"{col}"' for col in columns])
                
                # Reset file read cursor back to beginning
                f.seek(0)
                
                # Execute COPY protocol
                copy_query = f"COPY {table_name} ({columns_str}) FROM STDIN WITH CSV HEADER"
                cursor.copy_expert(copy_query, f)
                
            # Log row counts
            cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
            count = cursor.fetchone()[0]
            print(f"  -> Imported successfully. Total rows in '{table_name}': {count} (Took {time.time() - table_start:.2f}s)")
            
        # 3. Restore replication role
        if disable_triggers:
            cursor.execute("SET session_replication_role = 'origin';")
            print("Session replication role restored to 'origin'.")
            
        conn.commit()
        print(f"\n[SUCCESS] Bulk import completed successfully in {time.time() - start_time:.2f} seconds.")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"\n[FATAL ERROR] Bulk import failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    import_all_data()
