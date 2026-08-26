import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Sur Render, la variable d'environnement DATABASE_URL est fournie
    # automatiquement (PostgreSQL) — voir backend/README.md pour le déploiement.
    raw_url = os.environ.get("DATABASE_URL")
    if not raw_url:
        raise RuntimeError(
            "DATABASE_URL n'est pas définie. Ajoute cette variable d'environnement "
            "(fournie automatiquement par Render une fois la base PostgreSQL créée)."
        )

    # Render donne parfois une URL qui commence par "postgres://" — SQLAlchemy veut "postgresql://".
    if raw_url.startswith("postgres://"):
        raw_url = raw_url.replace("postgres://", "postgresql://", 1)

    SQLALCHEMY_DATABASE_URI = raw_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SECRET_KEY = os.environ.get("SECRET_KEY", "change-moi-en-production")

    # Origine(s) autorisée(s) à appeler l'API avec les cookies de session.
    # En local : le frontend ouvert via Live Server ou file:// selon ton setup.
    FRONTEND_ORIGIN = os.environ.get("FRONTEND_ORIGIN", "*")

