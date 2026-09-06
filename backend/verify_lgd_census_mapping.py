import os
import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

MAPPING_FILE = (
    r"C:\MINI_PROJECT\PROJECT\backend"
    r"\census_mapping\lgd_census_village_mapping.csv"
)

OUTPUT_FILE = (
    r"C:\MINI_PROJECT\PROJECT\backend"
    r"\census_mapping\lgd_census_verification.csv"
)


# ============================================================
# START
# ============================================================

print("=" * 75)
print("KRUSHI SAMRUDDHI ODISHA AI")
print("LGD → CENSUS MAPPING VERIFICATION")
print("=" * 75)


# ============================================================
# CHECK FILE
# ============================================================

if not os.path.exists(MAPPING_FILE):

    raise FileNotFoundError(
        f"Mapping file not found:\n{MAPPING_FILE}"
    )


print("\nReading mapping file...")

df = pd.read_csv(
    MAPPING_FILE,
    dtype=str,
    keep_default_na=False
)


print(
    f"Mapping records loaded: {len(df)}"
)


# ============================================================
# FILTER DIRECT MATCHES
# ============================================================

direct = df[
    df["match_status"]
    == "DIRECT_LGD_CENSUS_MATCH"
].copy()


print(
    f"Direct matches: {len(direct)}"
)


# ============================================================
# NORMALIZE CODES
# ============================================================

direct["district_id"] = (
    direct["district_id"]
    .astype(str)
    .str.strip()
)

direct["census_district_code"] = (
    direct["census_district_code"]
    .astype(str)
    .str.strip()
)


direct["lgd_code"] = (
    direct["lgd_code"]
    .astype(str)
    .str.strip()
)

direct["matched_census_code"] = (
    direct["matched_census_code"]
    .astype(str)
    .str.strip()
)


# ============================================================
# VERIFY LGD = CENSUS CODE
# ============================================================

direct["code_match"] = (
    direct["lgd_code"]
    ==
    direct["matched_census_code"]
)


# ============================================================
# CHECK CENSUS DISTRICT INFORMATION
# ============================================================

# We don't assume that database district_id and
# Census District Code use the same numbering system.
#
# Therefore, we only report the Census district code here.
#
# The actual district-name verification will be done using
# an official Census district-code mapping in the next step.


# ============================================================
# NAME COMPARISON
# ============================================================

direct["name_match"] = (
    direct["village_name_en"]
    .str.strip()
    .str.lower()
    ==
    direct["census_village_name"]
    .str.strip()
    .str.lower()
)


# ============================================================
# STATUS
# ============================================================

direct["verification_status"] = "REVIEW"


direct.loc[
    (
        direct["code_match"]
        &
        direct["name_match"]
    ),
    "verification_status"
] = "CODE_AND_NAME_CONFIRMED"


direct.loc[
    (
        direct["code_match"]
        &
        ~direct["name_match"]
    ),
    "verification_status"
] = "CODE_CONFIRMED_NAME_DIFFERENT"


direct.loc[
    ~direct["code_match"],
    "verification_status"
] = "CODE_MISMATCH"


# ============================================================
# SUMMARY
# ============================================================

code_confirmed = int(
    direct["code_match"].sum()
)

name_confirmed = int(
    direct["name_match"].sum()
)

code_and_name_confirmed = int(
    (
        direct["verification_status"]
        ==
        "CODE_AND_NAME_CONFIRMED"
    ).sum()
)

code_confirmed_name_different = int(
    (
        direct["verification_status"]
        ==
        "CODE_CONFIRMED_NAME_DIFFERENT"
    ).sum()
)

code_mismatch = int(
    (
        direct["verification_status"]
        ==
        "CODE_MISMATCH"
    ).sum()
)


# ============================================================
# SAVE
# ============================================================

direct.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8"
)


# ============================================================
# PRINT RESULTS
# ============================================================

print("\n")
print("=" * 75)
print("VERIFICATION SUMMARY")
print("=" * 75)

print(
    f"Direct LGD-Census matches       : "
    f"{len(direct)}"
)

print(
    f"LGD code = Census code          : "
    f"{code_confirmed}"
)

print(
    f"Village name also matches       : "
    f"{name_confirmed}"
)

print(
    f"Code + name confirmed           : "
    f"{code_and_name_confirmed}"
)

print(
    f"Code confirmed, name different  : "
    f"{code_confirmed_name_different}"
)

print(
    f"Code mismatch                   : "
    f"{code_mismatch}"
)


# ============================================================
# SHOW NAME DIFFERENCES
# ============================================================

different_names = direct[
    direct["verification_status"]
    ==
    "CODE_CONFIRMED_NAME_DIFFERENT"
]


print("\n")
print("=" * 75)
print("SAMPLE CODE-CONFIRMED NAME DIFFERENCES")
print("=" * 75)


if len(different_names) == 0:

    print(
        "No code-confirmed name differences found."
    )

else:

    print(
        different_names[
            [
                "village_id",
                "district_name_en",
                "block_name_en",
                "gp_name_en",
                "village_name_en",
                "census_village_name",
                "lgd_code",
                "matched_census_code",
            ]
        ]
        .head(20)
        .to_string(index=False)
    )


# ============================================================
# OUTPUT
# ============================================================

print("\n")
print("=" * 75)
print("OUTPUT")
print("=" * 75)

print(
    OUTPUT_FILE
)


# ============================================================
# SAFETY
# ============================================================

print("\n")
print("=" * 75)
print("DATABASE SAFETY")
print("=" * 75)

print(
    "This verification used only the CSV file."
)

print(
    "MySQL was NOT modified."
)

print(
    "No INSERT / UPDATE / DELETE / ALTER / DROP."
)

print("=" * 75)