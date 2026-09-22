with source as (
    select * from {{ source('gestobra_public', 'users') }}
),
renamed as (
    select
        id as user_id,
        name as user_name,
        email as user_email,
        phone as user_phone,
        created_at,
        updated_at
    from source
)
select * from renamed
