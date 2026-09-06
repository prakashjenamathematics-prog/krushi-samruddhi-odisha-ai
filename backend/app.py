from flask import Flask, jsonify
from flask_cors import CORS
from sqlalchemy import text

from config import Config
from database import engine

from routes.district_routes import district_bp
from routes.block_routes import block_bp
from routes.village_routes import village_bp
from routes.gp_routes import gp_bp
from routes.gis_routes import gis_bp


# ============================================================
# APPLICATION INITIALIZATION
# ============================================================

app = Flask(__name__)

# ============================================================
# UNICODE / ODIA JSON SUPPORT
# ============================================================

app.json.ensure_ascii = False

CORS(app)


# ============================================================
# APPLICATION CONFIGURATION
# ============================================================

app.config.from_object(Config)


# ============================================================
# REGISTER BLUEPRINTS
# ============================================================

app.register_blueprint(district_bp)
app.register_blueprint(block_bp)
app.register_blueprint(village_bp)
app.register_blueprint(gp_bp)
app.register_blueprint(gis_bp)


# ============================================================
# HOME API  
# ============================================================

@app.route("/")
def home():

    return jsonify({
        "status": "success",
        "message": "Krushi Samruddhi Odisha AI Backend is running"
    })


# ============================================================
# HEALTH CHECK API
# ============================================================

@app.route("/api/health")
def health():

    return jsonify({
        "status": "healthy",
        "service": "Krushi Samruddhi Odisha AI API"
    })


# ============================================================
# DATABASE TEST API
# ============================================================

@app.route("/api/database-test")
def database_test():

    try:

        with engine.connect() as connection:

            result = connection.execute(
                text(
                    "SELECT DATABASE() AS database_name"
                )
            )

            row = result.mappings().first()

        return jsonify({
            "status": "success",
            "message": "MySQL database connection successful",
            "database": row["database_name"]
        })

    except Exception as error:

        return jsonify({
            "status": "error",
            "message": "MySQL database connection failed",
            "error": str(error)
        }), 500


# ============================================================
# SERVER START
# ============================================================

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )