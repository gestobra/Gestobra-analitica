import os
import yaml

base_dir = "dbt_gestobra"

# 1. Create profiles.yml template
profiles_yaml = {
    "gestobra": {
        "target": "dev",
        "outputs": {
            "dev": {
                "type": "postgres",
                "host": "{{ env_var('DBT_HOST', 'app.gestobra.com') }}",
                "user": "{{ env_var('DBT_USER', 'gestobra_user') }}",
                "pass": "{{ env_var('DBT_PASSWORD', 'T5FJvlpdg9OzJKd') }}",
                "port": 5432,
                "dbname": "gestobra",
                "schema": "analytics",
                "threads": 4
            }
        }
    }
}

with open(os.path.join(base_dir, "profiles.yml"), "w", encoding="utf-8") as f:
    yaml.dump(profiles_yaml, f, default_flow_style=False, sort_keys=False)

# 2. Staging models for key domain entities
staging_models = {
    "stg_projects": """
with source as (
    select * from {{ source('gestobra_public', 'projects') }}
),
renamed as (
    select
        id as project_id,
        team_id,
        company_id,
        name as project_name,
        description,
        status,
        created_at,
        updated_at,
        deleted_at
    from source
)
select * from renamed
""",
    "stg_people": """
with source as (
    select * from {{ source('gestobra_public', 'people') }}
),
renamed as (
    select
        id as person_id,
        team_id,
        user_id,
        name as person_name,
        email as person_email,
        phone as person_phone,
        cargo_id,
        is_worker,
        is_client,
        is_supplier,
        created_at,
        updated_at
    from source
)
select * from renamed
""",
    "stg_users": """
with source as (
    select * from {{ source('gestobra_public', 'users') }}
),
renamed as (
    select
        id as user_id,
        name as user_name,
        email as user_email,
        phone as user_phone,
        created_at,
        updated_at
    from source
)
select * from renamed
""",
    "stg_companies": """
with source as (
    select * from {{ source('gestobra_public', 'companies') }}
),
renamed as (
    select
        id as company_id,
        name as client_name,
        tax_id,
        phone,
        email,
        created_at
    from source
)
select * from renamed
""",
    "stg_time_clock_records": """
with source as (
    select * from {{ source('gestobra_public', 'time_clock_records') }}
),
renamed as (
    select
        id as time_clock_id,
        user_id,
        team_id,
        record_type,
        clock_time,
        created_at
    from source
)
select * from renamed
""",
    "stg_project_imputations": """
with source as (
    select * from {{ source('gestobra_public', 'project_imputations') }}
),
renamed as (
    select
        id as imputation_id,
        project_id,
        user_id,
        task_id,
        hours_imputed,
        date as imputation_date,
        created_at
    from source
)
select * from renamed
""",
    "stg_messages": """
with source as (
    select * from {{ source('gestobra_public', 'messages') }}
),
renamed as (
    select
        id as message_id,
        user_id,
        team_id,
        person_id,
        contact_name,
        channel,
        direction,
        type as message_type,
        created_at
    from source
)
select * from renamed
""",
    "stg_daily_sessions": """
with source as (
    select * from {{ source('gestobra_public', 'daily_sessions') }}
),
renamed as (
    select
        id as session_id,
        user_id,
        session_date,
        state,
        started_at,
        finished_at
    from source
)
select * from renamed
"""
}

for name, sql in staging_models.items():
    with open(os.path.join(base_dir, "models", "staging", f"{name}.sql"), "w", encoding="utf-8") as f:
        f.write(sql.strip() + "\n")

# 3. Core Mart Models (Dimensions and Facts)
marts_models = {
    "dim_projects": """
with projects as (
    select * from {{ ref('stg_projects') }}
),
companies as (
    select * from {{ ref('stg_companies') }}
)
select
    p.project_id,
    p.project_name,
    coalesce(c.client_name, 'Gestobra') as client_name,
    p.status,
    p.created_at
from projects p
left join companies c on p.company_id = c.company_id
""",
    "dim_people": """
with people as (
    select * from {{ ref('stg_people') }}
),
users as (
    select * from {{ ref('stg_users') }}
)
select
    p.person_id,
    p.user_id,
    coalesce(p.person_name, u.user_name, 'Sin Nombre') as person_name,
    coalesce(p.person_email, u.user_email) as person_email,
    p.is_worker,
    p.is_client
from people p
left join users u on p.user_id = u.user_id
""",
    "fact_project_imputation": """
with imputations as (
    select * from {{ ref('stg_project_imputations') }}
),
projects as (
    select * from {{ ref('dim_projects') }}
),
people as (
    select * from {{ ref('dim_people') }}
)
select
    i.imputation_id,
    i.imputation_date as date,
    i.project_id,
    p.project_name,
    p.client_name,
    i.user_id,
    pe.person_id,
    pe.person_name,
    i.hours_imputed,
    round(i.hours_imputed * 20.0, 2) as calculated_cost
from imputations i
left join projects p on i.project_id = p.project_id
left join people pe on i.user_id = pe.user_id
""",
    "fact_messages": """
with messages as (
    select * from {{ ref('stg_messages') }}
)
select
    m.message_id,
    m.created_at::date as date,
    m.created_at,
    m.user_id,
    m.person_id,
    m.contact_name,
    m.channel,
    m.direction,
    m.message_type,
    case
        when lower(m.direction) in ('outgoing', 'outbound') then true
        else false
    end as is_automated
from messages m
"""
}

for name, sql in marts_models.items():
    with open(os.path.join(base_dir, "models", "marts", "core", f"{name}.sql"), "w", encoding="utf-8") as f:
        f.write(sql.strip() + "\n")

# 4. Create README.md for dbt_gestobra
readme_content = """# dbt_gestobra - Proyecto dbt para GestObra BI

Este directorio contiene el proyecto **dbt (data build tool)** para el módulo de Business Intelligence de **GestObra**.

El proyecto transforma los datos operacionales de PostgreSQL (esquema `public`) en un modelo analítico dimensional en estrella (esquema `analytics`) compuesto por vistas de staging y tablas de hechos/dimensiones de marts.

---

## 📁 Estructura del Proyecto

```
dbt_gestobra/
├── dbt_project.yml           # Configuración principal del proyecto dbt
├── profiles.yml              # Perfil de conexión a PostgreSQL
├── models/
│   ├── sources.yml           # Definición YAML de las 68 tablas origen no vacías de PostgreSQL
│   ├── staging/              # Modelos de transformación inicial (limpieza y renombrado)
│   │   ├── stg_projects.sql
│   │   ├── stg_people.sql
│   │   ├── stg_users.sql
│   │   ├── stg_companies.sql
│   │   ├── stg_time_clock_records.sql
│   │   ├── stg_project_imputations.sql
│   │   ├── stg_messages.sql
│   │   └── stg_daily_sessions.sql
│   └── marts/core/           # Capa de negocio analítica (Modelo en Estrella)
│       ├── dim_projects.sql
│       ├── dim_people.sql
│       ├── fact_project_imputation.sql
│       └── fact_messages.sql
```

---

## 🚀 Requisitos y Ejecución

### 1. Requisitos
Instala dbt para PostgreSQL:

```bash
pip install dbt-postgres
```

### 2. Configuración de Credenciales (`profiles.yml`)
El archivo `profiles.yml` lee las credenciales del entorno o utiliza las de `.env`:

```bash
export DBT_HOST=app.gestobra.com
export DBT_USER=gestobra_user
export DBT_PASSWORD=T5FJvlpdg9OzJKd
```

### 3. Comandos Principales de dbt

```bash
# Probar conexión con PostgreSQL
dbt debug --project-dir . --profiles-dir .

# Compilar todos los modelos SQL
dbt compile --project-dir . --profiles-dir .

# Ejecutar transformaciones (Creación de vistas staging y tablas de marts)
dbt run --project-dir . --profiles-dir .

# Ejecutar pruebas de calidad de datos (not_null, unique)
dbt test --project-dir . --profiles-dir .

# Generar y servir documentación interactiva
dbt docs generate --project-dir . --profiles-dir .
dbt docs serve --project-dir . --profiles-dir .
```
"""

with open(os.path.join(base_dir, "README.md"), "w", encoding="utf-8") as f:
    f.write(readme_content)

print("Created all staging models, marts models, profiles.yml, and README.md for dbt_gestobra successfully!")
