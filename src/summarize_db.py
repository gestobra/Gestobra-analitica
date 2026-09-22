import os
import psycopg2

# Load environment variables manually
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

db_host = env_vars.get("IP")
db_name = env_vars.get("DB")
db_user = env_vars.get("USER")
db_password = env_vars.get("PWD")

try:
    conn = psycopg2.connect(
        host=db_host,
        database=db_name,
        user=db_user,
        password=db_password,
        port=5432
    )
    cursor = conn.cursor()
    
    # 1. Get list of tables in public schema
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
        ORDER BY table_name;
    """)
    tables = [row[0] for row in cursor.fetchall()]
    
    print(f"Found {len(tables)} tables. Querying row counts and column counts...")
    
    summary = []
    for table in tables:
        # Get column count
        cursor.execute(f"""
            SELECT COUNT(*) 
            FROM information_schema.columns 
            WHERE table_schema = 'public' AND table_name = %s;
        """, (table,))
        col_count = cursor.fetchone()[0]
        
        # Get row count (using a try/except in case of permissions or locks, though we should have read access)
        try:
            cursor.execute(f'SELECT COUNT(*) FROM "public"."{table}";')
            row_count = cursor.fetchone()[0]
        except Exception as e:
            conn.rollback()
            row_count = "N/A (Error)"
            
        summary.append((table, col_count, row_count))
        
    # Sort tables by row count (descending) if numeric, otherwise put N/A at the bottom
    def sort_key(item):
        val = item[2]
        if isinstance(val, int):
            return (0, -val)
        return (1, val)
        
    summary.sort(key=sort_key)
    
    # Ensure output directory exists
    os.makedirs("output", exist_ok=True)
    
    # Write to a file
    with open("output/table_summary.md", "w", encoding="utf-8") as f:
        f.write("# Database Tables Summary\n\n")
        f.write("| Table Name | Columns | Row Count |\n")
        f.write("| --- | --- | --- |\n")
        for table, cols, rows in summary:
            f.write(f"| `{table}` | {cols} | {rows} |\n")
            
    print("Summary written to output/table_summary.md.")
    
    cursor.close()
    conn.close()
except Exception as e:
    print(f"Error: {e}")
