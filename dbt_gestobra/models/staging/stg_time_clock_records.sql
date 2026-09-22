with source as (
    select * from {{ source('gestobra_public', 'time_clock_records') }}
),
renamed as (
    select
        id as time_clock_id,
        user_id,
        team_id,
        record_type,
        clock_time,
        created_at
    from source
)
select * from renamed
