import csv
from collections import defaultdict
from pathlib import Path

import shapefile
from sqlalchemy import create_engine, text

from config import Config


GIS_FILE = Path(
    r"C:\MINI_PROJECT\DATASETS\GIS\ODISHA\ODISHA.shp"
)

OUTPUT_FILE = Path(
    r"C:\MINI_PROJECT\PROJECT\backend\gis_village_matching_audit.csv"
)


def normalize_code(value):
    if value is None:
        return ""

    text_value = str(value).strip()

    if text_value.lower() in {"", "none", "null", "<null>"}:
        return ""

    return text_value


def main():

    print("=" * 70)
    print("ODISHA GIS VILLAGE MATCHING AUDIT")
    print("=" * 70)

    # ---------------------------------------------------------
    # 1. Load MySQL villages
    # ---------------------------------------------------------

    print("\n[1] Loading villages from MySQL...")

    engine = create_engine(
        Config.SQLALCHEMY_DATABASE_URI,
        pool_pre_ping=True
    )

    with engine.connect() as connection:

        rows = connection.execute(
            text("""
                SELECT
                    village_id,
                    village_name_en,
                    lgd_code,
                    census_code
                FROM villages
                ORDER BY village_id
            """)
        ).mappings().all()

    db_villages = []

    for row in rows:

        db_villages.append({
            "village_id": row["village_id"],
            "village_name_en": row["village_name_en"],
            "lgd_code": normalize_code(row["lgd_code"]),
            "census_code": normalize_code(row["census_code"]),
        })

    db_by_lgd = {}

    for village in db_villages:

        lgd = village["lgd_code"]

        if lgd:
            db_by_lgd[lgd] = village

    print(f"MySQL villages: {len(db_villages):,}")
    print(f"MySQL villages with LGD: {len(db_by_lgd):,}")

    # ---------------------------------------------------------
    # 2. Load shapefile
    # ---------------------------------------------------------

    print("\n[2] Loading GIS shapefile...")

    reader = shapefile.Reader(str(GIS_FILE))

    fields = [
        field[0]
        for field in reader.fields[1:]
    ]

    print(f"GIS features: {len(reader):,}")
    print(f"GIS fields: {', '.join(fields)}")

    village_lgd_index = fields.index("Vill_LGD")
    village_name_index = fields.index("Vill_name")
    village_category_index = fields.index("Vill_Cat")
    district_index = fields.index("District")
    subdistrict_index = fields.index("Sub_dist")

    # ---------------------------------------------------------
    # 3. Group GIS records by Vill_LGD
    # ---------------------------------------------------------

    print("\n[3] Grouping GIS features by Vill_LGD...")

    gis_by_lgd = defaultdict(list)

    records_with_lgd = 0
    records_without_lgd = 0

    for index, record in enumerate(reader.iterRecords()):

        lgd = normalize_code(
            record[village_lgd_index]
        )

        if not lgd:
            records_without_lgd += 1
            continue

        records_with_lgd += 1

        gis_by_lgd[lgd].append({
            "shape_index": index,
            "vill_name": str(
                record[village_name_index]
            ).strip(),
            "vill_cat": str(
                record[village_category_index]
            ).strip(),
            "district": str(
                record[district_index]
            ).strip(),
            "subdistrict": str(
                record[subdistrict_index]
            ).strip(),
        })

    print(
        f"GIS records with LGD: "
        f"{records_with_lgd:,}"
    )

    print(
        f"GIS records without LGD: "
        f"{records_without_lgd:,}"
    )

    print(
        f"Unique GIS LGDs: "
        f"{len(gis_by_lgd):,}"
    )

    # ---------------------------------------------------------
    # 4. Compare database against GIS
    # ---------------------------------------------------------

    print("\n[4] Comparing MySQL villages with GIS...")

    matched = 0
    no_match = 0
    single_match = 0
    multiple_match = 0

    audit_rows = []

    for village in db_villages:

        lgd = village["lgd_code"]

        gis_records = gis_by_lgd.get(lgd, [])

        if not lgd or not gis_records:

            status = "NO_GIS_MATCH"
            no_match += 1

        elif len(gis_records) == 1:

            status = "SINGLE_GIS_MATCH"
            matched += 1
            single_match += 1

        else:

            status = "MULTIPLE_GIS_MATCHES"
            matched += 1
            multiple_match += 1

        audit_rows.append({
            "village_id": village["village_id"],
            "village_name_en": village["village_name_en"],
            "lgd_code": village["lgd_code"],
            "census_code": village["census_code"],
            "gis_match_count": len(gis_records),
            "match_status": status,
            "gis_names": " | ".join(
                sorted(
                    set(
                        x["vill_name"]
                        for x in gis_records
                    )
                )
            ),
            "gis_categories": " | ".join(
                sorted(
                    set(
                        x["vill_cat"]
                        for x in gis_records
                    )
                )
            ),
            "gis_districts": " | ".join(
                sorted(
                    set(
                        x["district"]
                        for x in gis_records
                    )
                )
            ),
        })

    # ---------------------------------------------------------
    # 5. Write audit CSV
    # ---------------------------------------------------------

    print("\n[5] Writing audit CSV...")

    fieldnames = [
        "village_id",
        "village_name_en",
        "lgd_code",
        "census_code",
        "gis_match_count",
        "match_status",
        "gis_names",
        "gis_categories",
        "gis_districts",
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
        writer.writerows(audit_rows)

    # ---------------------------------------------------------
    # 6. Summary
    # ---------------------------------------------------------

    print("\n" + "=" * 70)
    print("AUDIT SUMMARY")
    print("=" * 70)

    print(
        f"MySQL villages:              {len(db_villages):,}"
    )

    print(
        f"GIS unique LGDs:              {len(gis_by_lgd):,}"
    )

    print(
        f"Villages with GIS match:      {matched:,}"
    )

    print(
        f"Single GIS match:             {single_match:,}"
    )

    print(
        f"Multiple GIS matches:         {multiple_match:,}"
    )

    print(
        f"No GIS match:                 {no_match:,}"
    )

    if db_villages:
        percentage = (
            matched / len(db_villages)
        ) * 100

        print(
            f"GIS match percentage:         {percentage:.2f}%"
        )

    print("\nAudit file:")
    print(OUTPUT_FILE)

    print("=" * 70)


if __name__ == "__main__":
    main()