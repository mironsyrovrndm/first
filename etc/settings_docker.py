# Docker's override config

DEBUG = True

ADMIN_PASSWORD = "123123"

# === SQLAlchemy ===
# SQLALCHEMY_DATABASE_URI = "sqlite:////data/app.db"
SQLALCHEMY_DATABASE_URI = "postgresql://stas:stas@stas-db:5432/stas"

UPLOAD_FOLDER = "/uploads"
