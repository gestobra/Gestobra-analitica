# Agente de Business Intelligence (BI) - GestObra

Este archivo contiene el contexto completo del proyecto, la arquitectura del módulo analítico y las guías para agentes de IA o desarrolladores que continúen el trabajo en el sistema BI de **GestObra**.

---

## 1. Contexto del Proyecto y Estado Actual

**GestObra** es una plataforma integral de gestión de obras y proyectos de construcción. Permite controlar el personal, el control horario de fichajes (clock-in/clock-out), la imputación de horas y costes a proyectos, y cuenta con integración con bots de WhatsApp para reportes en campo (mensajes de texto, notas de voz, audios e imágenes).

### 🌟 Logros y Módulos Implementados en el Dashboard BI:
1. **17 Gráficos Analíticos Interactivos (Chart.js)**:
   - Distribución de Horas por Proyecto y Cliente.
   - Coste de Mano de Obra por Proyecto.
   - Evolución Temporal de Horas Imputadas (Tendencia Mensual).
   - Top Operarios por Horas Fichadas.
   - Top Operarios en Actividad de Mensajería WhatsApp.
   - Desglose de Mensajes Automáticos (Bot/Botones) vs Manuales.
   - Acciones e Interacciones de WhatsApp por Categoría.
   - Módulo Dedicado "Sin Obra" (Top Operarios, Distribución por Cliente, Tendencia Temporal).
   - Analítica Comparativa de Clientes (Obras vs Mensajes, Mensajes Automáticos vs Manuales).
   - Matriz Proyectos vs Mensajes.
   - Discrepancias Fichado vs Imputado (Alertas > 30 min).

2. **Visor Interactivo de Consultas SQL / ETL (`🔍 Ver Consulta`)**:
   - Cada uno de los 17 gráficos cuenta con su contenedor identificado (`card-{chartId}`) y un botón `🔍 Ver Consulta`.
   - Ventana modal interactiva (`#query-modal`) que muestra la consulta SQL PostgreSQL equivalente, la transformación Pandas ETL, las tablas involucradas y una descripción de negocio con botón de copiado en un clic.

3. **Módulo Especial "Sin Obra"**:
   - Identifica y analiza **12.216,1 h** de trabajo no asignadas a obras específicas (72.6% del total de horas registradas) con un impacto financiero estimado de **244.322,40 €**.

4. **Botón de Filtrado Dinámico "Omitir Gestobra Dev"**:
   - Botón de alternancia (*toggle*) en la barra superior para incluir o excluir instantáneamente datos de desarrollo/pruebas (`Gestobra Dev Team` y `Gestobra`) de todos los KPIs, gráficos, desplegables y tablas.

5. **Clasificación de Mensajería WhatsApp**:
   - Identificación automática de mensajes del Bot (`Bot_Automatico`) vs interacciones manuales (`Llamada_Manual`, `Nota_Voz_Manual`, `Multimedia_Manual`, `Texto_Manual`).

---

## 2. Estructura del Proyecto

```
gestobra/
├── .agents/
│   └── AGENTS.md                  # Reglas del asistente en español, seguridad y estándares BI
├── .env                           # Credenciales de PostgreSQL (IP, DB, USER, PWD)
├── README.md                      # Documentación general y guía de ejecución rápida
├── agent.md                       # Guía de arquitectura y contexto para agentes IA
├── integration_guide.md           # Guía técnica de integración en vivo (API + SQL)
├── chart_proposals.md             # Catálogo de 30 propuestas de gráficos de negocio
├── PROPOSALS.md                   # Documento de Propuestas Estratégicas del Equipo Multidisciplinario
├── dbt_gestobra/                  # Proyecto dbt para transformaciones analíticas en PostgreSQL
│   ├── dbt_project.yml           # Configuración del proyecto dbt
│   ├── profiles.yml              # Perfil de conexión a la base de datos
│   └── models/
│       ├── sources.yml           # Definición YAML de las 68 tablas origen no vacías con metadatos en español
│       ├── staging/              # Vistas de staging (stg_*.sql)
│       └── marts/core/           # Tablas dimensionales y de hechos en estrella (dim_*.sql, fact_*.sql)
├── src/
│   ├── etl_pipeline.py            # Pipeline ETL Pandas (Extrae de PostgreSQL y guarda CSVs)
│   ├── dashboard.py               # Generador del HTML estático autónomo con 17 gráficos y modal SQL
│   ├── server.py                  # Servidor backend (Flask) con API REST en vivo y Swagger UI
│   ├── inspect_db.py              # Utilidad de inspección de esquema PostgreSQL
│   └── summarize_db.py            # Resumen estadístico de filas por tabla
├── data/                          # Almacén dimensional local en CSV
│   ├── dim_date.csv, dim_project.csv, dim_person.csv, dim_task.csv
│   └── fact_time_clock.csv, fact_project_imputation.csv, fact_whatsapp_activity.csv, fact_messages.csv, distributed_clock.csv
└── output/
    ├── dashboard.html             # Dashboard estático interactivo autónomo completo
    ├── dashboard_live.html        # Dashboard conectado en tiempo real al backend server.py
    └── schema_dump.md             # Especificación técnica de tablas y tipos PostgreSQL
```

---

## 3. Endpoints de la API REST (`src/server.py`)

El servidor Backend se ejecuta en `http://localhost:8000` y expone:

- `GET /` -> Sirve `output/dashboard_live.html`.
- `GET /api/docs` -> **Swagger UI** interactivo para probar endpoints.
- `GET /api/clients` -> Listado de clientes únicos.
- `GET /api/projects?client=X` -> Proyectos filtrados por cliente.
- `GET /api/people` -> Listado de operarios y sus tarifas horarias.
- `GET /api/aggregations/client` -> Totales de horas, costes y proyectos por cliente.
- `GET /api/aggregations/person` -> Horas, costes y actividad de WhatsApp por operario.
- `GET /api/aggregations/project` -> Métricas acumuladas por obra.
- `GET /api/data?client=A&project=B&person=C` -> Payload dinámico completo para refresco en tiempo real.

---

## 4. Reglas de Ejecución para Agentes IA

1. **Idioma**: Toda la comunicación, documentación y mensajes al usuario deben realizarse en **Español**.
2. **Acceso Seguro a DB**:
   - Usar estrictamente lecturas (`SELECT`). **NUNCA** ejecutar `UPDATE`, `DELETE` o `DROP` en producción.
   - Credenciales leídas únicamente desde `.env`.
3. **Calidad de Código**:
   - Respetar PEP 8 en scripts de Python.
   - En JavaScript, mantener la consistencia con Chart.js, Tailwind CSS y componentes de modal.
4. **Verificación Estricta**:
   - Tras realizar cualquier modificación en `src/dashboard.py` o `src/etl_pipeline.py`, se debe ejecutar `python src/dashboard.py` y verificar visualmente o mediante navegador que el reporte HTML genera y renderiza sin errores.
