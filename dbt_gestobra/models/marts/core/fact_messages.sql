with messages as (
    select * from {{ ref('stg_messages') }}
)
select
    m.message_id,
    m.created_at::date as date,
    m.created_at,
    m.user_id,
    m.person_id,
    m.contact_name,
    m.channel,
    m.direction,
    m.message_type,
    case
        when lower(m.direction) in ('outgoing', 'outbound') then true
        else false
    end as is_automated
from messages m
