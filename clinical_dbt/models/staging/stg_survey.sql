select
    record_id::int as record_id,
    patient_name,
    mrn,
    survey_date::date as survey_date,
    weight::double as weight,
    bp_syst::int as bp_syst,
    bp_diast::int as bp_diast,
    likert_1::int as likert_1,
    likert_2::int as likert_2
from {{ source('raw', 'survey_export') }}