from pathlib import Path
import csv
import shutil
import re
from collections import Counter


# ============================================================
# KRUSHI SAMRUDDHI ODISHA AI
# PROCESSED PLANT HEALTH DATASET BUILDER v1
# ============================================================

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

PROCESSED_DIR = (
    BASE
    / "DATASETS"
    / "04_PROCESSED"
    / "Plant_Health"
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

OUTPUT_MANIFEST = (
    PROCESSED_DIR.parent
    / "processed_dataset_manifest_v1.csv"
)

OUTPUT_SUMMARY = (
    PROCESSED_DIR.parent
    / "processed_dataset_summary_v1.txt"
)


IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".webp",
    ".tif",
    ".tiff"
}


# ============================================================
# HELPERS
# ============================================================

def safe_name(value):

    value = value.strip()

    value = value.replace("/", "_")
    value = value.replace("\\", "_")

    value = re.sub(
        r"[^A-Za-z0-9._-]+",
        "_",
        value
    )

    value = re.sub(
        r"_+",
        "_",
        value
    )

    return value.strip("_")


def unique_destination(
    destination,
    dataset,
    original_path
):

    if not destination.exists():

        return destination

    stem = destination.stem
    suffix = destination.suffix

    dataset_prefix = safe_name(
        dataset
    )

    candidate = (
        destination.parent
        / f"{dataset_prefix}__{stem}{suffix}"
    )

    if not candidate.exists():

        return candidate

    counter = 2

    while True:

        candidate = (
            destination.parent
            / f"{dataset_prefix}__{stem}_{counter}{suffix}"
        )

        if not candidate.exists():

            return candidate

        counter += 1


# ============================================================
# START
# ============================================================

print("=" * 75)
print("KRUSHI SAMRUDDHI ODISHA AI")
print("PROCESSED PLANT HEALTH DATASET BUILDER v1")
print("=" * 75)


# ============================================================
# CHECK INPUTS
# ============================================================

print()
print("[1/5] Checking metadata...")


if not AUDIT_MANIFEST.exists():

    raise SystemExit(
        f"ERROR: Missing audit manifest:\n{AUDIT_MANIFEST}"
    )


if not MAPPING_FILE.exists():

    raise SystemExit(
        f"ERROR: Missing canonical mapping:\n{MAPPING_FILE}"
    )


# ============================================================
# LOAD MAPPING
# ============================================================

print("[2/5] Loading canonical mapping...")


with open(
    MAPPING_FILE,
    encoding="utf-8-sig",
    newline=""
) as f:

    mapping_rows = list(
        csv.DictReader(f)
    )


mapping = {}

for row in mapping_rows:

    key = (
        row["dataset"],
        row["original_class"]
    )

    mapping[key] = {
        "crop": row["crop"],
        "disease": row["canonical_disease"]
    }


print(
    f"Canonical mappings loaded: "
    f"{len(mapping)}"
)


# ============================================================
# LOAD AUDIT MANIFEST
# ============================================================

print("[3/5] Loading audit manifest...")


with open(
    AUDIT_MANIFEST,
    encoding="utf-8-sig",
    newline=""
) as f:

    audit_rows = list(
        csv.DictReader(f)
    )


print(
    f"Audit records loaded: "
    f"{len(audit_rows):,}"
)


# ============================================================
# CREATE PROCESSED ROOT
# ============================================================

PROCESSED_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# PROCESS
# ============================================================

print("[4/5] Copying accepted mapped images...")
print()
print(
    "This may take several minutes."
)
print(
    "Original source images will NOT be modified."
)
print()


processed_rows = []

status_counts = Counter()

canonical_counts = Counter()

dataset_counts = Counter()

copy_errors = []

processed_count = 0


for index, row in enumerate(
    audit_rows,
    start=1
):

    dataset = row["dataset"]
    original_class = row["original_class"]
    source_path = Path(
        row["source_path"]
    )

    status = row["status"]

    status_counts[status] += 1


    # --------------------------------------------------------
    # Only ACCEPT records enter processed dataset
    # --------------------------------------------------------

    if status != "ACCEPT":

        continue


    key = (
        dataset,
        original_class
    )


    # --------------------------------------------------------
    # Verify mapping exists
    # --------------------------------------------------------

    if key not in mapping:

        copy_errors.append({
            "source_path": str(source_path),
            "error": (
                "ACCEPT record has no canonical mapping."
            )
        })

        continue


    canonical = mapping[key]

    crop = canonical["crop"]
    disease = canonical["disease"]


    # --------------------------------------------------------
    # Build canonical directory
    # --------------------------------------------------------

    crop_dir = (
        PROCESSED_DIR
        / safe_name(crop)
    )

    disease_dir = (
        crop_dir
        / safe_name(disease)
    )

    disease_dir.mkdir(
        parents=True,
        exist_ok=True
    )


    # --------------------------------------------------------
    # Destination filename
    #
    # Prefix dataset to avoid accidental filename collision.
    # --------------------------------------------------------

    destination = (
        disease_dir
        / f"{safe_name(dataset)}__{source_path.name}"
    )


    destination = unique_destination(
        destination,
        dataset,
        source_path
    )


    # --------------------------------------------------------
    # Copy
    # --------------------------------------------------------

    try:

        shutil.copy2(
            source_path,
            destination
        )

        processed_count += 1

        canonical_counts[
            (crop, disease)
        ] += 1

        dataset_counts[
            dataset
        ] += 1

        processed_rows.append({

            "dataset":
                dataset,

            "source_split":
                row["source_split"],

            "original_class":
                original_class,

            "crop":
                crop,

            "canonical_disease":
                disease,

            "source_path":
                str(source_path),

            "processed_path":
                str(destination),

            "sha256":
                row["sha256"],

            "status":
                "PROCESSED"
        })


    except Exception as e:

        copy_errors.append({

            "source_path":
                str(source_path),

            "error":
                str(e)
        })


    # --------------------------------------------------------
    # Progress
    # --------------------------------------------------------

    if index % 5000 == 0:

        print(
            f"Processed audit records: "
            f"{index:,} / {len(audit_rows):,}"
        )


# ============================================================
# WRITE PROCESSED MANIFEST
# ============================================================

print()
print("[5/5] Writing processed metadata...")


manifest_fields = [
    "dataset",
    "source_split",
    "original_class",
    "crop",
    "canonical_disease",
    "source_path",
    "processed_path",
    "sha256",
    "status"
]


with open(
    OUTPUT_MANIFEST,
    "w",
    encoding="utf-8-sig",
    newline=""
) as f:

    writer = csv.DictWriter(
        f,
        fieldnames=manifest_fields
    )

    writer.writeheader()

    writer.writerows(
        processed_rows
    )


# ============================================================
# WRITE SUMMARY
# ============================================================

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
        "PROCESSED PLANT HEALTH DATASET SUMMARY v1\n"
    )
    f.write("=" * 75 + "\n\n")

    f.write(
        f"Audit records: "
        f"{len(audit_rows):,}\n"
    )

    f.write(
        f"Processed images: "
        f"{processed_count:,}\n"
    )

    f.write(
        f"Copy errors: "
        f"{len(copy_errors):,}\n\n"
    )

    f.write("AUDIT STATUS COUNTS\n")
    f.write("-" * 75 + "\n")

    for status, count in sorted(
        status_counts.items()
    ):

        f.write(
            f"{status}: {count:,}\n"
        )

    f.write("\nDATASET COUNTS\n")
    f.write("-" * 75 + "\n")

    for dataset, count in sorted(
        dataset_counts.items()
    ):

        f.write(
            f"{dataset}: {count:,}\n"
        )

    f.write("\nCANONICAL CLASS COUNTS\n")
    f.write("-" * 75 + "\n")

    for (crop, disease), count in sorted(
        canonical_counts.items()
    ):

        f.write(
            f"{crop} | {disease}: "
            f"{count:,}\n"
        )

    if copy_errors:

        f.write("\nCOPY ERRORS\n")
        f.write("-" * 75 + "\n")

        for error in copy_errors:

            f.write(
                f"{error['source_path']}\n"
            )

            f.write(
                f"ERROR: {error['error']}\n\n"
            )


# ============================================================
# FINAL CONSOLE REPORT
# ============================================================

print()
print("=" * 75)
print("PROCESSED DATASET BUILD COMPLETE")
print("=" * 75)

print()
print(
    f"Processed images: "
    f"{processed_count:,}"
)

print(
    f"Expected mapped accepted images: "
    f"65,779"
)

print(
    f"Copy errors: "
    f"{len(copy_errors):,}"
)

print()
print("Dataset counts:")

for dataset, count in sorted(
    dataset_counts.items()
):

    print(
        f"  {dataset}: {count:,}"
    )

print()
print("Canonical classes:")
print(
    f"  {len(canonical_counts)}"
)

print()
print("Processed dataset:")
print(PROCESSED_DIR)

print()
print("Manifest:")
print(OUTPUT_MANIFEST)

print()
print("Summary:")
print(OUTPUT_SUMMARY)

print()
print("IMPORTANT:")
print(
    "Original source datasets were not modified."
)