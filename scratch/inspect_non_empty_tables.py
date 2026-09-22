import os
import json
import psycopg2

config = {}
with open('.env', 'r') as f:
    for line in f:
        if ':' in line:
            parts = line.strip().split(':', 1)
            config[parts[0].strip()] = parts[1].strip()

conn = psycopg2.connect(
    host=config.get('IP'),
    database=config.get('DB'),
    user=config.get('USER'),
    password=config.get('PWD')
)
cursor = conn.cursor()

cursor.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
    ORDER BY table_name;
""")
tables = [r[0] for r in cursor.fetchall()]

non_empty_tables = {}
table_schemas = {}

for t in tables:
    try:
        cursor.execute(f'SELECT COUNT(*) FROM "{t}"')
        cnt = cursor.fetchone()[0]
        if cnt > 0:
            non_empty_tables[t] = cnt
            cursor.execute("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_schema = 'public' AND table_name = %s
                ORDER BY ordinal_position;
            """, (t,))
            cols = cursor.fetchall()
            table_schemas[t] = [
                {"name": c[0], "type": c[1], "nullable": c[2]} for c in cols
            ]
    except Exception as e:
        print(f"Error checking {t}: {e}")

cursor.close()
conn.close()

result = {
    "counts": non_empty_tables,
    "schemas": table_schemas
}

with open("scratch/non_empty_tables.json", "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2, ensure_ascii=False)

print(f"Found {len(non_empty_tables)} non-empty tables out of {len(tables)}:")
for t, cnt in non_empty_tables.items():
    print(f"  - {t}: {cnt} rows")
