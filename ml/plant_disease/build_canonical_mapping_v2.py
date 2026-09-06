from pathlib import Path
import csv

BASE = Path(r"C:\MINI_PROJECT")

METADATA_DIR = BASE / "DATASETS" / "08_METADATA"
REPORT_DIR = BASE / "DATASETS" / "09_REPORTS"

METADATA_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT = METADATA_DIR / "canonical_class_dictionary_v2.csv"


# ============================================================
# CANONICAL CLASS MAPPING
# ============================================================
#
# IMPORTANT:
# - Do not infer unspecified PlantDoc labels as healthy.
# - Do not merge classes solely because names look similar.
# - Only mappings already validated in the project are used.
# - Rice disease classes remain separate.
# ============================================================

mapping = [

    # ---------------- APPLE ----------------
    ("PlantDoc", "Apple Scab Leaf", "Apple", "Apple Scab"),
    ("PlantDoc", "Apple rust leaf", "Apple", "Apple Rust"),

    ("PlantVillage", "Apple___Apple_scab", "Apple", "Apple Scab"),
    ("PlantVillage", "Apple___Black_rot", "Apple", "Black Rot"),
    ("PlantVillage", "Apple___Cedar_apple_rust", "Apple", "Cedar Apple Rust"),
    ("PlantVillage", "Apple___healthy", "Apple", "Healthy"),

    # ----------- BELL PEPPER ---------------
    ("PlantDoc", "Bell_pepper leaf spot", "Bell Pepper", "Leaf Spot"),

    ("PlantVillage",
     "Pepper,_bell___Bacterial_spot",
     "Bell Pepper",
     "Bacterial Spot"),

    ("PlantVillage",
     "Pepper,_bell___healthy",
     "Bell Pepper",
     "Healthy"),

    # -------------- BLUEBERRY --------------
    ("PlantVillage",
     "Blueberry___healthy",
     "Blueberry",
     "Healthy"),

    # ---------------- CHERRY ----------------
    ("PlantVillage",
     "Cherry_(including_sour)___Powdery_mildew",
     "Cherry",
     "Powdery Mildew"),

    ("PlantVillage",
     "Cherry_(including_sour)___healthy",
     "Cherry",
     "Healthy"),

    # ---------------- CORN ------------------
    ("PlantDoc",
     "Corn Gray leaf spot",
     "Corn",
     "Gray Leaf Spot"),

    ("PlantDoc",
     "Corn leaf blight",
     "Corn",
     "Leaf Blight"),

    ("PlantDoc",
     "Corn rust leaf",
     "Corn",
     "Rust"),

    ("PlantVillage",
     "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot",
     "Corn",
     "Cercospora/Gray Leaf Spot"),

    ("PlantVillage",
     "Corn_(maize)___Common_rust_",
     "Corn",
     "Common Rust"),

    ("PlantVillage",
     "Corn_(maize)___Northern_Leaf_Blight",
     "Corn",
     "Northern Leaf Blight"),

    ("PlantVillage",
     "Corn_(maize)___healthy",
     "Corn",
     "Healthy"),

    # ---------------- GRAPE -----------------
    ("PlantDoc",
     "grape leaf black rot",
     "Grape",
     "Black Rot"),

    ("PlantVillage",
     "Grape___Black_rot",
     "Grape",
     "Black Rot"),

    ("PlantVillage",
     "Grape___Esca_(Black_Measles)",
     "Grape",
     "Esca (Black Measles)"),

    ("PlantVillage",
     "Grape___healthy",
     "Grape",
     "Healthy"),

    ("PlantVillage",
     "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)",
     "Grape",
     "Leaf Blight"),

    # ---------------- ORANGE ----------------
    ("PlantVillage",
     "Orange___Haunglongbing_(Citrus_greening)",
     "Orange",
     "Huanglongbing (Citrus Greening)"),

    # ---------------- PEACH -----------------
    ("PlantVillage",
     "Peach___Bacterial_spot",
     "Peach",
     "Bacterial Spot"),

    ("PlantVillage",
     "Peach___healthy",
     "Peach",
     "Healthy"),

    # ---------------- POTATO ----------------
    ("PlantDoc",
     "Potato leaf early blight",
     "Potato",
     "Early Blight"),

    ("PlantDoc",
     "Potato leaf late blight",
     "Potato",
     "Late Blight"),

    ("PlantVillage",
     "Potato___Early_blight",
     "Potato",
     "Early Blight"),

    ("PlantVillage",
     "Potato___Late_blight",
     "Potato",
     "Late Blight"),

    ("PlantVillage",
     "Potato___healthy",
     "Potato",
     "Healthy"),

    # --------------- RASPBERRY --------------
    ("PlantVillage",
     "Raspberry___healthy",
     "Raspberry",
     "Healthy"),

    # ---------------- RICE ------------------
    ("RiceLeafDiseaseBD",
     "Blast",
     "Rice",
     "Blast"),

    ("RiceLeafDiseaseBD",
     "Brown spot",
     "Rice",
     "Brown Spot"),

    ("RiceLeafDiseaseBD",
     "Healthy",
     "Rice",
     "Healthy"),

    ("RiceLeafDiseaseBD",
     "Leaf smut",
     "Rice",
     "Leaf Smut"),

    ("RiceLeafDiseaseBD",
     "Rice Tungro",
     "Rice",
     "Rice Tungro"),

    ("RiceLeafDiseaseBD",
     "Sheath blight",
     "Rice",
     "Sheath Blight"),

    # --------------- SOYBEAN ----------------
    ("PlantVillage",
     "Soybean___healthy",
     "Soybean",
     "Healthy"),

    # ---------------- SQUASH ----------------
    ("PlantDoc",
     "Squash Powdery mildew leaf",
     "Squash",
     "Powdery Mildew"),

    ("PlantVillage",
     "Squash___Powdery_mildew",
     "Squash",
     "Powdery Mildew"),

    # ------------- STRAWBERRY ---------------
    ("PlantVillage",
     "Strawberry___Leaf_scorch",
     "Strawberry",
     "Leaf Scorch"),

    ("PlantVillage",
     "Strawberry___healthy",
     "Strawberry",
     "Healthy"),

    # ---------------- TOMATO ----------------
    ("PlantDoc",
     "Tomato Early blight leaf",
     "Tomato",
     "Early Blight"),

    ("PlantDoc",
     "Tomato leaf bacterial spot",
     "Tomato",
     "Bacterial Spot"),

    ("PlantDoc",
     "Tomato leaf late blight",
     "Tomato",
     "Late Blight"),

    ("PlantDoc",
     "Tomato mold leaf",
     "Tomato",
     "Leaf Mold"),

    ("PlantDoc",
     "Tomato Septoria leaf spot",
     "Tomato",
     "Septoria Leaf Spot"),

    ("PlantDoc",
     "Tomato leaf mosaic virus",
     "Tomato",
     "Tomato Mosaic Virus"),

    ("PlantDoc",
     "Tomato two spotted spider mites leaf",
     "Tomato",
     "Two-Spotted Spider Mite"),

    ("PlantDoc",
     "Tomato leaf yellow virus",
     "Tomato",
     "Tomato Yellow Leaf Virus"),

    ("PlantVillage",
     "Tomato___Bacterial_spot",
     "Tomato",
     "Bacterial Spot"),

    ("PlantVillage",
     "Tomato___Early_blight",
     "Tomato",
     "Early Blight"),

    ("PlantVillage",
     "Tomato___Late_blight",
     "Tomato",
     "Late Blight"),

    ("PlantVillage",
     "Tomato___Leaf_Mold",
     "Tomato",
     "Leaf Mold"),

    ("PlantVillage",
     "Tomato___Septoria_leaf_spot",
     "Tomato",
     "Septoria Leaf Spot"),

    ("PlantVillage",
     "Tomato___Target_Spot",
     "Tomato",
     "Target Spot"),

    ("PlantVillage",
     "Tomato___Tomato_mosaic_virus",
     "Tomato",
     "Tomato Mosaic Virus"),

    ("PlantVillage",
     "Tomato___Tomato_Yellow_Leaf_Curl_Virus",
     "Tomato",
     "Tomato Yellow Leaf Curl Virus"),

    ("PlantVillage",
     "Tomato___Spider_mites Two-spotted_spider_mite",
     "Tomato",
     "Two-Spotted Spider Mite"),

    ("PlantVillage",
     "Tomato___healthy",
     "Tomato",
     "Healthy"),
]


fields = [
    "dataset",
    "original_class",
    "crop",
    "canonical_disease"
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

    for dataset, original_class, crop, disease in mapping:

        writer.writerow({
            "dataset": dataset,
            "original_class": original_class,
            "crop": crop,
            "canonical_disease": disease
        })


# ============================================================
# SUMMARY
# ============================================================

canonical = sorted(
    set(
        (
            crop,
            disease
        )
        for _, _, crop, disease in mapping
    )
)

source_classes = len(mapping)

print("=" * 75)
print("KRUSHI SAMRUDDHI ODISHA AI")
print("CANONICAL CLASS DICTIONARY v2")
print("=" * 75)

print()
print(f"Mapped source classes: {source_classes}")
print(
    f"Unique canonical classes represented: "
    f"{len(canonical)}"
)

print()
print("Canonical classes:")
print("-" * 75)

for crop, disease in canonical:

    print(
        f"{crop} | {disease}"
    )

print()
print("Dictionary created:")
print(OUTPUT)

print()
print("IMPORTANT:")
print("Unspecified PlantDoc classes remain excluded.")
print("No source images were modified.")