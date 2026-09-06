from sqlalchemy import create_engine

from config import Config


# ============================================================
# DATABASE ENGINE
# ============================================================

engine = create_engine(
    Config.SQLALCHEMY_DATABASE_URI,
    pool_pre_ping=True
)