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
