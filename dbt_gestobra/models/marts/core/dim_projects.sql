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
