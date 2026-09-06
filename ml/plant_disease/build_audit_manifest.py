from pathlib import Path
import csv
import hashlib


# ============================================================
# KRUSHI SAMRUDDHI ODISHA AI
# AUDITED DATASET MANIFEST v1
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

AUDITED_DIR = (
    BASE
    / "DATASETS"
    / "03_AUDITED"
)

REPORT_DIR.mkdir(parents=True, exist_ok=True)
AUDITED_DIR.mkdir(parents=True, exist_ok=True)


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
# SOURCE ROOTS
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
# EXISTING LEAKAGE MANIFEST
# ============================================================

LEAKAGE_FILE = (
    REPORT_DIR
    / "leakage_resolution_v1.csv"
)


# ============================================================
# HELPERS
# ============================================================

def is_image(path):
    return (
        path.is_file()
        and path.suffix.lower() in IMAGE_EXTENSIONS
    )


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


def collect_plantdoc():

    records = []

    # IMPORTANT:
    # Only train and test are valid PlantDoc ML sources.
    # Root-level documentation images are excluded.

    for split in ["train", "test"]:

        split_root = PLANTDOC_ROOT / split

        if not split_root.exists():
            continue

        for path in split_root.rglob("*"):

            if not is_image(path):
                continue

            records.append({
                "dataset": "PlantDoc",
                "source_split": split.upper(),
                "class": path.parent.name,
                "path": str(path)
            })

    return records


def collect_plantvillage():

    records = []

    for path in PLANTVILLAGE_ROOT.rglob("*"):

        if not is_image(path):
            continue

        records.append({
            "dataset": "PlantVillage",
            "source_split": "SOURCE",
            "class": path.parent.name,
            "path": str(path)
        })

    return records


def collect_rice():

    records = []

    for path in RICE_ROOT.rglob("*"):

        if not is_image(path):
            continue

        records.append({
            "dataset": "RiceLeafDiseaseBD",
            "source_split": "SOURCE",
            "class": path.parent.name,
            "path": str(path)
        })

    return records


# ============================================================
# LOAD LEAKAGE DECISIONS
# ============================================================

print("=" * 75)
print("KRUSHI SAMRUDDHI ODISHA AI")
print("AUDITED DATASET MANIFEST v1")
print("=" * 75)

print("\n[1/4] Loading leakage decisions...")


if not LEAKAGE_FILE.exists():

    print("ERROR:")
    print(LEAKAGE_FILE)
    print("does not exist.")

    raise SystemExit(1)


with open(
    LEAKAGE_FILE,
    "r",
    encoding="utf-8-sig",
    newline=""
) as f:

    leakage_rows = list(
        csv.DictReader(f)
    )


excluded_paths = {}
manual_paths = set()


for row in leakage_rows:

    decision = row["decision"]

    path_a = row["path_a"]
    path_b = row["path_b"]

    if decision == "EXCLUDE_BOTH":

        excluded_paths[path_a] = (
            "EXCLUDE_BOTH",
            row["pair_id"],
            row["reason"]
        )

        excluded_paths[path_b] = (
            "EXCLUDE_BOTH",
            row["pair_id"],
            row["reason"]
        )

    elif decision == "EXCLUDE_TEST_COPY":

        # Determine which side is TEST.
        if row["split_a"] == "TEST":

            excluded_paths[path_a] = (
                "EXCLUDE_TEST_COPY",
                row["pair_id"],
                row["reason"]
            )

        elif row["split_b"] == "TEST":

            excluded_paths[path_b] = (
                "EXCLUDE_TEST_COPY",
                row["pair_id"],
                row["reason"]
            )

    elif decision == "MANUAL_REVIEW":

        manual_paths.add(path_a)
        manual_paths.add(path_b)


# ============================================================
# COLLECT VALID SOURCE IMAGES
# ============================================================

print("\n[2/4] Collecting source images...")


records = []

records.extend(
    collect_plantdoc()
)

records.extend(
    collect_plantvillage()
)

records.extend(
    collect_rice()
)


print(
    f"Candidate images collected: "
    f"{len(records):,}"
)


# ============================================================
# BUILD MANIFEST
# ============================================================

print("\n[3/4] Building audit manifest...")


manifest = []

for item in records:

    path = item["path"]

    sha = sha256_file(
        Path(path)
    )

    # --------------------------------------------------------
    # Leakage exclusion
    # --------------------------------------------------------

    if path in excluded_paths:

        decision, pair_id, reason = (
            excluded_paths[path]
        )

        final_status = "EXCLUDE"

        audit_reason = (
            f"{decision}; "
            f"leakage pair {pair_id}; "
            f"{reason}"
        )

    # --------------------------------------------------------
    # Manual review
    # --------------------------------------------------------

    elif path in manual_paths:

        final_status = "MANUAL_REVIEW"

        audit_reason = (
            "Near-duplicate train/test candidate; "
            "visual review required before final dataset."
        )

    # --------------------------------------------------------
    # Normal accepted image
    # --------------------------------------------------------

    else:

        final_status = "ACCEPT"

        audit_reason = (
            "Valid image within defined ML candidate scope."
        )


    manifest.append({
        "dataset": item["dataset"],
        "source_split": item["source_split"],
        "original_class": item["class"],
        "source_path": path,
        "sha256": sha,
        "status": final_status,
        "audit_reason": audit_reason
    })


# ============================================================
# WRITE MANIFEST
# ============================================================

MANIFEST_FILE = (
    AUDITED_DIR
    / "plant_health_audit_manifest_v1.csv"
)


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
    MANIFEST_FILE,
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


# ============================================================
# SUMMARY
# ============================================================

from collections import Counter


status_counts = Counter(
    row["status"]
    for row in manifest
)

dataset_counts = Counter(
    row["dataset"]
    for row in manifest
)


SUMMARY_FILE = (
    AUDITED_DIR
    / "plant_health_audit_summary_v1.txt"
)


with open(
    SUMMARY_FILE,
    "w",
    encoding="utf-8"
) as f:

    f.write("=" * 75 + "\n")
    f.write(
        "KRUSHI SAMRUDDHI ODISHA AI\n"
    )
    f.write(
        "PLANT HEALTH AUDIT SUMMARY v1\n"
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

    f.write("\n")
    f.write("IMPORTANT\n")
    f.write("-" * 75 + "\n")

    f.write(
        "The external source datasets were not modified.\n"
    )

    f.write(
        "The audit manifest records decisions only.\n"
    )

    f.write(
        "EXCLUDE entries will not be copied into the final "
        "processed dataset.\n"
    )

    f.write(
        "MANUAL_REVIEW entries require review before final "
        "dataset construction.\n"
    )


# ============================================================
# FINAL OUTPUT
# ============================================================

print("\n[4/4] Audit manifest created.")

print("\n" + "=" * 75)
print("AUDIT MANIFEST COMPLETE")
print("=" * 75)

print(
    f"\nTotal candidate images: "
    f"{len(manifest):,}"
)

print("\nStatus:")

for status, count in sorted(
    status_counts.items()
):

    print(
        f"  {status}: {count:,}"
    )

print("\nDataset counts:")

for dataset, count in sorted(
    dataset_counts.items()
):

    print(
        f"  {dataset}: {count:,}"
    )

print("\nFiles created:")

print(MANIFEST_FILE)

print(SUMMARY_FILE)

print("\nNO SOURCE IMAGES WERE MODIFIED.")

print("\nNEXT:")
print(
    "Review the audit summary before constructing "
    "the processed dataset."
)