from datetime import timedelta

from flask import Flask
from sqlalchemy import text
from flask_cors import CORS

from config import Config
from extensions import db

from routes.auth import auth_bp
from routes.formations import formations_bp
from routes.achats import achats_bp
from routes.contact import contact_bp
from routes.avis import avis_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Nécessaire pour envoyer/recevoir le cookie de session depuis le frontend
    # (ex: fetch avec { credentials: "include" }).
    app.config["SESSION_COOKIE_SAMESITE"] = "None"
    app.config["SESSION_COOKIE_SECURE"] = True  # True en production (HTTPS sur Render)

    CORS(
        app,
        resources={r"/api/*": {"origins": ["https://edulya-tech-1.onrender.com"]}}, 
        supports_credentials=True
    )

    # L'utilisateur reste connecté 30 jours (session "permanente" côté Flask) —
    # il ne doit être déconnecté que s'il clique lui-même sur "Se déconnecter".
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=30)

    db.init_app(app)

    # ----- Sécurité : avertissements au démarrage -----
    # Ces valeurs par défaut sont pratiques en local mais NE DOIVENT PAS
    # rester telles quelles une fois le site déployé pour de vrai.
    if Config.SECRET_KEY == "change-moi-en-production":
        print("[SÉCURITÉ] ATTENTION : SECRET_KEY utilise encore la valeur par défaut. "
              "Définis une vraie valeur secrète dans les variables d'environnement avant le déploiement final.")
    if Config.FRONTEND_ORIGIN == "*":
        print("[SÉCURITÉ] ATTENTION : FRONTEND_ORIGIN autorise toutes les origines ('*'). "
              "Remplace-la par l'URL exacte de ton frontend une fois déployé.")

    # ----- Sécurité : en-têtes HTTP de base -----
    # Protections simples et sans risque de casser le site (contrairement à
    # une politique CSP stricte, qui demanderait d'auditer tous les scripts
    # inline utilisés pour le thème clair/sombre).
    @app.after_request
    def ajouter_headers_securite(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response

    # ----- Sécurité : ne jamais renvoyer de trace technique au client -----
    @app.errorhandler(500)
    def erreur_serveur(e):
        return {"error": "Une erreur interne est survenue."}, 500

    app.register_blueprint(auth_bp)
    app.register_blueprint(formations_bp)
    app.register_blueprint(achats_bp)
    app.register_blueprint(contact_bp)
    app.register_blueprint(avis_bp)

    @app.route("/api/health", methods=["GET"])
    def health():
        return {"status": "ok"}, 200

    # Crée les tables et insère le catalogue de formations au premier démarrage.
    # Comme ça, aucune commande manuelle (seed.py) n'est nécessaire sur Render :
    # le simple déploiement suffit à préparer la base de données.
    with app.app_context():
        db.create_all()
        _ajouter_colonne_consentement_si_necessaire()
        _seed_formations_if_needed()

    return app



def _ajouter_colonne_consentement_si_necessaire():
    """Ajoute la colonne de consentement aux bases déjà créées.

    db.create_all() ne modifie pas les tables existantes ; cette migration
    permet de déployer la nouvelle fonctionnalité sans perdre les comptes.
    """
    with db.engine.begin() as conn:
        if db.engine.dialect.name == "postgresql":
            conn.execute(text(
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS "
                "conditions_acceptees BOOLEAN NOT NULL DEFAULT FALSE"
            ))
        elif db.engine.dialect.name == "sqlite":
            colonnes = conn.execute(text("PRAGMA table_info(users)")).fetchall()
            noms = {row[1] for row in colonnes}
            if "conditions_acceptees" not in noms:
                conn.execute(text(
                    "ALTER TABLE users ADD COLUMN conditions_acceptees BOOLEAN NOT NULL DEFAULT 0"
                ))


def _seed_formations_if_needed():
    from models import Formation

    if Formation.query.first():
        return  # déjà peuplée, on ne touche à rien

    formations = [
        dict(id="cyber", titre="Cybersécurité",
             tagline="Protège systèmes et données : failles, défense et bonnes pratiques.",
             description="Découvre les fondamentaux de la sécurité informatique : comment les systèmes sont attaqués, comment les défendre, et les bons réflexes à adopter au quotidien.",
             niveau="Débutant", duree="8 semaines", prix=45000, image="images/formations/cyber.jpg",
             ressource_url="https://drive.google.com/drive/folders/1_7Q3OjRpMxNbzw0FUW8WTpHN2iC9nf0F?usp=drive_link",
             programme="Bases de la sécurité informatique\nFailles courantes et vecteurs d'attaque\nSécurisation des mots de passe et des accès\nIntroduction aux pare-feux et à la surveillance réseau\nBonnes pratiques et hygiène numérique"),
        dict(id="web", titre="Développement Web",
             tagline="HTML, CSS, JavaScript et frameworks modernes pour créer des sites complets.",
             description="Apprends à construire des sites web modernes, responsives et professionnels, de la structure HTML jusqu'à l'interactivité en JavaScript.",
             niveau="Débutant", duree="10 semaines", prix=50000, image="images/formations/web.jpg",
             ressource_url="https://drive.google.com/drive/folders/1eFSf8izpyAJ1qUdnwhUj2FwiX2ufds-7?usp=drive_link",
             programme="HTML5 et structure sémantique\nCSS3, mise en page et responsive design\nJavaScript : bases et manipulation du DOM\nIntroduction à un framework moderne\nDéploiement d'un projet complet"),
        dict(id="python", titre="Python",
             tagline="Automatisation, scripts et fondations solides pour la data et le web.",
             description="Un parcours pratique pour apprendre Python de zéro : syntaxe, logique de programmation, manipulation de données et automatisation.",
             niveau="Débutant", duree="6 semaines", prix=35000, image="images/formations/python.jpg",
             ressource_url="https://drive.google.com/file/d/1OcsNxcc1vOJFDUgHqLoLpJB25_6cAKNt/view?usp=drive_link",
             programme="Syntaxe et bases de Python\nStructures de données (listes, dictionnaires)\nFonctions et modules\nManipulation de fichiers et de données\nIntroduction à l'automatisation de scripts"),
        dict(id="ia", titre="Intelligence Artificielle",
             tagline="Comprends et construis des modèles d'IA appliqués à des cas réels.",
             description="Explore les concepts clés de l'intelligence artificielle et du machine learning, et construis tes premiers modèles.",
             niveau="Intermédiaire", duree="12 semaines", prix=65000, image="images/formations/ia.jpg",
             ressource_url="https://drive.google.com/drive/folders/1i_EuCO2q9WZQYAVtM0Jb0Lh1gu9cgwgL?usp=drive_link",
             programme="Fondamentaux du machine learning\nManipulation de données avec Python\nModèles de classification et de régression\nIntroduction aux réseaux de neurones\nProjet final appliqué"),
        dict(id="reseaux", titre="Réseaux & Systèmes",
             tagline="Architecture réseau, administration système et infrastructure.",
             description="Maîtrise les bases des réseaux informatiques et de l'administration système : architecture, protocoles, configuration et supervision.",
             niveau="Intermédiaire", duree="9 semaines", prix=48000, image="images/formations/reseaux.jpg",
             ressource_url="https://drive.google.com/file/d/19Lz9SJ1k0N2v2_bT7WGHFJRHeJc2vlSz/view?usp=drive_link",
             programme="Modèle OSI et protocoles réseau\nConfiguration d'un réseau local\nAdministration système Linux\nSupervision et dépannage réseau\nBonnes pratiques d'infrastructure"),
    ]

    for data in formations:
        db.session.add(Formation(**data))
    db.session.commit()


app = create_app()

if __name__ == "__main__":
    import os
    # En local, le mode debug est activé par défaut (pratique pour voir les erreurs).
    # Sur Render, ce bloc n'est JAMAIS exécuté (gunicorn lance directement `app`),
    # donc le debug n'est jamais actif en production, quoi qu'il arrive.
    debug_mode = os.environ.get("FLASK_DEBUG", "true").lower() == "true"
    app.run(debug=debug_mode, port=5000)
