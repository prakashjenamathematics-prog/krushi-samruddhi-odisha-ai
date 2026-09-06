from flask import Blueprint, jsonify
from sqlalchemy import text

from database import engine


# ============================================================
# DISTRICT BLUEPRINT
# ============================================================

district_bp = Blueprint(
    "district_bp",
    __name__,
    url_prefix="/api"
)


# ============================================================
# GET ALL DISTRICTS
# ============================================================

@district_bp.route("/districts", methods=["GET"])
def get_districts():

    try:

        query = text("""
            SELECT
                district_id,
                district_name_en,
                district_name_or,
                created_at
            FROM districts
            ORDER BY district_name_en
        """)

        with engine.connect() as connection:

            rows = connection.execute(
                query
            ).mappings().all()

        return jsonify({
            "status": "success",
            "count": len(rows),
            "data": [dict(row) for row in rows]
        })

    except Exception as error:

        return jsonify({
            "status": "error",
            "message": "Failed to fetch districts",
            "error": str(error)
        }), 500