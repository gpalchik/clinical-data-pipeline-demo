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