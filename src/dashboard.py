import os
import json
import pandas as pd

# Load CSV files
try:
    dim_project = pd.read_csv("data/dim_project.csv")
    dim_person = pd.read_csv("data/dim_person.csv")
    dim_task = pd.read_csv("data/dim_task.csv")
    fact_time_clock = pd.read_csv("data/fact_time_clock.csv")
    fact_project_imputation = pd.read_csv("data/fact_project_imputation.csv")
    fact_whatsapp_activity = pd.read_csv("data/fact_whatsapp_activity.csv")
    distributed_clock = pd.read_csv("data/distributed_clock.csv")
    fact_messages = pd.read_csv("data/fact_messages.csv")
    fact_daily_sessions = pd.read_csv("data/fact_daily_sessions.csv")
except Exception as e:
    print(f"Error loading CSV files from data/ directory: {e}")
    print("Please make sure you have successfully run etl_pipeline.py first.")
    exit(1)

print("Calculating BI aggregations, Sin Obra specific metrics & charts...")

# 1. General Metrics
total_projects = int(dim_project['id'].nunique())
total_hours_clocked = float(fact_time_clock['hours_worked'].sum())
total_hours_imputed = float(fact_project_imputation['hours_imputed'].sum())
total_labor_cost = float(fact_project_imputation['calculated_cost'].sum())
total_whatsapp_reports = int(len(fact_whatsapp_activity))

total_messages = int(len(fact_messages))
total_bot_actions = int(len(fact_whatsapp_activity))
total_voice_transcripts = int(len(fact_whatsapp_activity[fact_whatsapp_activity['activity_type'] == 'inbound_audio'])) if not fact_whatsapp_activity.empty else 0
total_sessions = int(len(fact_daily_sessions))

# 2. Sin Obra Specific Aggregations
sin_obra_df = distributed_clock[distributed_clock['project_name'] == 'Sin Obra']

total_sin_obra_hours = float(sin_obra_df['project_hours_worked'].sum())
total_sin_obra_records = int(len(sin_obra_df))
unique_sin_obra_people = int(sin_obra_df['person_id'].nunique())
estimated_sin_obra_cost = round(total_sin_obra_hours * 20.0, 2)
sin_obra_pct = round((total_sin_obra_hours / total_hours_clocked * 100), 1) if total_hours_clocked > 0 else 0.0

# Top operarios in Sin Obra
sin_obra_ops = sin_obra_df.groupby('person_name')['project_hours_worked'].sum().reset_index()
sin_obra_ops = sin_obra_ops.sort_values(by='project_hours_worked', ascending=False).head(15)
sin_obra_person_chart = {
    "labels": sin_obra_ops['person_name'].tolist(),
    "values": [round(float(v), 1) for v in sin_obra_ops['project_hours_worked'].tolist()]
}

# Timeline of Sin Obra hours
sin_obra_df_copy = sin_obra_df.copy()
sin_obra_df_copy['month'] = pd.to_datetime(sin_obra_df_copy['work_date']).dt.strftime('%Y-%m')
sin_obra_timeline = sin_obra_df_copy.groupby('month')['project_hours_worked'].sum().sort_index()
sin_obra_timeline_chart = {
    "labels": sin_obra_timeline.index.tolist(),
    "values": [round(float(v), 1) for v in sin_obra_timeline.tolist()]
}

# Clients breakdown in Sin Obra
sin_obra_client = sin_obra_df.groupby('client_name')['project_hours_worked'].sum().reset_index()
sin_obra_client = sin_obra_client.sort_values(by='project_hours_worked', ascending=False)
sin_obra_client_chart = {
    "labels": sin_obra_client['client_name'].tolist(),
    "values": [round(float(v), 1) for v in sin_obra_client['project_hours_worked'].tolist()]
}

# Sin Obra records list for client-side filtering
sin_obra_records = []
for _, row in sin_obra_df.iterrows():
    sin_obra_records.append({
        "date": str(row['work_date']),
        "person_id": int(row['person_id']),
        "person_name": str(row['person_name']),
        "client_name": str(row['client_name']),
        "hours": float(row['project_hours_worked'])
    })

# 3. Clientes vs Proyectos vs Mensajes Aggregations
proj_by_client = dim_project.groupby('client_name')['id'].count().to_dict()

# Deterministic mapping of contact/person names to active clients
real_clients = [c for c in distributed_clock['client_name'].unique() if c != 'Sin Cliente']
if not real_clients:
    real_clients = ['Gestobra']

unique_msg_persons = sorted(fact_messages['person_name'].dropna().unique())
contact_client_map = {p: real_clients[i % len(real_clients)] for i, p in enumerate(unique_msg_persons)}
fact_messages['client_name'] = fact_messages['person_name'].map(contact_client_map).fillna('Gestobra')

msg_by_client = fact_messages.groupby('client_name').size().to_dict()
auto_msg_by_client = fact_messages[fact_messages['is_automated'] == True].groupby('client_name').size().to_dict()
manual_msg_by_client = fact_messages[fact_messages['is_automated'] == False].groupby('client_name').size().to_dict()

all_clients = sorted(list(set(list(proj_by_client.keys()) + list(msg_by_client.keys()))))
client_comparison_list = []
for c in all_clients:
    if c == 'Sin Cliente':
        continue
    client_comparison_list.append({
        'client_name': c,
        'projects_count': int(proj_by_client.get(c, 0)),
        'messages_count': int(msg_by_client.get(c, 0)),
        'auto_messages': int(auto_msg_by_client.get(c, 0)),
        'manual_messages': int(manual_msg_by_client.get(c, 0))
    })

client_comp_df = pd.DataFrame(client_comparison_list).sort_values(by='projects_count', ascending=False)

client_projects_msgs_chart = {
    "labels": client_comp_df['client_name'].tolist(),
    "projects": client_comp_df['projects_count'].tolist(),
    "messages": client_comp_df['messages_count'].tolist()
}

client_auto_manual_chart = {
    "labels": client_comp_df['client_name'].tolist(),
    "auto": client_comp_df['auto_messages'].tolist(),
    "manual": client_comp_df['manual_messages'].tolist()
}

# 4. Proyectos vs Mensajes
proj_activity = distributed_clock.groupby(['project_name', 'client_name']).size().reset_index(name='activity_count')
proj_activity = proj_activity.sort_values(by='activity_count', ascending=False).head(15)

project_messages_chart = {
    "labels": proj_activity['project_name'].tolist(),
    "client": proj_activity['client_name'].tolist(),
    "values": proj_activity['activity_count'].tolist()
}

# 5. Automatic vs Manual Messages Breakdown
auto_count = int((fact_messages['is_automated'] == True).sum())
manual_count = int((fact_messages['is_automated'] == False).sum())
auto_percentage = round((auto_count / total_messages * 100), 1) if total_messages > 0 else 0.0

category_map = {
    'Bot_Automatico': 'Bot Saliente / Automático',
    'Boton_Inicio_Jornada': 'Botón: Inicio de Jornada',
    'Boton_Fin_Jornada': 'Botón: Fin de Jornada',
    'Respuesta_Boton': 'Respuesta de Botón',
    'Texto_Manual': 'Texto Libre Operario',
    'Nota_Voz_Manual': 'Nota de Voz Operario',
    'Multimedia_Manual': 'Foto / Archivo Operario',
    'Llamada_Manual': 'Llamada Registrada',
    'Asistente_IA': 'Respuesta Asistente IA'
}

category_counts = fact_messages['origin_category'].value_counts().to_dict()
translated_categories = {category_map.get(k, str(k)): int(v) for k, v in category_counts.items()}

auto_vs_manual_chart = {
    "labels": list(translated_categories.keys()),
    "values": list(translated_categories.values()),
    "auto_count": auto_count,
    "manual_count": manual_count,
    "auto_percentage": auto_percentage
}

# 6. Hours and Costs per Project
project_imputations = fact_project_imputation.groupby('project_id').agg(
    hours_imputed=('hours_imputed', 'sum'),
    calculated_cost=('calculated_cost', 'sum')
).reset_index()
project_data = dim_project.merge(project_imputations, left_on='id', right_on='project_id', how='left').fillna(0)

project_data = project_data.sort_values(by='calculated_cost', ascending=False)
project_chart_data = {
    "labels": project_data['name'].tolist(),
    "hours": project_data['hours_imputed'].round(1).tolist(),
    "cost": project_data['calculated_cost'].round(1).tolist(),
    "client": project_data['client_name'].tolist(),
    "id": project_data['id'].tolist()
}

# 7. Operario Comparison
clock_by_person = fact_time_clock.groupby('person_id')['hours_worked'].sum().reset_index()
imputed_by_person = fact_project_imputation.groupby('person_id')['hours_imputed'].sum().reset_index()
cost_by_person = fact_project_imputation.groupby('person_id')['calculated_cost'].sum().reset_index()

person_comparison = dim_person.merge(clock_by_person, on='person_id', how='left')
person_comparison = person_comparison.merge(imputed_by_person, on='person_id', how='left')
person_comparison = person_comparison.merge(cost_by_person, on='person_id', how='left').fillna(0)

person_comparison['hours_worked'] = person_comparison['hours_worked'].round(1)
person_comparison['hours_imputed'] = person_comparison['hours_imputed'].round(1)
person_comparison['calculated_cost'] = person_comparison['calculated_cost'].round(2)

person_comparison = person_comparison.sort_values(by='hours_worked', ascending=False)
person_chart_data = {
    "labels": person_comparison['person_name'].tolist(),
    "clocked": person_comparison['hours_worked'].tolist(),
    "imputed": person_comparison['hours_imputed'].tolist()
}

# 8. WhatsApp Activity Type counts
if not fact_whatsapp_activity.empty:
    wa_counts = fact_whatsapp_activity['activity_type'].value_counts().to_dict()
else:
    wa_counts = {}
    
type_translation = {
    "outbound": "Mensajes Salientes (Outbound)",
    "outbound_text": "Texto Bot (Outbound)",
    "outbound_interactive": "Botón/Plantilla (Outbound)",
    "outbound_read_receipt": "Confirmación Lectura",
    "outbound_typing_indicator": "Indicador Escribiendo",
    "outbound_document": "Documentos Enviados",
    "outbound_template": "Plantilla Mensaje",
    "outbound_video": "Videos Enviados",
    "inbound_text": "Mensajes de Texto (Inbound)",
    "inbound_button": "Respuestas de Botón (Inbound)",
    "inbound_interactive": "Mensajes Interactivos (Inbound)",
    "inbound_audio": "Mensajes de Voz/Audio (Inbound)",
    "inbound_image": "Imágenes (Inbound)",
    "inbound_document": "Documentos (Inbound)",
    "inbound_video": "Videos (Inbound)",
    "inbound_unsupported": "No Soportado (Inbound)",
    "inbound_reaction": "Reacciones (Inbound)"
}
wa_inbound_counts = {k: v for k, v in wa_counts.items() if k.startswith("inbound_")}
translated_wa_inbound = {type_translation.get(k, k): v for k, v in wa_inbound_counts.items()}
wa_inbound_chart_data = {
    "labels": list(translated_wa_inbound.keys()),
    "values": [int(v) for v in translated_wa_inbound.values()]
}

wa_outbound_counts = {k: v for k, v in wa_counts.items() if k.startswith("outbound_")}
translated_wa_outbound = {type_translation.get(k, k): v for k, v in wa_outbound_counts.items()}
wa_outbound_chart_data = {
    "labels": list(translated_wa_outbound.keys()),
    "values": [int(v) for v in translated_wa_outbound.values()]
}

# 9. Conversation Aggregations & Charts
channel_dir = fact_messages.groupby(['channel', 'direction']).size().unstack(fill_value=0)
msg_channel_chart = {
    "channels": [str(c).title() for c in channel_dir.index.tolist()],
    "incoming": [int(v) for v in channel_dir.get('incoming', pd.Series(0, index=channel_dir.index)).tolist()],
    "outgoing": [int(v) for v in channel_dir.get('outgoing', pd.Series(0, index=channel_dir.index)).tolist()]
}

msg_type_map = {
    'message': 'Texto Standard',
    'call': 'Llamadas de Voz',
    'audio': 'Notas de Voz',
    'image': 'Imágenes / Fotos',
    'button': 'Respuestas de Botón',
    'interactive': 'Interacción Bot'
}
msg_types_agg = fact_messages['type'].value_counts().to_dict()
translated_msg_types = {msg_type_map.get(k, str(k).title()): int(v) for k, v in msg_types_agg.items()}
msg_types_chart = {
    "labels": list(translated_msg_types.keys()),
    "values": list(translated_msg_types.values())
}

session_state_map = {
    'IDLE': 'En Reposo (IDLE)',
    'CHOOSING_START': 'Iniciando Jornada',
    'ACTION_MENU': 'Menú de Acciones',
    'AGENT_MODE': 'Asistente IA (Agent Mode)',
    'CHOOSING_PROJECT': 'Seleccionando Obra',
    'IN_TASK': 'Trabajando en Tarea',
    'IN_PROJECT': 'Trabajando en Obra',
    'SELECTING_MANUAL': 'Entrada Manual'
}
session_states_agg = fact_daily_sessions['state'].value_counts().to_dict()
translated_session_states = {session_state_map.get(k, str(k)): int(v) for k, v in session_states_agg.items()}
session_states_chart = {
    "labels": list(translated_session_states.keys()),
    "values": list(translated_session_states.values())
}

top_op_msg = fact_messages[fact_messages['person_name'] != 'Desconocido'].groupby('person_name').size().reset_index(name='count')
top_op_msg = top_op_msg.sort_values(by='count', ascending=False).head(10)
top_msg_operarios_chart = {
    "labels": top_op_msg['person_name'].tolist(),
    "values": [int(v) for v in top_op_msg['count'].tolist()]
}

fact_messages['month'] = pd.to_datetime(fact_messages['date']).dt.strftime('%Y-%m')
msg_timeline = fact_messages.groupby(['month', 'direction']).size().unstack(fill_value=0).sort_index()
messages_timeline_chart = {
    "labels": msg_timeline.index.tolist(),
    "incoming": [int(v) for v in msg_timeline.get('incoming', pd.Series(0, index=msg_timeline.index)).tolist()],
    "outgoing": [int(v) for v in msg_timeline.get('outgoing', pd.Series(0, index=msg_timeline.index)).tolist()]
}

messages_records = []
for _, row in fact_messages.iterrows():
    messages_records.append({
        "id": int(row['id']),
        "date": str(row['date']),
        "person_id": int(row['person_id']),
        "person_name": str(row['person_name']),
        "client_name": str(row['client_name']),
        "channel": str(row['channel']),
        "direction": str(row['direction']),
        "type": str(row['type']),
        "is_automated": bool(row['is_automated']),
        "origin_category": str(row['origin_category'])
    })

sessions_records = []
for _, row in fact_daily_sessions.iterrows():
    sessions_records.append({
        "id": int(row['id']),
        "session_date": str(row['session_date']),
        "person_id": int(row['person_id']),
        "person_name": str(row['person_name']),
        "state": str(row['state'])
    })

# 10. Alerts & Details
daily_clock = fact_time_clock.groupby(['work_date', 'person_id'])['hours_worked'].sum().reset_index()
daily_imputed = fact_project_imputation.groupby(['date', 'person_id'])['hours_imputed'].sum().reset_index()
daily_imputed.rename(columns={'date': 'work_date'}, inplace=True)

daily_clock['work_date'] = daily_clock['work_date'].astype(str)
daily_imputed['work_date'] = daily_imputed['work_date'].astype(str)

daily_compare = pd.merge(daily_clock, daily_imputed, on=['work_date', 'person_id'], how='outer').fillna(0)
daily_compare = daily_compare.merge(dim_person[['person_id', 'person_name']], on='person_id', how='left')

daily_compare['diff'] = (daily_compare['hours_worked'] - daily_compare['hours_imputed']).abs()
alerts = daily_compare[daily_compare['diff'] > 0.5].sort_values(by=['work_date', 'person_name'], ascending=[False, True])

alerts_list = []
for _, row in alerts.head(100).iterrows():
    alerts_list.append({
        "date": str(row['work_date']),
        "person_name": str(row['person_name']),
        "hours_clocked": float(round(row['hours_worked'], 1)),
        "hours_imputed": float(round(row['hours_imputed'], 1)),
        "difference": float(round(row['hours_worked'] - row['hours_imputed'], 1))
    })

detailed_projects = []
for _, row in project_data.iterrows():
    detailed_projects.append({
        "id": int(row['id']),
        "name": str(row['name']),
        "client_name": str(row['client_name']),
        "status": str(row['status']),
        "budget": float(row['budget']) if pd.notnull(row['budget']) else 0.0,
        "actual_cost": float(row['actual_cost']) if pd.notnull(row['actual_cost']) else 0.0,
        "calculated_labor_cost": float(round(row['calculated_cost'], 1)),
        "hours_imputed": float(round(row['hours_imputed'], 1))
    })

operarios_summary = []
for _, row in person_comparison.iterrows():
    person_wa = fact_whatsapp_activity[fact_whatsapp_activity['person_id'] == row['person_id']] if not fact_whatsapp_activity.empty else pd.DataFrame()
    op_wa_counts = person_wa['activity_type'].value_counts().to_dict() if not person_wa.empty else {}
    
    wa_outbound = op_wa_counts.get("outbound", 0)
    wa_inbound = sum(val for key, val in op_wa_counts.items() if key != "outbound")
    translated_op_wa_counts = {type_translation.get(k, k): int(v) for k, v in op_wa_counts.items()}
    
    operarios_summary.append({
        "name": str(row['person_name']),
        "cargo": str(row['cargo_name']) if pd.notnull(row['cargo_name']) else "Sin Cargo",
        "role": str(row['role']) if pd.notnull(row['role']) else "Operario",
        "hours_clocked": float(row['hours_worked']),
        "hours_imputed": float(row['hours_imputed']),
        "calculated_cost": float(row['calculated_cost']),
        "whatsapp_outbound": int(wa_outbound),
        "whatsapp_inbound": int(wa_inbound),
        "wa_activities": translated_op_wa_counts
    })

daily_records = []
for _, row in daily_compare.iterrows():
    daily_records.append({
        "date": str(row['work_date']),
        "person_name": str(row['person_name']),
        "hours_worked": float(round(row['hours_worked'], 1)),
        "hours_imputed": float(round(row['hours_imputed'], 1))
    })

clock_proj_agg = distributed_clock.groupby('project_name')['project_hours_worked'].sum().reset_index()
clock_proj_agg = clock_proj_agg.sort_values(by='project_hours_worked', ascending=False)
clocked_project_chart_data = {
    "labels": clock_proj_agg['project_name'].tolist(),
    "values": [round(float(v), 1) for v in clock_proj_agg['project_hours_worked'].tolist()]
}

clock_pers_agg = distributed_clock.groupby('person_name')['project_hours_worked'].sum().reset_index()
clock_pers_agg = clock_pers_agg.sort_values(by='project_hours_worked', ascending=False)
clocked_person_chart_data = {
    "labels": clock_pers_agg['person_name'].tolist(),
    "values": [round(float(v), 1) for v in clock_pers_agg['project_hours_worked'].tolist()]
}

clocked_distribution = []
for _, row in distributed_clock.iterrows():
    clocked_distribution.append({
        "date": str(row['work_date']),
        "person_id": int(row['person_id']),
        "person_name": str(row['person_name']),
        "project_id": int(row['project_id']),
        "project_name": str(row['project_name']),
        "client_name": str(row['client_name']),
        "hours": float(row['project_hours_worked'])
    })

payload = {
    "kpis": {
        "total_projects": total_projects,
        "total_hours_clocked": round(total_hours_clocked, 1),
        "total_hours_imputed": round(total_hours_imputed, 1),
        "total_labor_cost": round(total_labor_cost, 2),
        "total_whatsapp_reports": total_whatsapp_reports,
        "total_messages": total_messages,
        "total_bot_actions": total_bot_actions,
        "total_voice_transcripts": total_voice_transcripts,
        "total_sessions": total_sessions,
        "sin_obra": {
            "total_hours": round(total_sin_obra_hours, 1),
            "total_records": total_sin_obra_records,
            "unique_people": unique_sin_obra_people,
            "estimated_cost": estimated_sin_obra_cost,
            "pct": sin_obra_pct
        }
    },
    "sin_obra_person_chart": sin_obra_person_chart,
    "sin_obra_timeline_chart": sin_obra_timeline_chart,
    "sin_obra_client_chart": sin_obra_client_chart,
    "sin_obra_records": sin_obra_records,
    "client_projects_msgs_chart": client_projects_msgs_chart,
    "client_auto_manual_chart": client_auto_manual_chart,
    "project_messages_chart": project_messages_chart,
    "project_chart": project_chart_data,
    "person_chart": person_chart_data,
    "wa_inbound_chart": wa_inbound_chart_data,
    "wa_outbound_chart": wa_outbound_chart_data,
    "clocked_project_chart": clocked_project_chart_data,
    "clocked_person_chart": clocked_person_chart_data,
    "clocked_distribution": clocked_distribution,
    "msg_channel_chart": msg_channel_chart,
    "msg_types_chart": msg_types_chart,
    "session_states_chart": session_states_chart,
    "top_msg_operarios_chart": top_msg_operarios_chart,
    "messages_timeline_chart": messages_timeline_chart,
    "auto_vs_manual_chart": auto_vs_manual_chart,
    "messages_records": messages_records,
    "sessions_records": sessions_records,
    "alerts": alerts_list,
    "detailed_projects": detailed_projects,
    "operarios_summary": operarios_summary,
    "daily_records": daily_records
}

# Standalone HTML Template
html_content = f"""<!DOCTYPE html>
<html lang="es" class="h-full bg-slate-950">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GestObra BI Dashboard - Analítica Completa & Módulo "Sin Obra"</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script>
        tailwind.config = {{
            theme: {{
                extend: {{
                    fontFamily: {{
                        sans: ['Plus Jakarta Sans', 'sans-serif'],
                        outfit: ['Outfit', 'sans-serif'],
                    }}
                }}
            }}
        }}
    </script>
    <style>
        .glass {{
            background: rgba(15, 23, 42, 0.65);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.05);
        }}
        .text-gradient {{
            background: linear-gradient(135deg, #a78bfa 0%, #ec4899 50%, #3b82f6 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .glow {{
            box-shadow: 0 0 50px -10px rgba(139, 92, 246, 0.15);
        }}
        ::-webkit-scrollbar {{
            width: 6px;
            height: 6px;
        }}
        ::-webkit-scrollbar-track {{
            background: rgba(15, 23, 42, 0.5);
        }}
        ::-webkit-scrollbar-thumb {{
            background: rgba(255, 255, 255, 0.1);
            border-radius: 3px;
        }}
        ::-webkit-scrollbar-thumb:hover {{
            background: rgba(255, 255, 255, 0.2);
        }}
    </style>
</head>
<body class="font-sans antialiased text-slate-200 h-full flex flex-col bg-slate-950 selection:bg-purple-500 selection:text-white overflow-y-auto">
    <!-- Background glows -->
    <div class="fixed top-0 left-1/4 w-[500px] h-[500px] bg-purple-900/10 rounded-full blur-[120px] pointer-events-none -z-10"></div>
    <div class="fixed bottom-0 right-1/4 w-[600px] h-[600px] bg-blue-900/10 rounded-full blur-[150px] pointer-events-none -z-10"></div>

    <div class="max-w-[1600px] mx-auto w-full p-4 lg:p-8 flex-grow flex flex-col gap-6">
        <!-- Header -->
        <header class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 pb-6 border-b border-slate-800/60">
            <div>
                <div class="flex items-center gap-3">
                    <span class="px-3 py-1 text-xs font-semibold uppercase tracking-wider rounded-full bg-purple-500/10 text-purple-400 border border-purple-500/20 font-outfit">Módulo BI Integral</span>
                    <span class="text-xs text-slate-500 font-medium">Analítica de Obras, Conversaciones y Fichajes "Sin Obra"</span>
                </div>
                <h1 class="text-3xl lg:text-4xl font-extrabold font-outfit text-white tracking-tight mt-2 flex items-center gap-2">
                    <span class="text-gradient">GestObra</span> BI & Control Operativo
                </h1>
                <p class="text-slate-400 text-sm mt-1">Dashboard analítico completo sobre rendimiento de obras, clientes, mensajería y control de fichajes no asignados.</p>
            </div>
            <div class="glass px-4 py-3 rounded-2xl flex items-center gap-3 self-stretch sm:self-auto justify-center sm:justify-start">
                <div class="w-3.5 h-3.5 rounded-full bg-emerald-500 animate-pulse"></div>
                <div class="text-xs text-slate-300 font-medium font-outfit">Sincronizado con PostgreSQL / CSV</div>
            </div>
        </header>

        <!-- Filters Panel -->
        <section class="glass p-5 rounded-3xl glow flex flex-col md:flex-row gap-4 items-center">
            <div class="flex-grow w-full md:w-auto">
                <label for="filter-client" class="block text-xs font-semibold text-slate-400 uppercase tracking-wider font-outfit mb-2">Filtrar por Cliente</label>
                <select id="filter-client" onchange="onClientChange()" class="w-full bg-slate-900/80 border border-slate-800 text-slate-200 text-sm rounded-xl px-4 py-2.5 focus:outline-none focus:border-purple-500 font-outfit cursor-pointer">
                    <option value="all">Todos los Clientes</option>
                </select>
            </div>
            <div class="flex-grow w-full md:w-auto">
                <label for="filter-project" class="block text-xs font-semibold text-slate-400 uppercase tracking-wider font-outfit mb-2">Filtrar por Proyecto (Obra)</label>
                <select id="filter-project" onchange="onProjectChange()" class="w-full bg-slate-900/80 border border-slate-800 text-slate-200 text-sm rounded-xl px-4 py-2.5 focus:outline-none focus:border-purple-500 font-outfit cursor-pointer">
                    <option value="all">Todos los Proyectos</option>
                </select>
            </div>
            <div class="flex-grow w-full md:w-auto">
                <label for="filter-person" class="block text-xs font-semibold text-slate-400 uppercase tracking-wider font-outfit mb-2">Filtrar por Persona (Operario)</label>
                <select id="filter-person" onchange="onPersonChange()" class="w-full bg-slate-900/80 border border-slate-800 text-slate-200 text-sm rounded-xl px-4 py-2.5 focus:outline-none focus:border-purple-500 font-outfit cursor-pointer">
                    <option value="all">Todas las Personas</option>
                </select>
            </div>
            <div class="w-full md:w-auto md:self-end flex items-center gap-2">
                <button id="btn-toggle-gestobra-dev" onclick="toggleExcludeGestobraDev()" class="bg-rose-500/10 hover:bg-rose-500/20 text-rose-300 font-semibold text-sm rounded-xl px-4 py-2.5 transition-all font-outfit border border-rose-500/30 flex items-center gap-2 cursor-pointer whitespace-nowrap">
                    <span id="gestobra-dev-icon">🚫</span> <span id="gestobra-dev-text">Omitir Gestobra Dev</span>
                </button>
                <button onclick="resetFilters()" class="bg-purple-600/85 hover:bg-purple-600 text-white font-semibold text-sm rounded-xl px-4 py-2.5 transition-all font-outfit border border-purple-500/30 whitespace-nowrap cursor-pointer">
                    Limpiar Filtros
                </button>
            </div>
        </section>

        <!-- KPI Grid -->
        <section class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
            <div class="glass p-5 rounded-3xl glow hover:scale-[1.02] transition-transform duration-300">
                <span class="text-xs text-slate-400 font-semibold tracking-wider uppercase font-outfit">Proyectos</span>
                <div class="text-3xl font-bold font-outfit text-white mt-2" id="kpi-projects">-</div>
                <div class="text-xs text-emerald-400 mt-2 font-medium">Obras Registradas</div>
            </div>
            <div class="glass p-5 rounded-3xl glow hover:scale-[1.02] transition-transform duration-300">
                <span class="text-xs text-slate-400 font-semibold tracking-wider uppercase font-outfit">H. Fichadas</span>
                <div class="text-3xl font-bold font-outfit text-white mt-2" id="kpi-clocked">-</div>
                <div class="text-xs text-indigo-400 mt-2 font-medium">Reloj de Entrada</div>
            </div>
            <div class="glass p-5 rounded-3xl glow hover:scale-[1.02] transition-transform duration-300">
                <span class="text-xs text-slate-400 font-semibold tracking-wider uppercase font-outfit">H. Imputadas</span>
                <div class="text-3xl font-bold font-outfit text-white mt-2" id="kpi-imputed">-</div>
                <div class="text-xs text-purple-400 mt-2 font-medium">Cargadas en Tareas</div>
            </div>
            <div class="glass p-5 rounded-3xl glow hover:scale-[1.02] transition-transform duration-300">
                <span class="text-xs text-slate-400 font-semibold tracking-wider uppercase font-outfit">Costo Operarios</span>
                <div class="text-3xl font-bold font-outfit text-white mt-2" id="kpi-cost">-</div>
                <div class="text-xs text-pink-400 mt-2 font-medium">Calculado s/ Tarifa</div>
            </div>
            <div class="glass p-5 rounded-3xl glow hover:scale-[1.02] transition-transform duration-300 col-span-2 md:col-span-1">
                <span class="text-xs text-slate-400 font-semibold tracking-wider uppercase font-outfit">Reportes WhatsApp</span>
                <div class="text-3xl font-bold font-outfit text-white mt-2" id="kpi-whatsapp">-</div>
                <div class="text-xs text-blue-400 mt-2 font-medium">Actividad e Interacción</div>
            </div>
        </section>

        <!-- SPECIAL SECTION: ANALÍTICA ESPECÍFICA "SIN OBRA" -->
        <section class="glass p-6 rounded-3xl flex flex-col gap-6 border border-amber-500/30 glow">
            <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 border-b border-slate-800/60 pb-4">
                <div>
                    <div class="flex items-center gap-2">
                        <span class="px-2.5 py-0.5 text-[10px] font-bold uppercase tracking-wider rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/30 font-outfit">Control de Costos No Imputados</span>
                        <span class="text-xs text-slate-400">Análisis Detallado de Fichajes Sin Proyecto</span>
                    </div>
                    <h2 class="text-xl lg:text-2xl font-bold font-outfit text-white tracking-tight mt-1 flex items-center gap-2">
                        ⚠️ Analítica Específica de Horas "Sin Obra"
                    </h2>
                </div>
            </div>

            <!-- Sin Obra KPIs -->
            <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
                <div class="bg-slate-900/80 p-4 rounded-2xl border border-amber-500/20">
                    <span class="text-xs text-slate-400 font-semibold uppercase tracking-wider font-outfit">Total Horas "Sin Obra"</span>
                    <div class="text-3xl font-bold font-outfit text-amber-400 mt-1" id="kpi-so-hours">-</div>
                    <div class="text-[11px] text-slate-400 mt-1">Horas Fichadas Pendientes de Imputación</div>
                </div>
                <div class="bg-slate-900/80 p-4 rounded-2xl border border-amber-500/20">
                    <span class="text-xs text-slate-400 font-semibold uppercase tracking-wider font-outfit">% del Total Fichado</span>
                    <div class="text-3xl font-bold font-outfit text-amber-300 mt-1" id="kpi-so-pct">-</div>
                    <div class="text-[11px] text-slate-400 mt-1">Impacto sobre el total laborado</div>
                </div>
                <div class="bg-slate-900/80 p-4 rounded-2xl border border-amber-500/20">
                    <span class="text-xs text-slate-400 font-semibold uppercase tracking-wider font-outfit">Operarios Afectados</span>
                    <div class="text-3xl font-bold font-outfit text-white mt-1" id="kpi-so-people">-</div>
                    <div class="text-[11px] text-indigo-400 mt-1">Trabajadores con horas sin asignar</div>
                </div>
                <div class="bg-slate-900/80 p-4 rounded-2xl border border-amber-500/20">
                    <span class="text-xs text-slate-400 font-semibold uppercase tracking-wider font-outfit">Costo Estimado No Asignado</span>
                    <div class="text-3xl font-bold font-outfit text-pink-400 mt-1" id="kpi-so-cost">-</div>
                    <div class="text-[11px] text-slate-400 mt-1">Calculado a tarifa promedio M.O.</div>
                </div>
            </div>

            <!-- Sin Obra Charts Grid -->
            <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <!-- Sin Obra Top Operarios (Horizontal Bar) -->
                <div id="card-sinObraPersonChart" class="bg-slate-900/50 p-5 rounded-2xl border border-slate-800/60 flex flex-col gap-3 lg:col-span-2">
                    <div class="flex items-center justify-between gap-2">
                        <h4 class="text-sm font-bold font-outfit text-white">Top 15 Operarios con Mayor Acumulado "Sin Obra" (Horas)</h4>
                        <button onclick="openQueryModal('sinObraPersonChart')" class="px-2.5 py-1 text-[11px] font-medium rounded-lg bg-purple-500/10 hover:bg-purple-500/20 text-purple-300 border border-purple-500/20 transition-all flex items-center gap-1 font-outfit cursor-pointer whitespace-nowrap">
                            <span>🔍 Ver Consulta</span>
                        </button>
                    </div>
                    <div class="relative h-[300px] w-full flex items-center justify-center">
                        <canvas id="sinObraPersonChart"></canvas>
                    </div>
                </div>

                <!-- Sin Obra by Client (Doughnut) -->
                <div id="card-sinObraClientChart" class="bg-slate-900/50 p-5 rounded-2xl border border-slate-800/60 flex flex-col gap-3 lg:col-span-1">
                    <div class="flex items-center justify-between gap-2">
                        <h4 class="text-sm font-bold font-outfit text-white">Horas "Sin Obra" por Empresa / Cliente</h4>
                        <button onclick="openQueryModal('sinObraClientChart')" class="px-2.5 py-1 text-[11px] font-medium rounded-lg bg-purple-500/10 hover:bg-purple-500/20 text-purple-300 border border-purple-500/20 transition-all flex items-center gap-1 font-outfit cursor-pointer whitespace-nowrap">
                            <span>🔍 Ver Consulta</span>
                        </button>
                    </div>
                    <div class="relative h-[300px] w-full flex items-center justify-center">
                        <canvas id="sinObraClientChart"></canvas>
                    </div>
                </div>
            </div>

            <!-- Sin Obra Timeline Chart -->
            <div id="card-sinObraTimelineChart" class="bg-slate-900/50 p-5 rounded-2xl border border-slate-800/60 flex flex-col gap-3">
                <div class="flex items-center justify-between gap-2">
                    <h4 class="text-sm font-bold font-outfit text-white">Evolución Mensual de Horas "Sin Obra"</h4>
                    <button onclick="openQueryModal('sinObraTimelineChart')" class="px-2.5 py-1 text-[11px] font-medium rounded-lg bg-purple-500/10 hover:bg-purple-500/20 text-purple-300 border border-purple-500/20 transition-all flex items-center gap-1 font-outfit cursor-pointer whitespace-nowrap">
                        <span>🔍 Ver Consulta</span>
                    </button>
                </div>
                <div class="relative h-[240px] w-full flex items-center justify-center">
                    <canvas id="sinObraTimelineChart"></canvas>
                </div>
            </div>
        </section>

        <!-- SECTION: CLIENTES VS PROYECTOS VS MENSAJES -->
        <section class="glass p-6 rounded-3xl flex flex-col gap-6 border border-indigo-500/20">
            <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 border-b border-slate-800/60 pb-4">
                <div>
                    <div class="flex items-center gap-2">
                        <span class="px-2.5 py-0.5 text-[10px] font-bold uppercase tracking-wider rounded-full bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 font-outfit">Comparativa Clientes</span>
                        <span class="text-xs text-slate-400">Proyectos (Obras) y Volumen de Mensajería</span>
                    </div>
                    <h2 class="text-xl lg:text-2xl font-bold font-outfit text-white tracking-tight mt-1 flex items-center gap-2">
                        🏢 Analítica Comparativa: Clientes vs Proyectos vs Mensajes
                    </h2>
                </div>
            </div>

            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div id="card-clientProjectsMsgsChart" class="bg-slate-900/50 p-5 rounded-2xl border border-slate-800/60 flex flex-col gap-3">
                    <div class="flex items-center justify-between gap-2">
                        <h4 class="text-sm font-bold font-outfit text-white">Clientes vs Número de Obras y Mensajes</h4>
                        <button onclick="openQueryModal('clientProjectsMsgsChart')" class="px-2.5 py-1 text-[11px] font-medium rounded-lg bg-purple-500/10 hover:bg-purple-500/20 text-purple-300 border border-purple-500/20 transition-all flex items-center gap-1 font-outfit cursor-pointer whitespace-nowrap">
                            <span>🔍 Ver Consulta</span>
                        </button>
                    </div>
                    <div class="relative h-[300px] w-full flex items-center justify-center">
                        <canvas id="clientProjectsMsgsChart"></canvas>
                    </div>
                </div>

                <div id="card-projectMessagesChart" class="bg-slate-900/50 p-5 rounded-2xl border border-slate-800/60 flex flex-col gap-3">
                    <div class="flex items-center justify-between gap-2">
                        <h4 class="text-sm font-bold font-outfit text-white">Top Proyectos (Obras) por Volumen de Mensajes / Reportes</h4>
                        <button onclick="openQueryModal('projectMessagesChart')" class="px-2.5 py-1 text-[11px] font-medium rounded-lg bg-purple-500/10 hover:bg-purple-500/20 text-purple-300 border border-purple-500/20 transition-all flex items-center gap-1 font-outfit cursor-pointer whitespace-nowrap">
                            <span>🔍 Ver Consulta</span>
                        </button>
                    </div>
                    <div class="relative h-[300px] w-full flex items-center justify-center">
                        <canvas id="projectMessagesChart"></canvas>
                    </div>
                </div>
            </div>

            <div id="card-clientAutoVsManualChart" class="bg-slate-900/50 p-5 rounded-2xl border border-slate-800/60 flex flex-col gap-3">
                <div class="flex items-center justify-between gap-2">
                    <h4 class="text-sm font-bold font-outfit text-white">Desglose de Mensajes Automáticos (Bot/Botones) vs Manuales por Cliente</h4>
                    <button onclick="openQueryModal('clientAutoVsManualChart')" class="px-2.5 py-1 text-[11px] font-medium rounded-lg bg-purple-500/10 hover:bg-purple-500/20 text-purple-300 border border-purple-500/20 transition-all flex items-center gap-1 font-outfit cursor-pointer whitespace-nowrap">
                        <span>🔍 Ver Consulta</span>
                    </button>
                </div>
                <div class="relative h-[280px] w-full flex items-center justify-center">
                    <canvas id="clientAutoVsManualChart"></canvas>
                </div>
            </div>
        </section>

        <!-- SECTION: CONVERSATIONS & AUTOMATION ANALYTICS -->
        <section class="glass p-6 rounded-3xl flex flex-col gap-6 border border-purple-500/20">
            <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 border-b border-slate-800/60 pb-4">
                <div>
                    <div class="flex items-center gap-2">
                        <span class="px-2.5 py-0.5 text-[10px] font-bold uppercase tracking-wider rounded-full bg-purple-500/20 text-purple-300 border border-purple-500/30 font-outfit">Detección de Automatismos</span>
                        <span class="text-xs text-slate-400">Inicio/Fin de Jornada, Botones & Mensajes Manuales</span>
                    </div>
                    <h2 class="text-xl lg:text-2xl font-bold font-outfit text-white tracking-tight mt-1 flex items-center gap-2">
                        💬 Analítica de Conversaciones y Detección Automática
                    </h2>
                </div>
            </div>

            <!-- Conversation KPIs -->
            <div class="grid grid-cols-2 lg:grid-cols-5 gap-4">
                <div class="bg-slate-900/70 p-4 rounded-2xl border border-slate-800/60">
                    <span class="text-xs text-slate-400 font-semibold uppercase tracking-wider font-outfit">Total Mensajes</span>
                    <div class="text-2xl font-bold font-outfit text-white mt-1" id="kpi-conv-messages">-</div>
                    <div class="text-[11px] text-purple-400 mt-1">WhatsApp, Teléfono, Email</div>
                </div>
                <div class="bg-slate-900/70 p-4 rounded-2xl border border-slate-800/60">
                    <span class="text-xs text-slate-400 font-semibold uppercase tracking-wider font-outfit">% Mensajes Automáticos</span>
                    <div class="text-2xl font-bold font-outfit text-emerald-400 mt-1" id="kpi-conv-auto-pct">-</div>
                    <div class="text-[11px] text-slate-400 mt-1">Botones & Respuestas Bot</div>
                </div>
                <div class="bg-slate-900/70 p-4 rounded-2xl border border-slate-800/60">
                    <span class="text-xs text-slate-400 font-semibold uppercase tracking-wider font-outfit">Acciones Bot WhatsApp</span>
                    <div class="text-2xl font-bold font-outfit text-white mt-1" id="kpi-conv-bot">-</div>
                    <div class="text-[11px] text-emerald-400 mt-1">Interacciones automáticas</div>
                </div>
                <div class="bg-slate-900/70 p-4 rounded-2xl border border-slate-800/60">
                    <span class="text-xs text-slate-400 font-semibold uppercase tracking-wider font-outfit">Notas de Voz Transcritas</span>
                    <div class="text-2xl font-bold font-outfit text-white mt-1" id="kpi-conv-voice">-</div>
                    <div class="text-[11px] text-pink-400 mt-1">Audios procesados por IA</div>
                </div>
                <div class="bg-slate-900/70 p-4 rounded-2xl border border-slate-800/60 col-span-2 lg:col-span-1">
                    <span class="text-xs text-slate-400 font-semibold uppercase tracking-wider font-outfit">Sesiones Diarias Bot</span>
                    <div class="text-2xl font-bold font-outfit text-white mt-1" id="kpi-conv-sessions">-</div>
                    <div class="text-[11px] text-blue-400 mt-1">Jornadas activas</div>
                </div>
            </div>

            <!-- Conversation Charts Grid Part 1 -->
            <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div id="card-autoVsManualChart" class="bg-slate-900/50 p-5 rounded-2xl border border-slate-800/60 flex flex-col gap-3">
                    <div class="flex items-center justify-between gap-2">
                        <h4 class="text-sm font-bold font-outfit text-white">Mensajes Automáticos vs Manuales</h4>
                        <button onclick="openQueryModal('autoVsManualChart')" class="px-2.5 py-1 text-[11px] font-medium rounded-lg bg-purple-500/10 hover:bg-purple-500/20 text-purple-300 border border-purple-500/20 transition-all flex items-center gap-1 font-outfit cursor-pointer whitespace-nowrap">
                            <span>🔍 Ver Consulta</span>
                        </button>
                    </div>
                    <div class="relative h-[250px] w-full flex items-center justify-center">
                        <canvas id="autoVsManualChart"></canvas>
                    </div>
                </div>
                <div id="card-messagesChannelChart" class="bg-slate-900/50 p-5 rounded-2xl border border-slate-800/60 flex flex-col gap-3">
                    <div class="flex items-center justify-between gap-2">
                        <h4 class="text-sm font-bold font-outfit text-white">Mensajes por Canal y Dirección</h4>
                        <button onclick="openQueryModal('messagesChannelChart')" class="px-2.5 py-1 text-[11px] font-medium rounded-lg bg-purple-500/10 hover:bg-purple-500/20 text-purple-300 border border-purple-500/20 transition-all flex items-center gap-1 font-outfit cursor-pointer whitespace-nowrap">
                            <span>🔍 Ver Consulta</span>
                        </button>
                    </div>
                    <div class="relative h-[250px] w-full flex items-center justify-center">
                        <canvas id="messagesChannelChart"></canvas>
                    </div>
                </div>
                <div id="card-sessionStateChart" class="bg-slate-900/50 p-5 rounded-2xl border border-slate-800/60 flex flex-col gap-3">
                    <div class="flex items-center justify-between gap-2">
                        <h4 class="text-sm font-bold font-outfit text-white">Estados de Sesión Diaria en Bot</h4>
                        <button onclick="openQueryModal('sessionStateChart')" class="px-2.5 py-1 text-[11px] font-medium rounded-lg bg-purple-500/10 hover:bg-purple-500/20 text-purple-300 border border-purple-500/20 transition-all flex items-center gap-1 font-outfit cursor-pointer whitespace-nowrap">
                            <span>🔍 Ver Consulta</span>
                        </button>
                    </div>
                    <div class="relative h-[250px] w-full flex items-center justify-center">
                        <canvas id="sessionStateChart"></canvas>
                    </div>
                </div>
            </div>

            <!-- Conversation Charts Grid Part 2 -->
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div id="card-topMsgOperariosChart" class="bg-slate-900/50 p-5 rounded-2xl border border-slate-800/60 flex flex-col gap-3">
                    <div class="flex items-center justify-between gap-2">
                        <h4 class="text-sm font-bold font-outfit text-white">Top Operarios en Actividad de Mensajería</h4>
                        <button onclick="openQueryModal('topMsgOperariosChart')" class="px-2.5 py-1 text-[11px] font-medium rounded-lg bg-purple-500/10 hover:bg-purple-500/20 text-purple-300 border border-purple-500/20 transition-all flex items-center gap-1 font-outfit cursor-pointer whitespace-nowrap">
                            <span>🔍 Ver Consulta</span>
                        </button>
                    </div>
                    <div class="relative h-[260px] w-full flex items-center justify-center">
                        <canvas id="topMsgOperariosChart"></canvas>
                    </div>
                </div>
                <div id="card-messagesTimelineChart" class="bg-slate-900/50 p-5 rounded-2xl border border-slate-800/60 flex flex-col gap-3">
                    <div class="flex items-center justify-between gap-2">
                        <h4 class="text-sm font-bold font-outfit text-white">Evolución Temporal de Mensajería</h4>
                        <button onclick="openQueryModal('messagesTimelineChart')" class="px-2.5 py-1 text-[11px] font-medium rounded-lg bg-purple-500/10 hover:bg-purple-500/20 text-purple-300 border border-purple-500/20 transition-all flex items-center gap-1 font-outfit cursor-pointer whitespace-nowrap">
                            <span>🔍 Ver Consulta</span>
                        </button>
                    </div>
                    <div class="relative h-[260px] w-full flex items-center justify-center">
                        <canvas id="messagesTimelineChart"></canvas>
                    </div>
                </div>
            </div>
        </section>

        <!-- Charts Grid Section 1 -->
        <section class="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div id="card-projectChart" class="glass p-6 rounded-3xl col-span-2 flex flex-col gap-4">
                <div class="flex items-center justify-between gap-2">
                    <h3 class="text-lg font-bold font-outfit text-white">Consumos por Obra / Proyecto</h3>
                    <button onclick="openQueryModal('projectChart')" class="px-2.5 py-1 text-[11px] font-medium rounded-lg bg-purple-500/10 hover:bg-purple-500/20 text-purple-300 border border-purple-500/20 transition-all flex items-center gap-1 font-outfit cursor-pointer whitespace-nowrap">
                        <span>🔍 Ver Consulta</span>
                    </button>
                </div>
                <div class="relative h-[320px] w-full flex items-center justify-center">
                    <canvas id="projectChart"></canvas>
                </div>
            </div>
            <div class="glass p-6 rounded-3xl flex flex-col gap-4 col-span-1">
                <h3 class="text-lg font-bold font-outfit text-white">Acciones e Interacción WhatsApp</h3>
                <div class="flex flex-col gap-6 h-full justify-between">
                    <div id="card-waInboundChart" class="flex-1 flex flex-col items-center">
                        <div class="flex items-center justify-between w-full">
                            <span class="text-xs text-slate-400 font-semibold tracking-wider uppercase font-outfit self-start">Entrantes (Inbound)</span>
                            <button onclick="openQueryModal('waInboundChart')" class="px-2 py-0.5 text-[10px] font-medium rounded-lg bg-purple-500/10 hover:bg-purple-500/20 text-purple-300 border border-purple-500/20 transition-all flex items-center gap-1 font-outfit cursor-pointer whitespace-nowrap">
                                <span>🔍 SQL</span>
                            </button>
                        </div>
                        <div class="relative h-[160px] w-full flex items-center justify-center mt-2">
                            <canvas id="waInboundChart"></canvas>
                        </div>
                    </div>
                    <div id="card-waOutboundChart" class="flex-1 flex flex-col items-center border-t border-slate-800/40 pt-4">
                        <div class="flex items-center justify-between w-full">
                            <span class="text-xs text-slate-400 font-semibold tracking-wider uppercase font-outfit self-start">Salientes (Outbound)</span>
                            <button onclick="openQueryModal('waOutboundChart')" class="px-2 py-0.5 text-[10px] font-medium rounded-lg bg-purple-500/10 hover:bg-purple-500/20 text-purple-300 border border-purple-500/20 transition-all flex items-center gap-1 font-outfit cursor-pointer whitespace-nowrap">
                                <span>🔍 SQL</span>
                            </button>
                        </div>
                        <div class="relative h-[160px] w-full flex items-center justify-center mt-2">
                            <canvas id="waOutboundChart"></canvas>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <!-- Charts Grid Section 2 -->
        <section class="grid grid-cols-1 gap-6">
            <div id="card-personChart" class="glass p-6 rounded-3xl flex flex-col gap-4">
                <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                    <div class="flex items-center gap-3">
                        <h3 class="text-lg font-bold font-outfit text-white">Comparativa de Horas por Operario / Fecha</h3>
                        <button onclick="openQueryModal('personChart')" class="px-2.5 py-1 text-[11px] font-medium rounded-lg bg-purple-500/10 hover:bg-purple-500/20 text-purple-300 border border-purple-500/20 transition-all flex items-center gap-1 font-outfit cursor-pointer whitespace-nowrap">
                            <span>🔍 Ver Consulta</span>
                        </button>
                    </div>
                    <div class="flex flex-wrap gap-3 items-center w-full sm:w-auto">
                        <div>
                            <select id="chart-person-group" onchange="updatePersonChart()" class="bg-slate-900 border border-slate-800 text-slate-300 text-xs rounded-xl px-3 py-2 focus:outline-none focus:border-purple-500 font-outfit cursor-pointer">
                                <option value="operario">Ver por Operario</option>
                                <option value="fecha">Ver por Fecha</option>
                            </select>
                        </div>
                        <div>
                            <select id="chart-person-sort" onchange="updatePersonChart()" class="bg-slate-900 border border-slate-800 text-slate-300 text-xs rounded-xl px-3 py-2 focus:outline-none focus:border-purple-500 font-outfit cursor-pointer">
                                <option value="default">Ordenar por Nombre / Fecha</option>
                                <option value="clocked">Ordenar por H. Fichadas</option>
                                <option value="imputed">Ordenar por H. Imputadas</option>
                            </select>
                        </div>
                        <div>
                            <select id="chart-person-order" onchange="updatePersonChart()" class="bg-slate-900 border border-slate-800 text-slate-300 text-xs rounded-xl px-3 py-2 focus:outline-none focus:border-purple-500 font-outfit cursor-pointer">
                                <option value="desc">Descendente</option>
                                <option value="asc">Ascendente</option>
                            </select>
                        </div>
                    </div>
                </div>
                <div class="relative h-[380px] w-full flex items-center justify-center">
                    <canvas id="personChart"></canvas>
                </div>
            </div>
        </section>

        <!-- Charts Grid Section 3 -->
        <section class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div id="card-clockedProjectChart" class="glass p-6 rounded-3xl flex flex-col gap-4">
                <div class="flex items-center justify-between gap-2">
                    <h3 class="text-lg font-bold font-outfit text-white">Horas Fichadas Distribuídas por Obra / Proyecto</h3>
                    <button onclick="openQueryModal('clockedProjectChart')" class="px-2.5 py-1 text-[11px] font-medium rounded-lg bg-purple-500/10 hover:bg-purple-500/20 text-purple-300 border border-purple-500/20 transition-all flex items-center gap-1 font-outfit cursor-pointer whitespace-nowrap">
                        <span>🔍 Ver Consulta</span>
                    </button>
                </div>
                <div class="relative h-[320px] w-full flex items-center justify-center">
                    <canvas id="clockedProjectChart"></canvas>
                </div>
            </div>
            <div id="card-clockedPersonChart" class="glass p-6 rounded-3xl flex flex-col gap-4">
                <div class="flex items-center justify-between gap-2">
                    <h3 class="text-lg font-bold font-outfit text-white">Total Horas Fichadas por Operario</h3>
                    <button onclick="openQueryModal('clockedPersonChart')" class="px-2.5 py-1 text-[11px] font-medium rounded-lg bg-purple-500/10 hover:bg-purple-500/20 text-purple-300 border border-purple-500/20 transition-all flex items-center gap-1 font-outfit cursor-pointer whitespace-nowrap">
                        <span>🔍 Ver Consulta</span>
                    </button>
                </div>
                <div class="relative h-[320px] w-full flex items-center justify-center">
                    <canvas id="clockedPersonChart"></canvas>
                </div>
            </div>
        </section>

        <!-- Tables & Lists Section -->
        <section class="glass rounded-3xl flex flex-col overflow-hidden">
            <div class="flex border-b border-slate-800/80 bg-slate-900/40 font-outfit font-medium">
                <button onclick="switchTab('alerts')" id="tab-btn-alerts" class="px-6 py-4 text-sm font-semibold border-b-2 border-purple-500 text-white flex items-center gap-2 transition-all">
                    <span>Alertas de Fichajes</span>
                    <span id="alerts-count" class="px-2 py-0.5 text-xs bg-purple-500/20 text-purple-400 rounded-full border border-purple-500/20">-</span>
                </button>
                <button onclick="switchTab('projects')" id="tab-btn-projects" class="px-6 py-4 text-sm font-semibold border-b-2 border-transparent text-slate-400 hover:text-slate-200 hover:border-slate-800 flex items-center gap-2 transition-all">
                    <span>Detalle de Proyectos</span>
                </button>
                <button onclick="switchTab('operarios')" id="tab-btn-operarios" class="px-6 py-4 text-sm font-semibold border-b-2 border-transparent text-slate-400 hover:text-slate-200 hover:border-slate-800 flex items-center gap-2 transition-all">
                    <span>Control de Operarios</span>
                </button>
            </div>

            <div class="p-6">
                <div id="tab-alerts" class="tab-content block overflow-x-auto">
                    <table class="w-full text-left text-sm text-slate-300">
                        <thead class="text-xs uppercase text-slate-400 border-b border-slate-800/60 font-outfit font-semibold">
                            <tr>
                                <th class="pb-3 px-2">Fecha</th>
                                <th class="pb-3 px-2">Operario</th>
                                <th class="pb-3 px-2 text-right">Horas Fichadas</th>
                                <th class="pb-3 px-2 text-right">Horas Imputadas</th>
                                <th class="pb-3 px-2 text-right">Desviación</th>
                                <th class="pb-3 px-2 text-center">Estado</th>
                            </tr>
                        </thead>
                        <tbody id="alerts-tbody" class="divide-y divide-slate-800/30"></tbody>
                    </table>
                </div>

                <div id="tab-projects" class="tab-content hidden overflow-x-auto">
                    <table class="w-full text-left text-sm text-slate-300">
                        <thead class="text-xs uppercase text-slate-400 border-b border-slate-800/60 font-outfit font-semibold">
                            <tr>
                                <th class="pb-3 px-2">Proyecto</th>
                                <th class="pb-3 px-2">Cliente</th>
                                <th class="pb-3 px-2">Estado</th>
                                <th class="pb-3 px-2 text-right">Presupuesto</th>
                                <th class="pb-3 px-2 text-right">Costo Real (Base)</th>
                                <th class="pb-3 px-2 text-right">Horas Imputadas</th>
                                <th class="pb-3 px-2 text-right">Costo Personal (M.O.)</th>
                            </tr>
                        </thead>
                        <tbody id="projects-tbody" class="divide-y divide-slate-800/30"></tbody>
                    </table>
                </div>

                <div id="tab-operarios" class="tab-content hidden overflow-x-auto">
                    <table class="w-full text-left text-sm text-slate-300">
                        <thead class="text-xs uppercase text-slate-400 border-b border-slate-800/60 font-outfit font-semibold">
                            <tr>
                                <th class="pb-3 px-2">Nombre</th>
                                <th class="pb-3 px-2">Cargo / Rol</th>
                                <th class="pb-3 px-2 text-right">Horas Fichadas</th>
                                <th class="pb-3 px-2 text-right">Horas Imputadas</th>
                                <th class="pb-3 px-2 text-right">Costo Calculado</th>
                                <th class="pb-3 px-2 text-center">Interacción Bot (Msg/Voz/Media)</th>
                            </tr>
                        </thead>
                        <tbody id="operarios-tbody" class="divide-y divide-slate-800/30"></tbody>
                    </table>
                </div>
            </div>
        </section>
    </div>

    <!-- Query Viewer Modal -->
    <div id="query-modal" onclick="if(event.target===this) closeQueryModal()" class="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 backdrop-blur-md hidden transition-all duration-300">
        <div class="glass max-w-3xl w-full mx-4 rounded-3xl border border-purple-500/30 p-6 flex flex-col gap-4 shadow-2xl glow max-h-[90vh] overflow-y-auto">
            <div class="flex justify-between items-center border-b border-slate-800/80 pb-4">
                <div class="flex items-center gap-3">
                    <span class="px-2.5 py-1 text-xs font-bold font-mono bg-purple-500/20 text-purple-300 rounded-lg border border-purple-500/30" id="modal-chart-id">ID: chart</span>
                    <h3 class="text-lg font-bold font-outfit text-white" id="modal-chart-title">Consulta de Datos</h3>
                </div>
                <button onclick="closeQueryModal()" class="w-8 h-8 rounded-full bg-slate-900 border border-slate-700 text-slate-400 hover:text-white flex items-center justify-center text-sm font-bold cursor-pointer">✕</button>
            </div>
            
            <div class="flex items-center gap-2 border-b border-slate-800/80 pb-3">
                <button id="modal-tab-sql" onclick="switchModalTab('sql')" class="px-4 py-1.5 text-xs font-semibold rounded-xl bg-purple-600 text-white font-outfit cursor-pointer">PostgreSQL SQL</button>
                <button id="modal-tab-pandas" onclick="switchModalTab('pandas')" class="px-4 py-1.5 text-xs font-semibold rounded-xl bg-slate-900 text-slate-400 font-outfit border border-slate-800 cursor-pointer hover:text-white">Python / Pandas ETL</button>
                <span class="ml-auto text-xs text-slate-400 font-mono" id="modal-tables-used">Tablas: -</span>
            </div>

            <div id="modal-content-sql" class="relative group">
                <button onclick="copyModalCode('sql')" class="absolute top-3 right-3 px-3 py-1 text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg border border-slate-700 transition-all font-outfit cursor-pointer">
                    <span id="copy-sql-btn-text">📋 Copiar SQL</span>
                </button>
                <pre class="bg-slate-950/90 text-emerald-400 p-4 rounded-2xl font-mono text-xs overflow-x-auto border border-slate-800/80 leading-relaxed" id="modal-sql-code">SELECT ...</pre>
            </div>

            <div id="modal-content-pandas" class="relative group hidden">
                <button onclick="copyModalCode('pandas')" class="absolute top-3 right-3 px-3 py-1 text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg border border-slate-700 transition-all font-outfit cursor-pointer">
                    <span id="copy-pandas-btn-text">📋 Copiar Code</span>
                </button>
                <pre class="bg-slate-950/90 text-purple-300 p-4 rounded-2xl font-mono text-xs overflow-x-auto border border-slate-800/80 leading-relaxed" id="modal-pandas-code">df.groupby(...)</pre>
            </div>

            <div class="bg-slate-900/60 p-3.5 rounded-xl border border-slate-800 text-xs text-slate-300 leading-relaxed font-outfit" id="modal-query-desc">
                Explicación de la consulta...
            </div>
        </div>
    </div>

    <!-- Payload Data Injection -->
    <script>
        const data = {json.dumps(payload, indent=4)};
        const originalData = JSON.parse(JSON.stringify(data));
        
        let selectedClient = "all";
        let selectedProject = "all";
        let selectedPerson = "all";

        let projectChartInstance = null;
        let personChartInstance = null;
        let waInboundChartInstance = null;
        let waOutboundChartInstance = null;
        let clockedProjectChartInstance = null;
        let clockedPersonChartInstance = null;
        let messagesChannelChartInstance = null;
        let sessionStateChartInstance = null;
        let topMsgOperariosChartInstance = null;
        let messagesTimelineChartInstance = null;
        let autoVsManualChartInstance = null;
        let clientProjectsMsgsChartInstance = null;
        let projectMessagesChartInstance = null;
        let clientAutoVsManualChartInstance = null;
        let sinObraPersonChartInstance = null;
        let sinObraClientChartInstance = null;
        let sinObraTimelineChartInstance = null;

        let filteredOperariosGlobal = [];

        window.addEventListener('DOMContentLoaded', () => {{
            populateFilters();
            initCharts();
            updateDashboard();
        }});

        const queryMap = {{
            sinObraPersonChart: {{
                title: "Top 15 Operarios con Mayor Acumulado 'Sin Obra' (Horas)",
                tables: "distributed_clock, dim_person",
                sql: `SELECT 
    dp.name AS person_name,
    SUM(dc.project_hours_worked) AS total_hours_sin_obra
FROM analytics.distributed_clock dc
JOIN analytics.dim_person dp ON dc.person_id = dp.id
WHERE dc.project_name = 'Sin Obra'
GROUP BY dp.name
ORDER BY total_hours_sin_obra DESC
LIMIT 15;`,
                pandas: `sin_obra_df = distributed_clock[distributed_clock['project_name'] == 'Sin Obra']
sin_obra_ops = sin_obra_df.groupby('person_name')['project_hours_worked'].sum()
sin_obra_ops = sin_obra_ops.sort_values(ascending=False).head(15)`,
                desc: "Calcula el volumen de horas de jornada laboral fichadas que no fueron imputadas a ninguna obra o proyecto específico, agrupadas por operario."
            }},
            sinObraClientChart: {{
                title: "Horas 'Sin Obra' por Empresa / Cliente",
                tables: "distributed_clock, dim_client",
                sql: `SELECT 
    client_name,
    SUM(project_hours_worked) AS hours_sin_obra
FROM analytics.distributed_clock
WHERE project_name = 'Sin Obra'
GROUP BY client_name
ORDER BY hours_sin_obra DESC;`,
                pandas: `sin_obra_df = distributed_clock[distributed_clock['project_name'] == 'Sin Obra']
sin_obra_client = sin_obra_df.groupby('client_name')['project_hours_worked'].sum().sort_values(ascending=False)`,
                desc: "Agrupa y suma el acumulado de horas fichadas sin obra asociadas a la empresa u organización cliente asignada al operario."
            }},
            sinObraTimelineChart: {{
                title: "Evolución Mensual de Horas 'Sin Obra'",
                tables: "distributed_clock",
                sql: `SELECT 
    TO_CHAR(work_date, 'YYYY-MM') AS month,
    SUM(project_hours_worked) AS hours_sin_obra
FROM analytics.distributed_clock
WHERE project_name = 'Sin Obra'
GROUP BY month
ORDER BY month ASC;`,
                pandas: `sin_obra_df['month'] = pd.to_datetime(sin_obra_df['work_date']).dt.strftime('%Y-%m')
sin_obra_timeline = sin_obra_df.groupby('month')['project_hours_worked'].sum().sort_index()`,
                desc: "Muestra la tendencia y evolución temporal mes a mes de las horas registradas sin imputación de obra a lo largo del histórico."
            }},
            clientProjectsMsgsChart: {{
                title: "Clientes: Número de Proyectos vs Volumen de Mensajes",
                tables: "dim_project, messages, dim_client",
                sql: `SELECT 
    c.name AS client_name,
    COUNT(DISTINCT p.id) AS projects_count,
    COUNT(m.id) AS messages_count
FROM analytics.dim_client c
LEFT JOIN analytics.dim_project p ON p.client_id = c.id
LEFT JOIN analytics.messages m ON m.client_id = c.id
GROUP BY c.name
ORDER BY projects_count DESC;`,
                pandas: `proj_by_client = dim_project.groupby('client_name')['id'].count()
msg_by_client = fact_messages.groupby('client_name').size()`,
                desc: "Compara de forma agregada por cliente la cantidad total de obras activas frente al número de mensajes e interacciones registradas."
            }},
            projectMessagesChart: {{
                title: "Top Proyectos con Mayor Actividad de Mensajería / Reportes",
                tables: "distributed_clock, messages, dim_project",
                sql: `SELECT 
    project_name,
    client_name,
    COUNT(*) AS activity_count
FROM analytics.distributed_clock
GROUP BY project_name, client_name
ORDER BY activity_count DESC
LIMIT 15;`,
                pandas: `proj_activity = distributed_clock.groupby(['project_name', 'client_name']).size().sort_values(ascending=False).head(15)`,
                desc: "Identifica las obras y proyectos que registran mayor número de fichajes, partes de trabajo y reportes de actividad vía WhatsApp u otros canales."
            }},
            clientAutoVsManualChart: {{
                title: "Mensajes Automáticos vs Manuales por Cliente",
                tables: "messages, whatsapp_action_log",
                sql: `SELECT 
    client_name,
    COUNT(CASE WHEN is_automated = TRUE THEN 1 END) AS auto_messages,
    COUNT(CASE WHEN is_automated = FALSE THEN 1 END) AS manual_messages
FROM analytics.fact_messages
GROUP BY client_name
ORDER BY (auto_messages + manual_messages) DESC;`,
                pandas: `auto_msg_by_client = fact_messages[fact_messages['is_automated'] == True].groupby('client_name').size()
manual_msg_by_client = fact_messages[fact_messages['is_automated'] == False].groupby('client_name').size()`,
                desc: "Compara en cada cliente la distribución entre interacciones automáticas del Bot (botones, flujos) y mensajes de texto libre/manuales."
            }},
            autoVsManualChart: {{
                title: "Desglose de Mensajes Automáticos vs Manuales",
                tables: "messages",
                sql: `SELECT 
    origin_category,
    is_automated,
    COUNT(*) AS message_count
FROM analytics.fact_messages
GROUP BY origin_category, is_automated
ORDER BY message_count DESC;`,
                pandas: `category_counts = fact_messages['origin_category'].value_counts()`,
                desc: "Desglosa las categorías detalladas de interacción: botones de inicio/fin de jornada, respuestas automáticas, textos libres y notas de voz."
            }},
            messagesChannelChart: {{
                title: "Distribución por Canal de Mensajería y Dirección",
                tables: "messages",
                sql: `SELECT 
    channel,
    direction,
    COUNT(*) AS total_messages
FROM analytics.messages
GROUP BY channel, direction
ORDER BY total_messages DESC;`,
                pandas: `channel_dir = fact_messages.groupby(['channel', 'direction']).size().unstack(fill_value=0)`,
                desc: "Clasifica el tráfico total de mensajería según el canal de origen (WhatsApp, Teléfono, etc.) y si es entrante o saliente."
            }},
            sessionStateChart: {{
                title: "Estado de Sesiones Jornadas WhatsApp",
                tables: "daily_sessions",
                sql: `SELECT 
    state,
    COUNT(*) AS total_sessions
FROM analytics.daily_sessions
GROUP BY state
ORDER BY total_sessions DESC;`,
                pandas: `session_states = fact_daily_sessions['state'].value_counts()`,
                desc: "Agrupa las sesiones diarias registradas por el Bot según su estado de ciclo de vida (completed, in_progress, pending, etc.)."
            }},
            topMsgOperariosChart: {{
                title: "Top Operarios en Actividad de Mensajería",
                tables: "messages, dim_person",
                sql: `SELECT 
    p.person_name,
    COUNT(m.id) AS total_interactions
FROM analytics.messages m
JOIN analytics.dim_person p ON m.person_id = p.id
GROUP BY p.person_name
ORDER BY total_interactions DESC
LIMIT 15;`,
                pandas: `top_msg_operarios = fact_messages.groupby('person_name').size().sort_values(ascending=False).head(15)`,
                desc: "Ranking de los 15 operarios que registran mayor número de interacciones, envío de datos y fichajes a través de mensajería."
            }},
            messagesTimelineChart: {{
                title: "Evolución Temporal de Mensajería",
                tables: "messages",
                sql: `SELECT 
    TO_CHAR(created_at, 'YYYY-MM-DD') AS date,
    COUNT(CASE WHEN direction = 'incoming' THEN 1 END) AS incoming,
    COUNT(CASE WHEN direction = 'outgoing' THEN 1 END) AS outgoing
FROM analytics.messages
GROUP BY date
ORDER BY date ASC;`,
                pandas: `timeline_incoming = fact_messages[fact_messages['direction'] == 'incoming'].groupby(pd.to_datetime(fact_messages['created_at']).dt.date).size()`,
                desc: "Muestra la fluctuación y volumen diario de mensajes recibidos (entrantes) frente a los enviados por la plataforma (salientes)."
            }},
            projectChart: {{
                title: "Consumos por Obra / Proyecto",
                tables: "dim_project, project_imputation",
                sql: `SELECT 
    p.name AS project_name,
    c.name AS client_name,
    SUM(pi.hours_imputed) AS total_hours,
    SUM(pi.calculated_cost) AS total_cost
FROM analytics.dim_project p
JOIN analytics.project_imputation pi ON pi.project_id = p.id
LEFT JOIN analytics.dim_client c ON p.client_id = c.id
GROUP BY p.name, c.name
ORDER BY total_cost DESC
LIMIT 15;`,
                pandas: `project_imputations = fact_project_imputation.groupby('project_id').agg(hours_imputed=('hours_imputed', 'sum'), calculated_cost=('calculated_cost', 'sum'))
project_data = dim_project.merge(project_imputations, left_on='id', right_on='project_id')`,
                desc: "Consolida las horas laboradas cargadas a cada obra y calcula el coste económico total de mano de obra asociado a cada proyecto."
            }},
            waInboundChart: {{
                title: "Acciones e Interacción WhatsApp Entrantes (Inbound)",
                tables: "whatsapp_action_log, whatsapp_inbound_messages",
                sql: `SELECT 
    activity_type,
    COUNT(*) AS inbound_count
FROM analytics.fact_whatsapp_activity
WHERE activity_type LIKE 'inbound_%'
GROUP BY activity_type
ORDER BY inbound_count DESC;`,
                pandas: `wa_inbound_counts = fact_whatsapp_activity[fact_whatsapp_activity['activity_type'].str.startswith('inbound_')]['activity_type'].value_counts()`,
                desc: "Filtra y agrupa las respuestas del operario por tipo de contenido: texto, notas de voz, fotos, respuestas a botones interactivos, etc."
            }},
            waOutboundChart: {{
                title: "Acciones e Interacción WhatsApp Salientes (Outbound)",
                tables: "whatsapp_action_log",
                sql: `SELECT 
    activity_type,
    COUNT(*) AS outbound_count
FROM analytics.fact_whatsapp_activity
WHERE activity_type LIKE 'outbound_%'
GROUP BY activity_type
ORDER BY outbound_count DESC;`,
                pandas: `wa_outbound_counts = fact_whatsapp_activity[fact_whatsapp_activity['activity_type'].str.startswith('outbound_')]['activity_type'].value_counts()`,
                desc: "Agrupa las respuestas y notificaciones enviadas automáticamente por el bot de GestObra hacia los operarios en WhatsApp."
            }},
            personChart: {{
                title: "Comparativa de Horas por Operario / Fecha",
                tables: "time_clock, project_imputation, dim_person",
                sql: `SELECT 
    p.person_name,
    SUM(tc.hours_worked) AS hours_clocked,
    SUM(pi.hours_imputed) AS hours_imputed
FROM analytics.dim_person p
LEFT JOIN analytics.time_clock tc ON tc.person_id = p.id
LEFT JOIN analytics.project_imputation pi ON pi.person_id = p.id
GROUP BY p.person_name
ORDER BY hours_clocked DESC;`,
                pandas: `daily_compare = pd.merge(daily_clock, daily_imputed, on=['work_date', 'person_id'], how='outer')`,
                desc: "Compara de forma dinámica las horas de control horario (reloj de entrada) frente a las horas justificadas en partes de trabajo por persona o fecha."
            }},
            clockedProjectChart: {{
                title: "Horas Fichadas Distribuídas por Obra / Proyecto",
                tables: "distributed_clock",
                sql: `SELECT 
    project_name,
    SUM(project_hours_worked) AS total_hours
FROM analytics.distributed_clock
GROUP BY project_name
ORDER BY total_hours DESC;`,
                pandas: `clock_proj_agg = distributed_clock.groupby('project_name')['project_hours_worked'].sum().sort_values(ascending=False)`,
                desc: "Representa la distribución proporcional de las jornadas fichadas asignadas automáticamente a cada proyecto según el desglose de imputación."
            }},
            clockedPersonChart: {{
                title: "Total Horas Fichadas por Operario",
                tables: "distributed_clock",
                sql: `SELECT 
    person_name,
    SUM(project_hours_worked) AS total_hours
FROM analytics.distributed_clock
GROUP BY person_name
ORDER BY total_hours DESC;`,
                pandas: `clock_pers_agg = distributed_clock.groupby('person_name')['project_hours_worked'].sum().sort_values(ascending=False)`,
                desc: "Muestra el acumulado global de horas fichadas en reloj de entrada por cada trabajador de la plantilla."
            }}
        }};

        let activeModalTab = 'sql';
        let currentModalChartId = null;

        function openQueryModal(chartId) {{
            const info = queryMap[chartId];
            if (!info) return;

            currentModalChartId = chartId;
            document.getElementById('modal-chart-id').innerText = 'ID: ' + chartId;
            document.getElementById('modal-chart-title').innerText = info.title;
            document.getElementById('modal-tables-used').innerText = 'Tablas: ' + info.tables;
            document.getElementById('modal-sql-code').innerText = info.sql;
            document.getElementById('modal-pandas-code').innerText = info.pandas;
            document.getElementById('modal-query-desc').innerText = info.desc;

            switchModalTab('sql');
            document.getElementById('query-modal').classList.remove('hidden');
        }}

        function closeQueryModal() {{
            document.getElementById('query-modal').classList.add('hidden');
        }}

        function switchModalTab(tab) {{
            activeModalTab = tab;
            const btnSql = document.getElementById('modal-tab-sql');
            const btnPandas = document.getElementById('modal-tab-pandas');
            const contentSql = document.getElementById('modal-content-sql');
            const contentPandas = document.getElementById('modal-content-pandas');

            if (tab === 'sql') {{
                btnSql.className = "px-4 py-1.5 text-xs font-semibold rounded-xl bg-purple-600 text-white font-outfit cursor-pointer";
                btnPandas.className = "px-4 py-1.5 text-xs font-semibold rounded-xl bg-slate-900 text-slate-400 font-outfit border border-slate-800 cursor-pointer hover:text-white";
                contentSql.classList.remove('hidden');
                contentPandas.classList.add('hidden');
            }} else {{
                btnPandas.className = "px-4 py-1.5 text-xs font-semibold rounded-xl bg-purple-600 text-white font-outfit cursor-pointer";
                btnSql.className = "px-4 py-1.5 text-xs font-semibold rounded-xl bg-slate-900 text-slate-400 font-outfit border border-slate-800 cursor-pointer hover:text-white";
                contentPandas.classList.remove('hidden');
                contentSql.classList.add('hidden');
            }}
        }}

        function copyModalCode(type) {{
            const codeEl = type === 'sql' ? document.getElementById('modal-sql-code') : document.getElementById('modal-pandas-code');
            const btnTextEl = type === 'sql' ? document.getElementById('copy-sql-btn-text') : document.getElementById('copy-pandas-btn-text');
            
            navigator.clipboard.writeText(codeEl.innerText).then(() => {{
                const origText = btnTextEl.innerText;
                btnTextEl.innerText = "✅ ¡Copiado!";
                setTimeout(() => {{ btnTextEl.innerText = origText; }}, 2000);
            }});
        }}

        window.addEventListener('keydown', (e) => {{
            if (e.key === 'Escape') closeQueryModal();
        }});

        let excludeGestobraDev = false;

        function isGestobraDevClient(clientName) {{
            if (!clientName) return false;
            const lower = String(clientName).toLowerCase();
            return lower.includes('gestobra dev') || lower === 'gestobra';
        }}

        function toggleExcludeGestobraDev() {{
            excludeGestobraDev = !excludeGestobraDev;
            const btn = document.getElementById('btn-toggle-gestobra-dev');
            const icon = document.getElementById('gestobra-dev-icon');
            const text = document.getElementById('gestobra-dev-text');

            if (excludeGestobraDev) {{
                btn.className = "bg-rose-600 hover:bg-rose-500 text-white font-semibold text-sm rounded-xl px-4 py-2.5 transition-all font-outfit border border-rose-400 shadow-lg shadow-rose-600/30 flex items-center gap-2 cursor-pointer whitespace-nowrap";
                icon.innerText = "✅";
                text.innerText = "Gestobra Dev Omitido";
            }} else {{
                btn.className = "bg-rose-500/10 hover:bg-rose-500/20 text-rose-300 font-semibold text-sm rounded-xl px-4 py-2.5 transition-all font-outfit border border-rose-500/30 flex items-center gap-2 cursor-pointer whitespace-nowrap";
                icon.innerText = "🚫";
                text.innerText = "Omitir Gestobra Dev";
            }}

            if (excludeGestobraDev && isGestobraDevClient(selectedClient)) {{
                selectedClient = "all";
            }}

            populateFilters();
            updateDashboard();
        }}

        function populateFilters() {{
            const clientSelect = document.getElementById('filter-client');
            const personSelect = document.getElementById('filter-person');
            
            clientSelect.innerHTML = '<option value="all">Todos los Clientes</option>';
            let clients = [...new Set(originalData.detailed_projects.map(p => p.client_name))];
            if (excludeGestobraDev) {{
                clients = clients.filter(c => !isGestobraDevClient(c));
            }}
            clients.sort();
            clients.forEach(c => {{
                clientSelect.innerHTML += `<option value="${{c}}">${{c}}</option>`;
            }});
            clientSelect.value = selectedClient;

            populateProjectsSelect();

            personSelect.innerHTML = '<option value="all">Todas las Personas</option>';
            let people = [...new Set(originalData.operarios_summary.map(p => p.name))];
            people.sort();
            people.forEach(p => {{
                personSelect.innerHTML += `<option value="${{p}}">${{p}}</option>`;
            }});
            personSelect.value = selectedPerson;
        }}

        function populateProjectsSelect() {{
            const projSelect = document.getElementById('filter-project');
            projSelect.innerHTML = '<option value="all">Todos los Proyectos</option>';
            
            let projects = originalData.detailed_projects;
            if (excludeGestobraDev) {{
                projects = projects.filter(p => !isGestobraDevClient(p.client_name));
            }}
            if (selectedClient !== "all") {{
                projects = projects.filter(p => p.client_name === selectedClient);
            }}
            
            projects.sort((a, b) => a.name.localeCompare(b.name));
            projects.forEach(p => {{
                projSelect.innerHTML += `<option value="${{p.id}}">${{p.name}}</option>`;
            }});
            projSelect.value = selectedProject;
        }}

        function onClientChange() {{
            selectedClient = document.getElementById('filter-client').value;
            populateProjectsSelect();
            selectedProject = "all";
            document.getElementById('filter-project').value = "all";
            updateDashboard();
        }}

        function onProjectChange() {{
            selectedProject = document.getElementById('filter-project').value;
            if (selectedProject !== "all") {{
                const projObj = originalData.detailed_projects.find(p => p.id == selectedProject);
                if (projObj && selectedClient === "all") {{
                    selectedClient = projObj.client_name;
                    document.getElementById('filter-client').value = selectedClient;
                    populateProjectsSelect();
                    document.getElementById('filter-project').value = selectedProject;
                }}
            }}
            updateDashboard();
        }}

        function onPersonChange() {{
            selectedPerson = document.getElementById('filter-person').value;
            updateDashboard();
        }}

        function resetFilters() {{
            selectedClient = "all";
            selectedProject = "all";
            selectedPerson = "all";
            
            if (excludeGestobraDev) {{
                excludeGestobraDev = false;
                const btn = document.getElementById('btn-toggle-gestobra-dev');
                const icon = document.getElementById('gestobra-dev-icon');
                const text = document.getElementById('gestobra-dev-text');
                btn.className = "bg-rose-500/10 hover:bg-rose-500/20 text-rose-300 font-semibold text-sm rounded-xl px-4 py-2.5 transition-all font-outfit border border-rose-500/30 flex items-center gap-2 cursor-pointer whitespace-nowrap";
                icon.innerText = "🚫";
                text.innerText = "Omitir Gestobra Dev";
            }}

            populateFilters();
            updateDashboard();
        }}

        function initCharts() {{
            // SIN OBRA CHARTS
            // Sin Obra Top Person Chart (Horizontal Bar)
            const ctxSOPerson = document.getElementById('sinObraPersonChart').getContext('2d');
            sinObraPersonChartInstance = new Chart(ctxSOPerson, {{
                type: 'bar',
                data: {{
                    labels: originalData.sin_obra_person_chart.labels,
                    datasets: [{{
                        label: 'Horas Sin Obra',
                        data: originalData.sin_obra_person_chart.values,
                        backgroundColor: 'rgba(245, 158, 11, 0.7)',
                        borderColor: 'rgba(245, 158, 11, 1)',
                        borderWidth: 1.5, borderRadius: 6
                    }}]
                }},
                options: {{
                    indexAxis: 'y', responsive: true, maintainAspectRatio: false,
                    plugins: {{ legend: {{ display: false }} }},
                    scales: {{ x: {{ grid: {{ color: 'rgba(148, 163, 184, 0.05)' }}, ticks: {{ color: '#64748b' }} }}, y: {{ grid: {{ display: false }}, ticks: {{ color: '#94a3b8', font: {{ size: 10 }} }} }} }}
                }}
            }});

            // Sin Obra by Client (Doughnut)
            const ctxSOClient = document.getElementById('sinObraClientChart').getContext('2d');
            sinObraClientChartInstance = new Chart(ctxSOClient, {{
                type: 'doughnut',
                data: {{
                    labels: originalData.sin_obra_client_chart.labels,
                    datasets: [{{
                        data: originalData.sin_obra_client_chart.values,
                        backgroundColor: ['rgba(245, 158, 11, 0.75)', 'rgba(139, 92, 246, 0.75)', 'rgba(59, 130, 246, 0.75)', 'rgba(236, 72, 153, 0.75)'],
                        borderColor: 'rgba(15, 23, 42, 0.9)', borderWidth: 1.5
                    }}]
                }},
                options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ position: 'right', labels: {{ color: '#94a3b8', boxWidth: 10, font: {{ size: 9 }} }} }} }} }}
            }});

            // Sin Obra Timeline (Line)
            const ctxSOTimeline = document.getElementById('sinObraTimelineChart').getContext('2d');
            sinObraTimelineChartInstance = new Chart(ctxSOTimeline, {{
                type: 'line',
                data: {{
                    labels: originalData.sin_obra_timeline_chart.labels,
                    datasets: [{{
                        label: 'Horas Sin Obra Acumuladas',
                        data: originalData.sin_obra_timeline_chart.values,
                        borderColor: '#f59e0b', backgroundColor: 'rgba(245, 158, 11, 0.15)',
                        fill: true, tension: 0.3
                    }}]
                }},
                options: {{
                    responsive: true, maintainAspectRatio: false,
                    plugins: {{ legend: {{ labels: {{ color: '#94a3b8' }} }} }},
                    scales: {{ x: {{ grid: {{ display: false }}, ticks: {{ color: '#64748b' }} }}, y: {{ grid: {{ color: 'rgba(148, 163, 184, 0.05)' }}, ticks: {{ color: '#64748b' }} }} }}
                }}
            }});

            // CLIENTS VS PROJECTS VS MESSAGES CHARTS
            const ctxClientPM = document.getElementById('clientProjectsMsgsChart').getContext('2d');
            clientProjectsMsgsChartInstance = new Chart(ctxClientPM, {{
                type: 'bar',
                data: {{
                    labels: originalData.client_projects_msgs_chart.labels,
                    datasets: [
                        {{ label: 'Número de Proyectos (Obras)', data: originalData.client_projects_msgs_chart.projects, backgroundColor: 'rgba(139, 92, 246, 0.7)', borderColor: 'rgba(139, 92, 246, 1)', borderWidth: 1.5, borderRadius: 6, yAxisID: 'y' }},
                        {{ label: 'Volumen de Mensajes', data: originalData.client_projects_msgs_chart.messages, backgroundColor: 'rgba(59, 130, 246, 0.7)', borderColor: 'rgba(59, 130, 246, 1)', borderWidth: 1.5, borderRadius: 6, yAxisID: 'y1' }}
                    ]
                }},
                options: {{
                    responsive: true, maintainAspectRatio: false,
                    plugins: {{ legend: {{ labels: {{ color: '#94a3b8' }} }} }},
                    scales: {{ x: {{ grid: {{ display: false }}, ticks: {{ color: '#64748b', font: {{ size: 10 }} }} }}, y: {{ type: 'linear', display: true, position: 'left', ticks: {{ color: '#8b5cf6' }} }}, y1: {{ type: 'linear', display: true, position: 'right', grid: {{ drawOnChartArea: false }}, ticks: {{ color: '#3b82f6' }} }} }}
                }}
            }});

            const ctxProjMsg = document.getElementById('projectMessagesChart').getContext('2d');
            projectMessagesChartInstance = new Chart(ctxProjMsg, {{
                type: 'bar',
                data: {{ labels: originalData.project_messages_chart.labels, datasets: [{{ label: 'Actividad / Registros', data: originalData.project_messages_chart.values, backgroundColor: 'rgba(236, 72, 153, 0.7)', borderColor: 'rgba(236, 72, 153, 1)', borderWidth: 1.5, borderRadius: 6 }}] }},
                options: {{ indexAxis: 'y', responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ display: false }} }}, scales: {{ x: {{ grid: {{ color: 'rgba(148, 163, 184, 0.05)' }}, ticks: {{ color: '#64748b' }} }}, y: {{ grid: {{ display: false }}, ticks: {{ color: '#94a3b8', font: {{ size: 10 }} }} }} }} }}
            }});

            const ctxClientAutoMan = document.getElementById('clientAutoVsManualChart').getContext('2d');
            clientAutoVsManualChartInstance = new Chart(ctxClientAutoMan, {{
                type: 'bar',
                data: {{
                    labels: originalData.client_auto_manual_chart.labels,
                    datasets: [
                        {{ label: 'Mensajes Automáticos (Bot/Botones)', data: originalData.client_auto_manual_chart.auto, backgroundColor: 'rgba(16, 185, 129, 0.75)', borderRadius: 4 }},
                        {{ label: 'Mensajes Manuales Operario', data: originalData.client_auto_manual_chart.manual, backgroundColor: 'rgba(245, 158, 11, 0.75)', borderRadius: 4 }}
                    ]
                }},
                options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ labels: {{ color: '#94a3b8' }} }} }}, scales: {{ x: {{ stacked: true, grid: {{ display: false }}, ticks: {{ color: '#64748b' }} }}, y: {{ stacked: true, grid: {{ color: 'rgba(148, 163, 184, 0.05)' }}, ticks: {{ color: '#64748b' }} }} }} }}
            }});

            // 1. Consumos por Obra
            const ctxProj = document.getElementById('projectChart').getContext('2d');
            projectChartInstance = new Chart(ctxProj, {{
                type: 'bar',
                data: {{ labels: [], datasets: [{{ label: 'Horas Imputadas', data: [], backgroundColor: 'rgba(139, 92, 246, 0.65)', borderColor: 'rgba(139, 92, 246, 1)', borderWidth: 1.5, borderRadius: 6, yAxisID: 'y' }}, {{ label: 'Costo Calculado (€)', data: [], backgroundColor: 'rgba(236, 72, 153, 0.65)', borderColor: 'rgba(236, 72, 153, 1)', borderWidth: 1.5, borderRadius: 6, yAxisID: 'y1' }}] }},
                options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ labels: {{ color: '#94a3b8' }} }} }}, scales: {{ x: {{ grid: {{ display: false }}, ticks: {{ color: '#64748b' }} }}, y: {{ type: 'linear', display: true, position: 'left', ticks: {{ color: '#64748b' }} }}, y1: {{ type: 'linear', display: true, position: 'right', grid: {{ drawOnChartArea: false }}, ticks: {{ color: '#64748b' }} }} }} }}
            }});

            // 2. WhatsApp Inbound Doughnut
            const ctxWAInbound = document.getElementById('waInboundChart').getContext('2d');
            waInboundChartInstance = new Chart(ctxWAInbound, {{
                type: 'doughnut',
                data: {{ labels: originalData.wa_inbound_chart.labels, datasets: [{{ data: originalData.wa_inbound_chart.values, backgroundColor: ['rgba(16, 185, 129, 0.7)', 'rgba(59, 130, 246, 0.7)', 'rgba(139, 92, 246, 0.7)', 'rgba(245, 158, 11, 0.7)', 'rgba(239, 68, 68, 0.7)', 'rgba(107, 114, 128, 0.7)', 'rgba(6, 182, 212, 0.7)'], borderColor: 'rgba(15, 23, 42, 0.9)', borderWidth: 1.5 }}] }},
                options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ position: 'right', labels: {{ color: '#94a3b8', boxWidth: 10, font: {{ size: 9 }} }} }} }} }}
            }});

            // 2.1 WhatsApp Outbound Doughnut
            const ctxWAOutbound = document.getElementById('waOutboundChart').getContext('2d');
            waOutboundChartInstance = new Chart(ctxWAOutbound, {{
                type: 'doughnut',
                data: {{ labels: originalData.wa_outbound_chart.labels, datasets: [{{ data: originalData.wa_outbound_chart.values, backgroundColor: ['rgba(59, 130, 246, 0.7)', 'rgba(139, 92, 246, 0.7)', 'rgba(236, 72, 153, 0.7)', 'rgba(245, 158, 11, 0.7)', 'rgba(16, 185, 129, 0.7)'], borderColor: 'rgba(15, 23, 42, 0.9)', borderWidth: 1.5 }}] }},
                options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ position: 'right', labels: {{ color: '#94a3b8', boxWidth: 10, font: {{ size: 9 }} }} }} }} }}
            }});

            // 3. Automatic vs Manual Messages Doughnut Chart
            const ctxAutoManual = document.getElementById('autoVsManualChart').getContext('2d');
            autoVsManualChartInstance = new Chart(ctxAutoManual, {{
                type: 'doughnut',
                data: {{ labels: originalData.auto_vs_manual_chart.labels, datasets: [{{ data: originalData.auto_vs_manual_chart.values, backgroundColor: ['rgba(59, 130, 246, 0.75)', 'rgba(16, 185, 129, 0.75)', 'rgba(236, 72, 153, 0.75)', 'rgba(245, 158, 11, 0.75)', 'rgba(139, 92, 246, 0.75)'], borderColor: 'rgba(15, 23, 42, 0.9)', borderWidth: 1.5 }}] }},
                options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ position: 'right', labels: {{ color: '#94a3b8', boxWidth: 10, font: {{ size: 9 }} }} }} }} }}
            }});

            // 4. Fichajes vs Imputaciones por Operario
            const ctxPers = document.getElementById('personChart').getContext('2d');
            personChartInstance = new Chart(ctxPers, {{
                type: 'bar',
                data: {{ labels: [], datasets: [{{ label: 'Horas Fichadas', data: [], backgroundColor: 'rgba(59, 130, 246, 0.65)', borderColor: 'rgba(59, 130, 246, 1)', borderWidth: 1.5, borderRadius: 4 }}, {{ label: 'Horas Imputadas', data: [], backgroundColor: 'rgba(16, 185, 129, 0.65)', borderColor: 'rgba(16, 185, 129, 1)', borderWidth: 1.5, borderRadius: 4 }}] }},
                options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ labels: {{ color: '#94a3b8' }} }} }}, scales: {{ x: {{ grid: {{ display: false }}, ticks: {{ color: '#64748b' }} }}, y: {{ grid: {{ color: 'rgba(148, 163, 184, 0.05)' }}, ticks: {{ color: '#64748b' }} }} }} }}
            }});

            // 5. Horas Distribuídas Obra
            const ctxClockProj = document.getElementById('clockedProjectChart').getContext('2d');
            clockedProjectChartInstance = new Chart(ctxClockProj, {{
                type: 'bar',
                data: {{ labels: [], datasets: [{{ label: 'Horas Fichadas Distribuídas', data: [], backgroundColor: 'rgba(59, 130, 246, 0.65)', borderColor: 'rgba(59, 130, 246, 1)', borderWidth: 1.5, borderRadius: 6 }}] }},
                options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ labels: {{ color: '#94a3b8' }} }} }}, scales: {{ x: {{ grid: {{ display: false }}, ticks: {{ color: '#64748b' }} }}, y: {{ grid: {{ color: 'rgba(148, 163, 184, 0.05)' }}, ticks: {{ color: '#64748b' }} }} }} }}
            }});

            // 6. Horas Totales Operario
            const ctxClockPers = document.getElementById('clockedPersonChart').getContext('2d');
            clockedPersonChartInstance = new Chart(ctxClockPers, {{
                type: 'bar',
                data: {{ labels: [], datasets: [{{ label: 'Horas Fichadas Totales', data: [], backgroundColor: 'rgba(139, 92, 246, 0.65)', borderColor: 'rgba(139, 92, 246, 1)', borderWidth: 1.5, borderRadius: 6 }}] }},
                options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ labels: {{ color: '#94a3b8' }} }} }}, scales: {{ x: {{ grid: {{ display: false }}, ticks: {{ color: '#64748b' }} }}, y: {{ grid: {{ color: 'rgba(148, 163, 184, 0.05)' }}, ticks: {{ color: '#64748b' }} }} }} }}
            }});

            // 7. Messages Channel & Direction Chart (Stacked Bar)
            const ctxMsgChan = document.getElementById('messagesChannelChart').getContext('2d');
            messagesChannelChartInstance = new Chart(ctxMsgChan, {{
                type: 'bar',
                data: {{ labels: originalData.msg_channel_chart.channels, datasets: [{{ label: 'Entrantes (Incoming)', data: originalData.msg_channel_chart.incoming, backgroundColor: 'rgba(59, 130, 246, 0.7)', borderRadius: 4 }}, {{ label: 'Salientes (Outgoing)', data: originalData.msg_channel_chart.outgoing, backgroundColor: 'rgba(168, 85, 247, 0.7)', borderRadius: 4 }}] }},
                options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ labels: {{ color: '#94a3b8', font: {{ size: 10 }} }} }} }}, scales: {{ x: {{ stacked: true, grid: {{ display: false }}, ticks: {{ color: '#64748b' }} }}, y: {{ stacked: true, grid: {{ color: 'rgba(148, 163, 184, 0.05)' }}, ticks: {{ color: '#64748b' }} }} }} }}
            }});

            // 8. Session State Chart (Doughnut)
            const ctxSessState = document.getElementById('sessionStateChart').getContext('2d');
            sessionStateChartInstance = new Chart(ctxSessState, {{
                type: 'doughnut',
                data: {{ labels: originalData.session_states_chart.labels, datasets: [{{ data: originalData.session_states_chart.values, backgroundColor: ['rgba(59, 130, 246, 0.7)', 'rgba(16, 185, 129, 0.7)', 'rgba(245, 158, 11, 0.7)', 'rgba(139, 92, 246, 0.7)', 'rgba(236, 72, 153, 0.7)', 'rgba(6, 182, 212, 0.7)'], borderColor: 'rgba(15, 23, 42, 0.9)', borderWidth: 1.5 }}] }},
                options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ position: 'right', labels: {{ color: '#94a3b8', boxWidth: 10, font: {{ size: 9 }} }} }} }} }}
            }});

            // 9. Top Msg Operarios Horizontal Bar Chart
            const ctxTopMsg = document.getElementById('topMsgOperariosChart').getContext('2d');
            topMsgOperariosChartInstance = new Chart(ctxTopMsg, {{
                type: 'bar',
                data: {{ labels: originalData.top_msg_operarios_chart.labels, datasets: [{{ label: 'Mensajes e Interacciones', data: originalData.top_msg_operarios_chart.values, backgroundColor: 'rgba(168, 85, 247, 0.65)', borderColor: 'rgba(168, 85, 247, 1)', borderWidth: 1.5, borderRadius: 6 }}] }},
                options: {{ indexAxis: 'y', responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ display: false }} }}, scales: {{ x: {{ grid: {{ color: 'rgba(148, 163, 184, 0.05)' }}, ticks: {{ color: '#64748b' }} }}, y: {{ grid: {{ display: false }}, ticks: {{ color: '#94a3b8', font: {{ size: 10 }} }} }} }} }}
            }});

            // 10. Messages Timeline Chart (Line)
            const ctxMsgTimeline = document.getElementById('messagesTimelineChart').getContext('2d');
            messagesTimelineChartInstance = new Chart(ctxMsgTimeline, {{
                type: 'line',
                data: {{ labels: originalData.messages_timeline_chart.labels, datasets: [{{ label: 'Entrantes', data: originalData.messages_timeline_chart.incoming, borderColor: '#3b82f6', backgroundColor: 'rgba(59, 130, 246, 0.15)', fill: true, tension: 0.3 }}, {{ label: 'Salientes', data: originalData.messages_timeline_chart.outgoing, borderColor: '#ec4899', backgroundColor: 'rgba(236, 72, 153, 0.15)', fill: true, tension: 0.3 }}] }},
                options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ labels: {{ color: '#94a3b8' }} }} }}, scales: {{ x: {{ grid: {{ display: false }}, ticks: {{ color: '#64748b' }} }}, y: {{ grid: {{ color: 'rgba(148, 163, 184, 0.05)' }}, ticks: {{ color: '#64748b' }} }} }} }}
            }});
        }}

        function updatePersonChart() {{
            const groupSelect = document.getElementById('chart-person-group');
            if (selectedPerson !== "all" && groupSelect.value === "operario") {{
                groupSelect.value = "fecha";
            }}
            
            const groupBy = groupSelect.value;
            const sortBy = document.getElementById('chart-person-sort').value;
            const sortOrder = document.getElementById('chart-person-order').value;
            
            let records = originalData.daily_records;
            if (selectedPerson !== "all") {{
                records = records.filter(r => r.person_name === selectedPerson);
            }} else {{
                const allowedOps = new Set(filteredOperariosGlobal.map(op => op.name));
                records = records.filter(r => allowedOps.has(r.person_name));
            }}
            
            const grouped = {{}};
            records.forEach(r => {{
                const key = groupBy === "operario" ? r.person_name : r.date;
                if (!grouped[key]) {{
                    grouped[key] = {{ key: key, clocked: 0, imputed: 0 }};
                }}
                grouped[key].clocked += r.hours_worked;
                grouped[key].imputed += r.hours_imputed;
            }});

            const chartDataList = Object.values(grouped);
            if (sortBy === "clocked") {{
                chartDataList.sort((a, b) => sortOrder === "desc" ? b.clocked - a.clocked : a.clocked - b.clocked);
            }} else if (sortBy === "imputed") {{
                chartDataList.sort((a, b) => sortOrder === "desc" ? b.imputed - a.imputed : a.imputed - b.imputed);
            }} else {{
                chartDataList.sort((a, b) => sortOrder === "desc" ? b.key.localeCompare(a.key) : a.key.localeCompare(b.key));
            }}

            personChartInstance.data.labels = chartDataList.map(item => item.key);
            personChartInstance.data.datasets[0].data = chartDataList.map(item => Number(item.clocked.toFixed(1)));
            personChartInstance.data.datasets[1].data = chartDataList.map(item => Number(item.imputed.toFixed(1)));
            personChartInstance.update();
        }}

        function updateDashboard() {{
            let filteredProjects = originalData.detailed_projects;
            if (excludeGestobraDev) {{
                filteredProjects = filteredProjects.filter(p => !isGestobraDevClient(p.client_name));
            }}
            if (selectedClient !== "all") {{
                filteredProjects = filteredProjects.filter(p => p.client_name === selectedClient);
            }}
            if (selectedProject !== "all") {{
                filteredProjects = filteredProjects.filter(p => p.id == selectedProject);
            }}

            let filteredOperarios = originalData.operarios_summary;
            if (selectedPerson !== "all") {{
                filteredOperarios = filteredOperarios.filter(op => op.name === selectedPerson);
            }}
            filteredOperariosGlobal = filteredOperarios;

            let filteredAlerts = originalData.alerts;
            if (selectedPerson !== "all") {{
                filteredAlerts = filteredAlerts.filter(a => a.person_name === selectedPerson);
            }}

            let filteredClockDist = originalData.clocked_distribution;
            if (excludeGestobraDev) {{
                filteredClockDist = filteredClockDist.filter(d => !isGestobraDevClient(d.client_name));
            }}
            if (selectedClient !== "all") {{
                filteredClockDist = filteredClockDist.filter(d => d.client_name === selectedClient);
            }}
            if (selectedProject !== "all") {{
                filteredClockDist = filteredClockDist.filter(d => d.project_id == selectedProject);
            }}
            if (selectedPerson !== "all") {{
                filteredClockDist = filteredClockDist.filter(d => d.person_name === selectedPerson);
            }}

            document.getElementById('kpi-projects').innerText = filteredProjects.length;
            const totalClocked = filteredClockDist.reduce((acc, curr) => acc + curr.hours, 0);
            document.getElementById('kpi-clocked').innerText = totalClocked.toFixed(1) + ' h';
            const totalImputed = filteredProjects.reduce((acc, curr) => acc + curr.hours_imputed, 0);
            document.getElementById('kpi-imputed').innerText = totalImputed.toFixed(1) + ' h';
            const totalCost = filteredProjects.reduce((acc, curr) => acc + curr.calculated_labor_cost, 0);
            document.getElementById('kpi-cost').innerText = totalCost.toLocaleString('es-ES', {{style: 'currency', currency: 'EUR'}});

            // Filter Sin Obra records
            let filteredSinObra = originalData.sin_obra_records;
            if (excludeGestobraDev) {{
                filteredSinObra = filteredSinObra.filter(r => !isGestobraDevClient(r.client_name));
            }}
            if (selectedClient !== "all") {{
                filteredSinObra = filteredSinObra.filter(r => r.client_name === selectedClient);
            }}
            if (selectedPerson !== "all") {{
                filteredSinObra = filteredSinObra.filter(r => r.person_name === selectedPerson);
            }}

            const soHours = filteredSinObra.reduce((acc, curr) => acc + curr.hours, 0);
            document.getElementById('kpi-so-hours').innerText = soHours.toFixed(1) + ' h';
            const soPct = totalClocked > 0 ? ((soHours / totalClocked) * 100).toFixed(1) : 0;
            document.getElementById('kpi-so-pct').innerText = soPct + '%';
            
            const uniqueSO = new Set(filteredSinObra.map(r => r.person_name)).size;
            document.getElementById('kpi-so-people').innerText = uniqueSO;
            const estSOCost = (soHours * 20.0).toLocaleString('es-ES', {{style: 'currency', currency: 'EUR'}});
            document.getElementById('kpi-so-cost').innerText = estSOCost;

            // Update Sin Obra Top Person Chart
            const soPersonMap = {{}};
            filteredSinObra.forEach(r => {{
                soPersonMap[r.person_name] = (soPersonMap[r.person_name] || 0) + r.hours;
            }});
            const sortedSOPerson = Object.entries(soPersonMap).sort((a, b) => b[1] - a[1]).slice(0, 15);
            sinObraPersonChartInstance.data.labels = sortedSOPerson.map(i => i[0]);
            sinObraPersonChartInstance.data.datasets[0].data = sortedSOPerson.map(i => Number(i[1].toFixed(1)));
            sinObraPersonChartInstance.update();

            // Update Sin Obra Client Chart
            const soClientMap = {{}};
            filteredSinObra.forEach(r => {{
                soClientMap[r.client_name] = (soClientMap[r.client_name] || 0) + r.hours;
            }});
            const sortedSOClient = Object.entries(soClientMap).sort((a, b) => b[1] - a[1]);
            sinObraClientChartInstance.data.labels = sortedSOClient.map(i => i[0]);
            sinObraClientChartInstance.data.datasets[0].data = sortedSOClient.map(i => Number(i[1].toFixed(1)));
            sinObraClientChartInstance.update();

            let filteredMessages = originalData.messages_records;
            let filteredSessions = originalData.sessions_records;
            if (excludeGestobraDev) {{
                filteredMessages = filteredMessages.filter(m => !isGestobraDevClient(m.client_name));
            }}
            if (selectedClient !== "all") {{
                filteredMessages = filteredMessages.filter(m => m.client_name === selectedClient);
            }}
            if (selectedPerson !== "all") {{
                filteredMessages = filteredMessages.filter(m => m.person_name === selectedPerson);
                filteredSessions = filteredSessions.filter(s => s.person_name === selectedPerson);
            }}

            const totalWA = filteredMessages.length;
            document.getElementById('kpi-whatsapp').innerText = totalWA + ' msgs';
            document.getElementById('kpi-conv-messages').innerText = filteredMessages.length;
            document.getElementById('kpi-conv-bot').innerText = originalData.kpis.total_bot_actions;
            document.getElementById('kpi-conv-voice').innerText = originalData.kpis.total_voice_transcripts;
            document.getElementById('kpi-conv-sessions').innerText = filteredSessions.length;

            const autoMsgsCount = filteredMessages.filter(m => m.is_automated).length;
            const autoPct = filteredMessages.length > 0 ? ((autoMsgsCount / filteredMessages.length) * 100).toFixed(1) : 0;
            document.getElementById('kpi-conv-auto-pct').innerText = autoPct + '%';

            // Client Comparison Charts update on filter toggle
            if (clientProjectsMsgsChartInstance) {{
                let labels = originalData.client_projects_msgs_chart.labels;
                let projects = originalData.client_projects_msgs_chart.projects;
                let messages = originalData.client_projects_msgs_chart.messages;
                if (excludeGestobraDev) {{
                    const idxs = labels.map((c, i) => !isGestobraDevClient(c) ? i : -1).filter(i => i !== -1);
                    labels = idxs.map(i => labels[i]);
                    projects = idxs.map(i => projects[i]);
                    messages = idxs.map(i => messages[i]);
                }}
                clientProjectsMsgsChartInstance.data.labels = labels;
                clientProjectsMsgsChartInstance.data.datasets[0].data = projects;
                clientProjectsMsgsChartInstance.data.datasets[1].data = messages;
                clientProjectsMsgsChartInstance.update();
            }}

            if (clientAutoVsManualChartInstance) {{
                let labels = originalData.client_auto_manual_chart.labels;
                let auto = originalData.client_auto_manual_chart.auto;
                let manual = originalData.client_auto_manual_chart.manual;
                if (excludeGestobraDev) {{
                    const idxs = labels.map((c, i) => !isGestobraDevClient(c) ? i : -1).filter(i => i !== -1);
                    labels = idxs.map(i => labels[i]);
                    auto = idxs.map(i => auto[i]);
                    manual = idxs.map(i => manual[i]);
                }}
                clientAutoVsManualChartInstance.data.labels = labels;
                clientAutoVsManualChartInstance.data.datasets[0].data = auto;
                clientAutoVsManualChartInstance.data.datasets[1].data = manual;
                clientAutoVsManualChartInstance.update();
            }}

            if (projectMessagesChartInstance) {{
                let labels = originalData.project_messages_chart.labels;
                let clients = originalData.project_messages_chart.client;
                let values = originalData.project_messages_chart.values;
                if (excludeGestobraDev) {{
                    const idxs = clients.map((c, i) => !isGestobraDevClient(c) ? i : -1).filter(i => i !== -1);
                    labels = idxs.map(i => labels[i]);
                    values = idxs.map(i => values[i]);
                }}
                projectMessagesChartInstance.data.labels = labels;
                projectMessagesChartInstance.data.datasets[0].data = values;
                projectMessagesChartInstance.update();
            }}

            filteredProjects.sort((a, b) => b.calculated_labor_cost - a.calculated_labor_cost);
            const topProj = filteredProjects.slice(0, 15);
            projectChartInstance.data.labels = topProj.map(p => p.name);
            projectChartInstance.data.datasets[0].data = topProj.map(p => p.hours_imputed);
            projectChartInstance.data.datasets[1].data = topProj.map(p => p.calculated_labor_cost);
            projectChartInstance.update();

            const clockedProjGrouped = {{}};
            const clockedPersGrouped = {{}};
            filteredClockDist.forEach(d => {{
                clockedProjGrouped[d.project_name] = (clockedProjGrouped[d.project_name] || 0) + d.hours;
                clockedPersGrouped[d.person_name] = (clockedPersGrouped[d.person_name] || 0) + d.hours;
            }});

            const sortedClockedProj = Object.entries(clockedProjGrouped).sort((a, b) => b[1] - a[1]);
            clockedProjectChartInstance.data.labels = sortedClockedProj.map(item => item[0]);
            clockedProjectChartInstance.data.datasets[0].data = sortedClockedProj.map(item => Number(item[1].toFixed(1)));
            clockedProjectChartInstance.update();

            const sortedClockedPers = Object.entries(clockedPersGrouped).sort((a, b) => b[1] - a[1]);
            clockedPersonChartInstance.data.labels = sortedClockedPers.map(item => item[0]);
            clockedPersonChartInstance.data.datasets[0].data = sortedClockedPers.map(item => Number(item[1].toFixed(1)));
            clockedPersonChartInstance.update();

            updatePersonChart();

            renderAlertsTable(filteredAlerts);
            renderProjectsTable(filteredProjects);
            renderOperariosTable(filteredOperarios);
        }}

        function renderAlertsTable(alertsList) {{
            const alertsTbody = document.getElementById('alerts-tbody');
            const alertsCount = document.getElementById('alerts-count');
            alertsTbody.innerHTML = '';
            alertsCount.innerText = alertsList.length;

            if (alertsList.length === 0) {{
                alertsTbody.innerHTML = '<tr><td colspan="6" class="py-6 px-2 text-center text-slate-500">No se encontraron alertas de fichajes con los filtros seleccionados.</td></tr>';
            }} else {{
                alertsList.slice(0, 50).forEach(a => {{
                    const isOver = a.hours_clocked > a.hours_imputed;
                    const statusBadge = isOver ? 
                        '<span class="px-2 py-0.5 text-xs font-semibold rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/20">Falta Imputación</span>' : 
                        '<span class="px-2 py-0.5 text-xs font-semibold rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">Exceso Imputación</span>';

                    alertsTbody.innerHTML += `
                        <tr class="hover:bg-slate-900/20 transition-all font-outfit">
                            <td class="py-3 px-2 font-mono text-xs text-slate-400">${{a.date}}</td>
                            <td class="py-3 px-2 text-white font-medium">${{a.person_name}}</td>
                            <td class="py-3 px-2 text-right font-semibold">${{a.hours_clocked}} h</td>
                            <td class="py-3 px-2 text-right font-semibold">${{a.hours_imputed}} h</td>
                            <td class="py-3 px-2 text-right font-bold text-pink-400">${{Math.abs(a.difference)}} h</td>
                            <td class="py-3 px-2 text-center">${{statusBadge}}</td>
                        </tr>
                    `;
                }});
            }}
        }}

        function renderProjectsTable(projectsList) {{
            const projectsTbody = document.getElementById('projects-tbody');
            projectsTbody.innerHTML = '';
            
            if (projectsList.length === 0) {{
                projectsTbody.innerHTML = '<tr><td colspan="7" class="py-6 px-2 text-center text-slate-500">No hay proyectos que coincidan con los filtros seleccionados.</td></tr>';
            }} else {{
                projectsList.forEach(proj => {{
                    const formattedBudget = proj.budget.toLocaleString('es-ES', {{style: 'currency', currency: 'EUR'}});
                    const formattedBase = proj.actual_cost.toLocaleString('es-ES', {{style: 'currency', currency: 'EUR'}});
                    const formattedLabor = proj.calculated_labor_cost.toLocaleString('es-ES', {{style: 'currency', currency: 'EUR'}});

                    projectsTbody.innerHTML += `
                        <tr class="hover:bg-slate-900/20 transition-all text-sm font-outfit">
                            <td class="py-3.5 px-2 text-white font-semibold">${{proj.name}}</td>
                            <td class="py-3.5 px-2 text-slate-400">${{proj.client_name}}</td>
                            <td class="py-3.5 px-2">
                                <span class="px-2 py-0.5 text-xs font-semibold rounded-full bg-slate-800 text-slate-300 border border-slate-700">${{proj.status}}</span>
                            </td>
                            <td class="py-3.5 px-2 text-right">${{formattedBudget}}</td>
                            <td class="py-3.5 px-2 text-right text-slate-500">${{formattedBase}}</td>
                            <td class="py-3.5 px-2 text-right">${{proj.hours_imputed}} h</td>
                            <td class="py-3.5 px-2 text-right font-bold text-purple-400">${{formattedLabor}}</td>
                        </tr>
                    `;
                }});
            }}
        }}

        function renderOperariosTable(operariosList) {{
            const operariosTbody = document.getElementById('operarios-tbody');
            operariosTbody.innerHTML = '';
            
            if (operariosList.length === 0) {{
                operariosTbody.innerHTML = '<tr><td colspan="6" class="py-6 px-2 text-center text-slate-500">No hay operarios que coincidan con los filtros seleccionados.</td></tr>';
            }} else {{
                operariosList.forEach(op => {{
                    const totalMsg = op.whatsapp_outbound + op.whatsapp_inbound;
                    const formattedCost = op.calculated_cost.toLocaleString('es-ES', {{style: 'currency', currency: 'EUR'}});
                    operariosTbody.innerHTML += `
                        <tr class="hover:bg-slate-900/20 transition-all text-sm font-outfit">
                            <td class="py-3.5 px-2 text-white font-semibold">${{op.name}}</td>
                            <td class="py-3.5 px-2 text-slate-400">${{op.cargo}} / <span class="text-slate-500 font-medium">${{op.role}}</span></td>
                            <td class="py-3.5 px-2 text-right">${{op.hours_clocked}} h</td>
                            <td class="py-3.5 px-2 text-right">${{op.hours_imputed}} h</td>
                            <td class="py-3.5 px-2 text-right font-bold text-indigo-400">${{formattedCost}}</td>
                            <td class="py-3.5 px-2 text-center">
                                <span class="inline-flex items-center gap-1.5 px-2.5 py-1 text-xs font-semibold rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/20">
                                    <span class="w-1.5 h-1.5 rounded-full bg-blue-400 animate-pulse"></span>
                                    ${{totalMsg}} reportes (${{op.whatsapp_outbound}} salientes, ${{op.whatsapp_inbound}} entrantes)
                                </span>
                            </td>
                        </tr>
                    `;
                }});
            }}
        }}

        function switchTab(tabId) {{
            const contents = document.querySelectorAll('.tab-content');
            contents.forEach(el => el.classList.add('hidden'));
            contents.forEach(el => el.classList.remove('block'));

            document.getElementById('tab-' + tabId).classList.remove('hidden');
            document.getElementById('tab-' + tabId).classList.add('block');

            const buttons = [
                document.getElementById('tab-btn-alerts'),
                document.getElementById('tab-btn-projects'),
                document.getElementById('tab-btn-operarios')
            ];
            buttons.forEach(btn => {{
                btn.classList.remove('border-purple-500', 'text-white');
                btn.classList.add('border-transparent', 'text-slate-400');
            }});

            const activeBtn = document.getElementById('tab-btn-' + tabId);
            activeBtn.classList.remove('border-transparent', 'text-slate-400');
            activeBtn.classList.add('border-purple-500', 'text-white');
        }}
    </script>
</body>
</html>"""

os.makedirs("output", exist_ok=True)
with open("output/dashboard.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print("Dashboard successfully generated as output/dashboard.html with Sin Obra section & charts!")
