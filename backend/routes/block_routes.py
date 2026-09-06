from flask import Blueprint, jsonify
from sqlalchemy import text

from database import engine


# ============================================================
# BLOCK BLUEPRINT
# ============================================================

block_bp = Blueprint(
    "block_bp",
    __name__,
    url_prefix="/api"
)


# ============================================================
# GET BLOCKS BY DISTRICT
# ============================================================

@block_bp.route("/blocks/district/<int:district_id>", methods=["GET"])
def get_blocks_by_district(district_id):

    try:

        query = text("""
            SELECT
                block_id,
                district_id,
                block_name_en,
                block_name_or,
                lgd_block_code
            FROM blocks
            WHERE district_id = :district_id
            ORDER BY block_name_en
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
            "message": "Failed to fetch blocks",
            "error": str(error)
        }), 500