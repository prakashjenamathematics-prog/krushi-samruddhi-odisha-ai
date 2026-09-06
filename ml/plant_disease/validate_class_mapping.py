from pathlib import Path
import csv
from collections import Counter, defaultdict


BASE = Path(r"C:\MINI_PROJECT")

MAPPING_FILE = (
    BASE
    / "DATASETS"
    / "08_METADATA"
    / "class_mapping.csv"
)

REPORT_DIR = (
    BASE
    / "DATASETS"
    / "09_REPORTS"
)

REPORT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = REPORT_DIR / "class_mapping_validation_v1.txt"


# ============================================================
# LOAD MAPPING
# ============================================================

rows = []

with open(
    MAPPING_FILE,
    "r",
    encoding="utf-8-sig",
    newline=""
) as f:

    reader = csv.DictReader(f)

    for row in reader:
        rows.append(row)


# ============================================================
# BASIC COUNTS
# ============================================================

dataset_counts = Counter(
    row["dataset"]
    for row in rows
)

canonical_datasets = defaultdict(set)

for row in rows:
    canonical_datasets[
        row["canonical_class"]
    ].add(row["dataset"])


canonical_counts = Counter(
    row["canonical_class"]
    for row in rows
)


ambiguous = [
    row for row in rows
    if row["health_status"] == "Unspecified"
]


# ============================================================
# WRITE REPORT
# ============================================================

with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8"
) as report:

    report.write("=" * 75 + "\n")
    report.write("KRUSHI SAMRUDDHI ODISHA AI\n")
    report.write("CLASS MAPPING VALIDATION REPORT v1\n")
    report.write("=" * 75 + "\n\n")

    # --------------------------------------------------------
    # SOURCE DATASETS
    # --------------------------------------------------------

    report.write("1. SOURCE DATASET CLASS COUNTS\n")
    report.write("-" * 75 + "\n")

    for dataset, count in dataset_counts.items():
        report.write(
            f"{dataset}: {count} classes\n"
        )

    report.write(
        f"\nTotal source classes: {len(rows)}\n"
    )

    # --------------------------------------------------------
    # CANONICAL CLASSES
    # --------------------------------------------------------

    report.write("\n2. CANONICAL CLASS SUMMARY\n")
    report.write("-" * 75 + "\n")

    report.write(
        f"Unique canonical classes: "
        f"{len(canonical_counts)}\n"
    )

    for canonical, count in sorted(
        canonical_counts.items()
    ):
        datasets = ", ".join(
            sorted(canonical_datasets[canonical])
        )

        report.write(
            f"{canonical} | "
            f"source labels: {count} | "
            f"datasets: {datasets}\n"
        )

    # --------------------------------------------------------
    # CROSS-DATASET MAPPINGS
    # --------------------------------------------------------

    report.write("\n3. CANONICAL CLASSES SHARED BY DATASETS\n")
    report.write("-" * 75 + "\n")

    shared_found = False

    for canonical, datasets in sorted(
        canonical_datasets.items()
    ):

        if len(datasets) > 1:

            shared_found = True

            report.write(
                f"{canonical}\n"
                f"  Datasets: "
                f"{', '.join(sorted(datasets))}\n"
            )

    if not shared_found:
        report.write(
            "No canonical classes are currently shared "
            "across multiple datasets.\n"
        )

    # --------------------------------------------------------
    # AMBIGUOUS CLASSES
    # --------------------------------------------------------

    report.write("\n4. AMBIGUOUS / UNSPECIFIED SOURCE LABELS\n")
    report.write("-" * 75 + "\n")

    report.write(
        f"Total unspecified mappings: "
        f"{len(ambiguous)}\n\n"
    )

    for row in ambiguous:

        report.write(
            f"{row['dataset']} | "
            f"{row['original_class']} | "
            f"{row['canonical_class']}\n"
        )

    # --------------------------------------------------------
    # VERY LOW SOURCE CLASS COUNT
    # --------------------------------------------------------

    report.write("\n5. SOURCE CLASSES REQUIRING DATA REVIEW\n")
    report.write("-" * 75 + "\n")

    report.write(
        "The mapping file contains labels only; "
        "image counts are not stored in this file.\n"
    )

    report.write(
        "Very-small classes will be identified using "
        "the original dataset audit during the next phase.\n"
    )

    # --------------------------------------------------------
    # IMPORTANT RULES
    # --------------------------------------------------------

    report.write("\n6. VALIDATION RULES\n")
    report.write("-" * 75 + "\n")

    report.write(
        "1. Do not treat unspecified PlantDoc labels as healthy.\n"
    )

    report.write(
        "2. Do not merge classes solely because their names look similar.\n"
    )

    report.write(
        "3. Annotated RiceLeafDiseaseBD visual images are excluded "
        "from the primary classifier candidate set.\n"
    )

    report.write(
        "4. Original RiceLeafDiseaseBD images are the primary Rice "
        "candidate images.\n"
    )

    report.write(
        "5. Duplicate and cross-dataset leakage analysis must occur "
        "before train/validation/test splitting.\n"
    )

    report.write(
        "6. The mapping is not the final training dataset.\n"
    )

    # --------------------------------------------------------
    # FINAL STATUS
    # --------------------------------------------------------

    report.write("\n7. STATUS\n")
    report.write("-" * 75 + "\n")

    report.write(
        "Mapping Validation v1 completed.\n"
    )

    report.write(
        "NEXT PHASE: IMAGE-LEVEL DUPLICATE AND "
        "CROSS-DATASET LEAKAGE ANALYSIS.\n"
    )


print("=" * 75)
print("KRUSHI SAMRUDDHI ODISHA AI")
print("CLASS MAPPING VALIDATION REPORT v1")
print("=" * 75)

print(f"\nSource classes: {len(rows)}")
print(f"Canonical classes: {len(canonical_counts)}")
print(f"Unspecified mappings: {len(ambiguous)}")

print("\nDataset class counts:")

for dataset, count in dataset_counts.items():
    print(f"  {dataset}: {count}")

print(f"\nReport created:")
print(OUTPUT_FILE)

print("\nNEXT:")
print("Review the validation report before dataset construction.")