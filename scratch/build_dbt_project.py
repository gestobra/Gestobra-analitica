import os
import json
import yaml

# Load table schemas and counts
with open("scratch/non_empty_tables.json", "r", encoding="utf-8") as f:
    data = json.load(f)

schemas = data["schemas"]
counts = data["counts"]

# Direct translation dictionary for table names and column patterns in Spanish
TABLE_DESCRIPTIONS = {
    "accessories": "Accesorios y herramientas asociadas a equipos o vehículos de obra.",
    "ai_jobs": "Cola de trabajos asíncronos y tareas procesadas por los agentes de IA.",
    "cache": "Caché temporal de la aplicación para optimización de rendimiento.",
    "cargos": "Catálogo de cargos, roles y puestos de trabajo del personal.",
    "channels": "Canales de comunicación activos (ej. WhatsApp, SMS, Web).",
    "checkpoint_blobs": "Bloques de datos persistentes de los flujos de trabajo e hilos de IA.",
    "checkpoint_migrations": "Historial de migraciones de esquema de checkpoints.",
    "checkpoint_writes": "Registros de escrituras intermedias de agentes de IA.",
    "checkpoints": "Puntos de control e historial de conversaciones de agentes de IA.",
    "cities": "Catálogo de ciudades y municipios.",
    "companies": "Información de empresas, clientes y contratas principales.",
    "countries": "Catálogo de países y prefijos telefónicos.",
    "daily_sessions": "Sesiones diarias de control horario e inicio/cierre de jornada laboral.",
    "file_types": "Categorías y tipos de archivos adjuntos (planos, albaranes, facturas).",
    "files": "Registro de archivos y documentos subidos al sistema.",
    "flyway_schema_history": "Historial de migraciones de base de datos Flyway.",
    "messages": "Mensajes intercambiados en la plataforma y vía bot de WhatsApp.",
    "migrations": "Migraciones de estructura de base de datos.",
    "milestones": "Hitos y fases principales de los proyectos de obra.",
    "notification_channels": "Configuración de canales para el envío de notificaciones.",
    "notification_items": "Elementos y plantillas de notificaciones del sistema.",
    "notification_type_channels": "Asociación entre tipos de notificaciones y canales de entrega.",
    "notification_types": "Tipos y eventos que disparan notificaciones.",
    "notifications": "Historial de notificaciones enviadas a usuarios y operarios.",
    "password_reset_tokens": "Tokens de seguridad para restablecimiento de contraseñas.",
    "people": "Personal, operarios, encargados y técnicos de la empresa.",
    "person_absences": "Registro de ausencias, vacaciones y bajas laborales del personal.",
    "person_specialty": "Especialidades y competencias técnicas asignadas a cada persona.",
    "personal_access_tokens": "Tokens de acceso personal para la API.",
    "plan_price_versions": "Versiones de precios de planes de suscripción.",
    "plans": "Planes de suscripción comercial del servicio.",
    "project_comments": "Comentarios y observaciones registrados en proyectos y obras.",
    "project_imputations": "Imputaciones de horas trabajadas y costes directos a proyectos.",
    "project_schedule_resource": "Asignación de recursos (operarios/maquinaria) a cronogramas de obras.",
    "project_schedules": "Cronogramas, planificación temporal y diagramas de Gantt de obras.",
    "project_specialty": "Especialidades requeridas para la ejecución de proyectos.",
    "projects": "Obras, proyectos de construcción y centros de trabajo.",
    "reports": "Informes y partes de trabajo generados en la plataforma.",
    "resources": "Recursos disponibles (equipos, vehículos, maquinaria, personal).",
    "sessions": "Sesiones de usuarios en la plataforma web.",
    "specialties": "Catálogo de especialidades técnicas de construcción.",
    "specialty_task": "Relación entre especialidades y tareas operativas.",
    "specialty_task_template": "Plantillas de tareas asociadas a especialidades.",
    "specialty_user": "Asignación de especialidades a usuarios.",
    "states": "Provincias o estados geográficos.",
    "task_comments": "Comentarios y notas sobre tareas específicas.",
    "task_recurrences": "Configuración de recurrencia para tareas periódicas.",
    "task_schedule_resource": "Recursos asignados a la programación de tareas.",
    "task_schedules": "Programación temporal de tareas individuales.",
    "task_templates": "Plantillas reutilizables para la creación rápida de tareas.",
    "tasks": "Tareas, partidas de obra y actividades operativas.",
    "team_absences": "Ausencias registradas a nivel de equipo o cuadrilla.",
    "team_invitations": "Invitaciones enviadas a nuevos miembros para unirse a un equipo.",
    "team_user": "Asociación de usuarios a equipos de trabajo.",
    "team_workday_settings": "Configuración de jornadas laborales por equipo (horarios, pausas).",
    "teams": "Equipos, cuadrillas de trabajo y organizaciones.",
    "time_clock_corrections": "Correcciones y solicitudes de ajuste de fichajes de jornada.",
    "time_clock_records": "Registros de fichajes (inicio/fin de jornada y pausas).",
    "user_notification_preferences": "Preferencias individuales de notificación por usuario.",
    "users": "Cuentas de usuario registradas en la plataforma.",
    "vehicle_accessories": "Accesorios y equipamiento asignado a vehículos.",
    "vehicles": "Flota de vehículos y maquinaria de transporte de la empresa.",
    "voice_inputs": "Audios y mensajes de voz recibidos para procesamiento NLP.",
    "whatsapp_action_log": "Log de auditoría de acciones e interacciones con el bot de WhatsApp.",
    "whatsapp_comment_links": "Vínculos entre comentarios de obra y mensajes de WhatsApp.",
    "whatsapp_inbound_messages": "Mensajes entrantes recibidos a través del webhook de WhatsApp.",
    "whatsapp_media_inputs": "Archivos multimedia (imágenes, documentos, vídeos) recibidos vía WhatsApp.",
    "workday_reminder_log": "Log de recordatorios automáticos de inicio/cierre de jornada laboral."
}

def infer_column_description(col_name, data_type):
    col = col_name.lower()
    if col == "id":
        return "Identificador único clave primaria de la tabla."
    elif col.endswith("_id"):
        entity = col[:-3]
        return f"Clave foránea que referencia al identificador único de '{entity}'."
    elif col in ["name", "title"]:
        return "Nombre o título descriptivo."
    elif col == "description":
        return "Descripción detallada o notas adicionales."
    elif col == "created_at":
        return "Fecha y hora de creación del registro en la base de datos."
    elif col == "updated_at":
        return "Fecha y hora de última actualización del registro."
    elif col == "deleted_at":
        return "Fecha y hora de borrado lógico (soft delete)."
    elif col == "is_active" or col.startswith("is_"):
        return f"Indicador booleano que determina el estado de '{col}'."
    elif "date" in col:
        return "Fecha asociada al evento o registro."
    elif "status" in col or "state" in col:
        return "Estado actual del flujo de trabajo."
    elif "phone" in col:
        return "Número de teléfono de contacto."
    elif "email" in col:
        return "Dirección de correo electrónico."
    elif "cost" in col or "price" in col or "rate" in col:
        return "Importe monetario o tarifa en euros (€)."
    elif "hours" in col or "duration" in col:
        return "Duración o tiempo registrado en horas."
    elif "code" in col:
        return "Código de identificación estándar o alfanumérico."
    else:
        return f"Campo de tipo {data_type} para almacenar {col_name}."

# Build dbt directory structure
base_dir = "dbt_gestobra"
os.makedirs(os.path.join(base_dir, "models", "staging"), exist_ok=True)
os.makedirs(os.path.join(base_dir, "models", "marts", "core"), exist_ok=True)
os.makedirs(os.path.join(base_dir, "macros"), exist_ok=True)
os.makedirs(os.path.join(base_dir, "seeds"), exist_ok=True)

# 1. dbt_project.yml
dbt_project = {
    "name": "dbt_gestobra",
    "version": "1.0.0",
    "config-version": 2,
    "profile": "gestobra",
    "model-paths": ["models"],
    "analysis-paths": ["analyses"],
    "test-paths": ["tests"],
    "seed-paths": ["seeds"],
    "macro-paths": ["macros"],
    "snapshot-paths": ["snapshots"],
    "clean-targets": ["target", "dbt_packages"],
    "models": {
        "dbt_gestobra": {
            "staging": {
                "+schema": "staging",
                "+materialized": "view"
            },
            "marts": {
                "+schema": "analytics",
                "+materialized": "table"
            }
        }
    }
}

with open(os.path.join(base_dir, "dbt_project.yml"), "w", encoding="utf-8") as f:
    yaml.dump(dbt_project, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

# 2. sources.yml
source_tables = []

for table_name in sorted(schemas.keys()):
    cols = schemas[table_name]
    parsed_cols = []
    for c in cols:
        col_name = c["name"]
        data_type = c["type"]
        desc = infer_column_description(col_name, data_type)
        col_def = {
            "name": col_name,
            "description": desc,
            "data_type": data_type
        }
        if col_name == "id" or (col_name.endswith("_id") and c["nullable"] == "NO"):
            col_def["tests"] = ["not_null"]
            if col_name == "id":
                col_def["tests"].append("unique")
        parsed_cols.append(col_def)

    source_tables.append({
        "name": table_name,
        "description": TABLE_DESCRIPTIONS.get(table_name, f"Tabla operacional {table_name} ({counts.get(table_name, 0)} registros)."),
        "meta": {
            "row_count": counts.get(table_name, 0)
        },
        "columns": parsed_cols
    })

sources_yaml = {
    "version": 2,
    "sources": [
        {
            "name": "gestobra_public",
            "database": "gestobra",
            "schema": "public",
            "description": "Base de datos transaccional operacional de GestObra en PostgreSQL conteniendo únicamente tablas con registros no vacíos.",
            "tables": source_tables
        }
    ]
}

with open(os.path.join(base_dir, "models", "sources.yml"), "w", encoding="utf-8") as f:
    yaml.dump(sources_yaml, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

print(f"Created dbt_project.yml and sources.yml with {len(source_tables)} non-empty tables successfully!")
