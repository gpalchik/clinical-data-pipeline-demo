select
    id as registry_id,
    dob::DATE as dob,
    COALESCE(
        TRY_STRPTIME(surgery_date, '%Y-%m-%d'),
        TRY_STRPTIME(surgery_date, '%m/%d/%Y'),
        TRY_STRPTIME(surgery_date, '%d-%b-%Y')
    )::DATE AS surgery_date,
        COALESCE(
        TRY_STRPTIME(adverse_event_date, '%Y-%m-%d'),
        TRY_STRPTIME(adverse_event_date, '%m/%d/%Y'),
        TRY_STRPTIME(adverse_event_date, '%d-%b-%Y')
    )::DATE AS adverse_event_date,
    ssn,
    name,
    adverse_event_type
from {{ source('raw', 'registry_extract') }}
