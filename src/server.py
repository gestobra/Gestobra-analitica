import os
import psycopg2
import pandas as pd
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

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

DB_HOST = env_vars.get("IP")
DB_NAME = env_vars.get("DB")
DB_USER = env_vars.get("USER")
DB_PASSWORD = env_vars.get("PWD")

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=5432
    )

def fetch_operational_data():
    """Conecta a PostgreSQL y carga las tablas en memoria como DataFrames."""
    conn = get_db_connection()
    tables = [
        "projects", "people", "users", "team_user", "cargos", "time_clock_records",
        "project_imputations", "tasks", "whatsapp_action_log", "voice_inputs", 
        "whatsapp_media_inputs", "resources", "teams", "messages", "daily_sessions",
        "whatsapp_inbound_messages"
    ]
    dfs = {}
    for table in tables:
        query = f'SELECT * FROM "public"."{table}"'
        dfs[table] = pd.read_sql_query(query, conn)
    conn.close()
    return dfs

def process_dimensional_model(dfs):
    """Procesa las tablas operacionales en un modelo dimensional (Hechos y Dimensiones)."""
    # 1. dim_project
    projects_df = dfs["projects"]
    teams_df_names = dfs["teams"][["id", "name"]].rename(columns={"id": "project_team_id", "name": "client_name"})
    dim_project = projects_df.merge(teams_df_names, left_on="team_id", right_on="project_team_id", how="left")
    dim_project["client_name"] = dim_project["client_name"].fillna("Sin Cliente")
    
    # 2. dim_person
    people_df = dfs["people"]
    resources_df = dfs["resources"][["id", "name", "nickname", "hourly_rate"]].rename(columns={"id": "resource_id", "hourly_rate": "resource_rate"})
    users_df = dfs["users"][["id", "name", "email", "phone"]].rename(columns={"id": "user_id_usr", "name": "user_name", "email": "user_email", "phone": "user_phone"})
    cargos_df = dfs["cargos"][["id", "name"]].rename(columns={"id": "cargo_id_cgo", "name": "cargo_name"})
    team_user_df = dfs["team_user"][["user_id", "team_id", "role", "hourly_rate"]].rename(columns={"hourly_rate": "team_rate"})

    dim_person = people_df.merge(resources_df, left_on="id", right_on="resource_id", how="left")
    dim_person = dim_person.merge(users_df, left_on="user_id", right_on="user_id_usr", how="left")
    dim_person["person_name"] = dim_person["name"].fillna(dim_person["user_name"]).fillna("Operario " + dim_person["id"].astype(str))
    dim_person["person_email"] = dim_person["email"].fillna(dim_person["user_email"])
    dim_person["person_phone"] = dim_person["phone"].fillna(dim_person["user_phone"])
    dim_person = dim_person.merge(cargos_df, left_on="cargo_id", right_on="cargo_id_cgo", how="left")
    dim_person = dim_person.merge(team_user_df, left_on="user_id", right_on="user_id", how="left")
    dim_person = dim_person.merge(teams_df_names, left_on="team_id", right_on="project_team_id", how="left")
    dim_person = dim_person.rename(columns={"client_name": "team_client_name"})
    dim_person["hourly_rate_final"] = dim_person["resource_rate"].fillna(dim_person["team_rate"]).fillna(20.0)
    
    dim_person_final = dim_person[[
        "id", "person_name", "person_email", "person_phone", "cargo_name", "role", 
        "is_worker", "is_client", "is_external_worker", "is_supplier", "hourly_rate_final"
    ]].copy().rename(columns={"id": "person_id"})

    # 3. fact_time_clock
    time_clock = dfs["time_clock_records"].copy()
    time_clock["entry_at"] = pd.to_datetime(time_clock["entry_at"])
    time_clock["exit_at"] = pd.to_datetime(time_clock["exit_at"])
    time_clock["hours_worked"] = (time_clock["exit_at"] - time_clock["entry_at"]).dt.total_seconds() / 3600.0
    time_clock["hours_worked"] = time_clock["hours_worked"].round(2)
    fact_time_clock = time_clock[["id", "work_date", "person_id", "entry_at", "exit_at", "hours_worked"]].copy()

    # 4. fact_project_imputation
    imputations = dfs["project_imputations"].copy()
    imputations["date"] = pd.to_datetime(imputations["date"]).dt.date
    imputations["hours_imputed"] = imputations["minutes"].apply(lambda m: m / 60.0 if pd.notnull(m) else 0.0)
    imputations.loc[imputations["hours_imputed"] == 0.0, "hours_imputed"] = imputations["amount"].astype(float)
    imputations = imputations.merge(dim_person_final[["person_id", "hourly_rate_final"]], left_on="resource_id", right_on="person_id", how="left")
    imputations["hourly_rate_imputed"] = imputations["hourly_rate"].astype(float)
    imputations.loc[(imputations["hourly_rate_imputed"] == 0.0) | (imputations["hourly_rate_imputed"].isnull()), "hourly_rate_imputed"] = imputations["hourly_rate_final"]
    imputations["hourly_rate_imputed"] = imputations["hourly_rate_imputed"].fillna(20.0)
    imputations["calculated_cost"] = (imputations["hours_imputed"] * imputations["hourly_rate_imputed"]).round(2)
    fact_project_imputation = imputations[[
        "id", "date", "project_id", "resource_id", "hours_imputed", "hourly_rate_imputed", "calculated_cost", "description"
    ]].copy().rename(columns={"resource_id": "person_id"})

    # 5. fact_whatsapp_activity
    user_to_person = people_df[people_df["user_id"].notnull()][["user_id", "id"]].set_index("user_id")["id"].to_dict()
    action_log = dfs["whatsapp_action_log"].copy()
    action_log["date"] = pd.to_datetime(action_log["created_at"]).dt.date
    action_log["person_id"] = action_log["user_id"].map(user_to_person)
    
    voice_in = dfs["voice_inputs"].copy()
    voice_in["date"] = pd.to_datetime(voice_in["created_at"]).dt.date
    voice_in["person_id"] = voice_in["user_id"].map(user_to_person)
    
    media_in = dfs["whatsapp_media_inputs"].copy()
    media_in["date"] = pd.to_datetime(media_in["created_at"]).dt.date
    media_in["person_id"] = media_in["user_id"].map(user_to_person)

    act_list = []
    for _, row in action_log.iterrows():
        if pd.notnull(row["date"]):
            direction = str(row.get("direction", "")).lower()
            if direction == "internal":
                continue
            if direction == "outbound":
                msg_type = row.get("message_type", "text")
                if pd.isnull(msg_type) or not msg_type:
                    msg_type = "text"
                act_list.append({"date": row["date"], "person_id": row["person_id"], "activity_type": f"outbound_{str(msg_type).lower()}", "media_count": 0, "voice_duration_seconds": 0})
            elif direction == "inbound":
                msg_type = row.get("message_type", "text")
                if pd.isnull(msg_type) or not msg_type:
                    msg_type = "text"
                act_list.append({"date": row["date"], "person_id": row["person_id"], "activity_type": f"inbound_{str(msg_type).lower()}", "media_count": 0, "voice_duration_seconds": 0})
    for _, row in voice_in.iterrows():
        if pd.notnull(row["date"]):
            dur_ms = row["media_duration_ms"]
            dur_sec = dur_ms / 1000.0 if pd.notnull(dur_ms) else 0.0
            act_list.append({"date": row["date"], "person_id": row["person_id"], "activity_type": "inbound_audio", "media_count": 0, "voice_duration_seconds": int(dur_sec)})
    for _, row in media_in.iterrows():
        if pd.notnull(row["date"]):
            media_kind = str(row.get("media_kind", "image")).lower()
            act_list.append({"date": row["date"], "person_id": row["person_id"], "activity_type": f"inbound_{media_kind}", "media_count": 1, "voice_duration_seconds": 0})
    
    if act_list:
        fact_whatsapp_activity = pd.DataFrame(act_list)
        fact_whatsapp_activity["person_id"] = fact_whatsapp_activity["person_id"].fillna(-1).astype(int)
    else:
        fact_whatsapp_activity = pd.DataFrame(columns=["date", "person_id", "activity_type", "media_count", "voice_duration_seconds"])

    # 4. Proportional distribution of clocked hours to projects
    daily_clock = fact_time_clock.groupby(['work_date', 'person_id'])['hours_worked'].sum().reset_index()
    daily_clock['work_date'] = daily_clock['work_date'].astype(str)

    daily_imputed = fact_project_imputation.copy()
    daily_imputed['work_date'] = pd.to_datetime(daily_imputed['date']).dt.date.astype(str)
    daily_imputed_grouped = daily_imputed.groupby(['work_date', 'person_id', 'project_id'])['hours_imputed'].sum().reset_index()

    daily_imputed_totals = daily_imputed_grouped.groupby(['work_date', 'person_id'])['hours_imputed'].sum().reset_index().rename(columns={'hours_imputed': 'total_imputed'})
    imputed_merged = pd.merge(daily_imputed_grouped, daily_imputed_totals, on=['work_date', 'person_id'], how='left')

    clock_dist = pd.merge(imputed_merged, daily_clock, on=['work_date', 'person_id'], how='left')
    clock_dist['hours_worked'] = clock_dist['hours_worked'].fillna(0.0)

    clock_dist['project_hours_worked'] = 0.0
    valid_total_imputed = clock_dist['total_imputed'] > 0
    clock_dist.loc[valid_total_imputed, 'project_hours_worked'] = clock_dist['hours_worked'] * (clock_dist['hours_imputed'] / clock_dist['total_imputed'])

    unimputed_dates = daily_clock[~daily_clock.set_index(['work_date', 'person_id']).index.isin(daily_imputed_grouped.set_index(['work_date', 'person_id']).index)].copy()
    unimputed_dates['project_id'] = -1
    unimputed_dates['project_hours_worked'] = unimputed_dates['hours_worked']
    unimputed_dates['hours_imputed'] = 0.0
    unimputed_dates['total_imputed'] = 0.0

    distributed_clock = pd.concat([
        clock_dist[['work_date', 'person_id', 'project_id', 'project_hours_worked']],
        unimputed_dates[['work_date', 'person_id', 'project_id', 'project_hours_worked']]
    ], ignore_index=True)

    proj_map = dict(zip(dim_project['id'], dim_project['name']))
    proj_map[-1] = "Sin Obra"
    client_map = dict(zip(dim_project['id'], dim_project['client_name']))
    pers_map = dict(zip(dim_person_final['person_id'], dim_person_final['person_name']))
    person_team_client = dict(zip(dim_person['id'], dim_person['team_client_name']))

    distributed_clock['project_name'] = distributed_clock['project_id'].map(proj_map).fillna("Obra Desconocida")
    distributed_clock['client_name'] = distributed_clock['project_id'].map(client_map)

    # Fallback client name for unimputed projects to person's team client name
    unimputed_mask = distributed_clock['project_id'] == -1
    distributed_clock.loc[unimputed_mask, 'client_name'] = distributed_clock.loc[unimputed_mask, 'person_id'].map(person_team_client)
    distributed_clock['client_name'] = distributed_clock['client_name'].fillna("Sin Cliente")

    distributed_clock['person_name'] = distributed_clock['person_id'].map(pers_map).fillna("Operario Desconocido")

    return dim_project, dim_person_final, fact_time_clock, fact_project_imputation, fact_whatsapp_activity, distributed_clock

# ==========================================
# RUTAS DE SERVICIO E INTERFAZ
# ==========================================

@app.route('/')
def index():
    return send_from_directory('../output', 'dashboard_live.html')

@app.route('/output/<path:path>')
def serve_output(path):
    return send_from_directory('../output', path)

@app.route('/openapi.json')
def openapi_json():
    return send_from_directory('../output', 'openapi.json')

@app.route('/api/docs')
def api_docs():
    html = """<!DOCTYPE html>
<html>
<head>
  <title>GestObra BI API - Swagger UI</title>
  <link rel="stylesheet" type="text/css" href="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/4.15.5/swagger-ui.css">
  <script src="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/4.15.5/swagger-ui-bundle.js"></script>
  <style>
    body { background-color: #0f172a; margin: 0; }
    .swagger-ui .topbar { display: none; }
    .swagger-ui .info .title { color: #f8fafc !important; }
    .swagger-ui .info p, .swagger-ui .info li, .swagger-ui .info td, .swagger-ui .info blockquote { color: #cbd5e1 !important; }
    .swagger-ui .scheme-container { background-color: #1e293b !important; box-shadow: none !important; border-bottom: 1px solid #334155; }
    .swagger-ui .opblock { background-color: #1e293b !important; border-color: #334155 !important; }
    .swagger-ui .opblock .opblock-summary-operation-id, .swagger-ui .opblock .opblock-summary-path, .swagger-ui .opblock .opblock-summary-description { color: #cbd5e1 !important; }
    .swagger-ui .tabli button { color: #94a3b8 !important; }
    .swagger-ui .tabli.active button { color: #f8fafc !important; }
    .swagger-ui .opblock-description-wrapper p, .swagger-ui .opblock-external-docs-wrapper p, .swagger-ui .opblock-title_normal p { color: #94a3b8 !important; }
    .swagger-ui .response-col_status { color: #f8fafc !important; }
    .swagger-ui table thead tr th { color: #f8fafc !important; border-bottom: 2px solid #334155 !important; }
    .swagger-ui .dialog-ux .modal-ux { background-color: #1e293b !important; border: 1px solid #334155 !important; }
    .swagger-ui .parameter__name { color: #f8fafc !important; }
    .swagger-ui .parameter__type { color: #38bdf8 !important; }
    .swagger-ui select { background-color: #0f172a !important; color: #cbd5e1 !important; border-color: #334155 !important; }
    .swagger-ui input[type=text] { background-color: #0f172a !important; color: #cbd5e1 !important; border-color: #334155 !important; }
    .swagger-ui .response-col_links { color: #94a3b8 !important; }
  </style>
</head>
<body>
  <div id="swagger-ui"></div>
  <script>
    const ui = SwaggerUIBundle({
      url: '/openapi.json',
      dom_id: '#swagger-ui',
      presets: [
        SwaggerUIBundle.presets.apis,
        SwaggerUIBundle.SwaggerUIStandalonePreset
      ],
      layout: "BaseLayout",
      deepLinking: true
    })
  </script>
</body>
</html>
"""
    return html

# ==========================================
# ENDPOINTS MODULARES DE LA API (PRODUCCIÓN)
# ==========================================

@app.route('/api/clients', methods=['GET'])
def get_clients():
    """Retorna la lista de nombres únicos de clientes registrados."""
    try:
        dfs = fetch_operational_data()
        dim_project, _, _, _, _ = process_dimensional_model(dfs)
        clients = sorted(list(dim_project['client_name'].unique()))
        return jsonify(clients)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/projects', methods=['GET'])
def get_projects():
    """
    Retorna la lista de proyectos.
    Permite filtrar opcionalmente por cliente usando el parámetro de consulta ?client=NombreCliente.
    """
    client_filter = request.args.get('client', None)
    try:
        dfs = fetch_operational_data()
        dim_project, _, _, _, _ = process_dimensional_model(dfs)
        
        filtered = dim_project
        if client_filter:
            filtered = dim_project[dim_project['client_name'] == client_filter]
            
        projects_list = []
        for _, row in filtered.sort_values(by='name').iterrows():
            projects_list.append({
                "id": int(row['id']),
                "name": str(row['name']),
                "client_name": str(row['client_name']),
                "status": str(row['status']),
                "budget": float(row['budget']) if pd.notnull(row['budget']) else 0.0,
                "actual_cost": float(row['actual_cost']) if pd.notnull(row['actual_cost']) else 0.0
            })
        return jsonify(projects_list)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/people', methods=['GET'])
def get_people():
    """Retorna la lista de operarios/personas registradas."""
    try:
        dfs = fetch_operational_data()
        _, dim_person, _, _, _ = process_dimensional_model(dfs)
        people_list = []
        for _, row in dim_person.sort_values(by='person_name').iterrows():
            people_list.append({
                "person_id": int(row['person_id']),
                "name": str(row['person_name']),
                "cargo": str(row['cargo_name']) if pd.notnull(row['cargo_name']) else "Sin Cargo",
                "role": str(row['role']) if pd.notnull(row['role']) else "Operario",
                "hourly_rate": float(row['hourly_rate_final'])
            })
        return jsonify(people_list)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/aggregations/client', methods=['GET'])
def get_aggregations_by_client():
    """Retorna métricas e imputaciones de costo y horas agrupadas por Cliente."""
    try:
        dfs = fetch_operational_data()
        dim_project, _, _, fact_project_imputation, _ = process_dimensional_model(dfs)
        
        # Join imputaciones con proyectos
        merged = fact_project_imputation.merge(dim_project, on='project_id', how='left')
        
        client_agg = merged.groupby('client_name').agg(
            hours_imputed=('hours_imputed', 'sum'),
            calculated_cost=('calculated_cost', 'sum'),
            projects_count=('project_id', 'nunique')
        ).reset_index()
        
        result = []
        for _, row in client_agg.iterrows():
            result.append({
                "client_name": str(row['client_name']),
                "hours_imputed": float(round(row['hours_imputed'], 1)),
                "calculated_cost": float(round(row['calculated_cost'], 2)),
                "projects_count": int(row['projects_count'])
            })
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/aggregations/person', methods=['GET'])
def get_aggregations_by_person():
    """Retorna métricas de horas fichadas, horas imputadas, costo y uso del bot agrupados por Persona."""
    try:
        dfs = fetch_operational_data()
        _, dim_person, fact_time_clock, fact_project_imputation, fact_whatsapp_activity = process_dimensional_model(dfs)
        
        clock_agg = fact_time_clock.groupby('person_id')['hours_worked'].sum().reset_index()
        imputed_agg = fact_project_imputation.groupby('person_id').agg(
            hours_imputed=('hours_imputed', 'sum'),
            calculated_cost=('calculated_cost', 'sum')
        ).reset_index()
        wa_agg = fact_whatsapp_activity.groupby('person_id')['activity_type'].count().reset_index().rename(columns={'activity_type': 'bot_interactions'})
        
        # Merge dimensions with metrics
        merged = dim_person.merge(clock_agg, on='person_id', how='left')
        merged = merged.merge(imputed_agg, on='person_id', how='left')
        merged = merged.merge(wa_agg, on='person_id', how='left').fillna(0)
        
        result = []
        for _, row in merged.iterrows():
            result.append({
                "person_id": int(row['person_id']),
                "name": str(row['person_name']),
                "cargo": str(row['cargo_name']) if pd.notnull(row['cargo_name']) else "Sin Cargo",
                "hours_clocked": float(round(row['hours_worked'], 1)),
                "hours_imputed": float(round(row['hours_imputed'], 1)),
                "calculated_cost": float(round(row['calculated_cost'], 2)),
                "bot_interactions": int(row['bot_interactions'])
            })
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/aggregations/project', methods=['GET'])
def get_aggregations_by_project():
    """Retorna métricas acumuladas de horas e imputaciones por Obra/Proyecto."""
    try:
        dfs = fetch_operational_data()
        dim_project, _, _, fact_project_imputation, _ = process_dimensional_model(dfs)
        
        imputed_agg = fact_project_imputation.groupby('project_id').agg(
            hours_imputed=('hours_imputed', 'sum'),
            calculated_cost=('calculated_cost', 'sum')
        ).reset_index()
        
        merged = dim_project.merge(imputed_agg, left_on='id', right_on='project_id', how='left').fillna(0)
        
        result = []
        for _, row in merged.iterrows():
            result.append({
                "project_id": int(row['id']),
                "name": str(row['name']),
                "client_name": str(row['client_name']),
                "status": str(row['status']),
                "hours_imputed": float(round(row['hours_imputed'], 1)),
                "calculated_cost": float(round(row['calculated_cost'], 2))
            })
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ==========================================
# ENDPOINT MONOLÍTICO COMPATIBILIDAD DASHBOARD
# ==========================================

@app.route('/api/data', methods=['GET'])
def get_live_data():
    client_filter = request.args.get('client', 'all')
    project_filter = request.args.get('project', 'all')
    person_filter = request.args.get('person', 'all')

    try:
        dfs = fetch_operational_data()
        dim_project, dim_person_final, fact_time_clock, fact_project_imputation, fact_whatsapp_activity, distributed_clock = process_dimensional_model(dfs)
    except Exception as e:
        return jsonify({"error": f"Database error: {e}"}), 500

    # Apply filters dynamically on dataframes
    # Clients
    filtered_projects = dim_project
    if client_filter != 'all':
        filtered_projects = filtered_projects[filtered_projects['client_name'] == client_filter]
    
    # Projects
    if project_filter != 'all':
        filtered_projects = filtered_projects[filtered_projects['id'] == int(project_filter)]
        
    allowed_project_ids = set(filtered_projects['id'].tolist())
    
    # Filter Imputations
    filtered_imputations = fact_project_imputation[fact_project_imputation['project_id'].isin(allowed_project_ids)]
    
    # Operarios Global Filter
    filtered_persons = dim_person_final
    if person_filter != 'all':
        filtered_persons = filtered_persons[filtered_persons['person_name'] == person_filter]
        
    allowed_person_ids = set(filtered_persons['person_id'].tolist())
    
    # Filter Imputations and Clock by person
    filtered_imputations = filtered_imputations[filtered_imputations['person_id'].isin(allowed_person_ids)]
    filtered_time_clock = fact_time_clock[fact_time_clock['person_id'].isin(allowed_person_ids)]
    filtered_whatsapp = fact_whatsapp_activity[fact_whatsapp_activity['person_id'].isin(allowed_person_ids)]

    # Aggregate metrics
    total_projects_cnt = int(filtered_projects['id'].nunique())
    total_hours_clocked = float(filtered_time_clock['hours_worked'].sum())
    total_hours_imputed = float(filtered_imputations['hours_imputed'].sum())
    total_labor_cost = float(filtered_imputations['calculated_cost'].sum())
    total_whatsapp_reports = int(len(filtered_whatsapp))

    # Project Chart Data
    project_imputations_agg = filtered_imputations.groupby('project_id').agg(
        hours_imputed=('hours_imputed', 'sum'),
        calculated_cost=('calculated_cost', 'sum')
    ).reset_index()
    project_chart_df = filtered_projects.merge(project_imputations_agg, left_on='id', right_on='project_id', how='left').fillna(0)
    project_chart_df = project_chart_df.sort_values(by='calculated_cost', ascending=False)
    
    project_chart_data = {
        "labels": project_chart_df['name'].tolist(),
        "hours": project_chart_df['hours_imputed'].round(1).tolist(),
        "cost": project_chart_df['calculated_cost'].round(1).tolist(),
        "client": project_chart_df['client_name'].tolist(),
        "id": project_chart_df['id'].tolist()
    }

    # Person Chart Data
    clock_by_person = filtered_time_clock.groupby('person_id')['hours_worked'].sum().reset_index()
    imputed_by_person = filtered_imputations.groupby('person_id')['hours_imputed'].sum().reset_index()
    cost_by_person = filtered_imputations.groupby('person_id')['calculated_cost'].sum().reset_index()

    person_comparison = filtered_persons.merge(clock_by_person, on='person_id', how='left')
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

    # WhatsApp Activity Chart Data
    wa_counts = filtered_whatsapp['activity_type'].value_counts().to_dict()
    type_translation = {
        "outbound_text": "Mensajes de Texto (Outbound)",
        "outbound_template": "Mensajes de Plantilla (Outbound)",
        "outbound_document": "Documentos Enviados (Outbound)",
        "outbound_image": "Imágenes Enviadas (Outbound)",
        "outbound_audio": "Audios Enviados (Outbound)",
        "outbound_video": "Videos Enviados (Outbound)",
        "outbound_button": "Botones Enviados (Outbound)",
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
    wa_inbound_chart = {
        "labels": list(translated_wa_inbound.keys()),
        "values": [int(v) for v in translated_wa_inbound.values()]
    }

    wa_outbound_counts = {k: v for k, v in wa_counts.items() if k.startswith("outbound_")}
    translated_wa_outbound = {type_translation.get(k, k): v for k, v in wa_outbound_counts.items()}
    wa_outbound_chart = {
        "labels": list(translated_wa_outbound.keys()),
        "values": [int(v) for v in translated_wa_outbound.values()]
    }

    # Distributed Clock Charts Data
    filtered_clock = distributed_clock.copy()
    if client_filter != 'all':
        filtered_clock = filtered_clock[filtered_clock['client_name'] == client_filter]
    if project_filter != 'all':
        filtered_clock = filtered_clock[filtered_clock['project_id'] == int(project_filter)]
    if person_filter != 'all':
        filtered_clock = filtered_clock[filtered_clock['person_name'] == person_filter]

    clock_proj_agg = filtered_clock.groupby('project_name')['project_hours_worked'].sum().reset_index()
    clock_proj_agg = clock_proj_agg.sort_values(by='project_hours_worked', ascending=False)
    clocked_project_chart = {
        "labels": clock_proj_agg['project_name'].tolist(),
        "values": [round(float(v), 1) for v in clock_proj_agg['project_hours_worked'].tolist()]
    }

    clock_pers_agg = filtered_clock.groupby('person_name')['project_hours_worked'].sum().reset_index()
    clock_pers_agg = clock_pers_agg.sort_values(by='project_hours_worked', ascending=False)
    clocked_person_chart = {
        "labels": clock_pers_agg['person_name'].tolist(),
        "values": [round(float(v), 1) for v in clock_pers_agg['project_hours_worked'].tolist()]
    }

    # Alerts List
    daily_clock_agg = filtered_time_clock.groupby(['work_date', 'person_id'])['hours_worked'].sum().reset_index()
    daily_imputed_agg = filtered_imputations.groupby(['date', 'person_id'])['hours_imputed'].sum().reset_index()
    daily_imputed_agg.rename(columns={'date': 'work_date'}, inplace=True)
    daily_clock_agg['work_date'] = daily_clock_agg['work_date'].astype(str)
    daily_imputed_agg['work_date'] = daily_imputed_agg['work_date'].astype(str)

    daily_compare = pd.merge(daily_clock_agg, daily_imputed_agg, on=['work_date', 'person_id'], how='outer').fillna(0)
    daily_compare = daily_compare.merge(dim_person_final[['person_id', 'person_name']], on='person_id', how='left')
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

    # Detailed Project List
    detailed_projects = []
    for _, row in project_chart_df.iterrows():
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

    # Operarios Summary List
    operarios_summary = []
    for _, row in person_comparison.iterrows():
        person_wa = filtered_whatsapp[filtered_whatsapp['person_id'] == row['person_id']]
        op_wa_counts = person_wa['activity_type'].value_counts().to_dict()
        
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

    # Daily Records (Complete compare for frontend flexible sorting/grouping)
    daily_records = []
    for _, row in daily_compare.iterrows():
        daily_records.append({
            "date": str(row['work_date']),
            "person_name": str(row['person_name']),
            "hours_worked": float(round(row['hours_worked'], 1)),
            "hours_imputed": float(round(row['hours_imputed'], 1))
        })

    # Available filters metadata for client dropdowns
    available_clients = sorted(list(dim_project['client_name'].unique()))
    available_projects = []
    for _, row in dim_project.sort_values(by='name').iterrows():
        available_projects.append({"id": int(row['id']), "name": str(row['name']), "client_name": str(row['client_name'])})
    available_people = sorted(list(dim_person_final['person_name'].unique()))

    payload = {
        "kpis": {
            "total_projects": total_projects_cnt,
            "total_hours_clocked": round(total_hours_clocked, 1),
            "total_hours_imputed": round(total_hours_imputed, 1),
            "total_labor_cost": round(total_labor_cost, 2),
            "total_whatsapp_reports": total_whatsapp_reports
        },
        "project_chart": project_chart_data,
        "person_chart": person_chart_data,
        "wa_inbound_chart": wa_inbound_chart,
        "wa_outbound_chart": wa_outbound_chart,
        "clocked_project_chart": clocked_project_chart,
        "clocked_person_chart": clocked_person_chart,
        "alerts": alerts_list,
        "detailed_projects": detailed_projects,
        "operarios_summary": operarios_summary,
        "daily_records": daily_records,
        "filters": {
            "clients": available_clients,
            "projects": available_projects,
            "people": available_people
        }
    }

    return jsonify(payload)

@app.route('/api/aggregations/conversations', methods=['GET'])
def get_conversations_aggregation():
    """Retorna agregaciones y métricas en vivo sobre mensajes, canales y sesiones del bot."""
    try:
        dfs = fetch_operational_data()
        messages_df = dfs.get("messages", pd.DataFrame())
        sessions_df = dfs.get("daily_sessions", pd.DataFrame())
        voice_df = dfs.get("voice_inputs", pd.DataFrame())
        action_df = dfs.get("whatsapp_action_log", pd.DataFrame())
        
        total_messages = int(len(messages_df)) if not messages_df.empty else 0
        total_sessions = int(len(sessions_df)) if not sessions_df.empty else 0
        total_voice_inputs = int(len(voice_df)) if not voice_df.empty else 0
        total_bot_actions = int(len(action_df)) if not action_df.empty else 0
        
        channels_agg = {}
        if not messages_df.empty and 'channel' in messages_df.columns and 'direction' in messages_df.columns:
            grouped = messages_df.groupby(['channel', 'direction']).size().unstack(fill_value=0).to_dict(orient='index')
            for ch, dir_counts in grouped.items():
                channels_agg[str(ch)] = {str(k): int(v) for k, v in dir_counts.items()}
                
        states_agg = {}
        if not sessions_df.empty and 'state' in sessions_df.columns:
            states_counts = sessions_df['state'].value_counts().to_dict()
            states_agg = {str(k): int(v) for k, v in states_counts.items()}

        types_agg = {}
        if not messages_df.empty and 'type' in messages_df.columns:
            types_counts = messages_df['type'].value_counts().to_dict()
            types_agg = {str(k): int(v) for k, v in types_counts.items()}

        return jsonify({
            "total_messages": total_messages,
            "total_daily_sessions": total_sessions,
            "total_voice_transcripts": total_voice_inputs,
            "total_bot_actions": total_bot_actions,
            "channel_breakdown": channels_agg,
            "message_types": types_agg,
            "session_states": states_agg
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':

    print("Starting GestObra Production-Ready Backend server on http://localhost:8000...")
    app.run(host='0.0.0.0', port=8000, debug=True)
