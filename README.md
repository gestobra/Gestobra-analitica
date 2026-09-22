# GestObra - Módulo de Business Intelligence (BI) & Dashboard Analítico

Este repositorio contiene el sistema completo de **Business Intelligence (BI)**, pipeline de datos (ETL), backend REST API y Dashboard Web Interactivo de la plataforma de gestión de obras **GestObra**.

El sistema extrae, transforma y modela los datos operacionales de PostgreSQL mediante un esquema en estrella (*Star Schema*), generando métricas analíticas sobre productividad de operarios, imputación de costes por obra, auditoría de fichajes, horas "Sin Obra" e interacción con el bot de mensajería de WhatsApp.

---

## 🌟 Características Destacadas del Dashboard

1. **17 Gráficos Analíticos e Interactivos (Chart.js)**:
   - **Distribución de Horas Imputadas por Proyecto**: Comparativa visual del esfuerzo por obra.
   - **Coste de Mano de Obra por Proyecto (€)**: Impacto financiero por obra y cliente.
   - **Evolución Temporal de Horas Imputadas**: Tendencia mensual acumulada.
   - **Top Operarios por Horas Fichadas**: Rendimiento de personal con ordenación ascendente/descendente.
   - **Top Operarios en Actividad de Mensajería WhatsApp**: Volumen de interacciones por operario.
   - **Desglose de Mensajes Automáticos (Bot/Botones) vs Manuales por Cliente**: Distribución de automatización por organización.
   - **Acciones e Interacciones de WhatsApp**: Clasificación en Bot Automático, Notas de Voz, Multimedia, Llamadas y Texto.
   - **Módulo Específico "Sin Obra"**: Analítica detallada de fichajes sin proyecto asignado (Top Operarios, Distribución por Cliente y Evolución Mensual).
   - **Comparativa por Cliente**: Proyectos vs Mensajes y Mensajes Automáticos vs Manuales.
   - **Matriz de Actividad Proyectos vs Mensajes**: Obras con mayor volumen de reporte en campo.
   - **Alertas de Discrepancia**: Detección de desviaciones > 30 min entre horas fichadas e imputadas.

2. **🔍 Visor Interactivo de Consultas SQL / ETL (`🔍 Ver Consulta`)**:
   - Cada gráfico dispone de un contenedor con ID propio y un botón individual `🔍 Ver Consulta`.
   - Abre un visor modal interactivo (`#query-modal`) con la consulta **PostgreSQL**, la sentencia **Pandas ETL**, las **tablas del esquema** utilizadas, una **explicación de negocio** y un botón de copiado en un clic con confirmación visual.

3. **🚫 Filtro Dinámico "Omitir Gestobra Dev"**:
   - Botón de alternancia en la barra superior para excluir al instante los registros de desarrollo y pruebas (`Gestobra Dev Team` y `Gestobra`) de todos los KPIs, gráficos y tablas.

4. **⚡ API REST en Tiempo Real & Swagger UI (`src/server.py`)**:
   - Backend en Flask/Python que permite consultar métricas en vivo directamente sobre la base de datos sin depender de archivos CSV.
   - Documentación OpenAPI / Swagger UI interactiva en `http://localhost:8000/api/docs`.

---

## 📁 Estructura del Proyecto

```
gestobra/
├── .agents/
│   └── AGENTS.md                  # Directrices y reglas de desarrollo para agentes IA (Español)
├── .env                           # Credenciales de conexión a PostgreSQL
├── README.md                      # Documentación principal del proyecto
├── agent.md                       # Contexto de arquitectura y guías para agentes de IA
├── integration_guide.md           # Guía técnica de integración en vivo (Servidor + API + SQL)
├── chart_proposals.md             # Catálogo inicial de 30 propuestas de gráficos BI
├── PROPOSALS.md                   # Documento de Propuestas Estratégicas del Equipo Multidisciplinario
├── dbt_gestobra/                  # [NUEVO] Proyecto dbt con 68 tablas origen no vacías, vistas staging y marts
│   ├── dbt_project.yml
│   ├── profiles.yml
│   └── models/
│       ├── sources.yml            # Definición YAML completa de 68 tablas origen con descripciones en español
│       ├── staging/               # Vistas de transformación inicial (stg_*.sql)
│       └── marts/core/            # Modelo en estrella dimensional (dim_*.sql, fact_*.sql)
├── src/
│   ├── etl_pipeline.py            # Pipeline ETL de extracción PostgreSQL -> CSVs dimensionales
│   ├── dashboard.py               # Generador del HTML estático autónomo con 17 gráficos
│   ├── server.py                  # Servidor Backend (Flask) con API REST en vivo y Swagger UI
│   ├── inspect_db.py              # Inspección de esquemas y tipos de columnas PostgreSQL
│   └── summarize_db.py            # Estadísticas de conteo de filas por tabla
├── data/                          # Almacén dimensional local (CSV)
│   ├── dim_date.csv, dim_project.csv, dim_person.csv, dim_task.csv
│   └── fact_time_clock.csv, fact_project_imputation.csv, fact_whatsapp_activity.csv, fact_messages.csv, distributed_clock.csv
└── output/
    ├── dashboard.html             # Dashboard estático interactivo autónomo completo
    ├── dashboard_live.html        # Dashboard conectado en tiempo real al backend server.py
    └── schema_dump.md             # Especificación técnica del esquema PostgreSQL
```

---

## 🚀 Instalación y Ejecución

### 1. Requisitos Previos
Instala las dependencias necesarias de Python:

```bash
pip install psycopg2-binary python-dotenv pandas flask flask-cors
```

### 2. Generación Batch (Procesamiento CSV)

```bash
# Paso 1: Extraer datos de PostgreSQL y actualizar dimensiones en data/
python src/etl_pipeline.py

# Paso 2: Generar el Dashboard analítico estático en output/dashboard.html
python src/dashboard.py
```
Abre [`output/dashboard.html`](file:///c:/Users/gabri/Documents/gestobra/output/dashboard.html) en tu navegador para ver el panel de control.

### 3. Ejecución del Servidor Backend (Live BI API)

```bash
python src/server.py
```
Accede a las interfaces en tu navegador:
* 🖥️ **Live Dashboard**: [http://localhost:8000/](http://localhost:8000/)
* 📚 **Documentación API (Swagger UI)**: [http://localhost:8000/api/docs](http://localhost:8000/api/docs)
* ⚙️ **Esquema OpenAPI**: [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json)

---

## 📊 Hallazgos Analíticos Clave

- **Horas "Sin Obra"**: **12.216,1 h** (72.6% del total registradas) con un impacto económico estimado de **244.322,40 €**.
- **Canales de Mensajería WhatsApp**: **2.904 interacciones totales**, clasificadas en **960 mensajes automáticos del Bot** (33.1%) y **1.944 interacciones manuales** (66.9% notas de voz, fotos, llamadas y texto).
- **Productividad por Operario**: Identificación clara de operarios con mayor volumen de horas registradas e imputadas (ej. *Unger Alejandro Alvarez Andino*, *Pedro José Palomo Barriopedro*).
