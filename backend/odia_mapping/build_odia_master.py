from pathlib import Path
import csv
import os
import sys

import pymysql
from dotenv import load_dotenv


# ============================================================
# KRUSHI SAMRUDDHI ODISHA AI
# ODIA MASTER CSV BUILDER
#
# IMPORTANT:
# - READ ONLY from MySQL
# - NEVER modifies MySQL
# - Creates CSV files only
# - UTF-8 compatible
# ============================================================


# ------------------------------------------------------------
# PATHS
# ------------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent

BACKEND_DIR = SCRIPT_DIR.parent
ENV_FILE = BACKEND_DIR / ".env"

VILLAGE_CSV = SCRIPT_DIR / "village_odia_master.csv"
GP_CSV = SCRIPT_DIR / "gp_odia_master.csv"


# ------------------------------------------------------------
# LOAD ENVIRONMENT
# ------------------------------------------------------------

if not ENV_FILE.exists():
    print("ERROR: .env file not found:")
    print(ENV_FILE)
    sys.exit(1)

load_dotenv(ENV_FILE)


MYSQL_HOST = os.getenv("MYSQL_HOST", "127.0.0.1")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
MYSQL_DATABASE = os.getenv(
    "MYSQL_DATABASE",
    "krushi_samruddhi_odisha"
)


# ------------------------------------------------------------
# CSV COLUMNS
# ------------------------------------------------------------

VILLAGE_COLUMNS = [
    "village_id",
    "district_id",
    "district_name_en",
    "district_name_or",
    "block_id",
    "block_name_en",
    "block_name_or",
    "gp_id",
    "gp_name_en",
    "gp_name_or",
    "village_name_en",
    "village_name_or",
    "lgd_code",
    "census_code",
    "latitude",
    "longitude",
    "source",
    "verification_status",
]


GP_COLUMNS = [
    "gp_id",
    "district_id",
    "district_name_en",
    "district_name_or",
    "block_id",
    "block_name_en",
    "block_name_or",
    "gp_name_en",
    "gp_name_or",
    "lgd_gp_code",
    "source",
    "verification_status",
]


# ------------------------------------------------------------
# HELPERS
# ------------------------------------------------------------

def has_value(value):
    """
    Returns True when a database field contains
    a non-empty value.
    """
    if value is None:
        return False

    return str(value).strip() != ""


def clean_value(value):
    """
    Convert database values safely to CSV values.
    """
    if value is None:
        return ""

    return str(value)


# ------------------------------------------------------------
# DATABASE CONNECTION
# ------------------------------------------------------------

def get_connection():
    print("=" * 70)
    print("CONNECTING TO MYSQL")
    print("=" * 70)

    print(f"Host     : {MYSQL_HOST}")
    print(f"Port     : {MYSQL_PORT}")
    print(f"Database : {MYSQL_DATABASE}")
    print(f"User     : {MYSQL_USER}")
    print()

    connection = pymysql.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        read_timeout=30,
        write_timeout=30,
    )

    print("MySQL connection successful.")
    print()

    return connection


# ------------------------------------------------------------
# BUILD VILLAGE CSV
# ------------------------------------------------------------

def build_village_csv(connection):

    print("=" * 70)
    print("BUILDING VILLAGE MASTER CSV")
    print("=" * 70)

    query = """
        SELECT
            v.village_id,
            d.district_id,
            d.district_name_en,
            d.district_name_or,

            b.block_id,
            b.block_name_en,
            b.block_name_or,

            gp.gp_id,
            gp.gp_name_en,
            gp.gp_name_or,

            v.village_name_en,
            v.village_name_or,

            v.lgd_code,
            v.census_code,
            v.latitude,
            v.longitude

        FROM villages v

        INNER JOIN gram_panchayats gp
            ON v.gp_id = gp.gp_id

        INNER JOIN blocks b
            ON gp.block_id = b.block_id

        INNER JOIN districts d
            ON b.district_id = d.district_id

        ORDER BY
            d.district_name_en,
            b.block_name_en,
            gp.gp_name_en,
            v.village_name_en
    """

    with connection.cursor() as cursor:

        cursor.execute(query)

        rows = cursor.fetchall()

    print(f"Database records retrieved: {len(rows)}")
    print()

    village_count = 0
    village_odia_count = 0
    village_missing_odia = 0

    with open(
        VILLAGE_CSV,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=VILLAGE_COLUMNS,
            extrasaction="ignore"
        )

        writer.writeheader()

        for row in rows:

            village_odia_exists = has_value(
                row["village_name_or"]
            )

            if village_odia_exists:
                source = "existing_database"
                verification_status = "existing"
                village_odia_count += 1
            else:
                source = ""
                verification_status = "missing"
                village_missing_odia += 1

            output_row = {
                "village_id": clean_value(row["village_id"]),
                "district_id": clean_value(row["district_id"]),
                "district_name_en": clean_value(
                    row["district_name_en"]
                ),
                "district_name_or": clean_value(
                    row["district_name_or"]
                ),
                "block_id": clean_value(row["block_id"]),
                "block_name_en": clean_value(
                    row["block_name_en"]
                ),
                "block_name_or": clean_value(
                    row["block_name_or"]
                ),
                "gp_id": clean_value(row["gp_id"]),
                "gp_name_en": clean_value(
                    row["gp_name_en"]
                ),
                "gp_name_or": clean_value(
                    row["gp_name_or"]
                ),
                "village_name_en": clean_value(
                    row["village_name_en"]
                ),
                "village_name_or": clean_value(
                    row["village_name_or"]
                ),
                "lgd_code": clean_value(row["lgd_code"]),
                "census_code": clean_value(
                    row["census_code"]
                ),
                "latitude": clean_value(row["latitude"]),
                "longitude": clean_value(
                    row["longitude"]
                ),
                "source": source,
                "verification_status": verification_status,
            }

            writer.writerow(output_row)

            village_count += 1

    print(f"Village CSV created:")
    print(VILLAGE_CSV)
    print()
    print(f"Total villages       : {village_count}")
    print(f"With Odia names      : {village_odia_count}")
    print(f"Missing Odia names   : {village_missing_odia}")
    print()

    return village_count, village_odia_count, village_missing_odia


# ------------------------------------------------------------
# BUILD GP CSV
# ------------------------------------------------------------

def build_gp_csv(connection):

    print("=" * 70)
    print("BUILDING GP MASTER CSV")
    print("=" * 70)

    query = """
        SELECT
            gp.gp_id,

            d.district_id,
            d.district_name_en,
            d.district_name_or,

            b.block_id,
            b.block_name_en,
            b.block_name_or,

            gp.gp_name_en,
            gp.gp_name_or,

            gp.lgd_gp_code

        FROM gram_panchayats gp

        INNER JOIN blocks b
            ON gp.block_id = b.block_id

        INNER JOIN districts d
            ON b.district_id = d.district_id

        ORDER BY
            d.district_name_en,
            b.block_name_en,
            gp.gp_name_en
    """

    with connection.cursor() as cursor:

        cursor.execute(query)

        rows = cursor.fetchall()

    print(f"Database records retrieved: {len(rows)}")
    print()

    gp_count = 0
    gp_odia_count = 0
    gp_missing_odia = 0

    with open(
        GP_CSV,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=GP_COLUMNS,
            extrasaction="ignore"
        )

        writer.writeheader()

        for row in rows:

            gp_odia_exists = has_value(
                row["gp_name_or"]
            )

            if gp_odia_exists:
                source = "existing_database"
                verification_status = "existing"
                gp_odia_count += 1
            else:
                source = ""
                verification_status = "missing"
                gp_missing_odia += 1

            output_row = {
                "gp_id": clean_value(row["gp_id"]),
                "district_id": clean_value(
                    row["district_id"]
                ),
                "district_name_en": clean_value(
                    row["district_name_en"]
                ),
                "district_name_or": clean_value(
                    row["district_name_or"]
                ),
                "block_id": clean_value(
                    row["block_id"]
                ),
                "block_name_en": clean_value(
                    row["block_name_en"]
                ),
                "block_name_or": clean_value(
                    row["block_name_or"]
                ),
                "gp_name_en": clean_value(
                    row["gp_name_en"]
                ),
                "gp_name_or": clean_value(
                    row["gp_name_or"]
                ),
                "lgd_gp_code": clean_value(
                    row["lgd_gp_code"]
                ),
                "source": source,
                "verification_status": verification_status,
            }

            writer.writerow(output_row)

            gp_count += 1

    print(f"GP CSV created:")
    print(GP_CSV)
    print()
    print(f"Total GPs            : {gp_count}")
    print(f"With Odia names      : {gp_odia_count}")
    print(f"Missing Odia names   : {gp_missing_odia}")
    print()

    return gp_count, gp_odia_count, gp_missing_odia


# ------------------------------------------------------------
# VALIDATE CSV
# ------------------------------------------------------------

def validate_village_csv():

    print("=" * 70)
    print("VALIDATING VILLAGE CSV")
    print("=" * 70)

    required_columns = VILLAGE_COLUMNS

    row_count = 0
    duplicate_ids = []
    empty_english = 0

    seen_ids = set()

    with open(
        VILLAGE_CSV,
        "r",
        newline="",
        encoding="utf-8-sig"
    ) as file:

        reader = csv.DictReader(file)

        if reader.fieldnames != required_columns:
            print("ERROR: Village CSV columns do not match.")
            print("Expected:")
            print(required_columns)
            print("Found:")
            print(reader.fieldnames)
            return False

        for row in reader:

            row_count += 1

            village_id = row["village_id"]

            if village_id in seen_ids:
                duplicate_ids.append(village_id)

            seen_ids.add(village_id)

            if not row["village_name_en"].strip():
                empty_english += 1

    print(f"Rows                  : {row_count}")
    print(f"Duplicate village IDs : {len(duplicate_ids)}")
    print(f"Empty English names   : {empty_english}")
    print("UTF-8 validation      : PASS")
    print("Column validation     : PASS")

    if duplicate_ids:
        print("Duplicate IDs:")
        print(duplicate_ids[:20])
        return False

    if empty_english:
        return False

    print("Village CSV validation: PASS")
    print()

    return True


def validate_gp_csv():

    print("=" * 70)
    print("VALIDATING GP CSV")
    print("=" * 70)

    required_columns = GP_COLUMNS

    row_count = 0
    duplicate_ids = []
    empty_english = 0

    seen_ids = set()

    with open(
        GP_CSV,
        "r",
        newline="",
        encoding="utf-8-sig"
    ) as file:

        reader = csv.DictReader(file)

        if reader.fieldnames != required_columns:
            print("ERROR: GP CSV columns do not match.")
            print("Expected:")
            print(required_columns)
            print("Found:")
            print(reader.fieldnames)
            return False

        for row in reader:

            row_count += 1

            gp_id = row["gp_id"]

            if gp_id in seen_ids:
                duplicate_ids.append(gp_id)

            seen_ids.add(gp_id)

            if not row["gp_name_en"].strip():
                empty_english += 1

    print(f"Rows                  : {row_count}")
    print(f"Duplicate GP IDs      : {len(duplicate_ids)}")
    print(f"Empty English names   : {empty_english}")
    print("UTF-8 validation      : PASS")
    print("Column validation     : PASS")

    if duplicate_ids:
        print("Duplicate IDs:")
        print(duplicate_ids[:20])
        return False

    if empty_english:
        return False

    print("GP CSV validation: PASS")
    print()

    return True


# ------------------------------------------------------------
# MAIN
# ------------------------------------------------------------

def main():

    print()
    print("=" * 70)
    print("KRUSHI SAMRUDDHI ODISHA AI")
    print("ODIA MASTER CSV GENERATOR")
    print("=" * 70)
    print()
    print("MODE: READ-ONLY")
    print("MySQL will NOT be modified.")
    print()

    connection = None

    try:

        connection = get_connection()

        village_total, village_odia, village_missing = (
            build_village_csv(connection)
        )

        gp_total, gp_odia, gp_missing = (
            build_gp_csv(connection)
        )

    except Exception as error:

        print()
        print("=" * 70)
        print("ERROR")
        print("=" * 70)
        print(error)
        sys.exit(1)

    finally:

        if connection:
            connection.close()
            print("MySQL connection closed.")

    print()

    village_valid = validate_village_csv()
    gp_valid = validate_gp_csv()

    print("=" * 70)
    print("FINAL SUMMARY")
    print("=" * 70)

    print()
    print("VILLAGES")
    print(f"Total                : {village_total}")
    print(f"Odia available       : {village_odia}")
    print(f"Odia missing         : {village_missing}")

    print()
    print("GRAM PANCHAYATS")
    print(f"Total                : {gp_total}")
    print(f"Odia available       : {gp_odia}")
    print(f"Odia missing         : {gp_missing}")

    print()
    print("OUTPUT FILES")
    print(f"Village CSV          : {VILLAGE_CSV}")
    print(f"GP CSV               : {GP_CSV}")

    print()
    print("VALIDATION")

    if village_valid:
        print("Village CSV          : PASS")
    else:
        print("Village CSV          : FAIL")

    if gp_valid:
        print("GP CSV               : PASS")
    else:
        print("GP CSV               : FAIL")

    print()
    print("=" * 70)
    print("COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()