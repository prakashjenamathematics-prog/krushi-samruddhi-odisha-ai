from flask import Blueprint, jsonify
from sqlalchemy import text

from database import engine


# ============================================================
# GRAM PANCHAYAT BLUEPRINT
# ============================================================

gp_bp = Blueprint(
    "gp_bp",
    __name__,
    url_prefix="/api"
)


# ============================================================
# GET GRAM PANCHAYATS BY BLOCK
# ============================================================

@gp_bp.route("/gps/block/<int:block_id>", methods=["GET"])
def get_gps_by_block(block_id):

    try:

        query = text("""
            SELECT
                gp_id,
                block_id,
                gp_name_en,
                gp_name_or
            FROM gram_panchayats
            WHERE block_id = :block_id
            ORDER BY gp_name_en
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
            "message": "Failed to fetch Gram Panchayats",
            "error": str(error)
        }), 500