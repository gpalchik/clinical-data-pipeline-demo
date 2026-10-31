import random
from pathlib import Path

import pandas as pd

from people import make_people

SEED = 44

EVENT_TYPES = ["Infection", "Rejection", "Bleeding", "Stroke", "Readmission"]


def make_registry(people, ehr, seed=SEED):
    rng = random.Random(seed)
    # Registry covers about 85% of people, so some are missing on purpose
    subset = people.sample(frac=0.85, random_state=seed)
    ehr_dates = ehr.set_index("_person_id")["procedure_date"].to_dict()
    rows = []
    for _, p in subset.iterrows():
        surgery = pd.Timestamp(ehr_dates[p["person_id"]])
        has_event = rng.random() < 0.3
        event_date = (
            (surgery + pd.Timedelta(days=rng.randint(1, 180))).strftime("%Y-%m-%d")
            if has_event
            else None
        )
        rows.append(
            {
                "id": f"REG-{p['person_id'] * 7 + 1000:05d}",
                "ssn": p["ssn"],
                "name": p["name"],
                "dob": p["dob"].strftime("%Y-%m-%d"),
                "surgery_date": surgery.strftime("%Y-%m-%d"),
                "adverse_event_date": event_date,
                "adverse_event_type": rng.choice(EVENT_TYPES) if has_event else None,
                "_person_id": p["person_id"],
            }
        )
    return pd.DataFrame(rows)


def plant_registry_problems(reg, seed=SEED):
    rng = random.Random(seed + 1)
    reg = reg.copy()
    idx = rng.sample(range(len(reg)), 12)

    # Problem: DOB differs from the EHR by one day (6 rows)
    for i in idx[:6]:
        d = pd.Timestamp(reg.at[i, "dob"]) + pd.Timedelta(days=rng.choice([-1, 1]))
        reg.at[i, "dob"] = d.strftime("%Y-%m-%d")

    # Problem: misspelled last name, one letter dropped (6 rows)
    for i in idx[6:]:
        first, last = reg.at[i, "name"].split(" ", 1)
        pos = rng.randint(0, len(last) - 1)
        reg.at[i, "name"] = first + " " + last[:pos] + last[pos + 1:]
    return reg


if __name__ == "__main__":
    from ehr import make_ehr

    out = Path("data")
    out.mkdir(exist_ok=True)
    people = make_people()
    ehr = make_ehr(people)
    reg = make_registry(people, ehr)
    reg.to_csv(out / "registry_clean.csv", index=False)
    dirty = plant_registry_problems(reg)
    dirty.to_csv(out / "registry_dirty.csv", index=False)
    print(len(reg), "clean rows,", len(dirty), "dirty rows written")
    changed = dirty[(dirty["dob"] != reg["dob"]) | (dirty["name"] != reg["name"])]
    print(len(changed), "rows changed")