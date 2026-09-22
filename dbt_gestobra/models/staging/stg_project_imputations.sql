with source as (
    select * from {{ source('gestobra_public', 'project_imputations') }}
),
renamed as (
    select
        id as imputation_id,
        project_id,
        user_id,
        task_id,
        hours_imputed,
        date as imputation_date,
        created_at
    from source
)
select * from renamed
