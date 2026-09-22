with source as (
    select * from {{ source('gestobra_public', 'people') }}
),
renamed as (
    select
        id as person_id,
        team_id,
        user_id,
        name as person_name,
        email as person_email,
        phone as person_phone,
        cargo_id,
        is_worker,
        is_client,
        is_supplier,
        created_at,
        updated_at
    from source
)
select * from renamed
