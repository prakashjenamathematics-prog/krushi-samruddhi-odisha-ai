from pathlib import Path
from collections import defaultdict
import hashlib
import csv
import sys

from PIL import Image


# ============================================================
# KRUSHI SAMRUDDHI ODISHA AI
# NEAR-DUPLICATE ANALYSIS v1
#
# Purpose:
# Detect visually similar images using perceptual hashing.
#
# This script:
# - DOES NOT modify source images
# - DOES NOT delete files
# - DOES NOT move files
# - excludes PlantDoc documentation files
# - creates reports for review
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
# DATASET ROOTS
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
# IMAGE VALIDATION
# ============================================================

def is_image(path):
    return (
        path.is_file()
        and path.suffix.lower() in IMAGE_EXTENSIONS
    )


# ============================================================
# COLLECT IMAGES
# ============================================================

def collect_images(dataset_name, root):

    images = []

    if not root.exists():

        print(
            f"[WARNING] Missing dataset path:\n{root}"
        )

        return images

    for path in root.rglob("*"):

        if is_image(path):

            images.append({
                "dataset": dataset_name,
                "path": str(path),
                "relative_path": str(
                    path.relative_to(root)
                )
            })

    return images


# ============================================================
# PERCEPTUAL HASH
# ============================================================

def average_hash(image):

    image = image.convert("L").resize((32, 32))

    pixels = list(image.getdata())

    average = sum(pixels) / len(pixels)

    bits = [
        1 if pixel >= average else 0
        for pixel in pixels
    ]

    value = 0

    for bit in bits:

        value = (
            value << 1
        ) | bit

    return value


def hamming_distance(a, b):

    return (a ^ b).bit_count()


# ============================================================
# MAIN
# ============================================================

print("=" * 75)
print("KRUSHI SAMRUDDHI ODISHA AI")
print("NEAR-DUPLICATE ANALYSIS v1")
print("=" * 75)


print("\n[1/4] Collecting ML candidate images...")


images = []

images.extend(
    collect_images(
        "PlantDoc",
        PLANTDOC_ROOT
    )
)

images.extend(
    collect_images(
        "PlantVillage",
        PLANTVILLAGE_ROOT
    )
)

images.extend(
    collect_images(
        "RiceLeafDiseaseBD",
        RICE_ROOT
    )
)


print(
    f"Candidate images discovered: "
    f"{len(images):,}"
)


# ============================================================
# HASH IMAGES
# ============================================================

print("\n[2/4] Computing perceptual hashes...")
print("This may take several minutes.")


hash_records = []

errors = []


for index, item in enumerate(
    images,
    start=1
):

    path = Path(item["path"])

    try:

        with Image.open(path) as image:

            image.load()

            phash = average_hash(image)

        item["phash"] = phash

        hash_records.append(item)

    except Exception as exc:

        errors.append({
            "path": str(path),
            "error": str(exc)
        })

    if index % 1000 == 0:

        print(
            f"  Processed "
            f"{index:,}/{len(images):,}"
        )


# ============================================================
# SAVE HASH INVENTORY
# ============================================================

hash_inventory = (
    METADATA_DIR
    / "perceptual_hash_inventory_v1.csv"
)


with open(
    hash_inventory,
    "w",
    newline="",
    encoding="utf-8"
) as f:

    writer = csv.writer(f)

    writer.writerow([
        "dataset",
        "relative_path",
        "absolute_path",
        "perceptual_hash"
    ])

    for item in hash_records:

        writer.writerow([
            item["dataset"],
            item["relative_path"],
            item["path"],
            format(item["phash"], "0256b")
        ])


# ============================================================
# NEAR-DUPLICATE SEARCH
# ============================================================

print("\n[3/4] Searching for near-duplicates...")


# ------------------------------------------------------------
# IMPORTANT:
# A Hamming distance <= 5 is treated as a candidate.
#
# This is intentionally a candidate threshold.
# It does NOT automatically mean the images are duplicates.
# ------------------------------------------------------------

THRESHOLD = 5


near_duplicates = []

total = len(hash_records)


for i in range(total):

    current = hash_records[i]

    for j in range(i + 1, total):

        other = hash_records[j]

        distance = hamming_distance(
            current["phash"],
            other["phash"]
        )

        if distance <= THRESHOLD:

            near_duplicates.append({
                "distance": distance,
                "dataset_a": current["dataset"],
                "path_a": current["path"],
                "dataset_b": other["dataset"],
                "path_b": other["path"]
            })


# ============================================================
# CLASSIFY CROSS-DATASET CANDIDATES
# ============================================================

cross_dataset = [
    item
    for item in near_duplicates
    if item["dataset_a"]
    != item["dataset_b"]
]


same_dataset = [
    item
    for item in near_duplicates
    if item["dataset_a"]
    == item["dataset_b"]
]


# ============================================================
# WRITE NEAR-DUPLICATE REPORT
# ============================================================

near_csv = (
    REPORT_DIR
    / "near_duplicate_candidates_v1.csv"
)


with open(
    near_csv,
    "w",
    newline="",
    encoding="utf-8"
) as f:

    writer = csv.writer(f)

    writer.writerow([
        "hamming_distance",
        "dataset_a",
        "path_a",
        "dataset_b",
        "path_b"
    ])

    for item in near_duplicates:

        writer.writerow([
            item["distance"],
            item["dataset_a"],
            item["path_a"],
            item["dataset_b"],
            item["path_b"]
        ])


# ============================================================
# WRITE CROSS-DATASET REPORT
# ============================================================

cross_csv = (
    REPORT_DIR
    / "near_duplicate_cross_dataset_v1.csv"
)


with open(
    cross_csv,
    "w",
    newline="",
    encoding="utf-8"
) as f:

    writer = csv.writer(f)

    writer.writerow([
        "hamming_distance",
        "dataset_a",
        "path_a",
        "dataset_b",
        "path_b"
    ])

    for item in cross_dataset:

        writer.writerow([
            item["distance"],
            item["dataset_a"],
            item["path_a"],
            item["dataset_b"],
            item["path_b"]
        ])


# ============================================================
# FINAL REPORT
# ============================================================

report_file = (
    REPORT_DIR
    / "near_duplicate_analysis_v1.txt"
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
        "NEAR-DUPLICATE ANALYSIS v1\n"
    )
    report.write("=" * 75 + "\n\n")

    report.write(
        f"Candidate images: "
        f"{len(images):,}\n"
    )

    report.write(
        f"Successfully hashed: "
        f"{len(hash_records):,}\n"
    )

    report.write(
        f"Image processing errors: "
        f"{len(errors):,}\n\n"
    )

    report.write(
        f"Perceptual hash threshold: "
        f"{THRESHOLD}\n"
    )

    report.write(
        f"Near-duplicate candidate pairs: "
        f"{len(near_duplicates):,}\n"
    )

    report.write(
        f"Same-dataset candidate pairs: "
        f"{len(same_dataset):,}\n"
    )

    report.write(
        f"Cross-dataset candidate pairs: "
        f"{len(cross_dataset):,}\n\n"
    )

    report.write(
        "INTERPRETATION:\n"
    )

    report.write(
        "A near-duplicate candidate is NOT automatically "
        "considered a duplicate.\n"
    )

    report.write(
        "Candidate pairs must be reviewed before exclusion.\n"
    )

    report.write(
        "The original datasets were not modified.\n"
    )


# ============================================================
# CONSOLE OUTPUT
# ============================================================

print("\n" + "=" * 75)
print("NEAR-DUPLICATE ANALYSIS COMPLETE")
print("=" * 75)

print(
    f"\nCandidate images: "
    f"{len(images):,}"
)

print(
    f"Successfully hashed: "
    f"{len(hash_records):,}"
)

print(
    f"Processing errors: "
    f"{len(errors):,}"
)

print(
    f"Near-duplicate candidate pairs: "
    f"{len(near_duplicates):,}"
)

print(
    f"Same-dataset candidates: "
    f"{len(same_dataset):,}"
)

print(
    f"Cross-dataset candidates: "
    f"{len(cross_dataset):,}"
)

print("\nReports created:")

print(report_file)

print(near_csv)

print(cross_csv)

print(hash_inventory)

print("\nNo source images were modified.")

print("\nNEXT:")
print(
    "Review near-duplicate candidates before "
    "final dataset construction."
)