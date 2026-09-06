from pathlib import Path
import csv


BASE = Path(r"C:\MINI_PROJECT")

INPUT = (
    BASE
    / "DATASETS"
    / "09_REPORTS"
    / "near_duplicate_review_v1.csv"
)

OUTPUT = (
    BASE
    / "DATASETS"
    / "09_REPORTS"
    / "leakage_resolution_v1.csv"
)


with open(
    INPUT,
    "r",
    encoding="utf-8-sig",
    newline=""
) as f:

    rows = list(csv.DictReader(f))


results = []


for row in rows:

    category = row["category"]

    # --------------------------------------------------------
    # Exact train/test duplicate - same label
    # --------------------------------------------------------

    if category == "CRITICAL_TRAIN_TEST_LEAKAGE":

        decision = "EXCLUDE_TEST_COPY"

        reason = (
            "Exact SHA-256 duplicate exists in both train and "
            "test with the same source class. Retain training "
            "copy and exclude test copy from final dataset."
        )

    # --------------------------------------------------------
    # Exact train/test duplicate - conflicting labels
    # --------------------------------------------------------

    elif category == "CRITICAL_TRAIN_TEST_LEAKAGE_CONFLICTING_LABEL":

        decision = "EXCLUDE_BOTH"

        reason = (
            "Identical image has conflicting source labels across "
            "train and test. Ground truth cannot be established "
            "from the source folder labels alone."
        )

    # --------------------------------------------------------
    # Near duplicate train/test
    # --------------------------------------------------------

    elif category == "NEAR_DUPLICATE_TRAIN_TEST":

        decision = "MANUAL_REVIEW"

        reason = (
            "Perceptual-hash similarity does not prove identical "
            "imagery. Requires visual review before exclusion."
        )

    else:
        continue


    results.append({
        "pair_id": row["pair_id"],
        "category": category,

        "dataset_a": row["dataset_a"],
        "class_a": row["class_a"],
        "split_a": row["split_a"],
        "path_a": row["path_a"],

        "dataset_b": row["dataset_b"],
        "class_b": row["class_b"],
        "split_b": row["split_b"],
        "path_b": row["path_b"],

        "sha256_identical": row["sha256_identical"],
        "hamming_distance": row["hamming_distance"],

        "decision": decision,
        "reason": reason
    })


# ============================================================
# WRITE MANIFEST
# ============================================================

fields = [
    "pair_id",
    "category",

    "dataset_a",
    "class_a",
    "split_a",
    "path_a",

    "dataset_b",
    "class_b",
    "split_b",
    "path_b",

    "sha256_identical",
    "hamming_distance",

    "decision",
    "reason"
]


with open(
    OUTPUT,
    "w",
    encoding="utf-8-sig",
    newline=""
) as f:

    writer = csv.DictWriter(
        f,
        fieldnames=fields
    )

    writer.writeheader()
    writer.writerows(results)


# ============================================================
# SUMMARY
# ============================================================

from collections import Counter

decisions = Counter(
    row["decision"]
    for row in results
)


print("=" * 75)
print("KRUSHI SAMRUDDHI ODISHA AI")
print("LEAKAGE RESOLUTION MANIFEST v1")
print("=" * 75)

print()

print(
    f"Critical/near train-test pairs reviewed: "
    f"{len(results)}"
)

print()

for decision, count in sorted(
    decisions.items()
):

    print(
        f"{decision}: {count}"
    )

print()

print("Manifest created:")

print(OUTPUT)

print()

print("IMPORTANT:")
print("No source images were moved.")
print("No source images were deleted.")
print("No source images were modified.")

print()

print(
    "NEXT: Review this manifest before applying "
    "any exclusion during final dataset construction."
)