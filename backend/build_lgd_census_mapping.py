import os
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
    "lgd_census_village_mapping.csv"
)

NOT_FOUND_FILE = os.path.join(
    OUTPUT_DIR,
    "lgd_census_not_found.csv"
)


# ============================================================
# CREATE OUTPUT DIRECTORY
# ============================================================

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)


# ============================================================
# HEADER
# ============================================================

print("=" * 75)
print("KRUSHI SAMRUDDHI ODISHA AI")
print("DIRECT LGD → CENSUS VILLAGE CODE MAPPING")
print("=" * 75)


# ============================================================
# CHECK CENSUS FILE
# ============================================================

print("\nChecking Census file...")

if not os.path.exists(CENSUS_FILE):

    raise FileNotFoundError(
        f"Census file not found:\n{CENSUS_FILE}"
    )

print("Census file found.")


# ============================================================
# READ DATABASE
# ============================================================

print("\nReading village data from MySQL...")

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

    db_df = pd.read_sql(
        query,
        connection
    )


print(
    f"Database villages retrieved: {len(db_df)}"
)


# ============================================================
# VALIDATE DATABASE COUNT
# ============================================================

if len(db_df) == 49413:

    print(
        "Database village count: PASS"
    )

else:

    print(
        "WARNING:"
        f" Expected 49,413 villages, "
        f"found {len(db_df)}"
    )


# ============================================================
# LOAD CENSUS EXCEL
# ============================================================

print("\nReading Census Excel file...")

census_df = pd.read_excel(
    CENSUS_FILE,
    sheet_name="Sheet1",
    dtype=str
)


# ============================================================
# CLEAN COLUMN NAMES
# ============================================================

census_df.columns = [
    str(column).strip()
    for column in census_df.columns
]


# ============================================================
# VERIFY REQUIRED COLUMNS
# ============================================================

required_columns = [
    "State Code",
    "District Code",
    "Sub District Code",
    "Town-Village Code",
    "Town-Village Name"
]


missing_columns = [
    column
    for column in required_columns
    if column not in census_df.columns
]


if missing_columns:

    raise RuntimeError(
        "Required Census columns are missing:\n"
        + "\n".join(
            f" - {column}"
            for column in missing_columns
        )
    )


print(
    "Census columns verified."
)


# ============================================================
# CLEAN CENSUS VALUES
# ============================================================

for column in required_columns:

    census_df[column] = (
        census_df[column]
        .fillna("")
        .astype(str)
        .str.strip()
    )


# ============================================================
# FILTER ODISHA
# ============================================================

print("\nFiltering Census data for Odisha...")

census_df = census_df[
    census_df["State Code"].isin(
        [
            "21",
            "021",
            "21.0"
        ]
    )
].copy()


print(
    f"Odisha Census records: {len(census_df)}"
)


# ============================================================
# REMOVE EMPTY CODES
# ============================================================

census_df = census_df[
    census_df["Town-Village Code"] != ""
].copy()


# ============================================================
# CHECK CENSUS CODE DUPLICATES
# ============================================================

duplicate_census_codes = (
    census_df["Town-Village Code"]
    .duplicated(keep=False)
)


duplicate_count = int(
    duplicate_census_codes.sum()
)


print(
    f"Census records with duplicate "
    f"village codes: {duplicate_count}"
)


# ============================================================
# CREATE CENSUS CODE INDEX
# ============================================================

print("\nBuilding Census code index...")

census_index = {}

duplicate_index_codes = set()


for _, row in census_df.iterrows():

    code = row[
        "Town-Village Code"
    ]

    record = {
        "census_village_code": code,
        "census_village_name":
            row["Town-Village Name"],
        "census_district_code":
            row["District Code"],
        "census_subdistrict_code":
            row["Sub District Code"],
    }


    if code in census_index:

        duplicate_index_codes.add(code)

        existing = census_index[code]

        if isinstance(existing, list):

            existing.append(record)

        else:

            census_index[code] = [
                existing,
                record
            ]

    else:

        census_index[code] = record


print(
    f"Unique Census village codes: "
    f"{len(census_index)}"
)


# ============================================================
# MATCH LGD CODES
# ============================================================

print("\nMatching database LGD codes...")

results = []

not_found = []

direct_matches = 0

not_found_count = 0

ambiguous_code_count = 0


for _, row in db_df.iterrows():

    lgd_code = str(
        row["lgd_code"]
    ).strip()


    census_record = census_index.get(
        lgd_code
    )


    # ========================================================
    # DIRECT MATCH
    # ========================================================

    if census_record is not None:

        # ----------------------------------------------------
        # Duplicate Census code
        # ----------------------------------------------------

        if isinstance(
            census_record,
            list
        ):

            ambiguous_code_count += 1

            result = row.to_dict()

            result.update(
                {
                    "census_village_name":
                        "",

                    "matched_census_code":
                        lgd_code,

                    "census_district_code":
                        "",

                    "census_subdistrict_code":
                        "",

                    "match_status":
                        "AMBIGUOUS_CENSUS_CODE",

                    "match_method":
                        "LGD_CODE",

                    "candidate_count":
                        len(census_record)
                }
            )

            results.append(
                result
            )

        # ----------------------------------------------------
        # Unique Census code
        # ----------------------------------------------------

        else:

            direct_matches += 1

            result = row.to_dict()

            result.update(
                {
                    "census_village_name":
                        census_record[
                            "census_village_name"
                        ],

                    "matched_census_code":
                        census_record[
                            "census_village_code"
                        ],

                    "census_district_code":
                        census_record[
                            "census_district_code"
                        ],

                    "census_subdistrict_code":
                        census_record[
                            "census_subdistrict_code"
                        ],

                    "match_status":
                        "DIRECT_LGD_CENSUS_MATCH",

                    "match_method":
                        "LGD_CODE",

                    "candidate_count":
                        1
                }
            )

            results.append(
                result
            )


    # ========================================================
    # LGD CODE NOT FOUND
    # ========================================================

    else:

        not_found_count += 1

        result = row.to_dict()

        result.update(
            {
                "census_village_name":
                    "",

                "matched_census_code":
                    "",

                "census_district_code":
                    "",

                "census_subdistrict_code":
                    "",

                "match_status":
                    "LGD_NOT_FOUND_IN_CENSUS",

                "match_method":
                    "",

                "candidate_count":
                    0
            }
        )

        results.append(
            result
        )


        not_found.append(
            {
                "village_id":
                    row["village_id"],

                "district_id":
                    row["district_id"],

                "district_name_en":
                    row["district_name_en"],

                "block_id":
                    row["block_id"],

                "block_name_en":
                    row["block_name_en"],

                "gp_id":
                    row["gp_id"],

                "gp_name_en":
                    row["gp_name_en"],

                "village_name_en":
                    row["village_name_en"],

                "lgd_code":
                    row["lgd_code"],
            }
        )


# ============================================================
# CREATE DATAFRAMES
# ============================================================

result_df = pd.DataFrame(
    results
)


not_found_df = pd.DataFrame(
    not_found
)


# ============================================================
# SAVE MAIN MAPPING
# ============================================================

print("\nSaving main mapping CSV...")

result_df.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8"
)


# ============================================================
# SAVE NOT FOUND
# ============================================================

print(
    "Saving LGD codes not found in Census..."
)

not_found_df.to_csv(
    NOT_FOUND_FILE,
    index=False,
    encoding="utf-8"
)


# ============================================================
# CALCULATE PERCENTAGE
# ============================================================

total_villages = len(db_df)

if total_villages > 0:

    match_percentage = (
        direct_matches
        / total_villages
    ) * 100

else:

    match_percentage = 0


# ============================================================
# SUMMARY
# ============================================================

print("\n")
print("=" * 75)
print("DIRECT LGD → CENSUS MAPPING SUMMARY")
print("=" * 75)

print(
    f"Database villages             : "
    f"{total_villages}"
)

print(
    f"Odisha Census records          : "
    f"{len(census_df)}"
)

print(
    f"Unique Census codes            : "
    f"{len(census_index)}"
)

print(
    f"Direct LGD → Census matches    : "
    f"{direct_matches}"
)

print(
    f"LGD codes not found            : "
    f"{not_found_count}"
)

print(
    f"Ambiguous Census codes         : "
    f"{ambiguous_code_count}"
)

print(
    f"Direct match percentage        : "
    f"{match_percentage:.2f}%"
)


# ============================================================
# VALIDATION
# ============================================================

print("\n")
print("=" * 75)
print("VALIDATION")
print("=" * 75)


# Result count

if len(result_df) == len(db_df):

    print(
        "Result row count               : PASS"
    )

else:

    print(
        "Result row count               : FAIL"
    )


# Village ID duplicates

duplicate_village_ids = (
    result_df["village_id"]
    .duplicated()
    .sum()
)


if duplicate_village_ids == 0:

    print(
        "Duplicate village IDs         : PASS"
    )

else:

    print(
        f"Duplicate village IDs         : "
        f"FAIL ({duplicate_village_ids})"
    )


# LGD uniqueness

database_unique_lgd = (
    db_df["lgd_code"]
    .astype(str)
    .nunique()
)


if database_unique_lgd == total_villages:

    print(
        "Database LGD uniqueness       : PASS"
    )

else:

    print(
        "Database LGD uniqueness       : FAIL"
    )


# Check matched codes

matched_rows = result_df[
    result_df["match_status"]
    == "DIRECT_LGD_CENSUS_MATCH"
]


matched_code_count = (
    matched_rows["matched_census_code"]
    .astype(str)
    .nunique()
)


if matched_code_count == direct_matches:

    print(
        "Matched Census code uniqueness: PASS"
    )

else:

    print(
        "Matched Census code uniqueness: WARNING"
    )


# Output files

for file_path in [
    OUTPUT_FILE,
    NOT_FOUND_FILE
]:

    if os.path.exists(file_path):

        print(
            f"File created                  : PASS - "
            f"{os.path.basename(file_path)}"
        )

    else:

        print(
            f"File created                  : FAIL - "
            f"{os.path.basename(file_path)}"
        )


# ============================================================
# SAMPLE MATCHES
# ============================================================

print("\n")
print("=" * 75)
print("SAMPLE DIRECT MATCHES")
print("=" * 75)


sample_columns = [
    "village_id",
    "district_name_en",
    "block_name_en",
    "gp_name_en",
    "village_name_en",
    "lgd_code",
    "census_village_name",
    "matched_census_code",
    "match_status"
]


print(
    result_df[
        sample_columns
    ]
    .head(10)
    .to_string(index=False)
)


# ============================================================
# DATABASE SAFETY
# ============================================================

print("\n")
print("=" * 75)
print("DATABASE SAFETY")
print("=" * 75)

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
    "No village names were modified."
)

print(
    "No Census codes were written to MySQL."
)

print(
    "No coordinates were written to MySQL."
)

print("=" * 75)