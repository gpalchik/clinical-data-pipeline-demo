import pandas as pd

ehr = pd.read_csv("data/ehr_clean.csv")
reg = pd.read_csv("data/registry_clean.csv")
srv = pd.read_csv("data/survey_clean.csv")

in_ehr = set(ehr["_person_id"])
in_reg = set(reg["_person_id"])
in_srv = set(srv["_person_id"])

print("EHR only:", len(in_ehr - in_reg - in_srv))
print("Registry only:", len(in_reg - in_ehr - in_srv))
print("Survey only:", len(in_srv - in_ehr - in_reg))
print("EHR + Registry (not Survey):", len((in_ehr & in_reg) - in_srv))
print("EHR + Survey (not Registry):", len((in_ehr & in_srv) - in_reg))
print("Registry + Survey (not EHR):", len((in_reg & in_srv) - in_ehr))
print("All three:", len(in_ehr & in_reg & in_srv))
print("In any source:", len(in_ehr | in_reg | in_srv))