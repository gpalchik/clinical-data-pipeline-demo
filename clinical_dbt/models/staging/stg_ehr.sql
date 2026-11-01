select
    mrn,
    ssn,
    name,
    dob::DATE as dob,
    sex,
    COALESCE(
        TRY_STRPTIME(procedure_date, '%Y-%m-%d'),
        TRY_STRPTIME(procedure_date, '%m/%d/%Y'),
        TRY_STRPTIME(procedure_date, '%d-%b-%Y')
    )::DATE AS clean_procedure_date,
    procedure_name
from {{ source('raw', 'ehr_extract') }}