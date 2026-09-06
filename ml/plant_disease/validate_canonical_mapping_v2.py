from pathlib import Path
import csv
from collections import Counter, defaultdict


BASE = Path(r"C:\MINI_PROJECT")

AUDITED_DIR = (
    BASE
    / "DATASETS"
    / "03_AUDITED"
)

METADATA_DIR = (
    BASE
    / "DATASETS"
    / "08_METADATA"
)

REPORT_DIR = (
    BASE
    / "DATASETS"
    / "09_REPORTS"
)

AUDIT_MANIFEST = (
    AUDITED_DIR
    / "plant_health_audit_manifest_v2.csv"
)

MAPPING_FILE = (
    METADATA_DIR
    / "canonical_class_dictionary_v2.csv"
)

POLICY_FILE = (
    METADATA_DIR
    / "plant_health_class_policy_v1.csv"
)

REPORT_FILE = (
    REPORT_DIR
    / "canonical_mapping_validation_v2.txt"
)


print("=" * 75)
print("KRUSHI SAMRUDDHI ODISHA AI")
print("CANONICAL CLASS MAPPING VALIDATION v2")
print("=" * 75)


# ============================================================
# LOAD AUDIT MANIFEST
# ============================================================

with open(
    AUDIT_MANIFEST,
    encoding="utf-8-sig",
    newline=""
) as f:

    audit_rows = list(
        csv.DictReader(f)
    )


# ============================================================
# LOAD CANONICAL MAPPING
# ============================================================

with open(
    MAPPING_FILE,
    encoding="utf-8-sig",
    newline=""
) as f:

    mapping_rows = list(
        csv.DictReader(f)
    )


# ============================================================
# LOAD EXCLUSION POLICY
# ============================================================

with open(
    POLICY_FILE,
    encoding="utf-8-sig",
    newline=""
) as f:

    policy_rows = list(
        csv.DictReader(f)
    )


# ============================================================
# SOURCE CLASS SET
# ============================================================

source_classes = set(
    (
        r["dataset"],
        r["original_class"]
    )
    for r in audit_rows
)


# ============================================================
# MAPPING CLASS SET
# ============================================================

mapping_classes = [
    (
        r["dataset"],
        r["original_class"]
    )
    for r in mapping_rows
]

mapping_class_set = set(
    mapping_classes
)


# ============================================================
# POLICY EXCLUSION SET
# ============================================================

excluded_classes = set(
    (
        r["dataset"],
        r["original_class"]
    )
    for r in policy_rows
    if r["training_policy"] == "EXCLUDE_UNSPECIFIED"
)


# ============================================================
# DUPLICATE MAPPING CHECK
# ============================================================

mapping_duplicates = [
    item
    for item, count in Counter(
        mapping_classes
    ).items()
    if count > 1
]


# ============================================================
# RECONCILIATION
# ============================================================

missing_classes = (
    source_classes
    - mapping_class_set
    - excluded_classes
)

unexpected_mappings = (
    mapping_class_set
    - source_classes
)

excluded_and_mapped = (
    mapping_class_set
    & excluded_classes
)


# ============================================================
# CANONICAL CLASS CHECK
# ============================================================

canonical_classes = set(
    (
        r["crop"],
        r["canonical_disease"]
    )
    for r in mapping_rows
)


invalid_canonical_rows = []

for row in mapping_rows:

    if (
        not row["crop"].strip()
        or not row["canonical_disease"].strip()
    ):

        invalid_canonical_rows.append(row)


# ============================================================
# DATASET COUNTS
# ============================================================

dataset_source_counts = Counter(
    (
        r["dataset"],
        r["original_class"]
    )
    for r in audit_rows
)


# ============================================================
# CANONICAL IMAGE COUNTS
# ============================================================

lookup = {
    (
        r["dataset"],
        r["original_class"]
    ): (
        r["crop"],
        r["canonical_disease"]
    )
    for r in mapping_rows
}


canonical_image_counts = Counter()

excluded_image_count = 0

accepted_image_count = 0

for row in audit_rows:

    key = (
        row["dataset"],
        row["original_class"]
    )

    if row["status"] != "ACCEPT":
        continue

    if key in lookup:

        canonical_image_counts[
            lookup[key]
        ] += 1

        accepted_image_count += 1

    elif key in excluded_classes:

        excluded_image_count += 1


# ============================================================
# VALIDATION STATUS
# ============================================================

errors = []

if len(source_classes) != 72:
    errors.append(
        f"Expected 72 source classes, found {len(source_classes)}"
    )

if len(mapping_class_set) != 62:
    errors.append(
        f"Expected 62 mapped source classes, found {len(mapping_class_set)}"
    )

if len(excluded_classes) != 10:
    errors.append(
        f"Expected 10 excluded classes, found {len(excluded_classes)}"
    )

if missing_classes:
    errors.append(
        "Source classes missing from mapping/policy."
    )

if unexpected_mappings:
    errors.append(
        "Mapping contains classes not present in source datasets."
    )

if excluded_and_mapped:
    errors.append(
        "Excluded classes also appear in canonical mapping."
    )

if mapping_duplicates:
    errors.append(
        "Duplicate source-class mappings detected."
    )

if invalid_canonical_rows:
    errors.append(
        "One or more mappings have empty canonical fields."
    )


if errors:
    validation_status = "FAILED"
else:
    validation_status = "PASSED"


# ============================================================
# PRINT REPORT
# ============================================================

print()
print("SOURCE CLASS RECONCILIATION")
print("-" * 75)

print(
    f"Total source classes:        {len(source_classes)}"
)

print(
    f"Mapped source classes:       {len(mapping_class_set)}"
)

print(
    f"Excluded source classes:     {len(excluded_classes)}"
)

print(
    f"Canonical classes:            {len(canonical_classes)}"
)

print()
print("VALIDATION STATUS")
print("-" * 75)

print(validation_status)


if missing_classes:

    print()
    print("MISSING CLASSES:")

    for dataset, cls in sorted(
        missing_classes
    ):

        print(
            f"  {dataset} | {cls}"
        )


if unexpected_mappings:

    print()
    print("UNEXPECTED MAPPINGS:")

    for dataset, cls in sorted(
        unexpected_mappings
    ):

        print(
            f"  {dataset} | {cls}"
        )


if excluded_and_mapped:

    print()
    print("EXCLUDED + MAPPED CONFLICTS:")

    for dataset, cls in sorted(
        excluded_and_mapped
    ):

        print(
            f"  {dataset} | {cls}"
        )


if mapping_duplicates:

    print()
    print("DUPLICATE MAPPINGS:")

    for dataset, cls in mapping_duplicates:

        print(
            f"  {dataset} | {cls}"
        )


print()
print("ACCEPTED IMAGE RECONCILIATION")
print("-" * 75)

print(
    f"Accepted images mapped to canonical classes: "
    f"{accepted_image_count:,}"
)

print(
    f"Accepted images belonging to excluded policy classes: "
    f"{excluded_image_count:,}"
)


print()
print("CANONICAL CLASS IMAGE COUNTS")
print("-" * 75)

for (crop, disease), count in sorted(
    canonical_image_counts.items()
):

    print(
        f"{crop} | {disease}: {count:,}"
    )


# ============================================================
# WRITE REPORT
# ============================================================

with open(
    REPORT_FILE,
    "w",
    encoding="utf-8"
) as f:

    f.write("=" * 75 + "\n")
    f.write(
        "KRUSHI SAMRUDDHI ODISHA AI\n"
    )
    f.write(
        "CANONICAL CLASS MAPPING VALIDATION v2\n"
    )
    f.write("=" * 75 + "\n\n")

    f.write(
        f"Validation status: {validation_status}\n\n"
    )

    f.write("SOURCE CLASS RECONCILIATION\n")
    f.write("-" * 75 + "\n")

    f.write(
        f"Total source classes: {len(source_classes)}\n"
    )

    f.write(
        f"Mapped source classes: {len(mapping_class_set)}\n"
    )

    f.write(
        f"Excluded source classes: {len(excluded_classes)}\n"
    )

    f.write(
        f"Canonical classes: {len(canonical_classes)}\n"
    )

    f.write("\n")

    if missing_classes:

        f.write("MISSING CLASSES\n")

        for dataset, cls in sorted(
            missing_classes
        ):

            f.write(
                f"{dataset} | {cls}\n"
            )

        f.write("\n")

    if unexpected_mappings:

        f.write("UNEXPECTED MAPPINGS\n")

        for dataset, cls in sorted(
            unexpected_mappings
        ):

            f.write(
                f"{dataset} | {cls}\n"
            )

        f.write("\n")

    f.write("CANONICAL IMAGE COUNTS\n")
    f.write("-" * 75 + "\n")

    for (crop, disease), count in sorted(
        canonical_image_counts.items()
    ):

        f.write(
            f"{crop} | {disease}: {count:,}\n"
        )

    f.write("\n")

    if validation_status == "PASSED":

        f.write(
            "RESULT: All source classes are accounted for.\n"
        )

        f.write(
            "62 source classes are mapped to canonical classes.\n"
        )

        f.write(
            "10 unspecified PlantDoc classes are excluded "
            "under the approved class policy.\n"
        )

        f.write(
            "No source class is both excluded and mapped.\n"
        )

    else:

        f.write(
            "RESULT: Validation failed. "
            "Do not construct the processed dataset.\n"
        )


print()
print("Report created:")
print(REPORT_FILE)

print()
print("NEXT:")

if validation_status == "PASSED":

    print(
        "Canonical mapping is validated."
    )

    print(
        "Proceed to processed dataset construction."
    )

else:

    print(
        "Fix mapping errors before dataset construction."
    )