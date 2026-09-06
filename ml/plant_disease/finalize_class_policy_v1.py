from pathlib import Path
import csv


BASE = Path(r"C:\MINI_PROJECT")

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

METADATA_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)


OUTPUT = (
    METADATA_DIR
    / "plant_health_class_policy_v1.csv"
)


rows = [
    {
        "dataset": "PlantDoc",
        "original_class": "Apple leaf",
        "crop": "Apple",
        "disease": "",
        "health_status": "",
        "canonical_class": "",
        "training_policy": "EXCLUDE_UNSPECIFIED",
        "reason": "Crop/leaf identified but disease or healthy status is unspecified."
    },
    {
        "dataset": "PlantDoc",
        "original_class": "Bell_pepper leaf",
        "crop": "Bell Pepper",
        "disease": "",
        "health_status": "",
        "canonical_class": "",
        "training_policy": "EXCLUDE_UNSPECIFIED",
        "reason": "Crop/leaf identified but disease or healthy status is unspecified."
    },
    {
        "dataset": "PlantDoc",
        "original_class": "Blueberry leaf",
        "crop": "Blueberry",
        "disease": "",
        "health_status": "",
        "canonical_class": "",
        "training_policy": "EXCLUDE_UNSPECIFIED",
        "reason": "Crop/leaf identified but disease or healthy status is unspecified."
    },
    {
        "dataset": "PlantDoc",
        "original_class": "Cherry leaf",
        "crop": "Cherry",
        "disease": "",
        "health_status": "",
        "canonical_class": "",
        "training_policy": "EXCLUDE_UNSPECIFIED",
        "reason": "Crop/leaf identified but disease or healthy status is unspecified."
    },
    {
        "dataset": "PlantDoc",
        "original_class": "Peach leaf",
        "crop": "Peach",
        "disease": "",
        "health_status": "",
        "canonical_class": "",
        "training_policy": "EXCLUDE_UNSPECIFIED",
        "reason": "Crop/leaf identified but disease or healthy status is unspecified."
    },
    {
        "dataset": "PlantDoc",
        "original_class": "Raspberry leaf",
        "crop": "Raspberry",
        "disease": "",
        "health_status": "",
        "canonical_class": "",
        "training_policy": "EXCLUDE_UNSPECIFIED",
        "reason": "Crop/leaf identified but disease or healthy status is unspecified."
    },
    {
        "dataset": "PlantDoc",
        "original_class": "Soyabean leaf",
        "crop": "Soybean",
        "disease": "",
        "health_status": "",
        "canonical_class": "",
        "training_policy": "EXCLUDE_UNSPECIFIED",
        "reason": "Crop/leaf identified but disease or healthy status is unspecified."
    },
    {
        "dataset": "PlantDoc",
        "original_class": "Strawberry leaf",
        "crop": "Strawberry",
        "disease": "",
        "health_status": "",
        "canonical_class": "",
        "training_policy": "EXCLUDE_UNSPECIFIED",
        "reason": "Crop/leaf identified but disease or healthy status is unspecified."
    },
    {
        "dataset": "PlantDoc",
        "original_class": "Tomato leaf",
        "crop": "Tomato",
        "disease": "",
        "health_status": "",
        "canonical_class": "",
        "training_policy": "EXCLUDE_UNSPECIFIED",
        "reason": "Crop/leaf identified but disease or healthy status is unspecified."
    },
    {
        "dataset": "PlantDoc",
        "original_class": "grape leaf",
        "crop": "Grape",
        "disease": "",
        "health_status": "",
        "canonical_class": "",
        "training_policy": "EXCLUDE_UNSPECIFIED",
        "reason": "Crop/leaf identified but disease or healthy status is unspecified."
    }
]


fields = [
    "dataset",
    "original_class",
    "crop",
    "disease",
    "health_status",
    "canonical_class",
    "training_policy",
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
    writer.writerows(rows)


print("=" * 75)
print("KRUSHI SAMRUDDHI ODISHA AI")
print("CLASS POLICY v1")
print("=" * 75)

print()
print("Unspecified PlantDoc classes: 10")
print("Policy: EXCLUDE_UNSPECIFIED")
print("Reason: insufficient disease/health label")
print()
print("Policy file:")
print(OUTPUT)

print()
print("IMPORTANT:")
print("No source images were modified.")
print("No source images were deleted.")