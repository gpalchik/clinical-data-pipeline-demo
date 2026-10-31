import random
from pathlib import Path

import pandas as pd
from faker import Faker

SEED = 42
N_PEOPLE = 200


def make_ssn(rng):
    # Area 900-999 is, as far as I know, never issued. Verify on ssa.gov.
    area = rng.randint(900, 999)
    group = rng.randint(1, 99)
    serial = rng.randint(1, 9999)
    return f"{area:03d}-{group:02d}-{serial:04d}"


def make_people(n=N_PEOPLE, seed=SEED):
    rng = random.Random(seed)
    Faker.seed(seed)
    fake = Faker()
    rows = []
    for i in range(1, n + 1):
        sex = rng.choice(["M", "F"])
        first = fake.first_name_male() if sex == "M" else fake.first_name_female()
        rows.append(
            {
                "person_id": i,
                "name": f"{first} {fake.last_name()}",
                "dob": fake.date_of_birth(minimum_age=28, maximum_age=80),
                "sex": sex,
                "ssn": make_ssn(rng),
            }
        )
    return pd.DataFrame(rows)


if __name__ == "__main__":
    out = Path("data")
    out.mkdir(exist_ok=True)
    people = make_people()
    people.to_csv(out / "people_truth.csv", index=False)
    print(people.head())
    print(len(people), "people written")