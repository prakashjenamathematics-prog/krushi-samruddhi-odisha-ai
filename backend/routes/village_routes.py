from flask import Blueprint, jsonify
from sqlalchemy import text

from database import engine


# ============================================================
# VILLAGE BLUEPRINT
# ============================================================

village_bp = Blueprint(
    "village_bp",
    __name__,
    url_prefix="/api"
)


# ============================================================
# GET VILLAGES BY GRAM PANCHAYAT
# ============================================================

@village_bp.route("/villages/gp/<int:gp_id>", methods=["GET"])
def get_villages_by_gp(gp_id):

    try:

        query = text("""
            SELECT
                village_id,
                gp_id,
                village_name_en,
                village_name_or,
                lgd_code,
                census_code,
                latitude,
                longitude,
                created_at
            FROM villages
            WHERE gp_id = :gp_id
            ORDER BY village_name_en
        """)

        with engine.connect() as connection:

            rows = connection.execute(
                query,
                {
                    "gp_id": gp_id
                }
            ).mappings().all()

        return jsonify({
            "status": "success",
            "gp_id": gp_id,
            "count": len(rows),
            "data": [dict(row) for row in rows]
        })

    except Exception as error:

        return jsonify({
            "status": "error",
            "message": "Failed to fetch villages",
            "error": str(error)
        }), 500


# ============================================================
# GET VILLAGES BY BLOCK
# ============================================================

@village_bp.route("/villages/block/<int:block_id>", methods=["GET"])
def get_villages_by_block(block_id):

    try:

        query = text("""
            SELECT
                v.village_id,
                v.gp_id,
                v.village_name_en,
                v.village_name_or,
                v.lgd_code,
                v.census_code,
                v.latitude,
                v.longitude,
                v.created_at
            FROM villages v
            INNER JOIN gram_panchayats gp
                ON v.gp_id = gp.gp_id
            WHERE gp.block_id = :block_id
            ORDER BY v.village_name_en
        """)

        with engine.connect() as connection:

            rows = connection.execute(
                query,
                {
                    "block_id": block_id
                }
            ).mappings().all()

        return jsonify({
            "status": "success",
            "block_id": block_id,
            "count": len(rows),
            "data": [dict(row) for row in rows]
        })

    except Exception as error:

        return jsonify({
            "status": "error",
            "message": "Failed to fetch villages",
            "error": str(error)
        }), 500


# ============================================================
# GET VILLAGES BY DISTRICT
# ============================================================

@village_bp.route("/villages/district/<int:district_id>", methods=["GET"])
def get_villages_by_district(district_id):

    try:

        query = text("""
            SELECT
                v.village_id,
                v.gp_id,
                v.village_name_en,
                v.village_name_or,
                v.lgd_code,
                v.census_code,
                v.latitude,
                v.longitude,
                v.created_at
            FROM villages v
            INNER JOIN gram_panchayats gp
                ON v.gp_id = gp.gp_id
            INNER JOIN blocks b
                ON gp.block_id = b.block_id
            WHERE b.district_id = :district_id
            ORDER BY v.village_name_en
        """)

        with engine.connect() as connection:

            rows = connection.execute(
                query,
                {
                    "district_id": district_id
                }
            ).mappings().all()

        return jsonify({
            "status": "success",
            "district_id": district_id,
            "count": len(rows),
            "data": [dict(row) for row in rows]
        })

    except Exception as error:

        return jsonify({
            "status": "error",
            "message": "Failed to fetch villages",
            "error": str(error)
        }), 500