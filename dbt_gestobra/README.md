# dbt_gestobra - Proyecto dbt para GestObra BI

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
