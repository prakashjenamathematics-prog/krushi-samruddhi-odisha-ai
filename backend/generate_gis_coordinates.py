import csv
from collections import defaultdict
from pathlib import Path

import shapefile
from pyproj import CRS, Transformer
from sqlalchemy import text

from database import engine


# ============================================================
# PATHS
# ============================================================

GIS_FILE = Path(
    r"C:\MINI_PROJECT\DATASETS\GIS\ODISHA\ODISHA.shp"
)

OUTPUT_FILE = Path(
    r"C:\MINI_PROJECT\PROJECT\backend\gis_village_coordinates.csv"
)


# ============================================================
# CRS
# ============================================================

# Survey of India shapefile CRS:
# Lambert Conformal Conic / WGS84
SOURCE_CRS = CRS.from_proj4(
    "+proj=lcc "
    "+lat_1=12.472944 "
    "+lat_2=35.172806 "
    "+lat_0=24 "
    "+lon_0=80 "
    "+x_0=4000000 "
    "+y_0=4000000 "
    "+datum=WGS84 "
    "+units=m "
    "+no_defs"
)

TARGET_CRS = CRS.from_epsg(4326)

TRANSFORMER = Transformer.from_crs(
    SOURCE_CRS,
    TARGET_CRS,
    always_xy=True
)


# ============================================================
# HELPER
# ============================================================

def clean(value):
    if value is None:
        return ""

    return str(value).strip()


def calculate_polygon_centroid(shape):
    """
    Calculate centroid using the polygon bounding box
    as a safe fallback if geometry centroid is unavailable.

    For village-level map markers, the polygon center is sufficient.
    """

    points = shape.points

    if not points:
        return None, None

    xs = [point[0] for point in points]
    ys = [point[1] for point in points]

    x = (min(xs) + max(xs)) / 2
    y = (min(ys) + max(ys)) / 2

    return x, y


# ============================================================
# START
# ============================================================

print("=" * 70)
print("GENERATING GIS VILLAGE COORDINATES")
print("=" * 70)


# ============================================================
# CHECK GIS FILE
# ============================================================

if not GIS_FILE.exists():
    raise FileNotFoundError(
        f"GIS shapefile not found:\n{GIS_FILE}"
    )


print("\n[1] Loading villages from MySQL...")

with engine.connect() as connection:

    query = text("""
        SELECT
            village_id,
            village_name_en,
            lgd_code,
            census_code
        FROM villages
        WHERE lgd_code IS NOT NULL
        ORDER BY village_id
    """)

    rows = connection.execute(query).mappings().all()


print(f"MySQL villages loaded: {len(rows):,}")


# ============================================================
# GROUP DATABASE VILLAGES BY LGD
# ============================================================

db_villages = {}

for row in rows:

    lgd = clean(row["lgd_code"])

    if lgd:

        db_villages[lgd] = {
            "village_id": row["village_id"],
            "village_name_en": row["village_name_en"],
            "lgd_code": row["lgd_code"],
            "census_code": row["census_code"]
        }


print(f"MySQL villages with LGD: {len(db_villages):,}")


# ============================================================
# LOAD GIS
# ============================================================

print("\n[2] Loading Survey of India GIS shapefile...")

reader = shapefile.Reader(str(GIS_FILE))

print(f"GIS features: {len(reader):,}")


# ============================================================
# GIS FIELD INDEX
# ============================================================

field_names = [
    field[0]
    for field in reader.fields[1:]
]

field_index = {
    name: index
    for index, name in enumerate(field_names)
}

required_fields = [
    "Vill_LGD",
    "Vill_name",
    "Vill_Cat"
]

for field in required_fields:

    if field not in field_index:

        raise RuntimeError(
            f"Required GIS field missing: {field}"
        )


# ============================================================
# GROUP ONLY REQUIRED GIS FEATURES
# ============================================================

print("\n[3] Grouping GIS features by Vill_LGD...")

gis_by_lgd = defaultdict(list)

for record, shape in zip(
    reader.iterRecords(),
    reader.iterShapes()
):

    lgd = clean(
        record[field_index["Vill_LGD"]]
    )

    if not lgd:
        continue

    # Only process LGDs that actually exist
    # in our database.
    if lgd not in db_villages:
        continue

    village_name = clean(
        record[field_index["Vill_name"]]
    )

    village_category = clean(
        record[field_index["Vill_Cat"]]
    )

    gis_by_lgd[lgd].append({
        "village_name": village_name,
        "village_category": village_category,
        "shape": shape
    })


print(
    f"Database villages having GIS geometry: "
    f"{len(gis_by_lgd):,}"
)


# ============================================================
# GENERATE COORDINATES
# ============================================================

print("\n[4] Calculating coordinates...")

output_rows = []

matched = 0
unmatched = 0
invalid = 0

for lgd, village in db_villages.items():

    gis_records = gis_by_lgd.get(lgd, [])

    # --------------------------------------------------------
    # No GIS match
    # --------------------------------------------------------

    if len(gis_records) == 0:

        unmatched += 1

        output_rows.append({
            "village_id": village["village_id"],
            "village_name_en": village["village_name_en"],
            "lgd_code": village["lgd_code"],
            "census_code": village["census_code"],
            "gis_village_name": "",
            "gis_village_category": "",
            "latitude": "",
            "longitude": "",
            "coordinate_status": "NO_GIS_MATCH"
        })

        continue


    # --------------------------------------------------------
    # We already established that our audit has
    # zero multiple matches.
    # --------------------------------------------------------

    if len(gis_records) != 1:

        invalid += 1

        output_rows.append({
            "village_id": village["village_id"],
            "village_name_en": village["village_name_en"],
            "lgd_code": village["lgd_code"],
            "census_code": village["census_code"],
            "gis_village_name": "",
            "gis_village_category": "",
            "latitude": "",
            "longitude": "",
            "coordinate_status": "MULTIPLE_GIS_MATCH"
        })

        continue


    gis = gis_records[0]

    projected_x, projected_y = calculate_polygon_centroid(
        gis["shape"]
    )

    if projected_x is None or projected_y is None:

        invalid += 1

        output_rows.append({
            "village_id": village["village_id"],
            "village_name_en": village["village_name_en"],
            "lgd_code": village["lgd_code"],
            "census_code": village["census_code"],
            "gis_village_name": gis["village_name"],
            "gis_village_category": gis["village_category"],
            "latitude": "",
            "longitude": "",
            "coordinate_status": "INVALID_GEOMETRY"
        })

        continue


    # --------------------------------------------------------
    # Convert projected coordinates to WGS84
    # --------------------------------------------------------

    longitude, latitude = TRANSFORMER.transform(
        projected_x,
        projected_y
    )


    # --------------------------------------------------------
    # Validate coordinate range
    # --------------------------------------------------------

    if not (
        -90 <= latitude <= 90
        and -180 <= longitude <= 180
    ):

        invalid += 1

        output_rows.append({
            "village_id": village["village_id"],
            "village_name_en": village["village_name_en"],
            "lgd_code": village["lgd_code"],
            "census_code": village["census_code"],
            "gis_village_name": gis["village_name"],
            "gis_village_category": gis["village_category"],
            "latitude": "",
            "longitude": "",
            "coordinate_status": "INVALID_COORDINATE"
        })

        continue


    # --------------------------------------------------------
    # Successful
    # --------------------------------------------------------

    matched += 1

    output_rows.append({
        "village_id": village["village_id"],
        "village_name_en": village["village_name_en"],
        "lgd_code": village["lgd_code"],
        "census_code": village["census_code"],
        "gis_village_name": gis["village_name"],
        "gis_village_category": gis["village_category"],
        "latitude": round(latitude, 7),
        "longitude": round(longitude, 7),
        "coordinate_status": "READY"
    })


# ============================================================
# WRITE CSV
# ============================================================

print("\n[5] Writing coordinate CSV...")

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

fieldnames = [
    "village_id",
    "village_name_en",
    "lgd_code",
    "census_code",
    "gis_village_name",
    "gis_village_category",
    "latitude",
    "longitude",
    "coordinate_status"
]

with OUTPUT_FILE.open(
    "w",
    newline="",
    encoding="utf-8-sig"
) as file:

    writer = csv.DictWriter(
        file,
        fieldnames=fieldnames
    )

    writer.writeheader()
    writer.writerows(output_rows)


# ============================================================
# SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("COORDINATE GENERATION SUMMARY")
print("=" * 70)

print(
    f"MySQL villages:             {len(db_villages):,}"
)

print(
    f"Coordinates generated:      {matched:,}"
)

print(
    f"No GIS match:                {unmatched:,}"
)

print(
    f"Invalid/problem records:     {invalid:,}"
)

if len(db_villages) > 0:

    percentage = (
        matched / len(db_villages)
    ) * 100

    print(
        f"Coordinate coverage:         {percentage:.2f}%"
    )


print("\nOutput file:")
print(OUTPUT_FILE)

print("=" * 70)