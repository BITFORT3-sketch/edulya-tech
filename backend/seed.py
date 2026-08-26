"""
Script optionnel pour (re)créer les tables et insérer/mettre à jour les 5
formations de départ. Utile si tu veux repeupler la base manuellement — sinon,
app.py le fait déjà tout seul au démarrage.

Utilisation :
    python seed.py
"""

from app import create_app
from extensions import db
from models import Formation

FORMATIONS = [
    dict(
        id="cyber",
        titre="Cybersécurité",
        tagline="Protège systèmes et données : failles, défense et bonnes pratiques.",
        description="Découvre les fondamentaux de la sécurité informatique : comment les systèmes sont attaqués, comment les défendre, et les bons réflexes à adopter au quotidien.",
        niveau="Débutant",
        duree="8 semaines",
        prix=45000,
        image="images/formations/cyber.jpg",
        ressource_url="https://drive.google.com/drive/folders/1_7Q3OjRpMxNbzw0FUW8WTpHN2iC9nf0F?usp=drive_link",
        programme="Bases de la sécurité informatique\nFailles courantes et vecteurs d'attaque\nSécurisation des mots de passe et des accès\nIntroduction aux pare-feux et à la surveillance réseau\nBonnes pratiques et hygiène numérique",
    ),
    dict(
        id="web",
        titre="Développement Web",
        tagline="HTML, CSS, JavaScript et frameworks modernes pour créer des sites complets.",
        description="Apprends à construire des sites web modernes, responsives et professionnels, de la structure HTML jusqu'à l'interactivité en JavaScript.",
        niveau="Débutant",
        duree="10 semaines",
        prix=50000,
        image="images/formations/web.jpg",
        ressource_url="https://drive.google.com/drive/folders/1eFSf8izpyAJ1qUdnwhUj2FwiX2ufds-7?usp=drive_link",
        programme="HTML5 et structure sémantique\nCSS3, mise en page et responsive design\nJavaScript : bases et manipulation du DOM\nIntroduction à un framework moderne\nDéploiement d'un projet complet",
    ),
    dict(
        id="python",
        titre="Python",
        tagline="Automatisation, scripts et fondations solides pour la data et le web.",
        description="Un parcours pratique pour apprendre Python de zéro : syntaxe, logique de programmation, manipulation de données et automatisation.",
        niveau="Débutant",
        duree="6 semaines",
        prix=35000,
        image="images/formations/python.jpg",
        ressource_url="https://drive.google.com/file/d/1OcsNxcc1vOJFDUgHqLoLpJB25_6cAKNt/view?usp=drive_link",
        programme="Syntaxe et bases de Python\nStructures de données (listes, dictionnaires)\nFonctions et modules\nManipulation de fichiers et de données\nIntroduction à l'automatisation de scripts",
    ),
    dict(
        id="ia",
        titre="Intelligence Artificielle",
        tagline="Comprends et construis des modèles d'IA appliqués à des cas réels.",
        description="Explore les concepts clés de l'intelligence artificielle et du machine learning, et construis tes premiers modèles.",
        niveau="Intermédiaire",
        duree="12 semaines",
        prix=65000,
        image="images/formations/ia.jpg",
        ressource_url="https://drive.google.com/drive/folders/1i_EuCO2q9WZQYAVtM0Jb0Lh1gu9cgwgL?usp=drive_link",
        programme="Fondamentaux du machine learning\nManipulation de données avec Python\nModèles de classification et de régression\nIntroduction aux réseaux de neurones\nProjet final appliqué",
    ),
    dict(
        id="reseaux",
        titre="Réseaux & Systèmes",
        tagline="Architecture réseau, administration système et infrastructure.",
        description="Maîtrise les bases des réseaux informatiques et de l'administration système : architecture, protocoles, configuration et supervision.",
        niveau="Intermédiaire",
        duree="9 semaines",
        prix=48000,
        image="images/formations/reseaux.jpg",
        ressource_url="https://drive.google.com/file/d/19Lz9SJ1k0N2v2_bT7WGHFJRHeJc2vlSz/view?usp=drive_link",
        programme="Modèle OSI et protocoles réseau\nConfiguration d'un réseau local\nAdministration système Linux\nSupervision et dépannage réseau\nBonnes pratiques d'infrastructure",
    ),
]


def seed():
    app = create_app()
    with app.app_context():
        db.create_all()

        for data in FORMATIONS:
            existing = Formation.query.get(data["id"])
            if existing:
                for key, value in data.items():
                    setattr(existing, key, value)
            else:
                db.session.add(Formation(**data))

        db.session.commit()
        print(f"{len(FORMATIONS)} formations insérées/mises à jour.")


if __name__ == "__main__":
    seed()
