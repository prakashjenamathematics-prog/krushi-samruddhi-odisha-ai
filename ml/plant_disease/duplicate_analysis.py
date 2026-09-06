from pathlib import Path
from collections import defaultdict
import hashlib
import csv
import sys


# ============================================================
# KRUSHI SAMRUDDHI ODISHA AI
# PLANT HEALTH DUPLICATE ANALYSIS v1
#
# Purpose:
# 1. Identify exact duplicate images using SHA-256.
# 2. Separate datasets correctly.
# 3. Detect cross-dataset exact duplicates.
# 4. Generate reproducible audit reports.
#
# IMPORTANT:
# This script DOES NOT delete, move, resize, or modify images.
# ============================================================


BASE = Path(r"C:\MINI_PROJECT")

DATASET_ROOT = (
    BASE
    / "DATASETS"
    / "01_EXTERNAL_DATA"
    / "01_PLANT_HEALTH"
)

REPORT_DIR = (
    BASE
    / "DATASETS"
    / "09_REPORTS"
)

METADATA_DIR = (
    BASE
    / "DATASETS"
    / "08_METADATA"
)

REPORT_DIR.mkdir(parents=True, exist_ok=True)
METADATA_DIR.mkdir(parents=True, exist_ok=True)


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
# DATASET LOCATIONS
# ============================================================

PLANTDOC_ROOT = (
    DATASET_ROOT
    / "PlantDoc"
    / "EXTRACTED"
    / "PlantDoc-Dataset-master"
)

PLANTVILLAGE_ROOT = (
    DATASET_ROOT
    / "PlantVillage"
    / "EXTRACTED"
    / "PlantVillage-Dataset-master"
    / "raw"
    / "color"
)

RICE_ROOT = (
    DATASET_ROOT
    / "RiceLeafDiseaseBD"
    / "EXTRACTED_DATA"
    / "RiceLeafDiseaseBD"
    / "Original images"
)


# ============================================================
# HELPERS
# ============================================================

def is_image(path):
    return (
        path.is_file()
        and path.suffix.lower() in IMAGE_EXTENSIONS
    )


def sha256_file(path, chunk_size=1024 * 1024):

    digest = hashlib.sha256()

    try:

        with open(path, "rb") as f:

            while True:

                chunk = f.read(chunk_size)

                if not chunk:
                    break

                digest.update(chunk)

        return digest.hexdigest()

    except Exception as exc:

        print(
            f"[ERROR] Could not hash: {path}\n"
            f"        {exc}"
        )

        return None


def collect_images(dataset_name, root):

    if not root.exists():

        print(
            f"[WARNING] Dataset path does not exist:\n"
            f"{root}"
        )

        return []

    files = []

    for path in root.rglob("*"):

        if is_image(path):

            files.append({
                "dataset": dataset_name,
                "path": str(path),
                "relative_path": str(
                    path.relative_to(root)
                )
            })

    return files


# ============================================================
# COLLECT DATASET IMAGES
# ============================================================

print("=" * 75)
print("KRUSHI SAMRUDDHI ODISHA AI")
print("PLANT HEALTH DUPLICATE ANALYSIS v1")
print("=" * 75)

print("\n[1/4] Collecting image files...")


datasets = []

datasets.extend(
    collect_images(
        "PlantDoc",
        PLANTDOC_ROOT
    )
)

datasets.extend(
    collect_images(
        "PlantVillage",
        PLANTVILLAGE_ROOT
    )
)

datasets.extend(
    collect_images(
        "RiceLeafDiseaseBD",
        RICE_ROOT
    )
)


print(
    f"\nTotal candidate images discovered: "
    f"{len(datasets):,}"
)


# ============================================================
# SHA-256 HASHING
# ============================================================

print("\n[2/4] Computing SHA-256 hashes...")
print("This may take some time because the dataset is large.")


hash_groups = defaultdict(list)

errors = []

metadata_file = (
    METADATA_DIR
    / "image_hash_inventory_v1.csv"
)

with open(
    metadata_file,
    "w",
    newline="",
    encoding="utf-8"
) as f:

    writer = csv.writer(f)

    writer.writerow([
        "dataset",
        "relative_path",
        "absolute_path",
        "sha256"
    ])

    for index, item in enumerate(
        datasets,
        start=1
    ):

        path = Path(item["path"])

        digest = sha256_file(path)

        if digest is None:

            errors.append(item)

            continue

        item["sha256"] = digest

        hash_groups[digest].append(item)

        writer.writerow([
            item["dataset"],
            item["relative_path"],
            item["path"],
            digest
        ])

        if index % 1000 == 0:

            print(
                f"  Processed "
                f"{index:,}/{len(datasets):,}"
            )


# ============================================================
# IDENTIFY EXACT DUPLICATES
# ============================================================

print("\n[3/4] Analyzing exact duplicates...")


duplicate_groups = {
    digest: items
    for digest, items in hash_groups.items()
    if len(items) > 1
}


cross_dataset_groups = {}

for digest, items in duplicate_groups.items():

    dataset_names = {
        item["dataset"]
        for item in items
    }

    if len(dataset_names) > 1:

        cross_dataset_groups[digest] = items


duplicate_image_count = sum(
    len(items)
    for items in duplicate_groups.values()
)


duplicate_extra_count = sum(
    len(items) - 1
    for items in duplicate_groups.values()
)


cross_dataset_image_count = sum(
    len(items)
    for items in cross_dataset_groups.values()
)


cross_dataset_extra_count = sum(
    len(items) - 1
    for items in cross_dataset_groups.values()
)


# ============================================================
# REPORT
# ============================================================

print("\n[4/4] Writing reports...")


report_file = (
    REPORT_DIR
    / "duplicate_analysis_v1.txt"
)

duplicate_csv = (
    REPORT_DIR
    / "exact_duplicate_groups_v1.csv"
)

cross_dataset_csv = (
    REPORT_DIR
    / "cross_dataset_exact_duplicates_v1.csv"
)


with open(
    report_file,
    "w",
    encoding="utf-8"
) as report:

    report.write("=" * 75 + "\n")
    report.write(
        "KRUSHI SAMRUDDHI ODISHA AI\n"
    )
    report.write(
        "PLANT HEALTH DUPLICATE ANALYSIS v1\n"
    )
    report.write("=" * 75 + "\n\n")

    report.write(
        f"Candidate image files: "
        f"{len(datasets):,}\n"
    )

    report.write(
        f"Successfully hashed: "
        f"{len(hash_groups):,} unique SHA-256 values\n"
    )

    report.write(
        f"Hashing errors: "
        f"{len(errors):,}\n\n"
    )

    report.write(
        f"Exact duplicate groups: "
        f"{len(duplicate_groups):,}\n"
    )

    report.write(
        f"Images belonging to duplicate groups: "
        f"{duplicate_image_count:,}\n"
    )

    report.write(
        f"Duplicate extras beyond one copy per group: "
        f"{duplicate_extra_count:,}\n\n"
    )

    report.write(
        f"Cross-dataset exact duplicate groups: "
        f"{len(cross_dataset_groups):,}\n"
    )

    report.write(
        f"Images in cross-dataset duplicate groups: "
        f"{cross_dataset_image_count:,}\n"
    )

    report.write(
        f"Cross-dataset duplicate extras: "
        f"{cross_dataset_extra_count:,}\n\n"
    )

    report.write(
        "IMPORTANT:\n"
    )

    report.write(
        "Exact duplicate detection uses SHA-256.\n"
    )

    report.write(
        "Near-duplicate analysis is NOT performed in this version.\n"
    )

    report.write(
        "No files were deleted, moved, renamed, or modified.\n"
    )


# ============================================================
# DUPLICATE CSV
# ============================================================

with open(
    duplicate_csv,
    "w",
    newline="",
    encoding="utf-8"
) as f:

    writer = csv.writer(f)

    writer.writerow([
        "sha256",
        "dataset",
        "relative_path",
        "absolute_path"
    ])

    for digest, items in sorted(
        duplicate_groups.items()
    ):

        for item in items:

            writer.writerow([
                digest,
                item["dataset"],
                item["relative_path"],
                item["path"]
            ])


# ============================================================
# CROSS-DATASET CSV
# ============================================================

with open(
    cross_dataset_csv,
    "w",
    newline="",
    encoding="utf-8"
) as f:

    writer = csv.writer(f)

    writer.writerow([
        "sha256",
        "dataset",
        "relative_path",
        "absolute_path"
    ])

    for digest, items in sorted(
        cross_dataset_groups.items()
    ):

        for item in items:

            writer.writerow([
                digest,
                item["dataset"],
                item["relative_path"],
                item["path"]
            ])


# ============================================================
# FINAL CONSOLE OUTPUT
# ============================================================

print("\n" + "=" * 75)
print("DUPLICATE ANALYSIS COMPLETE")
print("=" * 75)

print(
    f"\nCandidate images: "
    f"{len(datasets):,}"
)

print(
    f"Hashing errors: "
    f"{len(errors):,}"
)

print(
    f"Exact duplicate groups: "
    f"{len(duplicate_groups):,}"
)

print(
    f"Duplicate extras: "
    f"{duplicate_extra_count:,}"
)

print(
    f"Cross-dataset duplicate groups: "
    f"{len(cross_dataset_groups):,}"
)

print(
    f"Cross-dataset duplicate extras: "
    f"{cross_dataset_extra_count:,}"
)

print("\nReports:")

print(report_file)

print(duplicate_csv)

print(cross_dataset_csv)

print("\nNo dataset files were modified.")
print("\nNEXT:")
print(
    "Review exact duplicates before performing "
    "near-duplicate analysis."
)