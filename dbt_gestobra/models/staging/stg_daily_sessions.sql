with source as (
    select * from {{ source('gestobra_public', 'daily_sessions') }}
),
renamed as (
    select
        id as session_id,
        user_id,
        session_date,
        state,
        started_at,
        finished_at
    from source
)
select * from renamed
