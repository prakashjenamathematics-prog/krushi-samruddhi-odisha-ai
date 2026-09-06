from pathlib import Path
from collections import Counter
from PIL import Image
import csv
import zipfile
import hashlib
import json
import sys


# ============================================================
# KRUSHI SAMRUDDHI ODISHA AI
# DATASET AUDIT v1
# ============================================================

BASE = Path(r"C:\MINI_PROJECT")

PLANT_HEALTH = (
    BASE
    / "DATASETS"
    / "01_EXTERNAL_DATA"
    / "01_PLANT_HEALTH"
)

REPORT_DIR = BASE / "DATASETS" / "09_REPORTS"
METADATA_DIR = BASE / "DATASETS" / "08_METADATA"

REPORT_DIR.mkdir(parents=True, exist_ok=True)
METADATA_DIR.mkdir(parents=True, exist_ok=True)

IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".webp",
    ".tif",
    ".tiff",
}


# ============================================================
# HELPERS
# ============================================================

def is_image(path: Path):
    return path.suffix.lower() in IMAGE_EXTENSIONS


def human_size(size):
    units = ["B", "KB", "MB", "GB", "TB"]

    value = float(size)

    for unit in units:
        if value < 1024:
            return f"{value:.2f} {unit}"
        value /= 1024

    return f"{value:.2f} PB"


def write_csv(path, headers, rows):
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)


# ============================================================
# DATASET 1 — PLANTDOC
# ============================================================

def audit_plantdoc():

    root = (
        PLANT_HEALTH
        / "PlantDoc"
        / "EXTRACTED"
        / "PlantDoc-Dataset-master"
    )

    rows = []
    class_counter = Counter()
    split_counter = Counter()
    extension_counter = Counter()

    corrupt_images = []

    total_files = 0
    total_images = 0

    if not root.exists():
        print("PlantDoc path not found.")
        return None

    for split in ["train", "test"]:

        split_path = root / split

        if not split_path.exists():
            continue

        for class_dir in sorted(split_path.iterdir()):

            if not class_dir.is_dir():
                continue

            class_name = class_dir.name

            for file in class_dir.rglob("*"):

                if not file.is_file():
                    continue

                total_files += 1

                if not is_image(file):
                    continue

                total_images += 1

                class_counter[class_name] += 1
                split_counter[split] += 1
                extension_counter[file.suffix.lower()] += 1

                try:
                    with Image.open(file) as img:
                        img.verify()

                except Exception:
                    corrupt_images.append(str(file))

                rows.append([
                    "PlantDoc",
                    split,
                    class_name,
                    file.suffix.lower(),
                    str(file)
                ])

    write_csv(
        METADATA_DIR / "plantdoc_image_inventory.csv",
        [
            "dataset",
            "split",
            "class",
            "extension",
            "path"
        ],
        rows
    )

    return {
        "dataset": "PlantDoc",
        "total_files": total_files,
        "total_images": total_images,
        "classes": len(class_counter),
        "class_counts": class_counter,
        "split_counts": split_counter,
        "extensions": extension_counter,
        "corrupt": corrupt_images,
    }


# ============================================================
# DATASET 2 — PLANTVILLAGE
# ============================================================

def audit_plantvillage():

    root = (
        PLANT_HEALTH
        / "PlantVillage"
        / "EXTRACTED"
        / "PlantVillage-Dataset-master"
        / "raw"
        / "color"
    )

    rows = []
    class_counter = Counter()
    extension_counter = Counter()

    corrupt_images = []

    total_files = 0
    total_images = 0

    if not root.exists():
        print("PlantVillage color path not found.")
        return None

    for class_dir in sorted(root.iterdir()):

        if not class_dir.is_dir():
            continue

        class_name = class_dir.name

        for file in class_dir.rglob("*"):

            if not file.is_file():
                continue

            total_files += 1

            if not is_image(file):
                continue

            total_images += 1

            class_counter[class_name] += 1
            extension_counter[file.suffix.lower()] += 1

            try:
                with Image.open(file) as img:
                    img.verify()

            except Exception:
                corrupt_images.append(str(file))

            rows.append([
                "PlantVillage",
                class_name,
                file.suffix.lower(),
                str(file)
            ])

    write_csv(
        METADATA_DIR / "plantvillage_image_inventory.csv",
        [
            "dataset",
            "class",
            "extension",
            "path"
        ],
        rows
    )

    return {
        "dataset": "PlantVillage",
        "total_files": total_files,
        "total_images": total_images,
        "classes": len(class_counter),
        "class_counts": class_counter,
        "extensions": extension_counter,
        "corrupt": corrupt_images,
    }


# ============================================================
# DATASET 3 — RICELEAFDISEASEBD
# ============================================================

def audit_riceleaf():

    root = (
        PLANT_HEALTH
        / "RiceLeafDiseaseBD"
        / "EXTRACTED_DATA"
        / "RiceLeafDiseaseBD"
    )

    rows = []
    class_counter = Counter()
    extension_counter = Counter()

    corrupt_images = []

    total_files = 0
    total_images = 0

    if not root.exists():
        print("RiceLeafDiseaseBD path not found.")
        return None

    for file in root.rglob("*"):

        if not file.is_file():
            continue

        total_files += 1

        if not is_image(file):
            continue

        total_images += 1

        # The immediate parent directory is treated as the
        # initial class candidate. We will verify this later.
        class_name = file.parent.name

        class_counter[class_name] += 1
        extension_counter[file.suffix.lower()] += 1

        try:
            with Image.open(file) as img:
                img.verify()

        except Exception:
            corrupt_images.append(str(file))

        rows.append([
            "RiceLeafDiseaseBD",
            class_name,
            file.suffix.lower(),
            str(file)
        ])

    write_csv(
        METADATA_DIR / "riceleaf_image_inventory.csv",
        [
            "dataset",
            "class_candidate",
            "extension",
            "path"
        ],
        rows
    )

    return {
        "dataset": "RiceLeafDiseaseBD",
        "total_files": total_files,
        "total_images": total_images,
        "classes": len(class_counter),
        "class_counts": class_counter,
        "extensions": extension_counter,
        "corrupt": corrupt_images,
    }


# ============================================================
# SUMMARY REPORT
# ============================================================

def create_summary(results):

    summary_rows = []

    for result in results:

        if result is None:
            continue

        summary_rows.append([
            result["dataset"],
            result["total_files"],
            result["total_images"],
            result["classes"],
            len(result["corrupt"]),
            ", ".join(
                f"{k}={v}"
                for k, v in result["extensions"].items()
            )
        ])

    write_csv(
        REPORT_DIR / "dataset_audit_summary.csv",
        [
            "dataset",
            "total_files",
            "total_images",
            "class_count",
            "corrupt_images",
            "extensions"
        ],
        summary_rows
    )


# ============================================================
# CLASS DISTRIBUTION
# ============================================================

def create_class_distribution(results):

    rows = []

    for result in results:

        if result is None:
            continue

        for class_name, count in sorted(
            result["class_counts"].items()
        ):

            rows.append([
                result["dataset"],
                class_name,
                count
            ])

    write_csv(
        REPORT_DIR / "class_distribution.csv",
        [
            "dataset",
            "class",
            "image_count"
        ],
        rows
    )


# ============================================================
# CORRUPTED IMAGE REPORT
# ============================================================

def create_corrupt_report(results):

    rows = []

    for result in results:

        if result is None:
            continue

        for image in result["corrupt"]:

            rows.append([
                result["dataset"],
                image
            ])

    write_csv(
        REPORT_DIR / "corrupt_images.csv",
        [
            "dataset",
            "image_path"
        ],
        rows
    )


# ============================================================
# DATASET REGISTRY
# ============================================================

def create_dataset_registry(results):

    rows = [
        [
            "PlantDoc",
            "External dataset",
            "Plant disease image dataset",
            "Train/Test structure",
            "Audit required before model integration"
        ],
        [
            "PlantVillage",
            "External dataset",
            "Multi-crop plant disease image dataset",
            "Color image classes",
            "Audit required before model integration"
        ],
        [
            "RiceLeafDiseaseBD",
            "External dataset",
            "Field-based rice leaf disease dataset",
            "Nested dataset archive",
            "Audit required before model integration"
        ],
    ]

    write_csv(
        METADATA_DIR / "dataset_registry.csv",
        [
            "dataset",
            "source_type",
            "purpose",
            "observed_structure",
            "status"
        ],
        rows
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("KRUSHI SAMRUDDHI ODISHA AI")
    print("PLANT HEALTH DATASET AUDIT v1")
    print("=" * 70)

    print("\n[1/3] Auditing PlantDoc...")
    plantdoc = audit_plantdoc()

    print("[2/3] Auditing PlantVillage...")
    plantvillage = audit_plantvillage()

    print("[3/3] Auditing RiceLeafDiseaseBD...")
    riceleaf = audit_riceleaf()

    results = [
        plantdoc,
        plantvillage,
        riceleaf
    ]

    create_summary(results)
    create_class_distribution(results)
    create_corrupt_report(results)
    create_dataset_registry(results)

    print("\n" + "=" * 70)
    print("AUDIT COMPLETE")
    print("=" * 70)

    for result in results:

        if result is None:
            continue

        print(f"\nDataset: {result['dataset']}")
        print(f"Total files: {result['total_files']}")
        print(f"Image files: {result['total_images']}")
        print(f"Classes: {result['classes']}")
        print(f"Corrupt images: {len(result['corrupt'])}")

    print("\nReports created in:")
    print(REPORT_DIR)

    print("\nMetadata created in:")
    print(METADATA_DIR)


if __name__ == "__main__":
    main()