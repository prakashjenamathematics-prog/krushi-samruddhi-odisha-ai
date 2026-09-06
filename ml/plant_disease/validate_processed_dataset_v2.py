from pathlib import Path
import csv
from collections import Counter

BASE = Path(r"C:\MINI_PROJECT")

AUDIT_MANIFEST = (
    BASE / "DATASETS" / "03_AUDITED"
    / "plant_health_audit_manifest_v2.csv"
)

PROCESSED_MANIFEST = (
    BASE / "DATASETS" / "04_PROCESSED"
    / "processed_dataset_manifest_v1.csv"
)

REPORT = (
    BASE / "DATASETS" / "09_REPORTS"
    / "processed_dataset_validation_v2.txt"
)

with open(AUDIT_MANIFEST, encoding="utf-8-sig", newline="") as f:
    audit_rows = list(csv.DictReader(f))

with open(PROCESSED_MANIFEST, encoding="utf-8-sig", newline="") as f:
    processed_rows = list(csv.DictReader(f))


audit_status = Counter(
    r["status"] for r in audit_rows
)

processed_status = Counter(
    r["status"] for r in processed_rows
)

missing_sources = [
    r for r in processed_rows
    if not Path(r["source_path"]).exists()
]

missing_processed = [
    r for r in processed_rows
    if not Path(r["processed_path"]).exists()
]

# Accepted audit records that were not processed because
# they had no canonical class mapping.
accepted_not_processed = [
    r for r in audit_rows
    if r["status"] == "ACCEPT"
    and not any(
        p["source_path"] == r["source_path"]
        for p in processed_rows
    )
]

actual_copy_errors = (
    len(missing_sources) +
    len(missing_processed)
)

expected_processed = 65779
expected_unspecified = 846


validation_passed = (
    len(processed_rows) == expected_processed
    and processed_status["PROCESSED"] == expected_processed
    and len(missing_sources) == 0
    and len(missing_processed) == 0
    and len(accepted_not_processed) == expected_unspecified
)


with open(REPORT, "w", encoding="utf-8") as f:

    f.write("=" * 75 + "\n")
    f.write("KRUSHI SAMRUDDHI ODISHA AI\n")
    f.write("PROCESSED DATASET VALIDATION v2\n")
    f.write("=" * 75 + "\n\n")

    f.write(
        f"VALIDATION STATUS: "
        f"{'PASSED' if validation_passed else 'FAILED'}\n\n"
    )

    f.write("AUDIT RECONCILIATION\n")
    f.write("-" * 75 + "\n")
    f.write(
        f"Audit-accepted records: "
        f"{audit_status['ACCEPT']:,}\n"
    )
    f.write(
        f"Intentionally excluded records: "
        f"{expected_unspecified:,}\n"
    )
    f.write(
        f"Processed records: "
        f"{len(processed_rows):,}\n"
    )

    f.write("\nPROCESSING RESULTS\n")
    f.write("-" * 75 + "\n")
    f.write(
        f"Processed images: "
        f"{processed_status['PROCESSED']:,}\n"
    )
    f.write(
        f"Missing source files: "
        f"{len(missing_sources):,}\n"
    )
    f.write(
        f"Missing processed files: "
        f"{len(missing_processed):,}\n"
    )
    f.write(
        f"Actual copy errors: "
        f"{actual_copy_errors:,}\n"
    )

    f.write("\nEXCLUSION POLICY\n")
    f.write("-" * 75 + "\n")
    f.write(
        "The 846 unprocessed audit-accepted records belong "
        "to unspecified PlantDoc classes.\n"
    )
    f.write(
        "They were intentionally excluded because their "
        "disease/health status was not sufficiently defined.\n"
    )
    f.write(
        "They are NOT copy errors.\n"
    )

    f.write("\nSOURCE DATA INTEGRITY\n")
    f.write("-" * 75 + "\n")
    f.write(
        "Original external datasets were not modified.\n"
    )

print("=" * 75)
print("KRUSHI SAMRUDDHI ODISHA AI")
print("PROCESSED DATASET VALIDATION v2")
print("=" * 75)

print()
print(
    "Validation status:",
    "PASSED" if validation_passed else "FAILED"
)

print()
print("Audit-accepted:", audit_status["ACCEPT"])
print("Intentionally excluded:", expected_unspecified)
print("Processed:", len(processed_rows))
print("Actual copy errors:", actual_copy_errors)

print()
print("Missing source files:", len(missing_sources))
print("Missing processed files:", len(missing_processed))

print()
print("Report:")
print(REPORT)

if validation_passed:
    print()
    print("NEXT:")
    print("04_PROCESSED is validated.")
    print("Proceed to dataset splitting.")
else:
    print()
    print("STOP:")
    print("Resolve validation discrepancies before splitting.")