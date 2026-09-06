from pathlib import Path
import csv


BASE = Path(r"C:\MINI_PROJECT")

OUTPUT = (
    BASE
    / "DATASETS"
    / "08_METADATA"
    / "class_mapping.csv"
)


# ============================================================
# KRUSHI SAMRUDDHI ODISHA AI
# CANONICAL CLASS MAPPING v1
# ============================================================


MAPPINGS = []


def add(
    dataset,
    original_class,
    crop,
    disease,
    health_status,
    canonical_class,
    confidence,
    reason
):
    MAPPINGS.append([
        dataset,
        original_class,
        crop,
        disease,
        health_status,
        canonical_class,
        confidence,
        reason
    ])


# ============================================================
# PLANTDOC
# ============================================================

plantdoc = {
    "Apple Scab Leaf": ("Apple", "Apple Scab", "Diseased"),
    "Apple rust leaf": ("Apple", "Apple Rust", "Diseased"),
    "Apple leaf": ("Apple", "Unspecified", "Unspecified"),

    "Bell_pepper leaf": ("Bell Pepper", "Unspecified", "Unspecified"),
    "Bell_pepper leaf spot": ("Bell Pepper", "Leaf Spot", "Diseased"),

    "Blueberry leaf": ("Blueberry", "Unspecified", "Unspecified"),
    "Cherry leaf": ("Cherry", "Unspecified", "Unspecified"),

    "Corn Gray leaf spot": ("Corn", "Gray Leaf Spot", "Diseased"),
    "Corn leaf blight": ("Corn", "Leaf Blight", "Diseased"),
    "Corn rust leaf": ("Corn", "Rust", "Diseased"),

    "Peach leaf": ("Peach", "Unspecified", "Unspecified"),

    "Potato leaf early blight": (
        "Potato",
        "Early Blight",
        "Diseased"
    ),

    "Potato leaf late blight": (
        "Potato",
        "Late Blight",
        "Diseased"
    ),

    "Raspberry leaf": ("Raspberry", "Unspecified", "Unspecified"),
    "Soyabean leaf": ("Soybean", "Unspecified", "Unspecified"),

    "Squash Powdery mildew leaf": (
        "Squash",
        "Powdery Mildew",
        "Diseased"
    ),

    "Strawberry leaf": ("Strawberry", "Unspecified", "Unspecified"),

    "Tomato Early blight leaf": (
        "Tomato",
        "Early Blight",
        "Diseased"
    ),

    "Tomato Septoria leaf spot": (
        "Tomato",
        "Septoria Leaf Spot",
        "Diseased"
    ),

    "Tomato leaf": (
        "Tomato",
        "Unspecified",
        "Unspecified"
    ),

    "Tomato leaf bacterial spot": (
        "Tomato",
        "Bacterial Spot",
        "Diseased"
    ),

    "Tomato leaf late blight": (
        "Tomato",
        "Late Blight",
        "Diseased"
    ),

    "Tomato leaf mosaic virus": (
        "Tomato",
        "Tomato Mosaic Virus",
        "Diseased"
    ),

    "Tomato leaf yellow virus": (
        "Tomato",
        "Tomato Yellow Leaf Virus",
        "Diseased"
    ),

    "Tomato mold leaf": (
        "Tomato",
        "Leaf Mold",
        "Diseased"
    ),

    "Tomato two spotted spider mites leaf": (
        "Tomato",
        "Two-Spotted Spider Mite",
        "Diseased"
    ),

    "grape leaf": (
        "Grape",
        "Unspecified",
        "Unspecified"
    ),

    "grape leaf black rot": (
        "Grape",
        "Black Rot",
        "Diseased"
    ),
}


# ============================================================
# PLANTVILLAGE
# ============================================================

plantvillage = {
    "Apple___Apple_scab":
        ("Apple", "Apple Scab", "Diseased"),

    "Apple___Black_rot":
        ("Apple", "Black Rot", "Diseased"),

    "Apple___Cedar_apple_rust":
        ("Apple", "Cedar Apple Rust", "Diseased"),

    "Apple___healthy":
        ("Apple", "Healthy", "Healthy"),

    "Blueberry___healthy":
        ("Blueberry", "Healthy", "Healthy"),

    "Cherry_(including_sour)___Powdery_mildew":
        ("Cherry", "Powdery Mildew", "Diseased"),

    "Cherry_(including_sour)___healthy":
        ("Cherry", "Healthy", "Healthy"),

    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot":
        ("Corn", "Cercospora/Gray Leaf Spot", "Diseased"),

    "Corn_(maize)___Common_rust_":
        ("Corn", "Common Rust", "Diseased"),

    "Corn_(maize)___Northern_Leaf_Blight":
        ("Corn", "Northern Leaf Blight", "Diseased"),

    "Corn_(maize)___healthy":
        ("Corn", "Healthy", "Healthy"),

    "Grape___Black_rot":
        ("Grape", "Black Rot", "Diseased"),

    "Grape___Esca_(Black_Measles)":
        ("Grape", "Esca (Black Measles)", "Diseased"),

    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)":
        ("Grape", "Leaf Blight", "Diseased"),

    "Grape___healthy":
        ("Grape", "Healthy", "Healthy"),

    "Orange___Haunglongbing_(Citrus_greening)":
        ("Orange", "Huanglongbing (Citrus Greening)", "Diseased"),

    "Peach___Bacterial_spot":
        ("Peach", "Bacterial Spot", "Diseased"),

    "Peach___healthy":
        ("Peach", "Healthy", "Healthy"),

    "Pepper,_bell___Bacterial_spot":
        ("Bell Pepper", "Bacterial Spot", "Diseased"),

    "Pepper,_bell___healthy":
        ("Bell Pepper", "Healthy", "Healthy"),

    "Potato___Early_blight":
        ("Potato", "Early Blight", "Diseased"),

    "Potato___healthy":
        ("Potato", "Healthy", "Healthy"),

    "Potato___Late_blight":
        ("Potato", "Late Blight", "Diseased"),

    "Raspberry___healthy":
        ("Raspberry", "Healthy", "Healthy"),

    "Soybean___healthy":
        ("Soybean", "Healthy", "Healthy"),

    "Squash___Powdery_mildew":
        ("Squash", "Powdery Mildew", "Diseased"),

    "Strawberry___Leaf_scorch":
        ("Strawberry", "Leaf Scorch", "Diseased"),

    "Strawberry___healthy":
        ("Strawberry", "Healthy", "Healthy"),

    "Tomato___Bacterial_spot":
        ("Tomato", "Bacterial Spot", "Diseased"),

    "Tomato___Early_blight":
        ("Tomato", "Early Blight", "Diseased"),

    "Tomato___healthy":
        ("Tomato", "Healthy", "Healthy"),

    "Tomato___Late_blight":
        ("Tomato", "Late Blight", "Diseased"),

    "Tomato___Leaf_Mold":
        ("Tomato", "Leaf Mold", "Diseased"),

    "Tomato___Septoria_leaf_spot":
        ("Tomato", "Septoria Leaf Spot", "Diseased"),

    "Tomato___Spider_mites Two-spotted_spider_mite":
        ("Tomato", "Two-Spotted Spider Mite", "Diseased"),

    "Tomato___Target_Spot":
        ("Tomato", "Target Spot", "Diseased"),

    "Tomato___Tomato_mosaic_virus":
        ("Tomato", "Tomato Mosaic Virus", "Diseased"),

    "Tomato___Tomato_Yellow_Leaf_Curl_Virus":
        ("Tomato", "Tomato Yellow Leaf Curl Virus", "Diseased"),
}


# ============================================================
# RICELEAFDISEASEBD
# ============================================================

riceleaf = {
    "Blast":
        ("Rice", "Blast", "Diseased"),

    "Brown spot":
        ("Rice", "Brown Spot", "Diseased"),

    "Healthy":
        ("Rice", "Healthy", "Healthy"),

    "Leaf smut":
        ("Rice", "Leaf Smut", "Diseased"),

    "Rice Tungro":
        ("Rice", "Rice Tungro", "Diseased"),

    "Sheath blight":
        ("Rice", "Sheath Blight", "Diseased"),
}


# ============================================================
# CREATE ROWS
# ============================================================

for original, values in plantdoc.items():

    crop, disease, health = values

    canonical = (
        f"{crop} | {disease}"
        if disease != "Unspecified"
        else f"{crop} | Unspecified"
    )

    confidence = (
        "High"
        if disease != "Unspecified"
        else "Medium"
    )

    reason = (
        "Direct disease/crop interpretation from source label"
        if disease != "Unspecified"
        else
        "Source identifies plant but does not explicitly identify "
        "a disease or healthy condition"
    )

    add(
        "PlantDoc",
        original,
        crop,
        disease,
        health,
        canonical,
        confidence,
        reason
    )


for original, values in plantvillage.items():

    crop, disease, health = values

    canonical = f"{crop} | {disease}"

    add(
        "PlantVillage",
        original,
        crop,
        disease,
        health,
        canonical,
        "High",
        "Explicit crop/disease or healthy label in source class name"
    )


for original, values in riceleaf.items():

    crop, disease, health = values

    canonical = f"{crop} | {disease}"

    add(
        "RiceLeafDiseaseBD",
        original,
        crop,
        disease,
        health,
        canonical,
        "High",
        "Explicit original-image class label"
    )


# ============================================================
# WRITE CSV
# ============================================================

with open(
    OUTPUT,
    "w",
    newline="",
    encoding="utf-8-sig"
) as f:

    writer = csv.writer(f)

    writer.writerow([
        "dataset",
        "original_class",
        "crop",
        "disease",
        "health_status",
        "canonical_class",
        "mapping_confidence",
        "mapping_reason"
    ])

    writer.writerows(MAPPINGS)


print("=" * 70)
print("KRUSHI SAMRUDDHI ODISHA AI")
print("CANONICAL CLASS MAPPING v1")
print("=" * 70)

print(f"\nRows created: {len(MAPPINGS)}")
print(f"Output: {OUTPUT}")

print("\nMapping summary:")

for dataset in [
    "PlantDoc",
    "PlantVillage",
    "RiceLeafDiseaseBD"
]:

    count = sum(
        1
        for row in MAPPINGS
        if row[0] == dataset
    )

    print(f"{dataset}: {count} classes")

print("\nNOTE:")
print("This is Mapping v1.")
print("It is a taxonomy proposal, not the final ML dataset.")
print("Duplicate and leakage analysis must be completed before training.")