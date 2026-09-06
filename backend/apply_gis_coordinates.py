import csv
from pathlib import Path

from sqlalchemy import text

from database import engine


CSV_FILE = Path(
    r"C:\MINI_PROJECT\PROJECT\backend\gis_village_coordinates.csv"
)


print("=" * 70)
print("APPLYING GIS COORDINATES TO MYSQL")
print("=" * 70)


# ------------------------------------------------------------
# Check CSV
# ------------------------------------------------------------

if not CSV_FILE.exists():
    raise FileNotFoundError(
        f"Coordinate CSV not found:\n{CSV_FILE}"
    )


# ------------------------------------------------------------
# Read CSV
# ------------------------------------------------------------

print("\n[1] Reading coordinate CSV...")

with CSV_FILE.open(
    "r",
    encoding="utf-8-sig",
    newline=""
) as file:

    rows = list(csv.DictReader(file))


print(f"CSV rows: {len(rows):,}")


ready_rows = [
    row
    for row in rows
    if row["coordinate_status"] == "READY"
]


print(f"READY rows: {len(ready_rows):,}")


# ------------------------------------------------------------
# Safety validation
# ------------------------------------------------------------

if len(rows) != 49413:
    raise RuntimeError(
        f"Unexpected CSV row count: {len(rows)}"
    )


if len(ready_rows) != 48749:
    raise RuntimeError(
        f"Unexpected READY count: {len(ready_rows)}"
    )


for row in ready_rows:

    if not row["village_id"]:
        raise RuntimeError(
            "Missing village_id in coordinate CSV"
        )

    if not row["latitude"]:
        raise RuntimeError(
            f"Missing latitude for village_id "
            f"{row['village_id']}"
        )

    if not row["longitude"]:
        raise RuntimeError(
            f"Missing longitude for village_id "
            f"{row['village_id']}"
        )


print("Validation passed.")


# ------------------------------------------------------------
# Update database
# ------------------------------------------------------------

print("\n[2] Updating MySQL...")


update_query = text("""
    UPDATE villages
    SET
        latitude = :latitude,
        longitude = :longitude
    WHERE village_id = :village_id
""")


updated = 0


with engine.begin() as connection:

    for row in ready_rows:

        result = connection.execute(
            update_query,
            {
                "latitude": row["latitude"],
                "longitude": row["longitude"],
                "village_id": row["village_id"]
            }
        )

        updated += result.rowcount


print(f"Rows updated: {updated:,}")


# ------------------------------------------------------------
# Verify database
# ------------------------------------------------------------

print("\n[3] Verifying database...")


verification_query = text("""
    SELECT
        COUNT(*) AS total_villages,
        SUM(latitude IS NOT NULL) AS latitude_present,
        SUM(longitude IS NOT NULL) AS longitude_present,
        SUM(
            latitude IS NOT NULL
            AND longitude IS NOT NULL
        ) AS coordinates_complete,
        SUM(
            latitude IS NULL
            OR longitude IS NULL
        ) AS coordinates_missing
    FROM villages
""")


with engine.connect() as connection:

    result = connection.execute(
        verification_query
    )

    stats = result.mappings().first()


print("\n" + "=" * 70)
print("GIS COORDINATE UPDATE SUMMARY")
print("=" * 70)

print(
    f"Total villages:              "
    f"{stats['total_villages']:,}"
)

print(
    f"Latitude present:            "
    f"{stats['latitude_present']:,}"
)

print(
    f"Longitude present:           "
    f"{stats['longitude_present']:,}"
)

print(
    f"Complete coordinates:        "
    f"{stats['coordinates_complete']:,}"
)

print(
    f"Coordinates missing:         "
    f"{stats['coordinates_missing']:,}"
)


if stats["coordinates_complete"] > 0:

    coverage = (
        stats["coordinates_complete"]
        / stats["total_villages"]
    ) * 100

    print(
        f"Coordinate coverage:         "
        f"{coverage:.2f}%"
    )


print("=" * 70)
print("GIS COORDINATE UPDATE COMPLETED")
print("=" * 70)