from datetime import datetime
from extensions import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(80), nullable=False)
    prenom = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    telephone = db.Column(db.String(30), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)

    # Réinitialisation de mot de passe : token à usage unique + date d'expiration.
    reset_token = db.Column(db.String(255), nullable=True)
    reset_token_expiry = db.Column(db.DateTime, nullable=True)
    # Consentement explicite aux conditions générales et à la politique de confidentialité.
    conditions_acceptees = db.Column(db.Boolean, nullable=False, default=False)

    achats = db.relationship("Purchase", backref="user", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "nom": self.nom,
            "prenom": self.prenom,
            "email": self.email,
            "telephone": self.telephone,
        }


class Formation(db.Model):
    __tablename__ = "formations"

    # id texte (ex: "cyber", "web") pour rester compatible avec le frontend existant
    id = db.Column(db.String(30), primary_key=True)
    titre = db.Column(db.String(120), nullable=False)
    tagline = db.Column(db.String(255))
    description = db.Column(db.Text)
    niveau = db.Column(db.String(50))
    duree = db.Column(db.String(50))
    prix = db.Column(db.Integer, nullable=False)  # en FCFA
    image = db.Column(db.String(255))
    # Lien vers le contenu de la formation (PDF hébergé sur Google Drive, par ex.)
    # — visible uniquement pour les utilisateurs ayant acheté la formation.
    ressource_url = db.Column(db.String(500))
    # Modules du cours, un par ligne (texte brut séparé par des retours à la ligne).
    programme = db.Column(db.Text)

    def to_dict(self):
        # NOTE SÉCURITÉ : ressource_url n'est JAMAIS inclus ici, même pour un
        # utilisateur connecté. L'accès au PDF passe uniquement par la route
        # GET /api/formations/<id>/telecharger, qui vérifie l'achat côté
        # serveur avant de rediriger — ainsi le lien ne peut pas être récupéré
        # depuis les réponses de l'API puis partagé/utilisé sans passer par
        # cette vérification.
        return {
            "id": self.id,
            "titre": self.titre,
            "tagline": self.tagline,
            "description": self.description,
            "niveau": self.niveau,
            "duree": self.duree,
            "prix": self.prix,
            "image": self.image,
            "programme": [l for l in (self.programme or "").split("\n") if l.strip()],
        }


class Purchase(db.Model):
    __tablename__ = "purchases"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    formation_id = db.Column(db.String(30), db.ForeignKey("formations.id"), nullable=False)
    date_achat = db.Column(db.DateTime, default=datetime.utcnow)

    formation = db.relationship("Formation")

    def to_dict(self):
        return {
            "id": self.id,
            "formation": self.formation.to_dict() if self.formation else None,
            "date_achat": self.date_achat.isoformat(),
        }


class Avis(db.Model):
    """Un message laissé par un apprenant dans la section d'avis d'une formation
    qu'il a achetée (affichée comme un petit fil de discussion sur la page
    du cours)."""
    __tablename__ = "avis"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    formation_id = db.Column(db.String(30), db.ForeignKey("formations.id"), nullable=False)
    message = db.Column(db.Text, nullable=False)
    date_envoi = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "auteur": f"{self.user.prenom} {self.user.nom[0]}." if self.user else "Utilisateur",
            "message": self.message,
            "date_envoi": self.date_envoi.isoformat(),
        }


class ContactMessage(db.Model):
    __tablename__ = "contact_messages"

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    sujet = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    date_envoi = db.Column(db.DateTime, default=datetime.utcnow)
