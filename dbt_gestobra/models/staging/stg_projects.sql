with source as (
    select * from {{ source('gestobra_public', 'projects') }}
),
renamed as (
    select
        id as project_id,
        team_id,
        company_id,
        name as project_name,
        description,
        status,
        created_at,
        updated_at,
        deleted_at
    from source
)
select * from renamed
