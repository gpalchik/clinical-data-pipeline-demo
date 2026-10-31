from pathlib import Path

from people import make_people
from ehr import make_ehr, plant_ehr_problems
from registry import make_registry, plant_registry_problems
from survey import make_survey, plant_survey_problems

out = Path("data/raw")
out.mkdir(parents=True, exist_ok=True)

people = make_people()
ehr_clean = make_ehr(people)
reg_clean = make_registry(people, ehr_clean)
srv_clean = make_survey(people)

ehr = plant_ehr_problems(ehr_clean)
reg = plant_registry_problems(reg_clean)
srv = plant_survey_problems(srv_clean)

# Hidden truth key is dropped from the files the pipeline will see
ehr.drop(columns=["_person_id"]).to_csv(out / "ehr_extract.csv", index=False)
reg.drop(columns=["_person_id"]).to_csv(out / "registry_extract.csv", index=False)
srv.drop(columns=["_person_id"]).to_csv(out / "survey_export.csv", index=False)

print("ehr_extract.csv:", len(ehr), "rows")
print("registry_extract.csv:", len(reg), "rows")
print("survey_export.csv:", len(srv), "rows")

# Truth log: what was planted, keyed by the hidden person id
log = []

# EHR duplicates: _person_id appears more than once in the dirty EHR
dup_ids = ehr["_person_id"][ehr["_person_id"].duplicated()].unique()
for pid in dup_ids:
    log.append({"source": "ehr", "problem": "duplicate_patient", "person_id": pid})

# Registry: compare dirty to clean, matched on _person_id
reg_c = reg_clean.set_index("_person_id")
reg_d = reg.set_index("_person_id")
for pid in reg_d.index:
    if reg_d.at[pid, "dob"] != reg_c.at[pid, "dob"]:
        log.append({"source": "registry", "problem": "dob_off_by_one_day", "person_id": pid})
    if reg_d.at[pid, "name"] != reg_c.at[pid, "name"]:
        log.append({"source": "registry", "problem": "name_misspelled", "person_id": pid})

# Survey: compare dirty to clean, matched on _person_id
srv_c = srv_clean.set_index("_person_id")
srv_d = srv.set_index("_person_id")
for pid in srv_d.index:
    if srv_d.at[pid, "mrn"] != srv_c.at[pid, "mrn"]:
        log.append({"source": "survey", "problem": "mrn_transposed", "person_id": pid})
    if srv_d.at[pid, "patient_name"] != srv_c.at[pid, "patient_name"]:
        log.append({"source": "survey", "problem": "name_misspelled", "person_id": pid})

import pandas as pd

log_df = pd.DataFrame(log)
log_df.to_csv("data/truth_log.csv", index=False)
print(log_df.groupby(["source", "problem"]).size())