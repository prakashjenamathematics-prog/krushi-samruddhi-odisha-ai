import os
import re
import unicodedata

import pandas as pd
from sqlalchemy import text

from database import engine


# ============================================================
# CONFIGURATION
# ============================================================

CENSUS_FILE = r"C:\MINI_PROJECT\DATASETS\PC11_TV_DIR.xlsx"

OUTPUT_DIR = r"C:\MINI_PROJECT\PROJECT\backend\census_mapping"

OUTPUT_FILE = os.path.join(
    OUTPUT_DIR,
    "odisha_village_census_mapping.csv"
)

UNMATCHED_FILE = os.path.join(
    OUTPUT_DIR,
    "odisha_village_census_unmatched.csv"
)

AMBIGUOUS_FILE = os.path.join(
    OUTPUT_DIR,
    "odisha_village_census_ambiguous.csv"
)


# ============================================================
# DIRECTORY SETUP
# ============================================================

os.makedirs(OUTPUT_DIR, exist_ok=True)


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def normalize_name(value):
    """
    Normalize a village name ONLY for comparison.

    The original database and Census names are never modified.
    """

    if pd.isna(value):
        return ""

    value = str(value).strip()

    value = unicodedata.normalize("NFKD", value)

    value = "".join(
        char
        for char in value
        if not unicodedata.combining(char)
    )

    value = value.lower()

    value = value.replace("&", "and")

    value = re.sub(r"[^a-z0-9]+", " ", value)

    value = re.sub(r"\s+", " ", value)

    return value.strip()


# ============================================================
# START
# ============================================================

print("=" * 70)
print("KRUSHI SAMRUDDHI ODISHA AI")
print("CENSUS VILLAGE CODE MAPPING")
print("=" * 70)


# ============================================================
# CHECK CENSUS FILE
# ============================================================

print("\nChecking Census file...")

if not os.path.exists(CENSUS_FILE):
    raise FileNotFoundError(
        f"\nCensus file not found:\n{CENSUS_FILE}"
    )

print("Census file found.")


# ============================================================
# LOAD DATABASE VILLAGES
# ============================================================

print("\nReading villages from MySQL...")

query = text("""
    SELECT
        v.village_id,
        d.district_id,
        d.district_name_en,
        d.district_name_or,
        b.block_id,
        b.block_name_en,
        b.block_name_or,
        g.gp_id,
        g.gp_name_en,
        g.gp_name_or,
        v.village_name_en,
        v.village_name_or,
        v.lgd_code,
        v.census_code,
        v.latitude,
        v.longitude
    FROM villages v
    JOIN gram_panchayats g
        ON v.gp_id = g.gp_id
    JOIN blocks b
        ON g.block_id = b.block_id
    JOIN districts d
        ON b.district_id = d.district_id
    ORDER BY
        d.district_name_en,
        b.block_name_en,
        g.gp_name_en,
        v.village_name_en
""")

with engine.connect() as connection:
    db_df = pd.read_sql(query, connection)

print(
    f"Database villages retrieved: {len(db_df)}"
)


# ============================================================
# DATABASE VALIDATION
# ============================================================

if len(db_df) != 49413:
    print(
        "\nWARNING:"
        f" Expected 49,413 villages but found {len(db_df)}."
    )

print("\nDatabase sample:")

print(
    db_df[
        [
            "village_id",
            "district_name_en",
            "block_name_en",
            "gp_name_en",
            "village_name_en",
            "lgd_code",
        ]
    ]
    .head(5)
    .to_string(index=False)
)


# ============================================================
# READ CENSUS EXCEL
# ============================================================

print("\nReading Census Excel file...")

excel = pd.ExcelFile(CENSUS_FILE)

print("\nAvailable Census sheets:")

for sheet in excel.sheet_names:
    print(" -", sheet)


# ============================================================
# SELECT SHEET
# ============================================================

# The downloaded PC11_TV_DIR.xlsx contains Sheet1.
# We still verify the required columns before continuing.

if "Sheet1" in excel.sheet_names:
    selected_sheet = "Sheet1"
else:
    selected_sheet = excel.sheet_names[0]

print(
    f"\nSelected Census sheet: {selected_sheet}"
)


# ============================================================
# LOAD CENSUS DATA
# ============================================================

census_df = pd.read_excel(
    CENSUS_FILE,
    sheet_name=selected_sheet,
    dtype=str
)

print(
    f"Census records loaded: {len(census_df)}"
)


# ============================================================
# CLEAN COLUMN NAMES
# ============================================================

census_df.columns = [
    str(column).strip()
    for column in census_df.columns
]


print("\nCensus columns:")

for column in census_df.columns:
    print(" -", column)


# ============================================================
# EXACT REQUIRED CENSUS COLUMNS
# ============================================================

REQUIRED_COLUMNS = [
    "State Code",
    "District Code",
    "Sub District Code",
    "Town-Village Code",
    "Town-Village Name",
]


missing_columns = [
    column
    for column in REQUIRED_COLUMNS
    if column not in census_df.columns
]


if missing_columns:

    raise RuntimeError(
        "\nThe Census Excel file does not contain "
        "the expected columns:\n"
        + "\n".join(
            f" - {column}"
            for column in missing_columns
        )
    )


print("\nCensus columns verified successfully.")

print("State code       : State Code")
print("District code    : District Code")
print("Sub-district     : Sub District Code")
print("Census code      : Town-Village Code")
print("Village name     : Town-Village Name")


# ============================================================
# CLEAN CENSUS COLUMNS
# ============================================================

for column in REQUIRED_COLUMNS:

    census_df[column] = (
        census_df[column]
        .fillna("")
        .astype(str)
        .str.strip()
    )


# ============================================================
# FILTER ODISHA
# ============================================================

print("\nFiltering Census records for Odisha...")

odisha_census_df = census_df[
    census_df["State Code"].isin(
        ["21", "021", "21.0"]
    )
].copy()


print(
    f"Odisha Census records: {len(odisha_census_df)}"
)


if len(odisha_census_df) == 0:

    raise RuntimeError(
        "\nNo Odisha records were found."
        "\nExpected Census State Code: 21"
    )


# ============================================================
# PREPARE CENSUS DATA
# ============================================================

census_work = odisha_census_df[
    [
        "State Code",
        "District Code",
        "Sub District Code",
        "Town-Village Code",
        "Town-Village Name",
    ]
].copy()


census_work.columns = [
    "state_code",
    "district_code",
    "subdistrict_code",
    "census_village_code",
    "census_village_name",
]


# ============================================================
# REMOVE EMPTY VILLAGE NAMES
# ============================================================

census_work = census_work[
    census_work["census_village_name"].str.strip() != ""
].copy()


# ============================================================
# NORMALIZE CENSUS NAMES
# ============================================================

census_work["normalized_name"] = (
    census_work["census_village_name"]
    .apply(normalize_name)
)


census_work = census_work[
    census_work["normalized_name"] != ""
].copy()


print(
    f"Usable Odisha Census records: {len(census_work)}"
)


# ============================================================
# DISPLAY CENSUS SAMPLE
# ============================================================

print("\nCensus sample:")

print(
    census_work[
        [
            "district_code",
            "subdistrict_code",
            "census_village_code",
            "census_village_name",
        ]
    ]
    .head(10)
    .to_string(index=False)
)


# ============================================================
# BUILD CENSUS NAME INDEX
# ============================================================

print("\nBuilding Census village index...")

census_index = {}


for _, row in census_work.iterrows():

    normalized_name = row["normalized_name"]

    record = {
        "name": row["census_village_name"],
        "code": row["census_village_code"],
        "district_code": row["district_code"],
        "subdistrict_code": row["subdistrict_code"],
    }

    census_index.setdefault(
        normalized_name,
        []
    ).append(record)


print(
    f"Unique normalized Census names: "
    f"{len(census_index)}"
)


# ============================================================
# MATCH DATABASE VILLAGES
# ============================================================

print("\nMatching database villages...")

results = []

unmatched = []

ambiguous = []

exact_matches = 0

ambiguous_matches = 0

unmatched_count = 0


for _, db_row in db_df.iterrows():

    db_name = db_row["village_name_en"]

    normalized_db_name = normalize_name(
        db_name
    )

    candidates = census_index.get(
        normalized_db_name,
        []
    )

    candidate_count = len(candidates)

    match_status = "UNMATCHED"

    census_name = ""

    census_code = ""

    census_district_code = ""

    census_subdistrict_code = ""

    match_method = ""


    # ========================================================
    # EXACT UNIQUE NAME MATCH
    # ========================================================

    if candidate_count == 1:

        candidate = candidates[0]

        match_status = "EXACT_NAME_MATCH"

        census_name = candidate["name"]

        census_code = candidate["code"]

        census_district_code = (
            candidate["district_code"]
        )

        census_subdistrict_code = (
            candidate["subdistrict_code"]
        )

        match_method = "normalized_name"

        exact_matches += 1


    # ========================================================
    # AMBIGUOUS NAME
    # ========================================================

    elif candidate_count > 1:

        match_status = "AMBIGUOUS"

        ambiguous_matches += 1


        for candidate in candidates:

            ambiguous.append(
                {
                    "village_id":
                        db_row["village_id"],

                    "district_id":
                        db_row["district_id"],

                    "district_name_en":
                        db_row["district_name_en"],

                    "block_id":
                        db_row["block_id"],

                    "block_name_en":
                        db_row["block_name_en"],

                    "gp_id":
                        db_row["gp_id"],

                    "gp_name_en":
                        db_row["gp_name_en"],

                    "village_name_en":
                        db_name,

                    "lgd_code":
                        db_row["lgd_code"],

                    "candidate_census_name":
                        candidate["name"],

                    "candidate_census_code":
                        candidate["code"],

                    "candidate_district_code":
                        candidate["district_code"],

                    "candidate_subdistrict_code":
                        candidate["subdistrict_code"],
                }
            )


    # ========================================================
    # UNMATCHED
    # ========================================================

    else:

        unmatched_count += 1

        unmatched.append(
            {
                "village_id":
                    db_row["village_id"],

                "district_id":
                    db_row["district_id"],

                "district_name_en":
                    db_row["district_name_en"],

                "block_id":
                    db_row["block_id"],

                "block_name_en":
                    db_row["block_name_en"],

                "gp_id":
                    db_row["gp_id"],

                "gp_name_en":
                    db_row["gp_name_en"],

                "village_name_en":
                    db_name,

                "lgd_code":
                    db_row["lgd_code"],
            }
        )


    # ========================================================
    # CREATE RESULT
    # ========================================================

    result = db_row.to_dict()

    result.update(
        {
            "census_village_name":
                census_name,

            "matched_census_code":
                census_code,

            "census_district_code":
                census_district_code,

            "census_subdistrict_code":
                census_subdistrict_code,

            "match_status":
                match_status,

            "match_method":
                match_method,

            "candidate_count":
                candidate_count,
        }
    )

    results.append(result)


# ============================================================
# CREATE RESULT DATAFRAME
# ============================================================

result_df = pd.DataFrame(results)


# ============================================================
# CREATE UNMATCHED DATAFRAME
# ============================================================

unmatched_df = pd.DataFrame(
    unmatched
)


# ============================================================
# CREATE AMBIGUOUS DATAFRAME
# ============================================================

ambiguous_df = pd.DataFrame(
    ambiguous
)


# ============================================================
# SAVE MAIN MAPPING
# ============================================================

print("\nSaving mapping CSV...")

result_df.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8",
)


# ============================================================
# SAVE UNMATCHED
# ============================================================

unmatched_df.to_csv(
    UNMATCHED_FILE,
    index=False,
    encoding="utf-8",
)


# ============================================================
# SAVE AMBIGUOUS
# ============================================================

ambiguous_df.to_csv(
    AMBIGUOUS_FILE,
    index=False,
    encoding="utf-8",
)


# ============================================================
# CALCULATE PERCENTAGE
# ============================================================

if len(db_df) > 0:

    exact_percentage = (
        exact_matches
        / len(db_df)
        * 100
    )

else:

    exact_percentage = 0


# ============================================================
# SUMMARY
# ============================================================

print("\n")
print("=" * 70)
print("CENSUS MAPPING SUMMARY")
print("=" * 70)

print(
    f"Database villages        : {len(db_df)}"
)

print(
    f"Total Census records     : {len(census_df)}"
)

print(
    f"Odisha Census records    : "
    f"{len(odisha_census_df)}"
)

print(
    f"Usable Odisha records    : "
    f"{len(census_work)}"
)

print(
    f"Exact name matches       : "
    f"{exact_matches}"
)

print(
    f"Ambiguous matches        : "
    f"{ambiguous_matches}"
)

print(
    f"Unmatched villages       : "
    f"{unmatched_count}"
)

print(
    f"Exact match percentage   : "
    f"{exact_percentage:.2f}%"
)


# ============================================================
# OUTPUT FILES
# ============================================================

print("\nGenerated files:")

print(
    "\nMain mapping:"
)

print(
    OUTPUT_FILE
)

print(
    "\nUnmatched villages:"
)

print(
    UNMATCHED_FILE
)

print(
    "\nAmbiguous villages:"
)

print(
    AMBIGUOUS_FILE
)


# ============================================================
# VALIDATION
# ============================================================

print("\n")
print("=" * 70)
print("VALIDATION")
print("=" * 70)


# Check database result count

if len(result_df) == len(db_df):

    print(
        "Result row count       : PASS"
    )

else:

    print(
        "Result row count       : FAIL"
    )


# Check village IDs

duplicate_village_ids = (
    result_df["village_id"]
    .duplicated()
    .sum()
)


if duplicate_village_ids == 0:

    print(
        "Duplicate village IDs  : PASS"
    )

else:

    print(
        f"Duplicate village IDs  : FAIL "
        f"({duplicate_village_ids})"
    )


# Check CSV existence

for file_path in [
    OUTPUT_FILE,
    UNMATCHED_FILE,
    AMBIGUOUS_FILE,
]:

    if os.path.exists(file_path):

        print(
            f"File created           : PASS - "
            f"{os.path.basename(file_path)}"
        )

    else:

        print(
            f"File created           : FAIL - "
            f"{os.path.basename(file_path)}"
        )


# ============================================================
# DATABASE SAFETY
# ============================================================

print("\n")
print("=" * 70)
print("DATABASE SAFETY")
print("=" * 70)

print(
    "MySQL database was READ ONLY."
)

print(
    "No INSERT operation was executed."
)

print(
    "No UPDATE operation was executed."
)

print(
    "No DELETE operation was executed."
)

print(
    "No ALTER operation was executed."
)

print(
    "No DROP operation was executed."
)

print(
    "No Census code was written into MySQL."
)

print(
    "No coordinates were written into MySQL."
)

print(
    "No existing village names were modified."
)

print("=" * 70)