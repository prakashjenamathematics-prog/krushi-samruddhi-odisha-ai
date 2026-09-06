from pathlib import Path
import csv
import hashlib
from collections import Counter

# ============================================================
# KRUSHI SAMRUDDHI ODISHA AI
# NEAR-DUPLICATE REVIEW v1
# ============================================================

BASE = Path(r"C:\MINI_PROJECT")

CANDIDATE_FILE = (
    BASE / "DATASETS" / "09_REPORTS" /
    "near_duplicate_candidates_v1.csv"
)

REPORT_DIR = BASE / "DATASETS" / "09_REPORTS"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = REPORT_DIR / "near_duplicate_review_v1.csv"
SUMMARY_FILE = REPORT_DIR / "near_duplicate_review_summary_v1.txt"


def sha256_file(path):
    h = hashlib.sha256()

    try:
        with open(path, "rb") as f:
            while True:
                chunk = f.read(1024 * 1024)
                if not chunk:
                    break
                h.update(chunk)

        return h.hexdigest()

    except Exception:
        return ""


def dataset_from_path(path):
    parts = Path(path).parts

    if "PlantDoc" in parts:
        return "PlantDoc"

    if "PlantVillage" in parts:
        return "PlantVillage"

    if "RiceLeafDiseaseBD" in parts:
        return "RiceLeafDiseaseBD"

    return "Unknown"


def split_from_path(path):
    path_lower = str(path).lower()

    if "\\train\\" in path_lower:
        return "TRAIN"

    if "\\test\\" in path_lower:
        return "TEST"

    return "NOT_APPLICABLE"


def class_from_path(path):
    return Path(path).parent.name


def classify_pair(row, sha_a, sha_b):

    dataset_a = row["dataset_a"]
    dataset_b = row["dataset_b"]

    path_a = row["path_a"]
    path_b = row["path_b"]

    class_a = class_from_path(path_a)
    class_b = class_from_path(path_b)

    split_a = split_from_path(path_a)
    split_b = split_from_path(path_b)

    # --------------------------------------------------------
    # 1. Exact binary duplicate
    # --------------------------------------------------------

    if sha_a and sha_b and sha_a == sha_b:

        # Same dataset
        if dataset_a == dataset_b:

            # Train/Test leakage
            if {split_a, split_b} == {"TRAIN", "TEST"}:

                if class_a != class_b:
                    return (
                        "CRITICAL_TRAIN_TEST_LEAKAGE_CONFLICTING_LABEL",
                        "Exclude duplicate from test/train and resolve conflicting labels."
                    )

                return (
                    "CRITICAL_TRAIN_TEST_LEAKAGE",
                    "Same image exists in both train and test."
                )

            # Same class
            if class_a == class_b:

                return (
                    "EXACT_DUPLICATE_SAME_CLASS",
                    "Same image duplicated within the same class."
                )

            # Different class
            return (
                "EXACT_DUPLICATE_CONFLICTING_CLASS",
                "Same image assigned to different classes."
            )

        # Cross dataset
        return (
            "CROSS_DATASET_EXACT_DUPLICATE",
            "Same image exists in different datasets."
        )

    # --------------------------------------------------------
    # 2. Perceptual duplicate but binary file differs
    # --------------------------------------------------------

    if class_a != class_b:

        return (
            "NEAR_DUPLICATE_DIFFERENT_CLASS",
            "Visually similar images have different class labels."
        )

    if split_a != split_b and {split_a, split_b} == {"TRAIN", "TEST"}:

        return (
            "NEAR_DUPLICATE_TRAIN_TEST",
            "Visually similar images occur across train and test."
        )

    return (
        "NEAR_DUPLICATE_SAME_CLASS",
        "Visually similar images within the same class."
    )


# ============================================================
# LOAD CANDIDATES
# ============================================================

if not CANDIDATE_FILE.exists():

    print("ERROR: Candidate file not found:")
    print(CANDIDATE_FILE)
    raise SystemExit(1)


with open(
    CANDIDATE_FILE,
    "r",
    encoding="utf-8-sig",
    newline=""
) as f:

    rows = list(csv.DictReader(f))


print("=" * 75)
print("KRUSHI SAMRUDDHI ODISHA AI")
print("NEAR-DUPLICATE REVIEW v1")
print("=" * 75)

print()
print(f"Candidate pairs: {len(rows)}")
print()

# ============================================================
# REVIEW
# ============================================================

results = []

category_counter = Counter()
dataset_counter = Counter()

for index, row in enumerate(rows, start=1):

    path_a = Path(row["path_a"])
    path_b = Path(row["path_b"])

    sha_a = sha256_file(path_a)
    sha_b = sha256_file(path_b)

    category, recommendation = classify_pair(
        row,
        sha_a,
        sha_b
    )

    dataset_counter[
        f'{row["dataset_a"]} -> {row["dataset_b"]}'
    ] += 1

    category_counter[category] += 1

    results.append({
        "pair_id": index,
        "hamming_distance": row["hamming_distance"],
        "dataset_a": row["dataset_a"],
        "class_a": class_from_path(row["path_a"]),
        "split_a": split_from_path(row["path_a"]),
        "path_a": row["path_a"],
        "dataset_b": row["dataset_b"],
        "class_b": class_from_path(row["path_b"]),
        "split_b": split_from_path(row["path_b"]),
        "path_b": row["path_b"],
        "sha256_a": sha_a,
        "sha256_b": sha_b,
        "sha256_identical": "YES" if sha_a and sha_a == sha_b else "NO",
        "category": category,
        "recommendation": recommendation
    })


# ============================================================
# WRITE CSV
# ============================================================

fieldnames = [
    "pair_id",
    "hamming_distance",
    "dataset_a",
    "class_a",
    "split_a",
    "path_a",
    "dataset_b",
    "class_b",
    "split_b",
    "path_b",
    "sha256_a",
    "sha256_b",
    "sha256_identical",
    "category",
    "recommendation"
]

with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8-sig",
    newline=""
) as f:

    writer = csv.DictWriter(
        f,
        fieldnames=fieldnames
    )

    writer.writeheader()
    writer.writerows(results)


# ============================================================
# SUMMARY
# ============================================================

critical = (
    category_counter["CRITICAL_TRAIN_TEST_LEAKAGE"]
    + category_counter[
        "CRITICAL_TRAIN_TEST_LEAKAGE_CONFLICTING_LABEL"
    ]
)

with open(
    SUMMARY_FILE,
    "w",
    encoding="utf-8"
) as f:

    f.write("=" * 75 + "\n")
    f.write("KRUSHI SAMRUDDHI ODISHA AI\n")
    f.write("NEAR-DUPLICATE REVIEW SUMMARY v1\n")
    f.write("=" * 75 + "\n\n")

    f.write(f"Candidate pairs reviewed: {len(rows)}\n\n")

    f.write("CATEGORY SUMMARY\n")
    f.write("-" * 75 + "\n")

    for category, count in sorted(category_counter.items()):
        f.write(f"{category}: {count}\n")

    f.write("\n")

    f.write("DATASET PAIR SUMMARY\n")
    f.write("-" * 75 + "\n")

    for dataset_pair, count in sorted(dataset_counter.items()):
        f.write(f"{dataset_pair}: {count}\n")

    f.write("\n")

    f.write("CRITICAL FINDINGS\n")
    f.write("-" * 75 + "\n")

    f.write(
        f"Train/Test leakage candidates: {critical}\n"
    )

    f.write("\n")

    f.write("IMPORTANT RULE\n")
    f.write("-" * 75 + "\n")
    f.write(
        "No source images were deleted or moved by this script.\n"
    )
    f.write(
        "All decisions must be made before final dataset construction.\n"
    )


# ============================================================
# CONSOLE OUTPUT
# ============================================================

print("=" * 75)
print("REVIEW COMPLETE")
print("=" * 75)

print()
print("Category summary:")

for category, count in sorted(category_counter.items()):
    print(f"  {category}: {count}")

print()
print(f"Train/Test leakage candidates: {critical}")

print()
print("Reports created:")
print(OUTPUT_FILE)
print(SUMMARY_FILE)

print()
print("NO SOURCE IMAGES WERE MODIFIED.")
print()
print("NEXT:")
print("Review the generated CSV before dataset construction.")