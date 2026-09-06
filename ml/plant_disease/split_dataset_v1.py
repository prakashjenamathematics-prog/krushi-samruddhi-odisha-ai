from pathlib import Path
import shutil
import random
import csv

# ============================================================
# KRUSHI SAMRUDDHI ODISHA AI
# DATASET SPLITTING v1
# ============================================================

BASE = Path(r"C:\MINI_PROJECT")

SOURCE_DIR = (
    BASE / "DATASETS" / "04_PROCESSED" / "Plant_Health"
)

TRAIN_DIR = (
    BASE / "DATASETS" / "05_TRAIN" / "Plant_Health"
)

VALIDATION_DIR = (
    BASE / "DATASETS" / "06_VALIDATION" / "Plant_Health"
)

TEST_DIR = (
    BASE / "DATASETS" / "07_TEST" / "Plant_Health"
)

MANIFEST = (
    BASE / "DATASETS" / "08_METADATA"
    / "plant_health_split_manifest_v1.csv"
)

REPORT = (
    BASE / "DATASETS" / "09_REPORTS"
    / "plant_health_split_report_v1.txt"
)

# ============================================================
# SPLIT CONFIGURATION
# ============================================================

TRAIN_RATIO = 0.70
VALIDATION_RATIO = 0.15
TEST_RATIO = 0.15

RANDOM_SEED = 42

IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp"
}

# ============================================================
# VALIDATE CONFIGURATION
# ============================================================

if abs(
    TRAIN_RATIO + VALIDATION_RATIO + TEST_RATIO - 1.0
) > 0.000001:
    raise ValueError("Split ratios must add up to 1.0")

if not SOURCE_DIR.exists():
    raise FileNotFoundError(
        f"Source directory not found: {SOURCE_DIR}"
    )

# ============================================================
# FIND CLASSES
# ============================================================

classes = sorted(
    p.name
    for p in SOURCE_DIR.iterdir()
    if p.is_dir()
)

if not classes:
    raise RuntimeError("No class folders found.")

# ============================================================
# CREATE OUTPUT DIRECTORIES
# ============================================================

for class_name in classes:
    (TRAIN_DIR / class_name).mkdir(
        parents=True,
        exist_ok=True
    )

    (VALIDATION_DIR / class_name).mkdir(
        parents=True,
        exist_ok=True
    )

    (TEST_DIR / class_name).mkdir(
        parents=True,
        exist_ok=True
    )

MANIFEST.parent.mkdir(
    parents=True,
    exist_ok=True
)

REPORT.parent.mkdir(
    parents=True,
    exist_ok=True
)

# ============================================================
# RANDOM GENERATOR
# ============================================================

rng = random.Random(RANDOM_SEED)

manifest_rows = []
summary = []

total_source = 0
total_train = 0
total_validation = 0
total_test = 0

# ============================================================
# PROCESS EACH CLASS
# ============================================================

for class_name in classes:

    source_class_dir = SOURCE_DIR / class_name

    images = [
        p for p in source_class_dir.rglob("*")
        if p.is_file()
        and p.suffix.lower() in IMAGE_EXTENSIONS
    ]

    images.sort()

    total_class = len(images)

    if total_class == 0:
        print(
            f"WARNING: {class_name} contains no images."
        )
        continue

    # Reproducible shuffle
    rng.shuffle(images)

    train_count = int(total_class * TRAIN_RATIO)

    validation_count = int(
        total_class * VALIDATION_RATIO
    )

    test_count = (
        total_class
        - train_count
        - validation_count
    )

    train_images = images[
        :train_count
    ]

    validation_images = images[
        train_count:
        train_count + validation_count
    ]

    test_images = images[
        train_count + validation_count:
    ]

    # ========================================================
    # COPY TRAINING FILES
    # ========================================================

    for source_path in train_images:

        destination_path = (
            TRAIN_DIR
            / class_name
            / source_path.name
        )

        shutil.copy2(
            source_path,
            destination_path
        )

        manifest_rows.append({
            "class_name": class_name,
            "source_path": str(source_path),
            "split": "TRAIN",
            "destination_path": str(destination_path)
        })

    # ========================================================
    # COPY VALIDATION FILES
    # ========================================================

    for source_path in validation_images:

        destination_path = (
            VALIDATION_DIR
            / class_name
            / source_path.name
        )

        shutil.copy2(
            source_path,
            destination_path
        )

        manifest_rows.append({
            "class_name": class_name,
            "source_path": str(source_path),
            "split": "VALIDATION",
            "destination_path": str(destination_path)
        })

    # ========================================================
    # COPY TEST FILES
    # ========================================================

    for source_path in test_images:

        destination_path = (
            TEST_DIR
            / class_name
            / source_path.name
        )

        shutil.copy2(
            source_path,
            destination_path
        )

        manifest_rows.append({
            "class_name": class_name,
            "source_path": str(source_path),
            "split": "TEST",
            "destination_path": str(destination_path)
        })

    # ========================================================
    # UPDATE SUMMARY
    # ========================================================

    total_source += total_class
    total_train += train_count
    total_validation += validation_count
    total_test += test_count

    summary.append({
        "class_name": class_name,
        "total": total_class,
        "train": train_count,
        "validation": validation_count,
        "test": test_count
    })

    print(
        f"{class_name}: "
        f"{total_class} total | "
        f"{train_count} train | "
        f"{validation_count} validation | "
        f"{test_count} test"
    )

# ============================================================
# WRITE MANIFEST
# ============================================================

with open(
    MANIFEST,
    "w",
    encoding="utf-8-sig",
    newline=""
) as f:

    writer = csv.DictWriter(
        f,
        fieldnames=[
            "class_name",
            "source_path",
            "split",
            "destination_path"
        ]
    )

    writer.writeheader()
    writer.writerows(manifest_rows)

# ============================================================
# WRITE REPORT
# ============================================================

with open(
    REPORT,
    "w",
    encoding="utf-8"
) as f:

    f.write("=" * 75 + "\n")
    f.write("KRUSHI SAMRUDDHI ODISHA AI\n")
    f.write("PLANT HEALTH DATASET SPLIT REPORT v1\n")
    f.write("=" * 75 + "\n\n")

    f.write("SPLIT CONFIGURATION\n")
    f.write("-" * 75 + "\n")
    f.write("Training ratio: 70%\n")
    f.write("Validation ratio: 15%\n")
    f.write("Testing ratio: 15%\n")
    f.write(f"Random seed: {RANDOM_SEED}\n\n")

    f.write("CLASS-WISE DISTRIBUTION\n")
    f.write("-" * 75 + "\n")

    for row in summary:

        f.write(
            f"{row['class_name']}: "
            f"{row['total']:,} total | "
            f"{row['train']:,} train | "
            f"{row['validation']:,} validation | "
            f"{row['test']:,} test\n"
        )

    f.write("\n")
    f.write("TOTALS\n")
    f.write("-" * 75 + "\n")
    f.write(f"Source images: {total_source:,}\n")
    f.write(f"Training images: {total_train:,}\n")
    f.write(
        f"Validation images: "
        f"{total_validation:,}\n"
    )
    f.write(f"Test images: {total_test:,}\n")
    f.write(
        f"Combined split images: "
        f"{total_train + total_validation + total_test:,}\n"
    )

    f.write("\n")
    f.write("SOURCE DATA\n")
    f.write("-" * 75 + "\n")
    f.write(
        "The original 04_PROCESSED dataset "
        "was not modified.\n"
    )

    f.write("\n")
    f.write("REPRODUCIBILITY\n")
    f.write("-" * 75 + "\n")
    f.write(
        f"Random seed used: {RANDOM_SEED}\n"
    )

# ============================================================
# FINAL CONSOLE OUTPUT
# ============================================================

print()
print("=" * 75)
print("KRUSHI SAMRUDDHI ODISHA AI")
print("PLANT HEALTH DATASET SPLIT v1")
print("=" * 75)

print()
print("Classes:", len(classes))
print("Source images:", total_source)
print("Training images:", total_train)
print("Validation images:", total_validation)
print("Test images:", total_test)
print(
    "Combined split images:",
    total_train + total_validation + total_test
)

print()
print("Manifest:")
print(MANIFEST)

print()
print("Report:")
print(REPORT)

print()
print("Source dataset remains unchanged.")
print("Dataset splitting completed.")