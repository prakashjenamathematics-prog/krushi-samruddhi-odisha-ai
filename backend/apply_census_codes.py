import os
import pandas as pd
from sqlalchemy import text

from database import engine


# ============================================================
# CONFIGURATION
# ============================================================

MAPPING_FILE = (
    r"C:\MINI_PROJECT\PROJECT\backend"
    r"\census_mapping\lgd_census_village_mapping.csv"
)


# ============================================================
# HEADER
# ============================================================

print("=" * 75)
print("KRUSHI SAMRUDDHI ODISHA AI")
print("VERIFIED CENSUS CODE DATABASE UPDATE")
print("=" * 75)


# ============================================================
# SAFETY: CHECK FILE
# ============================================================

if not os.path.exists(MAPPING_FILE):

    raise FileNotFoundError(
        f"\nMapping file not found:\n{MAPPING_FILE}"
    )


print("\nMapping file found.")


# ============================================================
# READ CSV
# ============================================================

print("\nReading verified mapping CSV...")

mapping_df = pd.read_csv(
    MAPPING_FILE,
    dtype=str,
    keep_default_na=False
)


print(
    f"Mapping records loaded: {len(mapping_df)}"
)


# ============================================================
# SELECT ONLY VERIFIED DIRECT MATCHES
# ============================================================

verified_df = mapping_df[
    mapping_df["match_status"]
    == "DIRECT_LGD_CENSUS_MATCH"
].copy()


print(
    f"Verified direct matches: {len(verified_df)}"
)


# ============================================================
# VALIDATE EXPECTED COUNT
# ============================================================

if len(verified_df) != 49250:

    raise RuntimeError(
        "\nSAFETY STOP\n"
        f"Expected exactly 49,250 verified mappings.\n"
        f"Found {len(verified_df)}.\n"
        "Database update has NOT started."
    )


print(
    "Verified mapping count: PASS"
)


# ============================================================
# VALIDATE REQUIRED COLUMNS
# ============================================================

required_columns = [
    "village_id",
    "lgd_code",
    "matched_census_code",
    "match_status",
]


missing_columns = [
    column
    for column in required_columns
    if column not in verified_df.columns
]


if missing_columns:

    raise RuntimeError(
        "\nMissing required columns:\n"
        + "\n".join(
            f" - {column}"
            for column in missing_columns
        )
    )


print(
    "Required CSV columns: PASS"
)


# ============================================================
# VALIDATE LGD CODES
# ============================================================

verified_df["lgd_code"] = (
    verified_df["lgd_code"]
    .astype(str)
    .str.strip()
)


verified_df["matched_census_code"] = (
    verified_df["matched_census_code"]
    .astype(str)
    .str.strip()
)


# ============================================================
# CHECK LGD = CENSUS
# ============================================================

code_match = (
    verified_df["lgd_code"]
    ==
    verified_df["matched_census_code"]
)


if not code_match.all():

    bad_count = int(
        (~code_match).sum()
    )

    raise RuntimeError(
        "\nSAFETY STOP\n"
        f"{bad_count} records have LGD/Census code mismatch.\n"
        "Database update has NOT started."
    )


print(
    "LGD = Census code validation: PASS"
)


# ============================================================
# CHECK CENSUS CODE FORMAT
# ============================================================

valid_format = (
    verified_df["matched_census_code"]
    .str.fullmatch(r"\d{6}")
)


if not valid_format.all():

    bad_count = int(
        (~valid_format).sum()
    )

    raise RuntimeError(
        "\nSAFETY STOP\n"
        f"{bad_count} Census codes are not six digits.\n"
        "Database update has NOT started."
    )


print(
    "Census code format: PASS"
)


# ============================================================
# CHECK CENSUS CODE ZERO
# ============================================================

zero_codes = (
    verified_df["matched_census_code"]
    == "000000"
)


if zero_codes.any():

    bad_count = int(
        zero_codes.sum()
    )

    raise RuntimeError(
        "\nSAFETY STOP\n"
        f"{bad_count} Census codes are 000000.\n"
        "Database update has NOT started."
    )


print(
    "Census code non-zero: PASS"
)


# ============================================================
# CHECK DUPLICATE LGD CODES
# ============================================================

duplicate_lgd = (
    verified_df["lgd_code"]
    .duplicated()
    .sum()
)


if duplicate_lgd != 0:

    raise RuntimeError(
        "\nSAFETY STOP\n"
        f"Duplicate LGD codes found: {duplicate_lgd}\n"
        "Database update has NOT started."
    )


print(
    "LGD code uniqueness: PASS"
)


# ============================================================
# CHECK DUPLICATE CENSUS CODES
# ============================================================

duplicate_census = (
    verified_df["matched_census_code"]
    .duplicated()
    .sum()
)


if duplicate_census != 0:

    raise RuntimeError(
        "\nSAFETY STOP\n"
        f"Duplicate Census codes found: {duplicate_census}\n"
        "Database update has NOT started."
    )


print(
    "Census code uniqueness: PASS"
)


# ============================================================
# CONNECT TO DATABASE
# ============================================================

print("\nConnecting to MySQL...")

with engine.begin() as connection:

    # ========================================================
    # DATABASE PRE-CHECK
    # ========================================================

    print("\nChecking current census_code values...")

    result = connection.execute(
        text("""
            SELECT
                COUNT(*) AS total_villages,
                SUM(census_code IS NOT NULL)
                    AS census_already_present,
                SUM(census_code IS NULL)
                    AS census_missing
            FROM villages
        """)
    )

    before = result.mappings().first()

    print(
        f"Total villages       : "
        f"{before['total_villages']}"
    )

    print(
        f"Census already set   : "
        f"{before['census_already_present']}"
    )

    print(
        f"Census missing       : "
        f"{before['census_missing']}"
    )


    # ========================================================
    # SAFETY CHECK
    # ========================================================

    if before["total_villages"] != 49413:

        raise RuntimeError(
            "\nSAFETY STOP\n"
            "Database does not contain exactly "
            "49,413 villages.\n"
            "No update performed."
        )


    # ========================================================
    # UPDATE VERIFIED RECORDS
    # ========================================================

    print(
        "\nApplying verified Census codes..."
    )

    update_sql = text("""
        UPDATE villages
        SET census_code = :census_code
        WHERE village_id = :village_id
          AND lgd_code = :lgd_code
          AND census_code IS NULL
    """)


    updated_rows = 0

    already_filled = 0


    # ========================================================
    # UPDATE ONE VERIFIED RECORD AT A TIME
    # ========================================================

    for _, row in verified_df.iterrows():

        result = connection.execute(
            update_sql,
            {
                "census_code":
                    int(row["matched_census_code"]),

                "village_id":
                    int(row["village_id"]),

                "lgd_code":
                    int(row["lgd_code"]),
            }
        )

        if result.rowcount == 1:

            updated_rows += 1

        else:

            already_filled += 1


    print(
        f"Rows updated: {updated_rows}"
    )

    print(
        f"Rows skipped: {already_filled}"
    )


    # ========================================================
    # TRANSACTION VERIFICATION
    # ========================================================

    print(
        "\nVerifying transaction..."
    )

    result = connection.execute(
        text("""
            SELECT
                COUNT(*) AS total_villages,
                SUM(census_code IS NOT NULL)
                    AS census_present,
                SUM(census_code IS NULL)
                    AS census_missing
            FROM villages
        """)
    )

    after = result.mappings().first()


    print(
        f"Total villages       : "
        f"{after['total_villages']}"
    )

    print(
        f"Census present       : "
        f"{after['census_present']}"
    )

    print(
        f"Census missing       : "
        f"{after['census_missing']}"
    )


    # ========================================================
    # FINAL SAFETY CHECK
    # ========================================================

    expected_present = (
        before["census_already_present"]
        + updated_rows
    )


    if (
        after["census_present"]
        != expected_present
    ):

        raise RuntimeError(
            "\nSAFETY STOP\n"
            "Verification failed.\n"
            "Transaction will be rolled back."
        )


    if (
        after["total_villages"]
        != 49413
    ):

        raise RuntimeError(
            "\nSAFETY STOP\n"
            "Village count changed unexpectedly.\n"
            "Transaction will be rolled back."
        )


# ============================================================
# TRANSACTION SUCCESS
# ============================================================

print("\n")
print("=" * 75)
print("UPDATE COMPLETED SUCCESSFULLY")
print("=" * 75)

print(
    f"Verified mappings       : 49,250"
)

print(
    f"Rows updated            : {updated_rows}"
)

print(
    f"Rows skipped            : {already_filled}"
)

print(
    f"Total villages          : "
    f"{after['total_villages']}"
)

print(
    f"Census codes present    : "
    f"{after['census_present']}"
)

print(
    f"Census codes missing    : "
    f"{after['census_missing']}"
)

print(
    "\nThe 160 LGD-not-found villages "
    "and 3 ambiguous Census-code records "
    "were NOT updated."
)

print("=" * 75)