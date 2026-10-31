import random
from pathlib import Path

import pandas as pd

from people import make_people

SEED = 43

PROCEDURES = [
    "Kidney transplant",
    "Liver transplant",
    "Heart transplant",
    "LVAD implant",
]


def make_ehr(people, seed=SEED):
    rng = random.Random(seed)
    rows = []
    for _, p in people.iterrows():
        proc_date = pd.Timestamp("2018-01-01") + pd.Timedelta(
            days=rng.randint(0, 365 * 7)
        )
        rows.append(
            {
                "mrn": f"MRN-{p['person_id'] + 100000:06d}",
                "ssn": p["ssn"],
                "name": p["name"],
                "dob": p["dob"].strftime("%Y-%m-%d"),
                "sex": p["sex"],
                "procedure_date": proc_date.strftime("%Y-%m-%d"),
                "procedure_name": rng.choice(PROCEDURES),
                "_person_id": p["person_id"],
            }
        )
    return pd.DataFrame(rows)


def plant_ehr_problems(ehr, seed=SEED):
    rng = random.Random(seed + 1)
    ehr = ehr.copy()

    # Problem 1: duplicate patients (same person, second MRN)
    dup_idx = rng.sample(range(len(ehr)), 8)
    dups = ehr.iloc[dup_idx].copy()
    dups["mrn"] = [f"MRN-{900000 + i}" for i in range(len(dups))]
    ehr = pd.concat([ehr, dups], ignore_index=True)

    # Problem 2: mixed date formats inside procedure_date
    fmt_idx = rng.sample(range(len(ehr)), 40)
    for i in fmt_idx:
        d = pd.Timestamp(ehr.at[i, "procedure_date"])
        ehr.at[i, "procedure_date"] = rng.choice(
            [d.strftime("%m/%d/%Y"), d.strftime("%d-%b-%Y")]
        )
    return ehr


if __name__ == "__main__":
    out = Path("data")
    out.mkdir(exist_ok=True)
    ehr = make_ehr(make_people())
    ehr.to_csv(out / "ehr_clean.csv", index=False)
    dirty = plant_ehr_problems(ehr)
    dirty.to_csv(out / "ehr_dirty.csv", index=False)
    print(len(ehr), "clean rows,", len(dirty), "dirty rows written")
    print(dirty["procedure_date"].sample(8, random_state=1).to_string())