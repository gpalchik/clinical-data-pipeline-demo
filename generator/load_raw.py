import duckdb

con = duckdb.connect("warehouse.duckdb")
con.execute("CREATE SCHEMA IF NOT EXISTS raw")

tables = {
    "ehr_extract": "data/raw/ehr_extract.csv",
    "registry_extract": "data/raw/registry_extract.csv",
    "survey_export": "data/raw/survey_export.csv",
}

for name, path in tables.items():
    con.execute(
        f"CREATE OR REPLACE TABLE raw.{name} AS "
        f"SELECT * FROM read_csv_auto('{path}', all_varchar=true)"
    )
    n = con.execute(f"SELECT COUNT(*) FROM raw.{name}").fetchone()[0]
    print(name, n, "rows")

con.close()