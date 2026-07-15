# KSP Crime Intelligence Platform - Database Initial Setup Script
# Automatically ensures dependencies and initializes schema

import os
import sys
import subprocess

# Ensure psycopg2-binary is installed
try:
    import psycopg2
    from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
except ImportError:
    print("psycopg2 not found. Installing psycopg2-binary dynamically...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "psycopg2-binary"])
    import psycopg2
    from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Database credentials (overrideable via environment variables)
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = os.environ.get("DB_PORT", "5432")
DB_USER = os.environ.get("DB_USER", "postgres")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "postgres")
DB_NAME = os.environ.get("DB_NAME", "ksp_db")

def create_database():
    """Connects to default postgres database to create ksp_db if it doesn't exist."""
    print(f"Connecting to database server at {DB_HOST}:{DB_PORT} as user '{DB_USER}'...")
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            dbname="postgres"
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s;", (DB_NAME,))
        exists = cursor.fetchone()
        
        if not exists:
            print(f"Database '{DB_NAME}' does not exist. Creating...")
            cursor.execute(f"CREATE DATABASE {DB_NAME};")
            print(f"Database '{DB_NAME}' created successfully.")
        else:
            print(f"Database '{DB_NAME}' already exists.")
            
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error checking/creating database: {e}")
        print("Please verify your PostgreSQL server is running and credentials are correct.")
        sys.exit(1)

def run_schema_file():
    """Connects to ksp_db and runs schema.sql DDL script."""
    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    if not os.path.exists(schema_path):
        print(f"Schema file not found at {schema_path}")
        sys.exit(1)
        
    print(f"Executing DDL schema from {schema_path} on database '{DB_NAME}'...")
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            dbname=DB_NAME
        )
        cursor = conn.cursor()
        
        with open(schema_path, "r", encoding="utf-8") as f:
            schema_sql = f.read()
            
        # Clean existing tables/types to prevent relation collision errors
        cursor.execute("DROP SCHEMA public CASCADE; CREATE SCHEMA public; CREATE EXTENSION IF NOT EXISTS postgis;")
        cursor.execute(schema_sql)
        conn.commit()
        print("Schema tables, constraints, extensions, and indexes initialized successfully.")
        
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error executing schema DDL: {e}")
        sys.exit(1)

if __name__ == "__main__":
    create_database()
    run_schema_file()
    print("Database setup complete.")
