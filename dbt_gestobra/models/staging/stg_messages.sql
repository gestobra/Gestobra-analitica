with source as (
    select * from {{ source('gestobra_public', 'messages') }}
),
renamed as (
    select
        id as message_id,
        user_id,
        team_id,
        person_id,
        contact_name,
        channel,
        direction,
        type as message_type,
        created_at
    from source
)
select * from renamed
