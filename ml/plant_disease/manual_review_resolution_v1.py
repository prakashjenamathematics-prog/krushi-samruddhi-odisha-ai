from pathlib import Path
import csv


BASE = Path(r"C:\MINI_PROJECT")

REPORT_DIR = (
    BASE
    / "DATASETS"
    / "09_REPORTS"
)

REPORT_DIR.mkdir(parents=True, exist_ok=True)


OUTPUT = (
    REPORT_DIR
    / "manual_review_resolution_v1.csv"
)


rows = [
    {
        "pair_id": "11",
        "dataset": "PlantDoc",
        "crop": "Tomato",
        "class": "Tomato leaf bacterial spot",
        "train_file": r"C:\MINI_PROJECT\DATASETS\01_EXTERNAL_DATA\01_PLANT_HEALTH\PlantDoc\EXTRACTED\PlantDoc-Dataset-master\train\Tomato leaf bacterial spot\bacterial-canker3x2400-2ia1kgd.jpg",
        "test_file": r"C:\MINI_PROJECT\DATASETS\01_EXTERNAL_DATA\01_PLANT_HEALTH\PlantDoc\EXTRACTED\PlantDoc-Dataset-master\test\Tomato leaf bacterial spot\07.17.18-Common_Tomato_Diseases_Canker-258x300.jpg",
        "hamming_distance": "3",
        "visual_result": "Same underlying image; resized/re-encoded representation.",
        "decision": "EXCLUDE_TEST_COPY",
        "reason": "Manual visual review confirmed that the TRAIN and TEST files depict the same underlying image. Training copy retained; test copy excluded."
    },
    {
        "pair_id": "13",
        "dataset": "PlantDoc",
        "crop": "Tomato",
        "class": "Tomato leaf late blight",
        "train_file": r"C:\MINI_PROJECT\DATASETS\01_EXTERNAL_DATA\01_PLANT_HEALTH\PlantDoc\EXTRACTED\PlantDoc-Dataset-master\train\Tomato leaf late blight\late_blight1.jpg",
        "test_file": r"C:\MINI_PROJECT\DATASETS\01_EXTERNAL_DATA\01_PLANT_HEALTH\PlantDoc\EXTRACTED\PlantDoc-Dataset-master\test\Tomato leaf late blight\18c.jpg",
        "hamming_distance": "0",
        "visual_result": "Same underlying image; resized/re-encoded representation.",
        "decision": "EXCLUDE_TEST_COPY",
        "reason": "Manual visual review confirmed that the TRAIN and TEST files depict the same underlying image. Training copy retained; test copy excluded."
    }
]


fields = [
    "pair_id",
    "dataset",
    "crop",
    "class",
    "train_file",
    "test_file",
    "hamming_distance",
    "visual_result",
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
    writer.writerows(rows)


print("=" * 75)
print("KRUSHI SAMRUDDHI ODISHA AI")
print("MANUAL NEAR-DUPLICATE RESOLUTION v1")
print("=" * 75)

print()
print("Reviewed pairs: 2")
print("Pair 11: EXCLUDE_TEST_COPY")
print("Pair 13: EXCLUDE_TEST_COPY")

print()
print("Report created:")
print(OUTPUT)

print()
print("NO SOURCE IMAGES WERE MODIFIED.")