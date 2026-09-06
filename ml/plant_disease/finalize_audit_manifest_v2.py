from pathlib import Path
import csv
from collections import Counter


BASE = Path(r"C:\MINI_PROJECT")

AUDITED_DIR = (
    BASE
    / "DATASETS"
    / "03_AUDITED"
)

REPORT_DIR = (
    BASE
    / "DATASETS"
    / "09_REPORTS"
)


INPUT_MANIFEST = (
    AUDITED_DIR
    / "plant_health_audit_manifest_v1.csv"
)

MANUAL_REVIEW_FILE = (
    REPORT_DIR
    / "manual_review_resolution_v1.csv"
)

OUTPUT_MANIFEST = (
    AUDITED_DIR
    / "plant_health_audit_manifest_v2.csv"
)

OUTPUT_SUMMARY = (
    AUDITED_DIR
    / "plant_health_audit_summary_v2.txt"
)


# ------------------------------------------------------------
# Load v1 manifest
# ------------------------------------------------------------

with open(
    INPUT_MANIFEST,
    "r",
    encoding="utf-8-sig",
    newline=""
) as f:

    manifest = list(
        csv.DictReader(f)
    )


# ------------------------------------------------------------
# Load manual review decisions
# ------------------------------------------------------------

with open(
    MANUAL_REVIEW_FILE,
    "r",
    encoding="utf-8-sig",
    newline=""
) as f:

    review_rows = list(
        csv.DictReader(f)
    )


# ------------------------------------------------------------
# Build lookup for test files
# ------------------------------------------------------------

test_decisions = {}

for row in review_rows:

    test_path = row["test_file"]

    test_decisions[test_path] = {
        "decision": row["decision"],
        "reason": row["reason"],
        "pair_id": row["pair_id"]
    }


# ------------------------------------------------------------
# Apply manual-review decisions
# ------------------------------------------------------------

updated = 0

for row in manifest:

    source_path = row["source_path"]

    if source_path in test_decisions:

        decision = test_decisions[
            source_path
        ]

        row["status"] = "EXCLUDE"

        row["audit_reason"] = (
            f"{decision['decision']}; "
            f"manual visual review pair "
            f"{decision['pair_id']}; "
            f"{decision['reason']}"
        )

        updated += 1

    elif row["status"] == "MANUAL_REVIEW":

        # The remaining manual-review entries should
        # correspond to the retained TRAIN copies.

        row["status"] = "ACCEPT"

        row["audit_reason"] = (
            "Near-duplicate train/test candidate "
            "manually reviewed. Same underlying image "
            "confirmed; TRAIN copy retained."
        )

        updated += 1


# ------------------------------------------------------------
# Write v2 manifest
# ------------------------------------------------------------

fields = [
    "dataset",
    "source_split",
    "original_class",
    "source_path",
    "sha256",
    "status",
    "audit_reason"
]


with open(
    OUTPUT_MANIFEST,
    "w",
    encoding="utf-8-sig",
    newline=""
) as f:

    writer = csv.DictWriter(
        f,
        fieldnames=fields
    )

    writer.writeheader()
    writer.writerows(manifest)


# ------------------------------------------------------------
# Calculate summary
# ------------------------------------------------------------

status_counts = Counter(
    row["status"]
    for row in manifest
)

dataset_counts = Counter(
    row["dataset"]
    for row in manifest
)


# ------------------------------------------------------------
# Write summary
# ------------------------------------------------------------

with open(
    OUTPUT_SUMMARY,
    "w",
    encoding="utf-8"
) as f:

    f.write("=" * 75 + "\n")
    f.write(
        "KRUSHI SAMRUDDHI ODISHA AI\n"
    )
    f.write(
        "PLANT HEALTH AUDIT SUMMARY v2\n"
    )
    f.write("=" * 75 + "\n\n")

    f.write(
        f"Total candidate images: "
        f"{len(manifest):,}\n\n"
    )

    f.write("STATUS SUMMARY\n")
    f.write("-" * 75 + "\n")

    for status, count in sorted(
        status_counts.items()
    ):

        f.write(
            f"{status}: {count:,}\n"
        )

    f.write("\nDATASET SUMMARY\n")
    f.write("-" * 75 + "\n")

    for dataset, count in sorted(
        dataset_counts.items()
    ):

        f.write(
            f"{dataset}: {count:,}\n"
        )

    f.write("\nMANUAL REVIEW\n")
    f.write("-" * 75 + "\n")
    f.write(
        "Two near-duplicate train/test pairs were "
        "visually reviewed.\n"
    )
    f.write(
        "Both were confirmed as the same underlying "
        "image.\n"
    )
    f.write(
        "Training copies were retained and test copies "
        "were excluded.\n"
    )

    f.write("\nSOURCE DATA POLICY\n")
    f.write("-" * 75 + "\n")
    f.write(
        "External source datasets remain unchanged.\n"
    )
    f.write(
        "No source image was deleted or modified.\n"
    )


print("=" * 75)
print("KRUSHI SAMRUDDHI ODISHA AI")
print("FINAL AUDIT MANIFEST v2")
print("=" * 75)

print()
print(
    f"Records updated: {updated}"
)

print()
print("STATUS SUMMARY")

for status, count in sorted(
    status_counts.items()
):

    print(
        f"  {status}: {count:,}"
    )

print()
print("DATASET SUMMARY")

for dataset, count in sorted(
    dataset_counts.items()
):

    print(
        f"  {dataset}: {count:,}"
    )

print()
print("Manifest:")
print(OUTPUT_MANIFEST)

print()
print("Summary:")
print(OUTPUT_SUMMARY)

print()
print("NO SOURCE IMAGES WERE MODIFIED.")