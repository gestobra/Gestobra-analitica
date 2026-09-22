with source as (
    select * from {{ source('gestobra_public', 'companies') }}
),
renamed as (
    select
        id as company_id,
        name as client_name,
        tax_id,
        phone,
        email,
        created_at
    from source
)
select * from renamed
