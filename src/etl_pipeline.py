import os
import pandas as pd
import psycopg2
from datetime import datetime, timedelta

# Create data directory if it doesn't exist
os.makedirs("data", exist_ok=True)

# Parse .env file manually to support both colon and equals separators
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

print("Extracting data from PostgreSQL (Read-Only)...")

# Read tables into DataFrames
tables = [
    "projects", "people", "users", "team_user", "cargos", "time_clock_records",
    "project_imputations", "tasks", "whatsapp_action_log", "voice_inputs", 
    "whatsapp_media_inputs", "resources", "teams", "messages", "daily_sessions",
    "whatsapp_inbound_messages"
]

dfs = {}

try:
    conn = psycopg2.connect(
        host=db_host,
        database=db_name,
        user=db_user,
        password=db_password,
        port=5432
    )
    
    for table in tables:
        query = f'SELECT * FROM "public"."{table}"'
        dfs[table] = pd.read_sql_query(query, conn)
        print(f"  Loaded public.{table}: {len(dfs[table])} rows")
        
    conn.close()
except Exception as e:
    print(f"Error loading tables: {e}")
    exit(1)

print("\nProcessing Dimensions...")

# 1. dim_date
# Generate date range from 2025-01-01 to 2027-12-31
start_date = datetime(2025, 1, 1)
end_date = datetime(2027, 12, 31)
date_list = [start_date + timedelta(days=x) for x in range((end_date - start_date).days + 1)]
dim_date = pd.DataFrame({
    'date': [d.date() for d in date_list],
    'year': [d.year for d in date_list],
    'month': [d.month for d in date_list],
    'month_name': [d.strftime('%B') for d in date_list],
    'day': [d.day for d in date_list],
    'day_of_week': [d.weekday() + 1 for d in date_list], # 1 = Monday, 7 = Sunday
    'day_name': [d.strftime('%A') for d in date_list]
})
dim_date.to_csv("data/dim_date.csv", index=False)
print("  Saved data/dim_date.csv")

# 2. dim_project
projects_df = dfs["projects"]
teams_df_names = dfs["teams"][["id", "name"]].rename(columns={"id": "project_team_id", "name": "client_name"})
dim_project = projects_df.merge(teams_df_names, left_on="team_id", right_on="project_team_id", how="left")
dim_project["client_name"] = dim_project["client_name"].fillna("Sin Cliente")

dim_project_final = dim_project[["id", "name", "status", "budget", "actual_cost", "start_date", "end_date", "client_name"]].copy()
dim_project_final.to_csv("data/dim_project.csv", index=False)
print("  Saved data/dim_project.csv")

# 3. dim_person
# Combine people, resources (for names), users, cargos, and team_user (for role/hourly_rate)
people_df = dfs["people"]
resources_df = dfs["resources"][["id", "name", "nickname", "hourly_rate"]].rename(columns={"id": "resource_id", "hourly_rate": "resource_rate"})
users_df = dfs["users"][["id", "name", "email", "phone"]].rename(columns={"id": "user_id_usr", "name": "user_name", "email": "user_email", "phone": "user_phone"})
cargos_df = dfs["cargos"][["id", "name"]].rename(columns={"id": "cargo_id_cgo", "name": "cargo_name"})
team_user_df = dfs["team_user"][["user_id", "team_id", "role", "hourly_rate"]].rename(columns={"hourly_rate": "team_rate"})

# Join people with resources (class table inheritance)
dim_person = people_df.merge(resources_df, left_on="id", right_on="resource_id", how="left")

# Join with users to fallback or supplement name and contact info
dim_person = dim_person.merge(users_df, left_on="user_id", right_on="user_id_usr", how="left")

# Combine name and contact info
dim_person["person_name"] = dim_person["name"].fillna(dim_person["user_name"]).fillna("Operario " + dim_person["id"].astype(str))
dim_person["person_email"] = dim_person["email"].fillna(dim_person["user_email"])
dim_person["person_phone"] = dim_person["phone"].fillna(dim_person["user_phone"])

# Join with cargos to get cargo name
dim_person = dim_person.merge(cargos_df, left_on="cargo_id", right_on="cargo_id_cgo", how="left")

# Join with team_user to get role and team rate
dim_person = dim_person.merge(team_user_df, left_on="user_id", right_on="user_id", how="left")

# Merge with teams_df_names to resolve team client name
dim_person = dim_person.merge(teams_df_names, left_on="team_id", right_on="project_team_id", how="left")
dim_person = dim_person.rename(columns={"client_name": "team_client_name"})

# Determine hourly rate: fallback resource_rate -> team_rate -> default 20.0
dim_person["hourly_rate_final"] = dim_person["resource_rate"].fillna(dim_person["team_rate"]).fillna(20.0)

# Filter/select final columns for dim_person
dim_person_final = dim_person[[
    "id", "person_name", "person_email", "person_phone", "cargo_name", "role", 
    "is_worker", "is_client", "is_external_worker", "is_supplier", "hourly_rate_final"
]].copy().rename(columns={"id": "person_id"})

dim_person_final.to_csv("data/dim_person.csv", index=False)
print("  Saved data/dim_person.csv")

# 4. dim_task
dim_task = dfs["tasks"][["id", "project_id", "title", "status", "priority", "estimated_hours"]].copy().rename(columns={"id": "task_id"})
dim_task.to_csv("data/dim_task.csv", index=False)
print("  Saved data/dim_task.csv")

print("\nProcessing Facts...")

# 1. fact_time_clock
time_clock = dfs["time_clock_records"].copy()
time_clock["entry_at"] = pd.to_datetime(time_clock["entry_at"])
time_clock["exit_at"] = pd.to_datetime(time_clock["exit_at"])
time_clock["hours_worked"] = (time_clock["exit_at"] - time_clock["entry_at"]).dt.total_seconds() / 3600.0
time_clock["hours_worked"] = time_clock["hours_worked"].round(2)

# Select columns
fact_time_clock = time_clock[["id", "work_date", "person_id", "entry_at", "exit_at", "hours_worked"]].copy()
fact_time_clock.to_csv("data/fact_time_clock.csv", index=False)
print("  Saved data/fact_time_clock.csv")

# 2. fact_project_imputation
imputations = dfs["project_imputations"].copy()
imputations["date"] = pd.to_datetime(imputations["date"]).dt.date

# Convert minutes to hours if minutes is present and not null, otherwise amount is hours
imputations["hours_imputed"] = imputations["minutes"].apply(lambda m: m / 60.0 if pd.notnull(m) else 0.0)
imputations.loc[imputations["hours_imputed"] == 0.0, "hours_imputed"] = imputations["amount"].astype(float)

# Join with dim_person to get the person's final hourly rate if imputation's rate is null/zero
imputations = imputations.merge(dim_person_final[["person_id", "hourly_rate_final"]], left_on="resource_id", right_on="person_id", how="left")
imputations["hourly_rate_imputed"] = imputations["hourly_rate"].astype(float)
imputations.loc[(imputations["hourly_rate_imputed"] == 0.0) | (imputations["hourly_rate_imputed"].isnull()), "hourly_rate_imputed"] = imputations["hourly_rate_final"]
imputations["hourly_rate_imputed"] = imputations["hourly_rate_imputed"].fillna(20.0)

# Calculate cost
imputations["calculated_cost"] = (imputations["hours_imputed"] * imputations["hourly_rate_imputed"]).round(2)

fact_imputations = imputations[[
    "id", "date", "project_id", "resource_id", "hours_imputed", "hourly_rate_imputed", "calculated_cost", "description"
]].copy().rename(columns={"resource_id": "person_id"})

fact_imputations.to_csv("data/fact_project_imputation.csv", index=False)
print("  Saved data/fact_project_imputation.csv")

# 3. fact_whatsapp_activity
# Aggregate whatsapp_action_log, voice_inputs, and whatsapp_media_inputs by date and person
user_to_person = people_df[people_df["user_id"].notnull()][["user_id", "id"]].set_index("user_id")["id"].to_dict()

# Process action log
action_log = dfs["whatsapp_action_log"].copy()
action_log["date"] = pd.to_datetime(action_log["created_at"]).dt.date
action_log["person_id"] = action_log["user_id"].map(user_to_person)

# Process voice inputs
voice_in = dfs["voice_inputs"].copy()
voice_in["date"] = pd.to_datetime(voice_in["created_at"]).dt.date
voice_in["person_id"] = voice_in["user_id"].map(user_to_person)

# Process media inputs
media_in = dfs["whatsapp_media_inputs"].copy()
media_in["date"] = pd.to_datetime(media_in["created_at"]).dt.date
media_in["person_id"] = media_in["user_id"].map(user_to_person)

# Aggregate counts per day per person
act_list = []

# Actions
for _, row in action_log.iterrows():
    if pd.notnull(row["date"]):
        direction = str(row.get("direction", "")).lower()
        if direction == "internal":
            continue
        
        if direction == "outbound":
            msg_type = row.get("message_type", "text")
            if pd.isnull(msg_type) or not msg_type:
                msg_type = "text"
            act_list.append({
                "date": row["date"],
                "person_id": row["person_id"],
                "activity_type": f"outbound_{str(msg_type).lower()}",
                "media_count": 0,
                "voice_duration_seconds": 0
            })
        elif direction == "inbound":
            msg_type = row.get("message_type", "text")
            if pd.isnull(msg_type) or not msg_type:
                msg_type = "text"
            act_list.append({
                "date": row["date"],
                "person_id": row["person_id"],
                "activity_type": f"inbound_{str(msg_type).lower()}",
                "media_count": 0,
                "voice_duration_seconds": 0
            })

# Voices
for _, row in voice_in.iterrows():
    if pd.notnull(row["date"]):
        dur_ms = row["media_duration_ms"]
        dur_sec = dur_ms / 1000.0 if pd.notnull(dur_ms) else 0.0
        act_list.append({
            "date": row["date"],
            "person_id": row["person_id"],
            "activity_type": "inbound_audio",
            "media_count": 0,
            "voice_duration_seconds": int(dur_sec)
        })

# Media
for _, row in media_in.iterrows():
    if pd.notnull(row["date"]):
        media_kind = str(row.get("media_kind", "image")).lower()
        act_list.append({
            "date": row["date"],
            "person_id": row["person_id"],
            "activity_type": f"inbound_{media_kind}",
            "media_count": 1,
            "voice_duration_seconds": 0
        })

if act_list:
    fact_whatsapp_activity = pd.DataFrame(act_list)
    fact_whatsapp_activity["person_id"] = fact_whatsapp_activity["person_id"].fillna(-1).astype(int)
    fact_whatsapp_activity.to_csv("data/fact_whatsapp_activity.csv", index=False)
    print("  Saved data/fact_whatsapp_activity.csv")
else:
    fact_whatsapp_activity = pd.DataFrame(columns=["date", "person_id", "activity_type", "media_count", "voice_duration_seconds"])
    fact_whatsapp_activity.to_csv("data/fact_whatsapp_activity.csv", index=False)
    print("  Saved empty data/fact_whatsapp_activity.csv")

# 4. Proportional distribution of clocked hours to projects
daily_clock = fact_time_clock.groupby(['work_date', 'person_id'])['hours_worked'].sum().reset_index()
daily_clock['work_date'] = daily_clock['work_date'].astype(str)

daily_imputed = fact_imputations.copy()
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

proj_map = dict(zip(dim_project_final['id'], dim_project_final['name']))
proj_map[-1] = "Sin Obra"
client_map = dict(zip(dim_project_final['id'], dim_project_final['client_name']))
pers_map = dict(zip(dim_person_final['person_id'], dim_person_final['person_name']))
person_team_client = dict(zip(dim_person['id'], dim_person['team_client_name']))

distributed_clock['project_name'] = distributed_clock['project_id'].map(proj_map).fillna("Obra Desconocida")
distributed_clock['client_name'] = distributed_clock['project_id'].map(client_map)

# Fallback client name for unimputed projects to person's team client name
unimputed_mask = distributed_clock['project_id'] == -1
distributed_clock.loc[unimputed_mask, 'client_name'] = distributed_clock.loc[unimputed_mask, 'person_id'].map(person_team_client)
distributed_clock['client_name'] = distributed_clock['client_name'].fillna("Sin Cliente")

distributed_clock['person_name'] = distributed_clock['person_id'].map(pers_map).fillna("Operario Desconocido")

distributed_clock.to_csv("data/distributed_clock.csv", index=False)
print("  Saved data/distributed_clock.csv")

# 5. fact_messages
msg_df = dfs["messages"].copy()
msg_df["created_at_dt"] = pd.to_datetime(msg_df["created_at"])
msg_df["date"] = msg_df["created_at_dt"].dt.date
# Map person_id if null using user_to_person map
msg_df["person_id"] = msg_df["person_id"].fillna(msg_df["user_id"].map(user_to_person)).fillna(-1).astype(int)

# Map person_name: first try person_id map, then fallback to contact_name, then fallback to Desconocido
msg_df["person_name"] = msg_df["person_id"].map(pers_map).fillna(msg_df["contact_name"]).fillna("Desconocido")

# Classification: Automatic vs Manual
def classify_msg(row):
    direct = str(row.get('direction', '')).lower()
    mtype = str(row.get('type', '')).lower()
    if direct in ['outgoing', 'outbound']:
        return True, 'Bot_Automatico'
    elif mtype in ['call']:
        return False, 'Llamada_Manual'
    elif mtype in ['audio']:
        return False, 'Nota_Voz_Manual'
    elif mtype in ['image', 'video', 'document']:
        return False, 'Multimedia_Manual'
    else:
        return False, 'Texto_Manual'

class_res = msg_df.apply(classify_msg, axis=1)
msg_df["is_automated"] = [c[0] for c in class_res]
msg_df["origin_category"] = [c[1] for c in class_res]

fact_messages = msg_df[[
    "id", "date", "created_at", "user_id", "person_id", "person_name", 
    "channel", "direction", "type", "contact_name", "call_duration", "is_read",
    "is_automated", "origin_category"
]].copy()
fact_messages.to_csv("data/fact_messages.csv", index=False)
print("  Saved data/fact_messages.csv")

# 6. fact_daily_sessions
sessions_df = dfs["daily_sessions"].copy()
sessions_df["person_id"] = sessions_df["user_id"].map(user_to_person).fillna(-1).astype(int)
sessions_df["person_name"] = sessions_df["person_id"].map(pers_map).fillna("Operario Desconocido")

fact_daily_sessions = sessions_df[[
    "id", "session_date", "user_id", "person_id", "person_name", 
    "state", "pending_action", "started_at", "finished_at"
]].copy()
fact_daily_sessions.to_csv("data/fact_daily_sessions.csv", index=False)
print("  Saved data/fact_daily_sessions.csv")

print("\nETL COMPLETE successfully! Data stored in data/*.csv.")

