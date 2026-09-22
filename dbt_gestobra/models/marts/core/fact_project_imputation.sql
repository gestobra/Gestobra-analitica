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
