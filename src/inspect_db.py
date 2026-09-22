import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables manually since it uses colon-separated format
env_vars = {}
if os.path.exists(".env"):
    with open(".env", "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if ":" in line:
                key, val = line.split(":", 1)
            elif "=" in line:
                key, val = line.split("=", 1)
            else:
                continue
            env_vars[key.strip()] = val.strip()

# Get connection parameters from environment
db_host = env_vars.get("IP")
db_name = env_vars.get("DB")
db_user = env_vars.get("USER")
db_password = env_vars.get("PWD")

print(f"Connecting to host: {db_host}, db: {db_name}, user: {db_user}...")

try:
    conn = psycopg2.connect(
        host=db_host,
        database=db_name,
        user=db_user,
        password=db_password,
        port=5432
    )
    cursor = conn.cursor()
    
    # Query to list all schemas, tables, and columns (excluding system schemas)
    query = """
        SELECT 
            table_schema, 
            table_name, 
            column_name, 
            data_type, 
            is_nullable
        FROM 
            information_schema.columns
        WHERE 
            table_schema NOT IN ('pg_catalog', 'information_schema')
        ORDER BY 
            table_schema, 
            table_name, 
            ordinal_position;
    """
    
    cursor.execute(query)
    rows = cursor.fetchall()
    
    if not rows:
        print("No user tables/columns found in the database.")
    else:
        # Organize the output
        db_structure = {}
        for schema, table, column, data_type, is_nullable in rows:
            if schema not in db_structure:
                db_structure[schema] = {}
            if table not in db_structure[schema]:
                db_structure[schema][table] = []
            db_structure[schema][table].append((column, data_type, is_nullable))
            
        # Ensure output directory exists
        os.makedirs("output", exist_ok=True)
        # Write to output/schema_dump.md
        with open("output/schema_dump.md", "w", encoding="utf-8") as f:
            f.write("# Database Schema Dump\n\n")
            f.write(f"Connected to Host: `{db_host}` | Database: `{db_name}`\n\n")
            
            for schema, tables in db_structure.items():
                f.write(f"## Schema: `{schema}`\n\n")
                for table, columns in tables.items():
                    f.write(f"### Table: `{table}`\n")
                    f.write("| Column | Data Type | Nullable |\n")
                    f.write("| --- | --- | --- |\n")
                    for col, dtype, nullable in columns:
                        f.write(f"| `{col}` | `{dtype}` | `{nullable}` |\n")
                    f.write("\n")
                    
        total_schemas = len(db_structure)
        total_tables = sum(len(tables) for tables in db_structure.values())
        print(f"Inspection complete. Found {total_schemas} schema(s) and {total_tables} table(s).")
        print("Schema details saved to output/schema_dump.md.")
                    
    cursor.close()
    conn.close()
except Exception as e:
    print(f"Error connecting to database: {e}")
