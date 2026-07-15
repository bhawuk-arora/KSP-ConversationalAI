# KSP Crime Intelligence Platform - CSV and SQL Schema Alignment Checker
# Scans all CSV files in database/raw_data and flags data type alignment issues.

import os
import re
import csv

RAW_DATA_DIR = "database/raw_data"
SCHEMA_FILE = "database/schema.sql"

# Simple mapping of SQL data types to Python validation types
SQL_TYPE_MAP = {
    "int": int,
    "serial": int,
    "integer": int,
    "decimal": float,
    "numeric": float,
    "double": float,
    "boolean": bool,
    "date": str,
    "timestamp": str,
    "varchar": str,
    "char": str,
    "text": str,
    "bit": int
}

def parse_sql_schema():
    """Parses schema.sql to extract table names and column names with their data types."""
    tables = {}
    current_table = None
    
    with open(SCHEMA_FILE, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Remove SQL comments
    content = re.sub(r'--.*', '', content)
    
    # Match CREATE TABLE blocks
    table_matches = re.finditer(r'CREATE\s+TABLE\s+(\w+)\s*\((.*?)\);', content, re.DOTALL | re.IGNORECASE)
    
    for match in table_matches:
        table_name = match.group(1).lower()
        column_defs = match.group(2)
        columns = {}
        
        # Split column definitions
        for line in column_defs.split('\n'):
            line = line.strip()
            if not line or line.upper().startswith(('PRIMARY', 'FOREIGN', 'CONSTRAINT', 'CHECK', 'UNIQUE')):
                continue
            
            parts = line.split()
            if len(parts) >= 2:
                col_name = parts[0].strip('"').strip('`').strip(',').strip(';').lower()
                col_type = parts[1].split('(')[0].strip(',').strip(';').lower()
                columns[col_name] = col_type
                
        tables[table_name] = columns
        
    return tables

def check_csv_files(sql_schema):
    """Checks each CSV file in database/raw_data against parsed SQL schema."""
    print("=== Diagnostic: Verifying CSV Data Fit with DDL Schema ===")
    
    for filename in sorted(os.listdir(RAW_DATA_DIR)):
        if not filename.endswith(".csv"):
            continue
            
        table_name = filename[:-4].lower()
        csv_path = os.path.join(RAW_DATA_DIR, filename)
        
        if table_name not in sql_schema:
            print(f"[WARNING] CSV file '{filename}' does not have a matching table in schema.sql")
            continue
            
        sql_cols = sql_schema[table_name]
        
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            headers = next(reader)
            first_row = next(reader, None)
            
        csv_cols = [h.lower() for h in headers]
        
        # Check column mismatches
        missing_in_sql = [c for c in csv_cols if c not in sql_cols]
        missing_in_csv = [c for c in sql_cols if c not in csv_cols and not sql_cols[c].startswith("serial")]
        
        if missing_in_sql:
            print(f"[MISMATCH] Table '{table_name}': Columns in CSV but missing in SQL schema: {missing_in_sql}")
        if missing_in_csv:
            print(f"[MISMATCH] Table '{table_name}': Columns in SQL schema but missing in CSV: {missing_in_csv}")
            
        # Check specific data values from the first row to spot type issues
        if first_row:
            for idx, val in enumerate(first_row):
                col_name = csv_cols[idx]
                if col_name in sql_cols:
                    sql_type = sql_cols[col_name]
                    # Check if integer column has non-numeric characters
                    if sql_type in ["int", "integer"] and val:
                        try:
                            int(val)
                        except ValueError:
                            print(f"[TYPE ALERT] Table '{table_name}', Column '{col_name}': Defined as '{sql_type}' in SQL, but CSV contains string value '{val}'")
                            
                    # Check if decimal column has non-numeric characters
                    elif sql_type in ["decimal", "numeric"] and val:
                        try:
                            float(val)
                        except ValueError:
                            print(f"[TYPE ALERT] Table '{table_name}', Column '{col_name}': Defined as '{sql_type}' in SQL, but CSV contains non-numeric '{val}'")
                            
                    # Check if date/timestamp columns are formatted
                    elif sql_type in ["date", "timestamp"] and val:
                        if not val.replace("-", "").replace(":", "").replace(" ", "").isdigit():
                            # Simple sanity check
                            pass

if __name__ == "__main__":
    schema_map = parse_sql_schema()
    check_csv_files(schema_map)
