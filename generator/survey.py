import random
from pathlib import Path

import pandas as pd

from people import make_people

SEED = 45


def transpose_mrn(mrn, rng):
    # Swap two adjacent DIFFERENT digits in the numeric part, e.g. MRN-100123 -> MRN-100132
    prefix, digits = mrn.split("-")
    d = list(digits)
    positions = [i for i in range(len(d) - 1) if d[i] != d[i + 1]]
    pos = rng.choice(positions)
    d[pos], d[pos + 1] = d[pos + 1], d[pos]
    return prefix + "-" + "".join(d)


def make_survey(people, seed=SEED):
    rng = random.Random(seed)
    # Survey covers about 70% of people
    subset = people.sample(frac=0.70, random_state=seed)
    rows = []
    record_id = 1
    for _, p in subset.iterrows():
        rows.append(
            {
                "record_id": record_id,
                "patient_name": p["name"],
                "mrn": f"MRN-{p['person_id'] + 100000:06d}",
                "survey_date": (
                    pd.Timestamp("2019-01-01")
                    + pd.Timedelta(days=rng.randint(0, 365 * 7))
                ).strftime("%Y-%m-%d"),
                "weight": round(rng.uniform(50, 120), 1),
                "bp_syst": rng.randint(95, 160),
                "bp_diast": rng.randint(55, 100),
                "likert_1": rng.randint(1, 5),
                "likert_2": rng.randint(1, 5),
                "_person_id": p["person_id"],
            }
        )
        record_id += 1
    return pd.DataFrame(rows)


def plant_survey_problems(survey, seed=SEED):
    rng = random.Random(seed + 1)
    survey = survey.copy()
    idx = rng.sample(range(len(survey)), 10)

    # Problem: MRN transposed (5 rows)
    for i in idx[:5]:
        survey.at[i, "mrn"] = transpose_mrn(survey.at[i, "mrn"], rng)

    # Problem: misspelled first name, one letter dropped (5 rows)
    for i in idx[5:]:
        first, last = survey.at[i, "patient_name"].split(" ", 1)
        pos = rng.randint(0, len(first) - 1)
        survey.at[i, "patient_name"] = first[:pos] + first[pos + 1:] + " " + last
    return survey


if __name__ == "__main__":
    out = Path("data")
    out.mkdir(exist_ok=True)
    survey = make_survey(make_people())
    survey.to_csv(out / "survey_clean.csv", index=False)
    dirty = plant_survey_problems(survey)
    dirty.to_csv(out / "survey_dirty.csv", index=False)
    print(len(survey), "clean rows,", len(dirty), "dirty rows written")
    changed = dirty[(dirty["mrn"] != survey["mrn"]) | (dirty["patient_name"] != survey["patient_name"])]
    print(len(changed), "rows changed")