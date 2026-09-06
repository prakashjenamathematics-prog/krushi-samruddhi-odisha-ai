from flask import Blueprint, jsonify
from pathlib import Path
import json

import shapefile
from pyproj import CRS, Transformer


gis_bp = Blueprint(
    "gis_bp",
    __name__,
    url_prefix="/api/gis"
)


# ============================================================
# Survey of India GIS file
# ============================================================

GIS_FILE = Path(
    r"C:\MINI_PROJECT\DATASETS\GIS\ODISHA\ODISHA.shp"
)


# ============================================================
# Coordinate system
# ============================================================

SOURCE_CRS = CRS.from_proj4(
    "+proj=lcc "
    "+lat_1=12.472944 "
    "+lat_2=35.172806 "
    "+lat_0=24 "
    "+lon_0=80 "
    "+x_0=4000000 "
    "+y_0=4000000 "
    "+datum=WGS84 "
    "+units=m "
    "+no_defs"
)

TARGET_CRS = CRS.from_epsg(4326)

TRANSFORMER = Transformer.from_crs(
    SOURCE_CRS,
    TARGET_CRS,
    always_xy=True
)


# ============================================================
# Shapefile field indexes
# ============================================================

reader = None
field_index = {}


def initialize_gis():

    global reader
    global field_index

    if not GIS_FILE.exists():
        raise FileNotFoundError(
            f"GIS shapefile not found: {GIS_FILE}"
        )

    reader = shapefile.Reader(
        str(GIS_FILE)
    )

    fields = [
        field[0]
        for field in reader.fields[1:]
    ]

    field_index = {
        name: index
        for index, name in enumerate(fields)
    }


initialize_gis()


# ============================================================
# Helpers
# ============================================================

def clean(value):

    if value is None:
        return ""

    return str(value).strip()


def convert_point(point):

    longitude, latitude = TRANSFORMER.transform(
        point[0],
        point[1]
    )

    return [
        round(longitude, 7),
        round(latitude, 7)
    ]


def shape_to_geojson(shape):

    """
    Convert a Polygon/PolygonZ shapefile geometry
    into GeoJSON coordinates.

    The Survey of India village data may contain
    multiple polygon parts.
    """

    points = shape.points
    parts = list(shape.parts)

    if not points:
        return None


    # --------------------------------------------------------
    # Split geometry into individual rings
    # --------------------------------------------------------

    rings = []

    for i, start in enumerate(parts):

        if i + 1 < len(parts):

            end = parts[i + 1]

        else:

            end = len(points)

        ring = points[start:end]

        if len(ring) >= 3:

            converted_ring = [
                convert_point(point)
                for point in ring
            ]

            # Ensure ring is closed
            if converted_ring[0] != converted_ring[-1]:

                converted_ring.append(
                    converted_ring[0]
                )

            rings.append(
                converted_ring
            )


    if not rings:
        return None


    # --------------------------------------------------------
    # Most village records are polygons.
    # We return MultiPolygon when multiple
    # polygon parts are present.
    # --------------------------------------------------------

    if len(rings) == 1:

        return {
            "type": "Polygon",
            "coordinates": [
                rings[0]
            ]
        }


    return {
        "type": "MultiPolygon",
        "coordinates": [
            [
                ring
            ]
            for ring in rings
        ]
    }


# ============================================================
# Village GIS API
# ============================================================

@gis_bp.route(
    "/village/<int:lgd_code>",
    methods=["GET"]
)
def get_village_geometry(lgd_code):

    try:

        target_lgd = str(lgd_code)

        for record, shape in zip(
            reader.iterRecords(),
            reader.iterShapes()
        ):

            gis_lgd = clean(
                record[
                    field_index["Vill_LGD"]
                ]
            )

            if gis_lgd != target_lgd:
                continue


            village_name = clean(
                record[
                    field_index["Vill_name"]
                ]
            )

            village_category = clean(
                record[
                    field_index["Vill_Cat"]
                ]
            )


            geometry = shape_to_geojson(
                shape
            )


            if geometry is None:

                return jsonify({
                    "status": "error",
                    "message": "Village geometry is empty",
                    "lgd_code": lgd_code
                }), 404


            return jsonify({
                "status": "success",

                "data": {

                    "lgd_code": lgd_code,

                    "village_name_gis":
                        village_name,

                    "village_category":
                        village_category,

                    "geometry":
                        geometry
                }
            })


        return jsonify({
            "status": "not_found",
            "message":
                "No GIS boundary found for this village",
            "lgd_code": lgd_code
        }), 404


    except Exception as error:

        return jsonify({

            "status": "error",

            "message":
                "Failed to retrieve village GIS boundary",

            "error":
                str(error)

        }), 500